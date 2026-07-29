/**
 * AssetIndexer
 *
 * B-roll 클립 인덱싱 통합 엔진
 */

import type { Asset, AssetIndex } from '@cutback/shared';
import { MetadataExtractor } from './metadata-extractor.js';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';

export interface IndexOptions {
  /** 사용자 지정 키워드 (파일명 → 키워드 매핑) */
  keywordMap?: Map<string, string[]>;
}

export class AssetIndexer {
  private metadataExtractor: MetadataExtractor;

  constructor() {
    this.metadataExtractor = new MetadataExtractor();
  }

  /**
   * 여러 비디오 파일을 인덱싱
   */
  async indexAssets(
    filePaths: string[],
    options: IndexOptions = {}
  ): Promise<AssetIndex> {
    const assets: Asset[] = [];
    let totalDuration = 0;

    for (const filePath of filePaths) {
      try {
        const asset = await this.indexSingleAsset(filePath, options);
        assets.push(asset);
        totalDuration += asset.duration;
      } catch (err) {
        console.error(`Failed to index asset: ${filePath}`, err);
        // 개별 파일 실패는 스킵하고 계속 진행
      }
    }

    return {
      assets,
      indexedAt: new Date(),
      totalDuration,
    };
  }

  /**
   * 단일 비디오 파일 인덱싱
   */
  private async indexSingleAsset(
    filePath: string,
    options: IndexOptions
  ): Promise<Asset> {
    const fileName = path.basename(filePath);
    const userKeywords = options.keywordMap?.get(fileName);

    const metadata = await this.metadataExtractor.createAssetMetadata(
      filePath,
      userKeywords
    );

    const duration = await this.extractDuration(filePath);

    return {
      id: uuidv4(),
      filePath,
      fileName,
      duration,
      metadata,
    };
  }

  /**
   * 비디오 길이 추출
   */
  private async extractDuration(filePath: string): Promise<number> {
    const meta = await this.metadataExtractor.extractVideoMetadata(filePath);
    return meta.duration;
  }

  /**
   * 기존 AssetIndex에 새 파일 추가
   */
  async addAsset(
    index: AssetIndex,
    filePath: string,
    userKeywords?: string[]
  ): Promise<AssetIndex> {
    const keywordMap = new Map<string, string[]>();
    if (userKeywords) {
      keywordMap.set(path.basename(filePath), userKeywords);
    }

    const newAsset = await this.indexSingleAsset(filePath, { keywordMap });

    return {
      assets: [...index.assets, newAsset],
      indexedAt: new Date(),
      totalDuration: index.totalDuration + newAsset.duration,
    };
  }

  /**
   * AssetIndex에서 에셋 제거
   */
  removeAsset(index: AssetIndex, assetId: string): AssetIndex {
    const asset = index.assets.find((a) => a.id === assetId);
    if (!asset) {
      return index;
    }

    return {
      assets: index.assets.filter((a) => a.id !== assetId),
      indexedAt: new Date(),
      totalDuration: index.totalDuration - asset.duration,
    };
  }
}
