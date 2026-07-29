import path from 'path';
import os from 'os';
import { spawn } from 'child_process';
import {
  Job,
  JobResults,
  Transcript,
  CutDecision,
  Caption,
  Preset,
  Statistics,
  createLogger,
  AUDIO_DEFAULTS,
  resolveFfmpegPath,
  describeFfmpegSource,
} from '@cutback/shared';
import { detectSilence } from '@cutback/audio-engine';
import { detectFillers, detectRetakes } from '@cutback/transcript-engine';
import { PythonClient } from './python-client';
import { v4 as uuidv4 } from 'uuid';

const logger = createLogger('pipeline');

/**
 * Pipeline 단계별 부분 결과.
 * Live Analysis Timeline 이 분석 중에도 단계별로 결과를 화면에 그리도록
 * 각 단계가 끝날 때마다 onProgress 의 4번째 인자로 partial 을 넘긴다.
 */
export interface PipelinePartial {
  /** 추출된 오디오 경로 (waveform 추출용). */
  audioPath?: string;
  silenceCuts?: CutDecision[];
  transcript?: Transcript;
  fillerCuts?: CutDecision[];
  retakeCuts?: CutDecision[];
  captionSegments?: CutDecision[];
}

export type ProgressCallback = (
  stage: string,
  progress: number,
  detail?: string,
  partial?: PipelinePartial
) => void;

/**
 * 영상 처리 파이프라인
 *
 * 1. 오디오 추출 (ffmpeg)
 * 2. 무음 감지
 * 3. STT (Whisper)
 * 4. Filler word 감지
 * 5. Retake 감지
 * 6. Cut decision 병합
 * 7. 자막 세그먼트 생성
 * 8. 통계 계산
 */
export class ProcessingPipeline {
  private pythonClient: PythonClient;

  constructor() {
    this.pythonClient = new PythonClient();
  }

  async execute(
    job: Job,
    preset: Preset,
    onProgress?: ProgressCallback
  ): Promise<JobResults> {
    const videoPath = job.videoPath;

    logger.info('Pipeline started', {
      jobId: job.id,
      video: videoPath,
      preset: preset.name,
    });

    // --- Stage 1: 오디오 추출 ---
    onProgress?.('audio_extract', 5, '오디오 추출 중...');
    const audioPath = await this.extractAudio(videoPath, job.id);
    logger.info('Audio extracted', { audioPath });
    onProgress?.('audio_extract', 10, '오디오 추출 완료', { audioPath });

    // --- Stage 2: 무음 감지 ---
    onProgress?.('silence_detect', 20, '무음 구간 분석 중...');
    if (!preset.audio) {
      throw new Error('Mode A preset requires audio parameters');
    }
    const silenceResults = await detectSilence(audioPath, preset.audio);
    const silencePresetRule =
      `audio.silence_threshold_db=${preset.audio.silence_threshold_db}, ` +
      `min_silence_duration_ms=${preset.audio.min_silence_duration_ms}`;
    const silenceCuts: CutDecision[] = silenceResults.map((s) => ({
      id: uuidv4(),
      type: 'silence',
      start: s.timestamp,
      end: s.timestamp + s.duration,
      duration: s.duration,
      confidence: s.confidence,
      reason: 'silence_over_threshold',
      reasonText: `무음 ${s.duration.toFixed(2)}s (${s.db_level.toFixed(1)} dB)`,
      source: 'automatic',
      presetRule: silencePresetRule,
      metadata: { db_level: s.db_level },
      enabled: true,
      user_approved: false,
    }));
    logger.info('Silence detected', { count: silenceCuts.length });
    onProgress?.('silence_detect', 35, `무음 ${silenceCuts.length}개 감지`, {
      silenceCuts,
    });

    // --- Stage 3: STT ---
    onProgress?.('stt', 40, 'AI 음성 인식 중...');
    let transcript: Transcript;
    try {
      transcript = await this.pythonClient.transcribe(audioPath, 'ko');
    } catch (err) {
      logger.warn('Python STT failed, using stub transcript', {
        error: (err as Error).message,
      });
      transcript = this.createStubTranscript();
    }
    logger.info('Transcript generated', {
      words: transcript.words.length,
      duration: transcript.duration,
    });
    onProgress?.('stt', 48, `${transcript.words.length}개 단어 인식 완료`, {
      transcript,
    });

    // --- Stage 4: Filler word 감지 ---
    // detectFillers 는 confidence 점수를 매겨
    //   - threshold 이상: enabled=true (자동 적용)
    //   - review_band: enabled=false + reviewRequired=true (UI 에서 사용자가 토글)
    //   - protected_words 와 너무 짧은 단어는 후보에서 제외
    onProgress?.('filler_detect', 50, '말버릇 분석 중...');
    if (!preset.filler_words) {
      throw new Error('Mode A preset requires filler_words parameters');
    }
    const fillerCutsRaw = await detectFillers(transcript, preset.filler_words);
    const fillerPresetRule =
      `filler_words.removal_strength=${preset.filler_words.removal_strength}` +
      (preset.filler_words.confidence_threshold !== undefined
        ? `, confidence_threshold=${preset.filler_words.confidence_threshold}`
        : '');
    const fillerCuts: CutDecision[] = fillerCutsRaw.map((c) => ({
      ...c,
      reason: c.reason ?? 'filler_detected',
      reasonText:
        c.reasonText ?? `말버릇 "${c.metadata?.filler_text ?? '?'}" 감지`,
      source: c.source ?? 'automatic',
      presetRule: c.presetRule ?? fillerPresetRule,
    }));
    const autoFillers = fillerCuts.filter((c) => c.enabled).length;
    const reviewFillers = fillerCuts.filter((c) => c.reviewRequired).length;
    logger.info('Fillers detected', {
      total: fillerCuts.length,
      auto: autoFillers,
      review: reviewFillers,
    });
    onProgress?.(
      'filler_detect',
      62,
      `말버릇 ${fillerCuts.length}개 감지 (자동 ${autoFillers}, 검수 ${reviewFillers})`,
      { fillerCuts }
    );

    // --- Stage 5: Retake 감지 ---
    onProgress?.('retake_detect', 65, '재시도 구간 분석 중...');
    const retakeCutsRaw = await detectRetakes(transcript);
    const retakeCuts: CutDecision[] = retakeCutsRaw.map((c) => ({
      ...c,
      reason: c.reason ?? 'duplicate_phrase',
      reasonText: c.reasonText ?? '중복 발화 (재시도 후보)',
      source: c.source ?? 'automatic',
      presetRule: c.presetRule ?? 'retake.duplicate_detection',
    }));
    logger.info('Retakes detected', { count: retakeCuts.length });
    onProgress?.('retake_detect', 72, `재시도 ${retakeCuts.length}개 감지`, {
      retakeCuts,
    });

    // --- Stage 6: Cut decision 병합 ---
    onProgress?.('merge_cuts', 75, '편집 포인트 계산 중...');
    const allCuts = this.mergeCutDecisions(silenceCuts, fillerCuts, retakeCuts);
    logger.info('Cut decisions merged', { total: allCuts.length });

    // --- Stage 7: 자막 생성 ---
    onProgress?.('captions', 85, '자막 생성 중...');
    let captions = this.generateCaptions(transcript, preset, allCuts);
    logger.info('Captions generated', { count: captions.length });

    // 자막 세그먼트 boundary 를 timeline overlay 에서 표시할 수 있도록
    // CutDecision 형태로도 변환 (enabled=false: 실제 cut 이 아니라 표시용).
    const captionSegments: CutDecision[] = captions.map((cap) => ({
      id: `caption-${cap.id}`,
      type: 'caption_segment',
      start: cap.start,
      end: cap.end,
      duration: cap.end - cap.start,
      confidence: 1.0,
      reason: 'caption_segment',
      reasonText: cap.text,
      source: 'automatic',
      presetRule: preset.captions
        ? `captions.segmentation_mode=${preset.captions.segmentation_mode}, ` +
          `max_chars_per_line=${preset.captions.max_chars_per_line}`
        : undefined,
      metadata: {
        caption_text: cap.text,
      },
      enabled: false, // 자막은 cut 이 아님 (표시용)
      user_approved: false,
    }));
    onProgress?.('captions', 88, `자막 ${captions.length}개 생성`, {
      captionSegments,
    });

    // --- Stage 7.5: 자막 한국어 맞춤법 교정 ---
    // STT 원본 오타를 자막 단계에서만 후처리로 보정한다.
    // (음성/타임스탬프는 그대로 두므로 안전)
    if (captions.length > 0) {
      onProgress?.('spell_check', 90, '한국어 맞춤법 교정 중...');
      try {
        const original = captions.map((c) => c.text);
        const corrected = await this.pythonClient.spellCheck(original);
        let changed = 0;
        captions = captions.map((cap, i) => {
          const fixed = corrected[i] ?? cap.text;
          if (fixed !== cap.text) changed++;
          return { ...cap, text: fixed };
        });
        logger.info('Captions spell-checked', {
          total: captions.length,
          changed,
        });
      } catch (err) {
        logger.warn('Spell check skipped', {
          error: (err as Error).message,
        });
      }
    }

    // --- Stage 8: 통계 계산 ---
    onProgress?.('statistics', 95, '결과 정리 중...');
    const originalDuration = transcript.duration || this.estimateDuration(allCuts);
    const stats = this.calculateStatistics(allCuts, originalDuration);

    const results: JobResults = {
      transcript,
      cutDecisions: allCuts,
      captions,
      naturalness_score: stats.naturalness_score,
      statistics: stats,
    };

    onProgress?.('complete', 100, '완료!');
    logger.info('Pipeline completed', {
      jobId: job.id,
      stats,
    });

    return results;
  }

  /**
   * ffmpeg로 영상에서 오디오만 추출
   * WAV 16kHz mono (Whisper 권장 포맷)
   *
   * 한국어 등 비-ASCII 파일명 문제를 피하기 위해
   * temp 디렉토리에 ASCII 이름으로 추출
   */
  private extractAudio(videoPath: string, jobId?: string): Promise<string> {
    return new Promise((resolve, reject) => {
      // ASCII-safe temp path 사용 (한국어 파일명 인코딩 문제 방지)
      const safeName = `cutback_${jobId || Date.now()}.wav`;
      const audioPath = path.join(os.tmpdir(), safeName);

      const args = [
        '-i', videoPath,
        '-vn',                // 비디오 제거
        '-acodec', 'pcm_s16le',
        '-ar', String(AUDIO_DEFAULTS.SAMPLE_RATE),
        '-ac', String(AUDIO_DEFAULTS.CHANNELS),
        '-y',                 // 덮어쓰기
        audioPath,
      ];

      const ffmpegBinary = resolveFfmpegPath();
      if (!ffmpegBinary) {
        reject(
          new Error(
            'ffmpeg 실행 파일을 찾지 못했습니다. `pnpm install` 로 ffmpeg-static 이 설치됐는지 확인하거나 시스템 PATH 에 ffmpeg 를 추가하세요.'
          )
        );
        return;
      }

      const proc = spawn(ffmpegBinary, args);
      logger.debug('Extracting audio', { binary: describeFfmpegSource() });

      let stderr = '';
      proc.stderr.on('data', (data: Buffer) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        if (code === 0) {
          resolve(audioPath);
        } else {
          reject(new Error(`ffmpeg failed (code ${code}): ${stderr.slice(-500)}`));
        }
      });

      proc.on('error', (err) => {
        reject(
          new Error(
            `ffmpeg 실행 실패 (${ffmpegBinary}): ${err.message}. \`pnpm install\` 로 ffmpeg-static 재설치하세요.`
          )
        );
      });
    });
  }

  /**
   * STT 실패 시 빈 transcript 반환
   */
  private createStubTranscript(): Transcript {
    return {
      words: [],
      full_text: '',
      language: 'ko',
      duration: 0,
    };
  }

  /**
   * 모든 컷 타입 병합 및 정렬
   * 겹치는 구간은 하나로 합침
   */
  private mergeCutDecisions(
    silenceCuts: CutDecision[],
    fillerCuts: CutDecision[],
    retakeCuts: CutDecision[] = []
  ): CutDecision[] {
    const all = [...silenceCuts, ...fillerCuts, ...retakeCuts].sort(
      (a, b) => a.start - b.start
    );

    if (all.length === 0) return [];

    // 겹치는 구간 병합
    const merged: CutDecision[] = [all[0]];
    for (let i = 1; i < all.length; i++) {
      const prev = merged[merged.length - 1];
      const curr = all[i];

      if (curr.start <= prev.end) {
        // 겹침 - 더 긴 구간으로 확장
        if (curr.end > prev.end) {
          prev.end = curr.end;
          prev.duration = prev.end - prev.start;
        }
      } else {
        merged.push(curr);
      }
    }

    return merged;
  }

  /**
   * 원본 timeline의 시간을 컷이 적용된 후의 timeline 시간으로 변환
   * (해당 시간 이전의 모든 enabled cut duration 만큼 빼줌)
   */
  private mapToEditedTime(originalTime: number, enabledCuts: CutDecision[]): number {
    let removed = 0;
    for (const cut of enabledCuts) {
      if (cut.end <= originalTime) {
        removed += cut.duration;
      } else if (cut.start < originalTime) {
        // originalTime이 cut 내부에 있는 경우 cut 시작점으로 clamp
        return Math.max(0, cut.start - removed);
      } else {
        break;
      }
    }
    return Math.max(0, originalTime - removed);
  }

  /**
   * Transcript에서 자막 세그먼트 생성
   *
   * 캡션의 start/end는 컷이 적용된 후의 timeline 시간으로 매핑된다.
   * (CapCut import 시 자막이 영상과 동기화되도록)
   */
  private generateCaptions(
    transcript: Transcript,
    preset: Preset,
    cutDecisions: CutDecision[]
  ): Caption[] {
    const { words } = transcript;
    if (words.length === 0) return [];

    if (!preset.captions) {
      throw new Error('Mode A preset requires captions parameters');
    }

    const rawCaptions: Caption[] = [];
    // 사용자 요구: 자막은 무조건 한 줄.
    // max_lines 가 무엇이든 한 줄 분량(max_chars_per_line)으로만 끊는다.
    const maxChars = preset.captions.max_chars_per_line;
    const mode = preset.captions.segmentation_mode;

    // enabled cuts 시간순 정렬
    const enabledCuts = cutDecisions
      .filter((c) => c.enabled)
      .sort((a, b) => a.start - b.start);

    // 컷 구간에 포함되지 않는 단어만 필터
    const activeWords = words.filter((word) => {
      return !enabledCuts.some(
        (cut) => word.start >= cut.start && word.end <= cut.end
      );
    });

    if (activeWords.length === 0) return [];

    if (mode === 'by_sentence') {
      // 문장 단위 끊기 (마침표/쉼표/물음표 + 호흡 + 글자 수 한도)
      // 한국어 STT 는 구두점이 거의 없으므로 호흡(pause)도 끊는 신호로 사용.
      let buffer: typeof activeWords = [];

      for (let i = 0; i < activeWords.length; i++) {
        const word = activeWords[i];
        buffer.push(word);
        const text = buffer.map((w) => w.text).join(' ');
        const nextWord = activeWords[i + 1];
        const gap = nextWord ? nextWord.start - word.end : Infinity;

        const isSentenceEnd =
          /[.!?。？！,，、]$/.test(word.text) ||
          text.length >= maxChars ||
          gap >= 0.6 ||
          i === activeWords.length - 1;

        if (isSentenceEnd && buffer.length > 0) {
          rawCaptions.push({
            id: uuidv4(),
            text: buffer.map((w) => w.text).join(' '),
            start: buffer[0].start,
            end: buffer[buffer.length - 1].end,
          });
          buffer = [];
        }
      }
    } else if (mode === 'by_time') {
      // 시간 단위 끊기 (3~4초)
      const maxDuration = 4;
      let buffer: typeof activeWords = [];

      for (const word of activeWords) {
        buffer.push(word);
        const duration = word.end - buffer[0].start;

        if (duration >= maxDuration || buffer.map((w) => w.text).join(' ').length >= maxChars) {
          rawCaptions.push({
            id: uuidv4(),
            text: buffer.map((w) => w.text).join(' '),
            start: buffer[0].start,
            end: buffer[buffer.length - 1].end,
          });
          buffer = [];
        }
      }

      if (buffer.length > 0) {
        rawCaptions.push({
          id: uuidv4(),
          text: buffer.map((w) => w.text).join(' '),
          start: buffer[0].start,
          end: buffer[buffer.length - 1].end,
        });
      }
    } else {
      // by_breath: pause 기반 끊기
      let buffer: typeof activeWords = [];

      for (let i = 0; i < activeWords.length; i++) {
        buffer.push(activeWords[i]);

        const nextWord = activeWords[i + 1];
        const gap = nextWord ? nextWord.start - activeWords[i].end : Infinity;
        const text = buffer.map((w) => w.text).join(' ');

        // pause가 0.3초 이상이거나 글자 수 초과하면 끊기
        if (gap > 0.3 || text.length >= maxChars || i === activeWords.length - 1) {
          rawCaptions.push({
            id: uuidv4(),
            text,
            start: buffer[0].start,
            end: buffer[buffer.length - 1].end,
          });
          buffer = [];
        }
      }
    }

    // 원본 timeline 시간 → 컷 후 timeline 시간으로 변환 + 스타일 적용
    return rawCaptions
      .map((cap) => {
        const newStart = this.mapToEditedTime(cap.start, enabledCuts);
        const newEnd = this.mapToEditedTime(cap.end, enabledCuts);
        return {
          ...cap,
          start: newStart,
          end: newEnd,
          style: preset.style,
        };
      })
      .filter((cap) => cap.end > cap.start); // 빈 자막 제거
  }

  /**
   * 통계 계산
   */
  private calculateStatistics(
    cutDecisions: CutDecision[],
    originalDuration: number
  ): Statistics {
    const enabledCuts = cutDecisions.filter((c) => c.enabled);
    const silenceRemoved = enabledCuts.filter((c) => c.type === 'silence');
    const fillersRemoved = enabledCuts.filter((c) => c.type === 'filler_word');
    const retakesRemoved = enabledCuts.filter((c) => c.type === 'retake');

    const totalRemovedTime = enabledCuts.reduce(
      (sum, c) => sum + c.duration,
      0
    );
    const editedDuration = Math.max(0, originalDuration - totalRemovedTime);
    const cutFrequency =
      originalDuration > 0
        ? enabledCuts.length / (originalDuration / 60)
        : 0;

    // 자연스러움 점수
    const naturalness = this.calculateNaturalnessScore(
      enabledCuts,
      originalDuration
    );

    return {
      original_duration: originalDuration,
      edited_duration: editedDuration,
      silence_removed: silenceRemoved.length,
      fillers_removed: fillersRemoved.length,
      retakes_removed: retakesRemoved.length,
      total_cuts: enabledCuts.length,
      cut_frequency: Math.round(cutFrequency * 10) / 10,
      naturalness_score: naturalness,
    };
  }

  /**
   * 자연스러움 점수 (0.0 ~ 1.0)
   */
  private calculateNaturalnessScore(
    cuts: CutDecision[],
    originalDuration: number
  ): number {
    if (originalDuration === 0 || cuts.length === 0) return 1.0;

    let score = 1.0;

    // 1. 과도한 컷 빈도 페널티 (분당 20회 초과)
    const cutsPerMinute = cuts.length / (originalDuration / 60);
    if (cutsPerMinute > 20) {
      score -= (cutsPerMinute - 20) * 0.01;
    }

    // 2. 너무 짧은 구간 페널티
    for (const cut of cuts) {
      if (cut.duration < 0.3) {
        score -= 0.02;
      }
    }

    // 3. 연속 컷 페널티
    for (let i = 0; i < cuts.length - 1; i++) {
      const gap = cuts[i + 1].start - cuts[i].end;
      if (gap < 0.5) {
        score -= 0.03;
      }
    }

    // 4. 전체 제거 비율 페널티 (50% 이상 제거는 과편집)
    const totalRemoved = cuts.reduce((sum, c) => sum + c.duration, 0);
    const removalRatio = totalRemoved / originalDuration;
    if (removalRatio > 0.5) {
      score -= (removalRatio - 0.5) * 0.3;
    }

    return Math.max(0, Math.min(1, Math.round(score * 100) / 100));
  }

  /**
   * Cut decisions로부터 원본 영상 길이 추정
   */
  private estimateDuration(cuts: CutDecision[]): number {
    if (cuts.length === 0) return 0;
    return Math.max(...cuts.map((c) => c.end)) + 5;
  }
}
