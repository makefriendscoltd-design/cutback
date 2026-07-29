/**
 * Lightweight cut recompute.
 *
 * Live Analysis Timeline 의 threshold 슬라이더가 값을 바꿀 때마다 전체 pipeline 을
 * 다시 돌리는 건 너무 비싸다 (오디오 추출 + STT + spell check = 분 단위).
 *
 * 대신 이미 추출된 audio file 과 STT transcript 를 재사용해서
 *   - silence detection 만 다시 (ffmpeg silencedetect; 1~2초)
 *   - filler detection 만 다시 (transcript 만 사용; 즉시)
 * 를 수행하고 새 CutDecision 배열을 돌려준다.
 *
 * 결과는 곧바로 overlay 에 반영해도 비파괴적이다 — 우리 pipeline 은 ffmpeg 편집을
 * 호출하지 않고 cut decision 만 만들기 때문.
 */

import {
  RecomputeRequest,
  RecomputeResult,
  CutDecision,
  Preset,
  createLogger,
} from '@cutback/shared';
import { detectSilence } from '@cutback/audio-engine';
import { detectFillers } from '@cutback/transcript-engine';
import { presetLoader } from '@cutback/preset-manager';
import { v4 as uuidv4 } from 'uuid';
import { getCalibrationRepository } from './calibration';

const logger = createLogger('recompute');

export async function recomputeCuts(req: RecomputeRequest): Promise<RecomputeResult> {
  const startedAt = Date.now();
  const recomputed: ('silence' | 'filler')[] = [];

  try {
    // base preset load
    let basePreset: Preset;
    try {
      basePreset = await presetLoader.load(req.presetId);
    } catch (err) {
      return {
        success: false,
        recomputed: [],
        durationMs: Date.now() - startedAt,
        error: `Preset not found: ${req.presetId}`,
      };
    }

    let silenceCuts: CutDecision[] | undefined;
    let fillerCuts: CutDecision[] | undefined;

    // ----- silence -----
    if (basePreset.audio || req.overrides.audio) {
      const audio = {
        ...(basePreset.audio ?? {}),
        ...(req.overrides.audio ?? {}),
      };
      // 필수 필드 보강 (override 만 부분으로 와도 detectSilence 가 동작하도록)
      const audioParams = {
        silence_threshold_db: audio.silence_threshold_db ?? -35,
        min_silence_duration_ms: audio.min_silence_duration_ms ?? 400,
        pre_cut_padding_ms: audio.pre_cut_padding_ms ?? 100,
        post_cut_padding_ms: audio.post_cut_padding_ms ?? 100,
      };
      const silenceResults = await detectSilence(req.audioPath, audioParams);
      const presetRule =
        `audio.silence_threshold_db=${audioParams.silence_threshold_db}, ` +
        `min_silence_duration_ms=${audioParams.min_silence_duration_ms} (preview)`;
      silenceCuts = silenceResults.map((s) => ({
        id: uuidv4(),
        type: 'silence' as const,
        start: s.timestamp,
        end: s.timestamp + s.duration,
        duration: s.duration,
        confidence: s.confidence,
        reason: 'silence_over_threshold' as const,
        reasonText: `무음 ${s.duration.toFixed(2)}s (${s.db_level.toFixed(1)} dB)`,
        source: 'automatic' as const,
        presetRule,
        metadata: { db_level: s.db_level },
        enabled: true,
        user_approved: false,
      }));
      recomputed.push('silence');
    }

    // ----- filler -----
    if (req.transcript && (basePreset.filler_words || req.overrides.filler_words)) {
      const fw = {
        ...(basePreset.filler_words ?? {}),
        ...(req.overrides.filler_words ?? {}),
      };
      const fillerParams = {
        removal_strength: fw.removal_strength ?? 'balanced',
        context_aware: fw.context_aware ?? true,
        preserve_natural_pauses: fw.preserve_natural_pauses ?? true,
        custom_fillers: fw.custom_fillers,
        confidence_threshold: fw.confidence_threshold,
        min_removable_duration_ms: fw.min_removable_duration_ms,
      };
      const presetRule =
        `filler_words.removal_strength=${fillerParams.removal_strength} (preview)`;
      const raw = await detectFillers(req.transcript, fillerParams);

      // Calibration: 사용자가 자주 복원한 단어는 자동 제거 후보에서 제외
      // (≥ 2회 복원한 단어를 학습값으로 인정)
      let restoredWords = new Set<string>();
      try {
        const cal = await getCalibrationRepository().get(req.presetId);
        if (cal) {
          for (const [word, count] of Object.entries(cal.restoredFillers)) {
            if (count >= 2) restoredWords.add(word);
          }
        }
      } catch {
        // calibration repo 가 없는 환경에서도 동작해야 함
      }

      fillerCuts = raw
        .filter((c) => {
          const text = c.metadata?.filler_text;
          if (typeof text === 'string' && restoredWords.has(text)) {
            // 학습됨: 자동 제거 안 함
            return false;
          }
          return true;
        })
        .map((c) => ({
          ...c,
          reason: c.reason ?? 'filler_detected',
          reasonText: c.reasonText ?? `말버릇 "${c.metadata?.filler_text ?? '?'}"`,
          source: c.source ?? 'automatic',
          presetRule: c.presetRule ?? presetRule,
        }));

      if (restoredWords.size > 0) {
        logger.info('Calibration applied to filler detection', {
          presetId: req.presetId,
          skippedWords: Array.from(restoredWords),
        });
      }
      recomputed.push('filler');
    }

    const durationMs = Date.now() - startedAt;
    logger.info('Recompute done', {
      jobId: req.jobId,
      recomputed,
      silence: silenceCuts?.length,
      filler: fillerCuts?.length,
      durationMs,
    });

    return {
      success: true,
      silenceCuts,
      fillerCuts,
      recomputed,
      durationMs,
    };
  } catch (err) {
    return {
      success: false,
      recomputed,
      durationMs: Date.now() - startedAt,
      error: (err as Error).message,
    };
  }
}
