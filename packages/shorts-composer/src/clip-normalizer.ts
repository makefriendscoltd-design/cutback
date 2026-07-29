/**
 * 클립 정규화 (릴스 9:16 규격 통일)
 *
 * 어떤 소스든 (가로/세로/정사각, 아무 해상도, HEVC 포함) →
 * scale + center-crop 으로 9:16 을 꽉 채우고 fps/픽셀포맷을 통일한 H.264 조각으로 변환.
 * 조각들의 스펙이 동일해지므로 concat demuxer 로 재인코딩 없이 이어붙일 수 있다.
 */

import { spawn } from 'child_process';
import { resolveFfmpegPath, createLogger } from '@cutback/shared';

const logger = createLogger('clip-normalizer');

export function getFfmpeg(): string {
  const p = resolveFfmpegPath();
  if (!p) {
    throw new Error(
      'ffmpeg not found. Set CUTBACK_FFMPEG or install ffmpeg-static.'
    );
  }
  return p;
}

function runFfmpeg(
  args: string[],
  opts: { onStderrLine?: (line: string) => void; allowFail?: boolean } = {}
): Promise<{ code: number; stderr: string }> {
  return new Promise((resolve, reject) => {
    const ffmpeg = getFfmpeg();
    const proc = spawn(ffmpeg, args, { windowsHide: true });
    let stderr = '';
    proc.stderr.on('data', (d: Buffer) => {
      const text = d.toString();
      stderr += text;
      if (opts.onStderrLine) {
        for (const line of text.split(/\r?\n/)) {
          if (line.trim()) opts.onStderrLine(line);
        }
      }
      // stderr 무한 축적 방지
      if (stderr.length > 200_000) stderr = stderr.slice(-100_000);
    });
    proc.on('error', reject);
    proc.on('close', (code) => {
      if (code === 0 || opts.allowFail) {
        resolve({ code: code ?? -1, stderr });
      } else {
        reject(
          new Error(`ffmpeg exited with ${code}\n${stderr.slice(-2000)}`)
        );
      }
    });
  });
}

export interface MediaProbe {
  duration: number;
  hasVideo: boolean;
  hasAudio: boolean;
}

/**
 * 미디어 길이/스트림 구성. ffprobe 의존 없이 `ffmpeg -i` stderr 를 파싱한다.
 * (asset-indexer 는 시스템 ffprobe 를 요구하지만 여기선 번들 ffmpeg 만으로 동작)
 */
export async function probeMedia(filePath: string): Promise<MediaProbe> {
  const { stderr } = await runFfmpeg(['-hide_banner', '-i', filePath], {
    allowFail: true, // 출력 없음 → ffmpeg 는 exit 1이 정상
  });
  const m = /Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/.exec(stderr);
  if (!m) {
    throw new Error(`미디어 정보를 읽을 수 없습니다 (손상되었거나 미지원 형식): ${filePath}`);
  }
  return {
    duration: Number(m[1]) * 3600 + Number(m[2]) * 60 + Number(m[3]),
    hasVideo: /Stream #[^\n]*: Video/.test(stderr),
    hasAudio: /Stream #[^\n]*: Audio/.test(stderr),
  };
}

/** 미디어 길이(초)만 필요할 때 */
export async function getMediaDuration(filePath: string): Promise<number> {
  return (await probeMedia(filePath)).duration;
}

export interface NormalizeOptions {
  input: string;
  output: string;
  /** 소스 시작 오프셋 (초) */
  sourceStart: number;
  /** 사용 길이 (초) */
  duration: number;
  width: number;
  height: number;
  fps: number;
}

/** 클립 하나를 9:16 규격 조각으로 변환 */
export async function normalizeClip(opts: NormalizeOptions): Promise<void> {
  const { input, output, sourceStart, duration, width, height, fps } = opts;
  const vf = [
    `scale=${width}:${height}:force_original_aspect_ratio=increase`,
    `crop=${width}:${height}`,
    `fps=${fps}`,
    'setsar=1',
    'format=yuv420p',
  ].join(',');

  const args = [
    '-y',
    '-hide_banner',
    '-loglevel', 'error',
    '-ss', sourceStart.toFixed(3),
    '-i', input,
    '-t', duration.toFixed(3),
    '-vf', vf,
    '-an',
    '-c:v', 'libx264',
    '-preset', 'veryfast',
    '-crf', '18',
    output,
  ];
  logger.debug('normalize', { input, duration });
  await runFfmpeg(args);
}

export { runFfmpeg };
