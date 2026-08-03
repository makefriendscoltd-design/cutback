/**
 * Browser-playable preview video generator.
 *
 * Chromium 기본 빌드는 HEVC/H.265 디코더가 빠져있어 iPhone/Mac 화면녹화/요즘 카메라
 * 영상은 video element 에서 안 뜬다. 분석 결과 검토용 Before/After 프리뷰만이라도
 * 안전하게 재생되도록 ffmpeg 로 H.264 + AAC 480p MP4 를 한 번 생성해 캐시한다.
 *
 * 캐시 키: source 영상의 절대 경로 + mtime. 한 번 만들어두면 같은 파일 다시 분석해도 재사용.
 */

import { spawn, ChildProcessWithoutNullStreams } from 'child_process';
import { stat, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { createHash } from 'crypto';
import path from 'path';
import os from 'os';
import { resolveFfmpegPath, createLogger } from '@cutback/shared';

const logger = createLogger('preview-generator');

export interface PreviewResult {
  /** 생성된 (또는 캐시된) preview 파일 절대경로 */
  previewPath: string;
  /** 캐시 hit 여부 — 디버깅/UX 표시용 */
  fromCache: boolean;
  /** ffmpeg 실행 시간 (ms). cache hit 면 0. */
  durationMs: number;
}

function getCacheDir(): string {
  return path.join(os.tmpdir(), 'cutback-previews');
}

async function getCachePath(sourcePath: string): Promise<string> {
  const stats = await stat(sourcePath);
  const hash = createHash('sha1')
    .update(sourcePath)
    .update(String(stats.size))
    .update(String(stats.mtimeMs))
    .digest('hex')
    .slice(0, 16);
  return path.join(getCacheDir(), `${hash}.mp4`);
}

export interface PreviewProgress {
  /** 현재 처리한 시간 (초) */
  current: number;
  /** 총 길이 (초) */
  total: number;
}

/** Chromium 이 기본 빌드에서 디코딩 가능한 조합 */
const PLAYABLE_CONTAINERS = new Set(['mp4', 'm4v', 'mov', 'webm']);
const PLAYABLE_VIDEO_CODECS = new Set(['h264', 'vp8', 'vp9', 'av1']);
const PLAYABLE_AUDIO_CODECS = new Set(['aac', 'mp3', 'opus', 'vorbis']);

/**
 * 원본을 그대로 video element 에 물려도 되는지 판정.
 *
 * ffmpeg -i 로 헤더만 읽으므로 1초 이내에 끝난다.
 * 판정 실패 시에는 false — 트랜스코딩으로 안전하게 폴백한다.
 */
async function isSourceBrowserPlayable(sourcePath: string): Promise<boolean> {
  const ext = path.extname(sourcePath).toLowerCase().replace('.', '');
  if (!PLAYABLE_CONTAINERS.has(ext)) return false;

  const ffmpegPath = resolveFfmpegPath();
  if (!ffmpegPath) return false;

  return new Promise<boolean>((resolve) => {
    // -i 만 주면 ffmpeg 는 스트림 정보를 stderr 로 뱉고 "at least one output" 에러로 종료한다.
    const proc = spawn(ffmpegPath, ['-i', sourcePath]);
    let stderr = '';
    proc.stderr.on('data', (c: Buffer) => (stderr += c.toString()));
    proc.on('error', () => resolve(false));
    proc.on('close', () => {
      const video = stderr.match(/Stream #\d+:\d+.*: Video: (\w+)/);
      const audio = stderr.match(/Stream #\d+:\d+.*: Audio: (\w+)/);
      if (!video) return resolve(false);

      const vOk = PLAYABLE_VIDEO_CODECS.has(video[1].toLowerCase());
      // 무음 영상도 있으므로 오디오 스트림이 없으면 통과로 본다
      const aOk = !audio || PLAYABLE_AUDIO_CODECS.has(audio[1].toLowerCase());

      logger.info('Source playability probe', {
        sourcePath,
        videoCodec: video[1],
        audioCodec: audio?.[1] ?? '(none)',
        playable: vOk && aOk,
      });
      resolve(vOk && aOk);
    });
  });
}

/**
 * source video → browser 에서 재생 가능한 파일 경로를 돌려준다.
 *
 * 원본이 이미 재생 가능한 코덱(H.264/AAC 등)이면 **트랜스코딩 없이 원본을 그대로 쓴다.**
 * 예전에는 무조건 480p 로 재인코딩했는데, 30분 영상이면 3분 넘게 걸리는 동안
 * 플레이어에 아무것도 안 물려서 "미리보기가 아예 안 된다" 로 보였다.
 *
 * HEVC/ProRes 처럼 Chromium 이 못 여는 코덱일 때만 480p H.264 로 변환한다.
 */
export async function generatePreviewVideo(
  sourcePath: string,
  onProgress?: (p: PreviewProgress) => void
): Promise<PreviewResult> {
  const cachePath = await getCachePath(sourcePath);

  if (existsSync(cachePath)) {
    logger.info('Preview cache hit', { sourcePath, cachePath });
    return { previewPath: cachePath, fromCache: true, durationMs: 0 };
  }

  // 원본이 그대로 재생 가능하면 변환 자체를 건너뛴다 (대부분의 카메라/화면녹화 H.264)
  if (await isSourceBrowserPlayable(sourcePath)) {
    logger.info('Source is browser-playable, skipping transcode', { sourcePath });
    return { previewPath: sourcePath, fromCache: true, durationMs: 0 };
  }

  await mkdir(getCacheDir(), { recursive: true });

  const ffmpegPath = resolveFfmpegPath();
  if (!ffmpegPath) {
    throw new Error('ffmpeg 를 찾을 수 없어 preview 를 생성할 수 없습니다');
  }

  const startedAt = Date.now();
  return new Promise<PreviewResult>((resolve, reject) => {
    // 480p, ultrafast preset, 안전한 H.264 baseline + AAC.
    // -movflags +faststart : video element 의 progressive download 가능.
    const args = [
      '-i', sourcePath,
      '-c:v', 'libx264',
      '-preset', 'ultrafast',
      '-crf', '30',
      '-vf', 'scale=-2:480',
      '-pix_fmt', 'yuv420p', // baseline 호환
      '-c:a', 'aac',
      '-b:a', '96k',
      '-movflags', '+faststart',
      '-y',
      cachePath,
    ];

    logger.info('Generating preview', {
      sourcePath,
      cachePath,
      cmd: `ffmpeg ${args.slice(0, 4).join(' ')} ...`,
    });

    const proc: ChildProcessWithoutNullStreams = spawn(ffmpegPath, args);
    let stderrBuffer = '';
    let totalDuration = 0;

    proc.stderr.on('data', (chunk: Buffer) => {
      const text = chunk.toString();
      stderrBuffer += text;
      // ffmpeg 가 stderr 로 progress 를 흘림
      // "Duration: 00:15:32.57" / "time=00:01:23.45"
      if (totalDuration === 0) {
        const m = stderrBuffer.match(/Duration: (\d+):(\d+):(\d+)\.(\d+)/);
        if (m) {
          totalDuration =
            parseInt(m[1]) * 3600 + parseInt(m[2]) * 60 + parseInt(m[3]);
        }
      }
      const tm = text.match(/time=(\d+):(\d+):(\d+)\.(\d+)/);
      if (tm && onProgress && totalDuration > 0) {
        const current =
          parseInt(tm[1]) * 3600 + parseInt(tm[2]) * 60 + parseInt(tm[3]);
        onProgress({ current, total: totalDuration });
      }
    });

    proc.on('error', reject);

    proc.on('close', (code: number | null) => {
      if (code !== 0) {
        const tail = stderrBuffer.split('\n').slice(-10).join('\n');
        logger.error('ffmpeg preview generation failed', { code, tail });
        reject(new Error(`ffmpeg exited ${code}: ${tail}`));
        return;
      }
      const durationMs = Date.now() - startedAt;
      logger.info('Preview generated', {
        previewPath: cachePath,
        durationMs,
      });
      resolve({ previewPath: cachePath, fromCache: false, durationMs });
    });
  });
}
