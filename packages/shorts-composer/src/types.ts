/**
 * Shorts Composer 타입 정의
 *
 * Mode C: 짧은 클립 여러 개 → 릴스(9:16) rough cut 자동 조립
 */

/** 출력 해상도 프리셋 (릴스 9:16 고정) */
export type ShortsResolution = 'fhd' | '4k';

export const RESOLUTION_MAP: Record<ShortsResolution, { width: number; height: number }> = {
  fhd: { width: 1080, height: 1920 },
  '4k': { width: 2160, height: 3840 },
};

/** 클립 하나당 사용할 길이 범위 (초). 기본 1.0 ~ 2.5초 */
export interface ClipDurationRange {
  min: number;
  max: number;
}

/** 자막 위치 */
export type SubtitlePosition = 'center' | 'bottom';

/**
 * 자막 끊기 단위.
 *  - 'syllable' : 음절 덩어리 (기본 3음절, 빠른 숏폼 템포)
 *  - 'sentence' : 문장 단위로 유지 (긴 문장은 한 줄 폭을 넘지 않게 단어 경계로 분할)
 */
export type SubtitleChunkMode = 'syllable' | 'sentence';

/**
 * 자막 출력 방식.
 *  - 'burn' : 영상에 구움 (예쁨, 수정 불가) — 기본값
 *  - 'srt'  : .srt 파일만 별도 출력 (캡컷에서 편집 가능, 스타일은 캡컷 것)
 *  - 'both' : 구운 영상 + .srt 백업 둘 다
 */
export type SubtitleMode = 'burn' | 'srt' | 'both';

export interface SubtitleStyleOptions {
  /** fonts.ts 레지스트리의 폰트 id. 기본 'pretendard-extrabold' */
  fontId?: string;
  /** PlayRes 1080x1920 기준 폰트 크기. 기본 96 (4K 출력 시 자동 스케일) */
  fontSize?: number;
  /** 자막 끊기 단위. 기본 'syllable' */
  chunkMode?: SubtitleChunkMode;
  /** 자막 한 덩어리당 음절 수 ('syllable' 모드). 기본 3 */
  chunkSyllables?: number;
  /** 'sentence' 모드에서 한 줄 최대 음절 (넘으면 분할 — 줄바꿈 방지). 기본 9 */
  maxLineSyllables?: number;
  /** 음성 없을 때 템포: 초당 음절 수. 클수록 빠름. 기본 6 */
  syllablesPerSecond?: number;
  /** '#RRGGBB' 글자색. 기본 '#FFFFFF' */
  primaryColor?: string;
  /** '#RRGGBB' 외곽선색. 기본 '#000000' */
  outlineColor?: string;
  /** 자막 위치. 기본 'center' (릴스 스타일) */
  position?: SubtitlePosition;
  /** CapCut 스타일 pop-in 애니메이션. 기본 true */
  popIn?: boolean;
}

/** STT 등 외부에서 계산된 단어 타임스탬프 (있으면 템포 대신 이걸 사용) */
export interface WordTiming {
  text: string;
  /** 초 */
  start: number;
  /** 초 */
  end: number;
}

export interface ShortsCompositionSpec {
  /** B-roll 클립 경로들 (순서 유지, 부족하면 순환 재사용) */
  clips: string[];
  /** 클립당 사용 길이. 기본 { min: 1.0, max: 2.5 } */
  clipDuration?: ClipDurationRange;
  /** 자막 스크립트. 없으면 자막 없이 조립만 */
  script?: string;
  /** 보이스오버 오디오 (mp3/wav 등). 있으면 총 길이 = 오디오 길이 */
  voiceoverPath?: string;
  /** STT 단어 타임스탬프 (voiceover와 함께 사용 시 자막 싱크 정확도 향상) */
  wordTimings?: WordTiming[];
  /**
   * 미리 만들어진(사용자가 검수/수정한) 자막 이벤트.
   * 있으면 script/wordTimings 로 다시 만들지 않고 이걸 그대로 사용한다.
   */
  events?: SubtitleEvent[];
  /** 자막 출력 방식. 기본 'burn' */
  subtitleMode?: SubtitleMode;
  /** 자막 스타일 */
  subtitle?: SubtitleStyleOptions;
  /** 출력 mp4 경로 */
  outputPath: string;
  /** 기본 'fhd' (1080x1920). '4k' = 2160x3840 */
  resolution?: ShortsResolution;
  /** 기본 30 */
  fps?: number;
  /** 배경음악 (선택). 보이스오버와 함께면 -14dB 덕킹 */
  bgmPath?: string;
}

export type ComposeStage = 'probe' | 'normalize' | 'concat' | 'render';

export interface ComposeProgress {
  stage: ComposeStage;
  /** 0~1 (전체 기준) */
  progress: number;
  message: string;
}

export type ComposeProgressCallback = (p: ComposeProgress) => void;

/** 조립 계획의 세그먼트 하나 (클립 i를 어디서부터 몇 초 쓸지) */
export interface SegmentPlan {
  clipPath: string;
  /** 소스에서 시작 오프셋 (초) */
  sourceStart: number;
  /** 사용 길이 (초) */
  duration: number;
}

export interface ComposeResult {
  outputPath: string;
  durationSec: number;
  segmentCount: number;
  subtitleEventCount: number;
  width: number;
  height: number;
  /** 'srt'/'both' 모드에서 생성된 .srt 경로 */
  srtPath?: string;
}

/** 자막 이벤트 (ASS Dialogue 하나) */
export interface SubtitleEvent {
  text: string;
  start: number;
  end: number;
}
