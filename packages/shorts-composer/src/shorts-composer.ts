/**
 * Shorts Composer — 오케스트레이션
 *
 * 클립 여러 개 → 정규화(9:16) → concat → 자막 하드번 + 오디오 먹싱 → mp4 (FHD/4K)
 *
 * 파이프라인 (MoneyPrinterTurbo / editly 의 조립 방식 참고):
 *  1. probe      : 각 클립 + 보이스오버 길이 측정
 *  2. plan       : 목표 총길이에 맞춰 세그먼트 계획 (클립 순환, 커서 전진)
 *  3. normalize  : 세그먼트별 9:16 통일 조각 생성 (병렬 아님 — ffmpeg가 코어를 다 씀)
 *  4. concat     : concat demuxer 로 무재인코딩 이어붙이기
 *  5. render     : ASS 자막 하드번 + 오디오 트랙 + 최종 인코딩 (한 번만 재인코딩)
 */

import { mkdir, writeFile, rm } from 'fs/promises';
import { existsSync } from 'fs';
import { createHash } from 'crypto';
import path from 'path';
import os from 'os';
import { createLogger } from '@cutback/shared';
import {
  RESOLUTION_MAP,
  type ShortsCompositionSpec,
  type ComposeProgressCallback,
  type ComposeResult,
  type SegmentPlan,
  type SubtitleEvent,
} from './types.js';
import {
  getFfmpeg,
  probeMedia,
  normalizeClip,
  runFfmpeg,
} from './clip-normalizer.js';
import {
  buildSubtitleEvents,
  generateAss,
  generateSrt,
} from './subtitle-engine.js';
import { getFont, getFontsDir, isFontAvailable } from './fonts.js';

const logger = createLogger('shorts-composer');

const DEFAULT_CLIP_RANGE = { min: 1.0, max: 2.5 };
const MAX_SEGMENTS = 300;

/** ffmpeg 필터 인자 안 파일경로 이스케이프 (Windows 드라이브 콜론 포함) */
function escapeForFilter(p: string): string {
  return p.replace(/\\/g, '/').replace(/:/g, '\\:').replace(/'/g, "\\'");
}

function tempWorkDir(spec: ShortsCompositionSpec): string {
  const hash = createHash('sha1')
    .update(JSON.stringify(spec))
    .update(String(process.pid))
    .digest('hex')
    .slice(0, 12);
  return path.join(os.tmpdir(), 'cutback-shorts', hash);
}

/**
 * 세그먼트 계획: 클립을 순환하며 targetDuration 을 채운다.
 * 같은 클립을 재사용할 땐 소스 커서를 전진시켜 같은 구간 반복을 피한다.
 */
export function planSegments(
  clips: Array<{ path: string; duration: number }>,
  range: { min: number; max: number },
  targetDuration?: number
): SegmentPlan[] {
  const segments: SegmentPlan[] = [];

  if (targetDuration === undefined) {
    // 목표 없음: 각 클립 1회, min~max 로 트림
    for (const c of clips) {
      segments.push({
        clipPath: c.path,
        sourceStart: 0,
        duration: Math.min(c.duration, range.max),
      });
    }
    return segments;
  }

  const cursors = new Map<string, number>();
  let remaining = targetDuration;
  let i = 0;
  while (remaining > 0.05 && segments.length < MAX_SEGMENTS) {
    const clip = clips[i % clips.length];
    i++;
    const d = Math.min(range.max, clip.duration, remaining);
    if (d < 0.15) break;

    let start = cursors.get(clip.path) ?? 0;
    if (start + d > clip.duration) start = 0; // 남은 소스 부족 → 처음부터
    cursors.set(clip.path, start + d);

    segments.push({ clipPath: clip.path, sourceStart: start, duration: d });
    remaining -= d;
  }
  return segments;
}

export class ShortsComposer {
  async compose(
    spec: ShortsCompositionSpec,
    onProgress?: ComposeProgressCallback
  ): Promise<ComposeResult> {
    if (!spec.clips || spec.clips.length === 0) {
      throw new Error('At least one clip is required');
    }
    for (const c of spec.clips) {
      if (!existsSync(c)) throw new Error(`Clip not found: ${c}`);
    }
    getFfmpeg(); // 없으면 여기서 명확히 throw

    const { width, height } = RESOLUTION_MAP[spec.resolution ?? 'fhd'];
    const fps = spec.fps ?? 30;
    const range = spec.clipDuration ?? DEFAULT_CLIP_RANGE;
    const workDir = tempWorkDir(spec);
    await mkdir(workDir, { recursive: true });
    await mkdir(path.dirname(path.resolve(spec.outputPath)), { recursive: true });

    try {
      // 1) probe -----------------------------------------------------------
      onProgress?.({ stage: 'probe', progress: 0, message: '클립 길이 분석 중' });
      const clipInfos: Array<{ path: string; duration: number }> = [];
      for (const c of spec.clips) {
        const probe = await probeMedia(c);
        if (!probe.hasVideo) {
          throw new Error(`클립에 비디오 트랙이 없습니다 (오디오 파일 아닌지 확인): ${path.basename(c)}`);
        }
        if (probe.duration < 0.15) {
          throw new Error(`클립이 너무 짧습니다 (0.15초 미만): ${path.basename(c)}`);
        }
        clipInfos.push({ path: c, duration: probe.duration });
      }

      let voiceoverDur: number | undefined;
      if (spec.voiceoverPath) {
        const voProbe = await probeMedia(spec.voiceoverPath);
        if (!voProbe.hasAudio) {
          throw new Error(
            `보이스오버 파일에 오디오 트랙이 없습니다: ${path.basename(spec.voiceoverPath)}`
          );
        }
        voiceoverDur = voProbe.duration;
      }

      // 2) 자막 이벤트 + 목표 총길이 ----------------------------------------
      // 사용자가 검수/수정한 events 가 오면 그대로 사용, 아니면 script/STT 로 생성
      const events: SubtitleEvent[] =
        spec.events && spec.events.length > 0
          ? spec.events
          : buildSubtitleEvents({
              script: spec.script,
              wordTimings: spec.wordTimings,
              voiceoverDur,
              chunkMode: spec.subtitle?.chunkMode,
              chunkSyllables: spec.subtitle?.chunkSyllables,
              maxLineSyllables: spec.subtitle?.maxLineSyllables,
              syllablesPerSecond: spec.subtitle?.syllablesPerSecond,
            });

      let targetDuration: number | undefined;
      if (voiceoverDur !== undefined) {
        targetDuration = voiceoverDur + 0.3;
      } else if (events.length > 0) {
        targetDuration = events[events.length - 1].end + 0.3;
      }

      // 3) plan + normalize --------------------------------------------------
      const segments = planSegments(clipInfos, range, targetDuration);
      if (segments.length === 0) throw new Error('Segment plan is empty');
      logger.info('Segment plan', {
        segments: segments.length,
        targetDuration,
        resolution: `${width}x${height}`,
      });

      const segPaths: string[] = [];
      for (let s = 0; s < segments.length; s++) {
        const seg = segments[s];
        const segPath = path.join(workDir, `seg-${String(s).padStart(3, '0')}.mp4`);
        onProgress?.({
          stage: 'normalize',
          progress: 0.05 + 0.55 * (s / segments.length),
          message: `클립 정규화 ${s + 1}/${segments.length}`,
        });
        await normalizeClip({
          input: seg.clipPath,
          output: segPath,
          sourceStart: seg.sourceStart,
          duration: seg.duration,
          width,
          height,
          fps,
        });
        segPaths.push(segPath);
      }

      // 4) concat ------------------------------------------------------------
      onProgress?.({ stage: 'concat', progress: 0.62, message: '클립 이어붙이는 중' });
      const listPath = path.join(workDir, 'concat.txt');
      await writeFile(
        listPath,
        segPaths
          .map((p) => `file '${p.replace(/\\/g, '/').replace(/'/g, "'\\''")}'`)
          .join('\n'),
        'utf8'
      );
      const concatPath = path.join(workDir, 'concat.mp4');
      await runFfmpeg([
        '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'concat', '-safe', '0',
        '-i', listPath,
        '-c', 'copy',
        concatPath,
      ]);

      const totalDuration =
        targetDuration ?? segments.reduce((sum, s) => sum + s.duration, 0);

      // 5) render: 자막 하드번 + 오디오 --------------------------------------
      onProgress?.({ stage: 'render', progress: 0.65, message: '자막/오디오 합성 중' });

      const subtitleMode = spec.subtitleMode ?? 'burn';
      const shouldBurn =
        events.length > 0 && (subtitleMode === 'burn' || subtitleMode === 'both');
      const shouldSrt =
        events.length > 0 && (subtitleMode === 'srt' || subtitleMode === 'both');

      const args: string[] = ['-y', '-hide_banner', '-i', concatPath];

      if (spec.voiceoverPath) args.push('-i', spec.voiceoverPath);
      if (spec.bgmPath) args.push('-stream_loop', '-1', '-i', spec.bgmPath);

      // 비디오 필터 (자막 하드번)
      if (shouldBurn) {
        const assPath = path.join(workDir, 'subtitles.ass');
        await writeFile(assPath, generateAss(events, spec.subtitle), 'utf8');

        const fontId = spec.subtitle?.fontId;
        if (!isFontAvailable(fontId)) {
          logger.warn(
            `Font file for '${getFont(fontId).family}' not found in ${getFontsDir()} — ` +
              'run "pnpm --filter @cutback/shorts-composer fonts". Falling back to system fonts.'
          );
        }
        const vf = `ass='${escapeForFilter(assPath)}':fontsdir='${escapeForFilter(getFontsDir())}'`;
        args.push('-vf', vf);
      }

      // 오디오 매핑
      const voIdx = spec.voiceoverPath ? 1 : -1;
      const bgmIdx = spec.bgmPath ? (spec.voiceoverPath ? 2 : 1) : -1;
      if (voIdx > 0 && bgmIdx > 0) {
        args.push(
          '-filter_complex',
          `[${bgmIdx}:a]volume=0.15[bgm];[${voIdx}:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]`,
          '-map', '0:v', '-map', '[aout]'
        );
      } else if (voIdx > 0) {
        args.push('-map', '0:v', '-map', `${voIdx}:a`);
      } else if (bgmIdx > 0) {
        args.push('-map', '0:v', '-map', `${bgmIdx}:a`);
      } else {
        args.push('-an');
      }

      args.push(
        '-t', totalDuration.toFixed(3),
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '17',
        '-pix_fmt', 'yuv420p'
      );
      if (voIdx > 0 || bgmIdx > 0) args.push('-c:a', 'aac', '-b:a', '192k');
      args.push('-movflags', '+faststart', spec.outputPath);

      await runFfmpeg(args, {
        onStderrLine: (line) => {
          const m = /time=(\d+):(\d+):(\d+(?:\.\d+)?)/.exec(line);
          if (m && onProgress) {
            const t = Number(m[1]) * 3600 + Number(m[2]) * 60 + Number(m[3]);
            onProgress({
              stage: 'render',
              progress: 0.65 + 0.35 * Math.min(t / totalDuration, 1),
              message: '자막/오디오 합성 중',
            });
          }
        },
      });

      // 6) SRT sidecar (캡컷 등에서 편집 가능) ------------------------------
      let srtPath: string | undefined;
      if (shouldSrt) {
        srtPath = spec.outputPath.replace(/\.[^.\\/]+$/, '') + '.srt';
        await writeFile(srtPath, generateSrt(events), 'utf8');
        logger.info('SRT sidecar written', { srtPath });
      }

      onProgress?.({ stage: 'render', progress: 1, message: '완료' });
      const result: ComposeResult = {
        outputPath: spec.outputPath,
        durationSec: totalDuration,
        segmentCount: segments.length,
        subtitleEventCount: events.length,
        width,
        height,
        srtPath,
      };
      logger.info('Compose done', result as unknown as Record<string, unknown>);
      return result;
    } finally {
      // 임시 조각 정리 (실패 시에도)
      await rm(workDir, { recursive: true, force: true }).catch(() => {});
    }
  }
}
