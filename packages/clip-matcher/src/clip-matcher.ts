/**
 * ClipMatcher
 *
 * 문장-클립 매칭 통합 엔진
 */

import type {
  Sentence,
  AssetIndex,
  ClipCandidate,
  MatchConfig,
} from '@cutback/shared';
import { KeywordScorer } from './keyword-scorer.js';

export class ClipMatcher {
  private keywordScorer: KeywordScorer;

  constructor() {
    this.keywordScorer = new KeywordScorer();
  }

  /**
   * 문장에 매칭되는 클립 후보 목록 생성
   */
  findCandidates(
    sentence: Sentence,
    assetIndex: AssetIndex,
    config: MatchConfig
  ): ClipCandidate[] {
    const candidates: ClipCandidate[] = [];

    for (const asset of assetIndex.assets) {
      const result = this.keywordScorer.scoreKeywordMatch(sentence, asset);

      // 최소 점수 필터링
      if (result.score < config.keywordMatching.minScore) {
        continue;
      }

      candidates.push({
        assetId: asset.id,
        score: result.score,
        maxUsableDuration: asset.duration,
        recommendedSpeed: this.calculateRecommendedSpeed(
          sentence.duration,
          asset.duration,
          config
        ),
        matchReason: {
          keywordMatch: result.matchedKeywords.length > 0,
          durationFit: result.durationFitScore > 0.7,
        },
      });
    }

    // 점수 순으로 정렬 (높은 순)
    candidates.sort((a, b) => b.score - a.score);

    return candidates;
  }

  /**
   * 추천 재생 속도 계산
   */
  private calculateRecommendedSpeed(
    sentenceDuration: number,
    assetDuration: number,
    config: MatchConfig
  ): number {
    if (assetDuration >= sentenceDuration) {
      // 에셋이 충분히 길면 원속도
      return 1.0;
    }

    // 속도 조정 필요
    const neededSpeed = sentenceDuration / assetDuration;

    // 설정 범위 내로 제한
    return Math.min(
      Math.max(neededSpeed, config.speedAdjustment.min),
      config.speedAdjustment.max
    );
  }

  /**
   * 여러 문장에 대한 일괄 매칭
   */
  matchBatch(
    sentences: Sentence[],
    assetIndex: AssetIndex,
    config: MatchConfig
  ): Map<string, ClipCandidate[]> {
    const results = new Map<string, ClipCandidate[]>();

    for (const sentence of sentences) {
      const candidates = this.findCandidates(sentence, assetIndex, config);
      results.set(sentence.id, candidates);
    }

    return results;
  }

  /**
   * 베스트 매칭 후보 선택 (가장 높은 점수)
   */
  selectBestCandidate(candidates: ClipCandidate[]): ClipCandidate | null {
    if (candidates.length === 0) return null;
    return candidates[0]; // 이미 점수 순 정렬되어 있음
  }
}
