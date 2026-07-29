/**
 * CrosscutPlanner
 *
 * Mode B 러프컷 생성 통합 엔진
 */

import type {
  SentenceTimeline,
  AssetIndex,
  RoughCutTimeline,
  MatchConfig,
} from '@cutback/shared';
import { ClipMatcher } from '@cutback/clip-matcher';
import { TimelineBuilder } from './timeline-builder.js';

export class CrosscutPlanner {
  private clipMatcher: ClipMatcher;
  private timelineBuilder: TimelineBuilder;

  constructor() {
    this.clipMatcher = new ClipMatcher();
    this.timelineBuilder = new TimelineBuilder();
  }

  /**
   * SentenceTimeline + AssetIndex → RoughCutTimeline 생성
   */
  async generateRoughCut(
    sentenceTimeline: SentenceTimeline,
    assetIndex: AssetIndex,
    config: MatchConfig
  ): Promise<RoughCutTimeline> {
    // 1. 각 문장에 대한 클립 후보 매칭
    const matchResults = this.clipMatcher.matchBatch(
      sentenceTimeline.sentences,
      assetIndex,
      config
    );

    // 2. 타임라인 빌드
    const roughCut = this.timelineBuilder.buildRoughCut(
      sentenceTimeline.sentences,
      matchResults,
      assetIndex,
      config
    );

    return roughCut;
  }

  /**
   * EDL 형식으로 내보내기
   */
  exportToEDL(timeline: RoughCutTimeline, assetIndex: AssetIndex): string {
    let edl = 'TITLE: Cutback Rough Cut\n';
    edl += 'FCM: NON-DROP FRAME\n\n';

    const videoTrack = timeline.tracks.find((t) => t.type === 'video');
    if (!videoTrack) return edl;

    videoTrack.clips.forEach((clip, index) => {
      const asset = assetIndex.assets.find((a) => a.id === clip.assetId);
      if (!asset) return;

      const eventNumber = String(index + 1).padStart(3, '0');
      const sourceIn = this.formatTimecode(clip.sourceIn);
      const sourceOut = this.formatTimecode(clip.sourceOut);
      const recordIn = this.formatTimecode(clip.timelineStart);
      const recordOut = this.formatTimecode(clip.timelineEnd);

      edl += `${eventNumber}  ${asset.fileName}       V     C        ${sourceIn} ${sourceOut} ${recordIn} ${recordOut}\n`;

      // 속도 조정이 있으면 M2 이벤트 추가
      if (clip.playbackSpeed !== 1.0) {
        edl += `* M2 ${asset.fileName}       ${clip.playbackSpeed.toFixed(2)}\n`;
      }
    });

    return edl;
  }

  /**
   * 초를 타임코드로 변환 (HH:MM:SS:FF)
   */
  private formatTimecode(seconds: number): string {
    const fps = 30; // 기본 30fps
    const totalFrames = Math.floor(seconds * fps);

    const hours = Math.floor(totalFrames / (fps * 3600));
    const minutes = Math.floor((totalFrames % (fps * 3600)) / (fps * 60));
    const secs = Math.floor((totalFrames % (fps * 60)) / fps);
    const frames = totalFrames % fps;

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}:${String(frames).padStart(2, '0')}`;
  }
}
