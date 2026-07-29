/**
 * TimelineBuilder
 *
 * TimelineClip 배치 및 타임라인 생성
 */

import type {
  Sentence,
  Asset,
  AssetIndex,
  ClipCandidate,
  TimelineClip,
  Track,
  RoughCutTimeline,
  MatchConfig,
} from '@cutback/shared';
import { v4 as uuidv4 } from 'uuid';
import { AdjustmentStrategy } from './adjustment-strategy.js';

export class TimelineBuilder {
  private adjustmentStrategy: AdjustmentStrategy;

  constructor() {
    this.adjustmentStrategy = new AdjustmentStrategy();
  }

  /**
   * 문장 + 매칭 후보 → TimelineClip 생성
   */
  createTimelineClip(
    sentence: Sentence,
    asset: Asset,
    candidate: ClipCandidate,
    timelineStart: number,
    config: MatchConfig
  ): TimelineClip {
    const adjustment = this.adjustmentStrategy.decide(
      sentence,
      asset,
      candidate,
      config
    );

    return {
      id: uuidv4(),
      sentenceId: sentence.id,
      assetId: asset.id,
      timelineStart,
      timelineEnd: timelineStart + sentence.duration,
      sourceIn: adjustment.sourceIn,
      sourceOut: adjustment.sourceOut,
      playbackSpeed: adjustment.playbackSpeed,
      confidence: candidate.score,
      alternatives: [], // 다른 후보들 (UI에서 교체 가능)
      adjustmentStrategy: adjustment.strategy,
    };
  }

  /**
   * 여러 문장에 대한 러프컷 타임라인 생성
   */
  buildRoughCut(
    sentences: Sentence[],
    matchResults: Map<string, ClipCandidate[]>,
    assetIndex: AssetIndex,
    config: MatchConfig
  ): RoughCutTimeline {
    const videoTrack: Track = {
      id: uuidv4(),
      type: 'video',
      clips: [],
    };

    let currentTime = 0;
    let totalConfidence = 0;
    let reviewRequiredCount = 0;

    for (const sentence of sentences) {
      const candidates = matchResults.get(sentence.id) || [];
      const bestCandidate = candidates[0]; // 최고 점수 후보

      if (!bestCandidate) {
        // 매칭 실패 - 검수 필요 표시
        console.warn(`No candidate for sentence: ${sentence.id}`);
        reviewRequiredCount++;
        currentTime += sentence.duration;
        continue;
      }

      const asset = assetIndex.assets.find(
        (a) => a.id === bestCandidate.assetId
      );

      if (!asset) {
        console.error(`Asset not found: ${bestCandidate.assetId}`);
        currentTime += sentence.duration;
        continue;
      }

      const clip = this.createTimelineClip(
        sentence,
        asset,
        bestCandidate,
        currentTime,
        config
      );

      // 대체 후보 저장 (상위 3개)
      clip.alternatives = candidates.slice(1, 4);

      videoTrack.clips.push(clip);
      totalConfidence += clip.confidence;

      // 낮은 confidence는 검수 필요
      if (clip.confidence < 0.6) {
        reviewRequiredCount++;
      }

      currentTime += sentence.duration;
    }

    const averageConfidence =
      videoTrack.clips.length > 0
        ? totalConfidence / videoTrack.clips.length
        : 0;

    return {
      tracks: [videoTrack],
      totalDuration: currentTime,
      metadata: {
        sentenceCount: sentences.length,
        assetCount: assetIndex.assets.length,
        averageConfidence,
        reviewRequiredCount,
      },
    };
  }

  /**
   * 타임라인 클립 교체 (사용자 수동 조정)
   */
  replaceClip(
    timeline: RoughCutTimeline,
    clipId: string,
    newCandidate: ClipCandidate,
    assetIndex: AssetIndex,
    sentence: Sentence,
    config: MatchConfig
  ): RoughCutTimeline {
    const videoTrack = timeline.tracks.find((t) => t.type === 'video');
    if (!videoTrack) return timeline;

    const clipIndex = videoTrack.clips.findIndex((c) => c.id === clipId);
    if (clipIndex === -1) return timeline;

    const oldClip = videoTrack.clips[clipIndex];
    const asset = assetIndex.assets.find((a) => a.id === newCandidate.assetId);
    if (!asset) return timeline;

    const newClip = this.createTimelineClip(
      sentence,
      asset,
      newCandidate,
      oldClip.timelineStart,
      config
    );

    // 대체 후보 업데이트 (기존 클립을 대체 후보에 추가)
    const oldCandidate: ClipCandidate = {
      assetId: oldClip.assetId,
      score: oldClip.confidence,
      maxUsableDuration: asset.duration,
      recommendedSpeed: oldClip.playbackSpeed,
      matchReason: {},
    };
    newClip.alternatives = [oldCandidate, ...oldClip.alternatives].slice(0, 3);

    videoTrack.clips[clipIndex] = newClip;

    return { ...timeline };
  }
}
