/**
 * @cutback/shorts-composer
 *
 * Mode C: 짧은 클립 여러 개를 속도감 있게 이어붙여 릴스(9:16) 영상으로 자동 조립.
 *  - 클립당 1.0~2.5초(조정 가능) 사용, 목표 길이에 맞춰 순환 재사용
 *  - 보이스오버(선택) / 음절 단위 빠른 템포 자막 (ASS 하드번, Pretendard/SUIT)
 *  - FHD(1080x1920) 또는 4K(2160x3840) mp4 추출
 */

export * from './types.js';
export {
  chunkScript,
  countSyllables,
  buildTempoEvents,
  buildScaledEvents,
  buildTimedEvents,
  buildSubtitleEvents,
  generateAss,
  generateSrt,
} from './subtitle-engine.js';
export { getMediaDuration, probeMedia, normalizeClip, type MediaProbe } from './clip-normalizer.js';
export { ShortsComposer, planSegments } from './shorts-composer.js';
export {
  FONTS,
  DEFAULT_FONT_ID,
  getFont,
  getFontsDir,
  setFontsDir,
  isFontAvailable,
  listFonts,
  type FontDef,
} from './fonts.js';
