import {
  CutDecision,
  createLogger,
  resolveFfmpegPath,
  describeFfmpegSource,
} from '@cutback/shared';
import { spawn } from 'child_process';
import fs from 'fs/promises';
import os from 'os';
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

  // FFmpeg filter_complex 생성 — select 방식.
  //
  // 예전에는 keep segment 마다 trim/atrim 을 만들고 concat 으로 이어붙였다.
  // concat 필터는 모든 입력에서 프레임을 버퍼링하므로 구간이 수백 개면
  // 메모리가 폭증한다. 실측: 30분 영상 434구간에서 ffmpeg 가 10GB 까지 자라
  // 16GB PC 의 가용 메모리를 2.4GB 로 떨어뜨리고 시스템 전체를 멈춰 세웠다.
  //
  // select 는 입력을 한 번만 훑으면서 유지 구간 밖의 프레임을 버린다.
  // 필터 체인이 하나뿐이라 메모리가 구간 수와 무관하게 일정하다.
  //   select='between(t,S1,E1)+between(t,S2,E2)+...',setpts=N/FRAME_RATE/TB
  const ranges = keepSegments
    .map((s) => `between(t,${s.start.toFixed(3)},${s.end.toFixed(3)})`)
    .join('+');

  const filterComplex =
    `[0:v]select='${ranges}',setpts=N/FRAME_RATE/TB[outv];` +
    `[0:a]aselect='${ranges}',asetpts=N/SR/TB[outa]`;

  // 출력 디렉토리 생성
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  // filter_complex 를 명령줄이 아니라 파일로 넘긴다.
  //
  // Windows 의 CreateProcess 는 명령줄 전체가 32,767 자를 넘으면 거부한다
  // (spawn ENAMETOOLONG). 이 필터는 유지 구간마다 약 150 자씩 늘어나므로
  // 224 구간이면 이미 한계를 넘는다. 30분 롱폼은 무음 컷만으로도 구간이
  // 수백~수천 개라 -filter_complex 로는 사실상 항상 실패한다.
  //
  // -filter_complex_script 는 같은 내용을 파일에서 읽으므로 길이 제한이 없다.
  const scriptPath = path.join(
    os.tmpdir(),
    `cutback-filter-${Date.now()}-${process.pid}.txt`
  );
  await fs.writeFile(scriptPath, filterComplex, 'utf-8');
  logger.info('Filter script written', {
    scriptPath,
    filterLength: filterComplex.length,
    segments: keepSegments.length,
  });

  // 비디오 인코더: NVENC(GPU) 우선, 실패하면 libx264(CPU).
  //
  // 실측(3분 구간) libx264 21.4s vs h264_nvenc 10.3s. 정적인 테스트 영상이라
  // 이 정도지 실제 촬영 영상은 격차가 더 크다. NVENC 은 인코더 목록에 있어도
  // 드라이버/GPU 가 없으면 실행 시점에 실패하므로 반드시 폴백을 둔다.
  const encoderCandidates: Array<{ name: string; args: string[] }> = [
    { name: 'h264_nvenc', args: ['-c:v', 'h264_nvenc', '-preset', 'p4', '-cq', '20'] },
    { name: 'libx264', args: ['-c:v', 'libx264', '-preset', 'fast', '-crf', '18'] },
  ];

  const cleanupScript = () => {
    fs.unlink(scriptPath).catch(() => {
      // 임시 파일 삭제 실패는 렌더링 결과에 영향 없음
    });
  };

  let lastError: Error | null = null;
  for (let i = 0; i < encoderCandidates.length; i++) {
    const encoder = encoderCandidates[i];
    const isLast = i === encoderCandidates.length - 1;
    try {
      await runFfmpeg(encoder, keepSegments, {
        videoPath,
        outputPath,
        scriptPath,
        onProgress,
      });
      cleanupScript();
      return outputPath;
    } catch (err) {
      lastError = err as Error;
      logger.warn('Encoder failed', {
        encoder: encoder.name,
        willRetry: !isLast,
        error: lastError.message.slice(-300),
      });
    }
  }

  cleanupScript();
  throw lastError ?? new Error('FFmpeg 렌더링 실패');
}

interface RunFfmpegContext {
  videoPath: string;
  outputPath: string;
  scriptPath: string;
  onProgress?: RenderProgressCallback;
}

function runFfmpeg(
  encoder: { name: string; args: string[] },
  keepSegments: Array<{ start: number; end: number }>,
  ctx: RunFfmpegContext
): Promise<void> {
  const { videoPath, outputPath, scriptPath, onProgress } = ctx;

  return new Promise<void>((resolve, reject) => {
    const args = [
      '-i', videoPath,
      '-filter_complex_script', scriptPath,
      '-map', '[outv]',
      '-map', '[outa]',
      ...encoder.args,
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

    // stderr 는 마지막 부분만 남긴다.
    //
    // ffmpeg 는 렌더링 내내 진행 상황을 stderr 로 계속 흘린다. 이걸 문자열에
    // 그대로 누적하면 20분짜리 렌더링에서 수백 MB 까지 자라 Node 가
    // "Zone Allocation failed - process out of memory" 로 죽는다.
    // Electron 메인에서 이게 터지면 창이 검은 채로 응답을 멈춘다.
    // 실패 메시지는 마지막 몇 줄이면 충분하므로 뒤쪽만 보관한다.
    const STDERR_KEEP_BYTES = 8000;
    let stderr = '';

    // 편집 후 총 길이 (진행률 분모)
    const totalKeepDuration = keepSegments.reduce(
      (sum, seg) => sum + (seg.end - seg.start),
      0
    );

    // 진행률 IPC 폭주 방지: 퍼센트가 실제로 바뀔 때만 통지한다.
    let lastPercent = -1;

    ffmpeg.stderr?.on('data', (data: Buffer) => {
      const line = data.toString();
      stderr = (stderr + line).slice(-STDERR_KEEP_BYTES);

      // FFmpeg progress 파싱 (time= 기반)
      const timeMatch = line.match(/time=(\d+):(\d+):(\d+\.\d+)/);
      if (timeMatch && onProgress && totalKeepDuration > 0) {
        const h = parseInt(timeMatch[1]);
        const m = parseInt(timeMatch[2]);
        const s = parseFloat(timeMatch[3]);
        const currentTime = h * 3600 + m * 60 + s;

        const percent = Math.min(
          99,
          Math.round((currentTime / totalKeepDuration) * 100)
        );
        if (percent !== lastPercent) {
          lastPercent = percent;
          onProgress(percent, `렌더링 중... ${percent}%`);
        }
      }
    });

    // 임시 필터 스크립트는 인코더 폴백 재시도에도 필요하므로
    // 여기서 지우지 않고 renderVideo 가 최종적으로 정리한다.
    ffmpeg.on('close', (code) => {
      if (code === 0) {
        onProgress?.(100, '렌더링 완료');
        logger.info('Video rendered successfully', {
          outputPath,
          encoder: encoder.name,
        });
        resolve();
      } else {
        const errorMsg = stderr.split('\n').slice(-5).join('\n');
        reject(
          new Error(
            `FFmpeg 렌더링 실패 (${encoder.name}, code ${code}): ${errorMsg}`
          )
        );
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
