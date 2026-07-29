/**
 * AdjustmentStrategy
 *
 * 클립 길이 조정 전략 결정
 */

import type { Sentence, Asset, ClipCandidate, MatchConfig } from '@cutback/shared';

export type AdjustmentType = 'trim' | 'speed' | 'repeat' | 'freeze';

export interface AdjustmentDecision {
  strategy: AdjustmentType;
  /** 트리밍 시작 지점 (초) */
  sourceIn: number;
  /** 트리밍 종료 지점 (초) */
  sourceOut: number;
  /** 재생 속도 (1.0 = 원속도) */
  playbackSpeed: number;
  /** 반복 횟수 (repeat 전략 시) */
  repeatCount?: number;
}

export class AdjustmentStrategy {
  /**
   * 최적의 조정 전략 결정
   */
  decide(
    sentence: Sentence,
    asset: Asset,
    _candidate: ClipCandidate,
    config: MatchConfig
  ): AdjustmentDecision {
    const sentenceDuration = sentence.duration;
    const assetDuration = asset.duration;

    // Case 1: 에셋이 충분히 길면 트리밍
    if (assetDuration >= sentenceDuration) {
      return this.createTrimDecision(sentenceDuration, assetDuration);
    }

    // Case 2: 에셋이 짧지만 속도 조정으로 커버 가능
    const speedNeeded = sentenceDuration / assetDuration;
    if (
      speedNeeded >= config.speedAdjustment.min &&
      speedNeeded <= config.speedAdjustment.max
    ) {
      return this.createSpeedDecision(assetDuration, speedNeeded);
    }

    // Case 3: 반복 허용 시 클립 반복
    if (config.allowRepeat) {
      return this.createRepeatDecision(sentenceDuration, assetDuration);
    }

    // Case 4: Freeze frame (마지막 프레임 정지)
    if (config.allowFreeze) {
      return this.createFreezeDecision(sentenceDuration, assetDuration);
    }

    // Fallback: 트리밍 (부족하더라도)
    return this.createTrimDecision(sentenceDuration, assetDuration);
  }

  /**
   * 트리밍 전략
   */
  private createTrimDecision(
    sentenceDuration: number,
    assetDuration: number
  ): AdjustmentDecision {
    // 에셋 중앙 부분 사용
    const useDuration = Math.min(sentenceDuration, assetDuration);
    const offset = (assetDuration - useDuration) / 2;

    return {
      strategy: 'trim',
      sourceIn: Math.max(0, offset),
      sourceOut: Math.min(assetDuration, offset + useDuration),
      playbackSpeed: 1.0,
    };
  }

  /**
   * 속도 조정 전략
   */
  private createSpeedDecision(
    assetDuration: number,
    speed: number
  ): AdjustmentDecision {
    return {
      strategy: 'speed',
      sourceIn: 0,
      sourceOut: assetDuration,
      playbackSpeed: speed,
    };
  }

  /**
   * 반복 전략
   */
  private createRepeatDecision(
    sentenceDuration: number,
    assetDuration: number
  ): AdjustmentDecision {
    const repeatCount = Math.ceil(sentenceDuration / assetDuration);

    return {
      strategy: 'repeat',
      sourceIn: 0,
      sourceOut: assetDuration,
      playbackSpeed: 1.0,
      repeatCount,
    };
  }

  /**
   * Freeze frame 전략
   */
  private createFreezeDecision(
    _sentenceDuration: number,
    assetDuration: number
  ): AdjustmentDecision {
    // 에셋 전체 재생 + 마지막 프레임 freeze
    // TODO: Phase 2 - sentenceDuration을 사용하여 freeze 구간 길이 계산
    return {
      strategy: 'freeze',
      sourceIn: 0,
      sourceOut: assetDuration,
      playbackSpeed: 1.0,
    };
  }
}
