/**
 * KeywordScorer
 *
 * 키워드 기반 문장-클립 매칭 점수 계산 (Phase 1 MVP)
 */

import type { Sentence, Asset } from '@cutback/shared';

export interface KeywordMatchResult {
  score: number; // 0.0 - 1.0
  matchedKeywords: string[];
  durationFitScore: number; // 0.0 - 1.0
}

export class KeywordScorer {
  /**
   * 문장과 에셋 간 키워드 매칭 점수 계산
   */
  scoreKeywordMatch(sentence: Sentence, asset: Asset): KeywordMatchResult {
    const sentenceKeywords = this.extractKeywords(sentence);
    const assetKeywords = asset.metadata.userKeywords || [];

    if (assetKeywords.length === 0) {
      // 키워드가 없는 에셋은 낮은 기본 점수
      return {
        score: 0.1,
        matchedKeywords: [],
        durationFitScore: this.calculateDurationFit(sentence, asset),
      };
    }

    // 키워드 매칭 개수 계산
    const matchedKeywords = assetKeywords.filter((keyword) =>
      sentenceKeywords.some((sentenceKw) =>
        this.isSimilar(keyword, sentenceKw)
      )
    );

    // 매칭 비율 계산
    const matchRatio = matchedKeywords.length / assetKeywords.length;

    // 문장 길이와 에셋 길이 적합도
    const durationFit = this.calculateDurationFit(sentence, asset);

    // 최종 점수: 키워드 매칭 70% + 길이 적합도 30%
    const score = matchRatio * 0.7 + durationFit * 0.3;

    return {
      score: Math.min(1.0, score),
      matchedKeywords,
      durationFitScore: durationFit,
    };
  }

  /**
   * 문장에서 키워드 추출
   * (Phase 1: 단순 명사 추출, Phase 2+: NLP 형태소 분석)
   */
  private extractKeywords(sentence: Sentence): string[] {
    // 사용자 지정 키워드 우선 사용
    if (sentence.metadata?.user_keywords) {
      return sentence.metadata.user_keywords;
    }

    // 간단한 키워드 추출 (공백 기준 토큰화)
    const tokens = sentence.text
      .toLowerCase()
      .replace(/[.,!?。？！]/g, '')
      .split(/\s+/)
      .filter((token) => token.length > 1); // 한 글자 제외

    return tokens;
  }

  /**
   * 두 키워드의 유사도 판단
   * (Phase 1: 단순 일치, Phase 2+: 형태소/임베딩 기반 유사도)
   */
  private isSimilar(keyword1: string, keyword2: string): boolean {
    const k1 = keyword1.toLowerCase().trim();
    const k2 = keyword2.toLowerCase().trim();

    // 완전 일치
    if (k1 === k2) return true;

    // 부분 포함
    if (k1.includes(k2) || k2.includes(k1)) return true;

    return false;
  }

  /**
   * 문장 길이와 에셋 길이의 적합도 계산
   */
  private calculateDurationFit(sentence: Sentence, asset: Asset): number {
    const sentenceDuration = sentence.duration;
    const assetDuration = asset.duration;

    if (assetDuration === 0) return 0;

    // 에셋이 문장보다 길면 OK (트리밍 가능)
    if (assetDuration >= sentenceDuration) {
      return 1.0;
    }

    // 에셋이 문장보다 짧으면 속도 조정 필요
    // 최대 1.5배 빠르게까지 허용 가능하다고 가정
    const speedNeeded = sentenceDuration / assetDuration;

    if (speedNeeded <= 1.5) {
      // 1.5배 이하 속도 조정이면 감점 없음
      return 1.0;
    } else if (speedNeeded <= 2.0) {
      // 1.5~2.0배 사이는 점진적 감점
      return 1.0 - ((speedNeeded - 1.5) / 0.5) * 0.5;
    } else {
      // 2배 이상 속도 조정 필요하면 부적합
      return 0.2;
    }
  }
}
