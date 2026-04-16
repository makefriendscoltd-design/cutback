import ffmpeg from 'fluent-ffmpeg';
import {
  SilenceDetectionResult,
  AudioParams,
  resolveFfmpegPath,
  describeFfmpegSource,
} from '@cutback/shared';
import { createLogger } from '@cutback/shared';

const logger = createLogger('silence-detector');

// 모듈 로드 시 ffmpeg 경로 결정 → fluent-ffmpeg 에 전달.
// 다른 PC 에서 system ffmpeg 가 없어도 ffmpeg-static 으로 fallback.
const resolvedFfmpegPath = resolveFfmpegPath();
if (resolvedFfmpegPath) {
  ffmpeg.setFfmpegPath(resolvedFfmpegPath);
  logger.info('FFmpeg resolved', { source: describeFfmpegSource() });
} else {
  logger.warn(
    'FFmpeg not found - silence detection will fail. Run `pnpm install` (ffmpeg-static) or install system ffmpeg.'
  );
}

export interface SilenceDetectorOptions {
  threshold_db: number;
  min_duration_ms: number;
  pre_padding_ms: number;
  post_padding_ms: number;
}

/**
 * ffmpeg를 사용한 무음 구간 감지
 * ffmpeg의 silencedetect 필터 사용
 */
export class SilenceDetector {
  async detect(
    audioPath: string,
    options: SilenceDetectorOptions
  ): Promise<SilenceDetectionResult[]> {
    logger.info('Starting silence detection', { audioPath, options });

    const results: SilenceDetectionResult[] = [];

    return new Promise((resolve, reject) => {
      const { threshold_db, min_duration_ms } = options;
      const min_duration_sec = min_duration_ms / 1000;

      ffmpeg(audioPath)
        .audioFilters([
          `silencedetect=noise=${threshold_db}dB:d=${min_duration_sec}`,
        ])
        .on('error', (err) => {
          logger.error('ffmpeg error', { error: err.message });
          reject(err);
        })
        .on('stderr', (stderrLine) => {
          // ffmpeg는 silencedetect 결과를 stderr로 출력
          // [silencedetect @ ...] silence_start: 1.23
          // [silencedetect @ ...] silence_end: 2.45 | silence_duration: 1.22

          const startMatch = stderrLine.match(/silence_start:\s*([\d.]+)/);
          const endMatch = stderrLine.match(
            /silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)/
          );

          if (startMatch) {
            // silence 시작 기록 (임시)
            const timestamp = parseFloat(startMatch[1]);
            logger.debug('Silence start detected', { timestamp });
          }

          if (endMatch) {
            const endTime = parseFloat(endMatch[1]);
            const duration = parseFloat(endMatch[2]);
            const startTime = endTime - duration;

            results.push({
              timestamp: startTime,
              duration,
              confidence: 0.95, // ffmpeg silencedetect는 신뢰도 높음
              db_level: threshold_db,
            });

            logger.debug('Silence detected', { startTime, endTime, duration });
          }
        })
        .on('end', () => {
          logger.info('Silence detection completed', {
            totalSilences: results.length,
          });

          // padding 적용
          const paddedResults = this.applyPadding(results, options);
          resolve(paddedResults);
        })
        // 실제로 변환하지 않고 분석만 하기 위해 null 출력
        .output('-')
        .format('null')
        .run();
    });
  }

  /**
   * 무음 구간에 padding 적용
   * 너무 빡빡하게 자르면 부자연스러우므로 앞뒤로 여백 추가
   */
  private applyPadding(
    results: SilenceDetectionResult[],
    options: SilenceDetectorOptions
  ): SilenceDetectionResult[] {
    const { pre_padding_ms, post_padding_ms } = options;
    const pre_padding_sec = pre_padding_ms / 1000;
    const post_padding_sec = post_padding_ms / 1000;

    return results.map((result) => {
      const newStart = Math.max(0, result.timestamp + pre_padding_sec);
      const newEnd = result.timestamp + result.duration - post_padding_sec;
      const newDuration = Math.max(0, newEnd - newStart);

      return {
        ...result,
        timestamp: newStart,
        duration: newDuration,
      };
    });
  }

  /**
   * AudioParams 프리셋을 SilenceDetectorOptions로 변환
   */
  static fromAudioParams(params: AudioParams): SilenceDetectorOptions {
    return {
      threshold_db: params.silence_threshold_db,
      min_duration_ms: params.min_silence_duration_ms,
      pre_padding_ms: params.pre_cut_padding_ms,
      post_padding_ms: params.post_cut_padding_ms,
    };
  }
}

/**
 * 편의 함수: 무음 감지 실행
 */
export async function detectSilence(
  audioPath: string,
  audioParams: AudioParams
): Promise<SilenceDetectionResult[]> {
  const detector = new SilenceDetector();
  const options = SilenceDetector.fromAudioParams(audioParams);
  return detector.detect(audioPath, options);
}
