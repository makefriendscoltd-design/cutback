import {
  CutDecision,
  createLogger,
  resolveFfmpegPath,
  describeFfmpegSource,
} from '@cutback/shared';
import { spawn } from 'child_process';
import fs from 'fs/promises';
import path from 'path';

const logger = createLogger('video-renderer');

export type RenderProgressCallback = (percent: number, detail: string) => void;

interface RenderOptions {
  videoPath: string;
  outputPath: string;
  videoDuration: number; // seconds
}

/**
 * FFmpeg를 사용하여 컷이 적용된 영상을 직접 렌더링
 *
 * 방식: filter_complex로 각 유지 구간을 trim → concat
 */
export async function renderVideo(
  cutDecisions: CutDecision[],
  options: RenderOptions,
  onProgress?: RenderProgressCallback
): Promise<string> {
  const { videoPath, outputPath, videoDuration } = options;

  const enabledCuts = cutDecisions
    .filter((c) => c.enabled)
    .sort((a, b) => a.start - b.start);

  // 유지할 구간 계산
  const keepSegments: Array<{ start: number; end: number }> = [];
  let cursor = 0;

  for (const cut of enabledCuts) {
    if (cut.start > cursor) {
      keepSegments.push({ start: cursor, end: cut.start });
    }
    cursor = Math.max(cursor, cut.end);
  }
  if (cursor < videoDuration) {
    keepSegments.push({ start: cursor, end: videoDuration });
  }

  if (keepSegments.length === 0) {
    throw new Error('모든 구간이 제거되어 렌더링할 내용이 없습니다.');
  }

  logger.info('Rendering video', {
    segments: keepSegments.length,
    cuts: enabledCuts.length,
    outputPath,
  });

  // FFmpeg filter_complex 생성
  // 각 keep segment를 trim/atrim → setpts/asetpts → concat
  const filterParts: string[] = [];
  const concatInputs: string[] = [];

  for (let i = 0; i < keepSegments.length; i++) {
    const seg = keepSegments[i];
    filterParts.push(
      `[0:v]trim=start=${seg.start.toFixed(6)}:end=${seg.end.toFixed(6)},setpts=PTS-STARTPTS[v${i}]`
    );
    filterParts.push(
      `[0:a]atrim=start=${seg.start.toFixed(6)}:end=${seg.end.toFixed(6)},asetpts=PTS-STARTPTS[a${i}]`
    );
    concatInputs.push(`[v${i}][a${i}]`);
  }

  const filterComplex =
    filterParts.join(';') +
    ';' +
    concatInputs.join('') +
    `concat=n=${keepSegments.length}:v=1:a=1[outv][outa]`;

  // 출력 디렉토리 생성
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  // FFmpeg 실행
  return new Promise<string>((resolve, reject) => {
    const args = [
      '-i', videoPath,
      '-filter_complex', filterComplex,
      '-map', '[outv]',
      '-map', '[outa]',
      '-c:v', 'libx264',
      '-preset', 'fast',
      '-crf', '18',
      '-c:a', 'aac',
      '-b:a', '192k',
      '-movflags', '+faststart',
      '-y',
      outputPath,
    ];

    const ffmpegBinary = resolveFfmpegPath();
    if (!ffmpegBinary) {
      reject(
        new Error(
          'FFmpeg 실행 파일을 찾지 못했습니다. `pnpm install` 로 ffmpeg-static 을 설치하거나 시스템 PATH 에 ffmpeg 를 추가하세요.'
        )
      );
      return;
    }

    logger.info('FFmpeg args', {
      bin: describeFfmpegSource(),
      args: args.join(' '),
    });

    const ffmpeg = spawn(ffmpegBinary, args, { stdio: ['pipe', 'pipe', 'pipe'] });

    let stderr = '';

    ffmpeg.stderr?.on('data', (data: Buffer) => {
      const line = data.toString();
      stderr += line;

      // FFmpeg progress 파싱 (time= 기반)
      const timeMatch = line.match(/time=(\d+):(\d+):(\d+\.\d+)/);
      if (timeMatch && onProgress) {
        const h = parseInt(timeMatch[1]);
        const m = parseInt(timeMatch[2]);
        const s = parseFloat(timeMatch[3]);
        const currentTime = h * 3600 + m * 60 + s;

        // 편집 후 총 길이 계산
        const totalKeepDuration = keepSegments.reduce(
          (sum, seg) => sum + (seg.end - seg.start), 0
        );
        const percent = Math.min(99, Math.round((currentTime / totalKeepDuration) * 100));
        onProgress(percent, `렌더링 중... ${percent}%`);
      }
    });

    ffmpeg.on('close', (code) => {
      if (code === 0) {
        onProgress?.(100, '렌더링 완료');
        logger.info('Video rendered successfully', { outputPath });
        resolve(outputPath);
      } else {
        const errorMsg = stderr.split('\n').slice(-5).join('\n');
        logger.error('FFmpeg failed', { code, error: errorMsg });
        reject(new Error(`FFmpeg 렌더링 실패 (code ${code}): ${errorMsg}`));
      }
    });

    ffmpeg.on('error', (err) => {
      reject(
        new Error(
          `FFmpeg 실행 실패: ${err.message} (binary=${ffmpegBinary}). \`pnpm install\` 으로 ffmpeg-static 이 설치됐는지 확인하세요.`
        )
      );
    });
  });
}
