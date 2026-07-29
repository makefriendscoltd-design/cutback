/**
 * MetadataExtractor
 *
 * ffprobe를 사용한 비디오 메타데이터 추출
 */

import { spawn } from 'child_process';
import type { AssetMetadata } from '@cutback/shared';
import { createHash } from 'crypto';
import { createReadStream } from 'fs';

export interface VideoMetadata {
  duration: number;
  width: number;
  height: number;
  fps: number;
  hasAudio: boolean;
}

export class MetadataExtractor {
  /**
   * ffprobe로 비디오 메타데이터 추출
   */
  async extractVideoMetadata(filePath: string): Promise<VideoMetadata> {
    return new Promise((resolve, reject) => {
      const args = [
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        filePath,
      ];

      const ffprobe = spawn('ffprobe', args);
      let stdout = '';
      let stderr = '';

      ffprobe.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      ffprobe.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      ffprobe.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`ffprobe failed: ${stderr}`));
          return;
        }

        try {
          const info = JSON.parse(stdout);
          const videoStream = info.streams.find((s: any) => s.codec_type === 'video');
          const audioStream = info.streams.find((s: any) => s.codec_type === 'audio');

          if (!videoStream) {
            reject(new Error('No video stream found'));
            return;
          }

          const duration = parseFloat(info.format.duration) || 0;
          const width = videoStream.width || 0;
          const height = videoStream.height || 0;

          // FPS 계산
          let fps = 0;
          if (videoStream.r_frame_rate) {
            const [num, den] = videoStream.r_frame_rate.split('/').map(Number);
            fps = den > 0 ? num / den : 0;
          }

          resolve({
            duration,
            width,
            height,
            fps,
            hasAudio: !!audioStream,
          });
        } catch (err) {
          reject(new Error(`Failed to parse ffprobe output: ${err}`));
        }
      });
    });
  }

  /**
   * 파일 해시 생성 (SHA-256)
   */
  async generateFileHash(filePath: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const hash = createHash('sha256');
      const stream = createReadStream(filePath);

      stream.on('data', (chunk) => hash.update(chunk));
      stream.on('end', () => resolve(hash.digest('hex')));
      stream.on('error', reject);
    });
  }

  /**
   * AssetMetadata 생성
   */
  async createAssetMetadata(
    filePath: string,
    userKeywords?: string[]
  ): Promise<AssetMetadata> {
    const [videoMeta, fileHash] = await Promise.all([
      this.extractVideoMetadata(filePath),
      this.generateFileHash(filePath),
    ]);

    return {
      fileHash,
      resolution: {
        width: videoMeta.width,
        height: videoMeta.height,
      },
      fps: videoMeta.fps,
      hasAudio: videoMeta.hasAudio,
      userKeywords,
      // Phase 2 이상에서 추가:
      // shotBoundaries: [],
      // ocrText: '',
      // thumbnailPath: '',
    };
  }
}
