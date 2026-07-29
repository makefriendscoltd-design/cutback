/**
 * Mode B Pipeline
 *
 * 보이스오버 + B-roll 자동 조합 파이프라인
 */

import type {
  Job,
  JobResults,
  Preset,
  SentenceTimeline,
  AssetIndex,
  RoughCutTimeline,
} from '@cutback/shared';
import { VoiceoverEngine } from '@cutback/voiceover-engine';
import { AssetIndexer } from '@cutback/asset-indexer';
import { CrosscutPlanner } from '@cutback/crosscut-planner';
import { createLogger } from '@cutback/shared';
import { PythonClient } from './python-client.js';

const logger = createLogger('mode-b-pipeline');

export type ModeBProgressCallback = (
  stage: string,
  progress: number,
  message: string
) => void;

export class ModeBPipeline {
  private voiceoverEngine: VoiceoverEngine;
  private assetIndexer: AssetIndexer;
  private crosscutPlanner: CrosscutPlanner;
  private pythonClient: PythonClient;

  constructor() {
    this.voiceoverEngine = new VoiceoverEngine();
    this.assetIndexer = new AssetIndexer();
    this.crosscutPlanner = new CrosscutPlanner();
    this.pythonClient = new PythonClient();
  }

  /**
   * Mode B 파이프라인 실행
   */
  async execute(
    job: Job,
    preset: Preset,
    onProgress?: ModeBProgressCallback
  ): Promise<JobResults> {
    logger.info('Mode B pipeline started', { jobId: job.id });

    if (!preset.modeBParams) {
      throw new Error('Mode B preset requires modeBParams');
    }

    if (!job.assetPaths || job.assetPaths.length === 0) {
      throw new Error('Mode B requires asset paths (B-roll clips)');
    }

    try {
      // --- Stage 1: 보이스오버 STT ---
      onProgress?.('voiceover_stt', 10, '보이스오버 음성 인식 중...');
      const sentenceTimeline = await this.processSentenceTimeline(
        job.videoPath,
        preset
      );
      logger.info('Sentence timeline created', {
        sentenceCount: sentenceTimeline.sentences.length,
      });

      // --- Stage 2: B-roll 인덱싱 ---
      onProgress?.('asset_indexing', 30, 'B-roll 클립 인덱싱 중...');
      const assetIndex = await this.indexAssets(job.assetPaths);
      logger.info('Assets indexed', { assetCount: assetIndex.assets.length });

      // --- Stage 3: 자동 매칭 및 러프컷 생성 ---
      onProgress?.('rough_cut', 60, '러프컷 타임라인 생성 중...');
      const roughCutTimeline = await this.crosscutPlanner.generateRoughCut(
        sentenceTimeline,
        assetIndex,
        preset.modeBParams.matchConfig
      );
      logger.info('Rough cut generated', {
        clipCount: roughCutTimeline.tracks[0]?.clips.length || 0,
        avgConfidence: roughCutTimeline.metadata.averageConfidence,
      });

      // --- Stage 4: 완료 ---
      onProgress?.('completed', 100, '완료');

      return {
        sentenceTimeline,
        assetIndex,
        roughCutTimeline,
        statistics: {
          original_duration: sentenceTimeline.totalDuration,
          edited_duration: roughCutTimeline.totalDuration,
          silence_removed: 0,
          fillers_removed: 0,
          retakes_removed: 0,
          total_cuts: roughCutTimeline.tracks[0]?.clips.length || 0,
          cut_frequency: 0,
          naturalness_score: roughCutTimeline.metadata.averageConfidence,
        },
      };
    } catch (error) {
      logger.error('Mode B pipeline failed', { error });
      throw error;
    }
  }

  /**
   * 보이스오버 → SentenceTimeline 변환
   */
  private async processSentenceTimeline(
    voiceoverPath: string,
    _preset: Preset
  ): Promise<SentenceTimeline> {
    try {
      // STT 실행
      const transcript = await this.pythonClient.transcribe(
        voiceoverPath,
        'ko'
      );

      // Sentence 단위로 세그먼트
      return this.voiceoverEngine.fromTranscript(transcript);
    } catch (error) {
      logger.warn('STT failed, falling back to empty timeline', { error });
      // Fallback: 빈 타임라인 반환 (Python 서비스 없을 때)
      return {
        sentences: [],
        totalDuration: 0,
        language: 'ko',
        source: 'stt',
      };
    }
  }

  /**
   * B-roll 클립 인덱싱
   */
  private async indexAssets(assetPaths: string[]): Promise<AssetIndex> {
    // TODO: 키워드 맵 지원 (UI에서 입력받거나 파일명 기반)
    return await this.assetIndexer.indexAssets(assetPaths);
  }

  /**
   * EDL 내보내기
   */
  exportToEDL(
    _sentenceTimeline: SentenceTimeline,
    assetIndex: AssetIndex,
    roughCutTimeline: RoughCutTimeline
  ): string {
    return this.crosscutPlanner.exportToEDL(roughCutTimeline, assetIndex);
  }

  /**
   * SRT 자막 내보내기 (보이스오버 텍스트)
   */
  exportToSRT(sentenceTimeline: SentenceTimeline): string {
    return this.voiceoverEngine.exportToSRT(sentenceTimeline);
  }
}
