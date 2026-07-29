/**
 * Waveform peaks extractor.
 *
 * ffmpeg 로 PCM s16le mono 를 stdout 으로 추출 → 일정 개수의 bucket 으로 다운샘플링.
 * 결과: 각 bucket 의 max abs amplitude (0.0 - 1.0).
 *
 * UI 는 이 값을 받아 Canvas 위에 파형으로 그린다.
 * 1500 bucket 정도면 화면 가로 픽셀 기준 충분한 해상도이고,
 * 60분 영상도 ~12KB 페이로드라 IPC 한 번이면 끝난다.
 */

import { spawn, ChildProcessWithoutNullStreams } from 'child_process';
import { resolveFfmpegPath, createLogger } from '@cutback/shared';

const logger = createLogger('waveform-extractor');

export interface WaveformPeaks {
  /** 0.0 - 1.0 normalized amplitude per bucket (max abs in window) */
  peaks: number[];
  /** 총 길이 (초) */
  duration: number;
  /** 샘플레이트 (decode 시 사용) */
  sampleRate: number;
}

export async function extractWaveformPeaks(
  audioPath: string,
  bucketCount: number = 1500
): Promise<WaveformPeaks> {
  const ffmpegPath = resolveFfmpegPath();
  if (!ffmpegPath) {
    throw new Error('ffmpeg 를 찾을 수 없습니다 (waveform 추출 불가)');
  }
  const sampleRate = 8000; // 파형 표시는 8kHz 면 충분

  return new Promise((resolve, reject) => {
    // PCM s16le mono → stdout
    const args = [
      '-i', audioPath,
      '-f', 's16le',
      '-acodec', 'pcm_s16le',
      '-ar', String(sampleRate),
      '-ac', '1',
      '-loglevel', 'error',
      'pipe:1',
    ];

    const proc: ChildProcessWithoutNullStreams = spawn(ffmpegPath, args);
    const chunks: Buffer[] = [];
    let stderr = '';

    proc.stdout.on('data', (chunk: Buffer) => {
      chunks.push(chunk);
    });

    proc.stderr.on('data', (chunk: Buffer) => {
      stderr += chunk.toString();
    });

    proc.on('error', reject);

    proc.on('close', (code: number | null) => {
      if (code !== 0) {
        logger.error('ffmpeg waveform extraction failed', { code, stderr });
        reject(new Error(`ffmpeg exited ${code}: ${stderr}`));
        return;
      }

      const buf = Buffer.concat(chunks);
      const sampleCount = buf.length / 2; // s16le = 2 bytes per sample
      const duration = sampleCount / sampleRate;

      if (sampleCount === 0) {
        resolve({ peaks: [], duration: 0, sampleRate });
        return;
      }

      // 각 bucket 의 max abs amplitude
      const samplesPerBucket = Math.max(1, Math.floor(sampleCount / bucketCount));
      const actualBuckets = Math.ceil(sampleCount / samplesPerBucket);
      const peaks: number[] = new Array(actualBuckets);

      for (let b = 0; b < actualBuckets; b++) {
        const start = b * samplesPerBucket;
        const end = Math.min(sampleCount, start + samplesPerBucket);
        let max = 0;
        for (let i = start; i < end; i++) {
          const sample = buf.readInt16LE(i * 2);
          const abs = Math.abs(sample);
          if (abs > max) max = abs;
        }
        // 32768 = INT16_MAX. 정규화 0.0 - 1.0
        peaks[b] = max / 32768;
      }

      logger.info('Waveform peaks extracted', {
        duration: duration.toFixed(2),
        buckets: peaks.length,
      });

      resolve({ peaks, duration, sampleRate });
    });
  });
}
