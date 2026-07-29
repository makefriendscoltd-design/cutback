// 공통 타입 정의

/** 작업 상태 */
export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

/** 작업 타입 */
export interface Job {
  id: string;
  /** Mode A: 단일 영상, Mode B: 보이스오버 오디오 */
  videoPath: string;
  /** Mode B 전용: B-roll 클립 경로 목록 */
  assetPaths?: string[];
  presetId: string;
  status: JobStatus;
  progress: number; // 0-100
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
  /** 편집 모드 (기본: mode-a) */
  editMode?: EditMode;
  results?: JobResults;
}

/** 작업 결과 */
export interface JobResults {
  /** Mode A: Transcript, Mode B: Sentence Timeline */
  transcript?: Transcript;
  sentenceTimeline?: SentenceTimeline;
  /** Mode A: Cut Decisions */
  cutDecisions?: CutDecision[];
  /** Mode A: Captions */
  captions?: Caption[];
  /** Mode B: Asset Index */
  assetIndex?: AssetIndex;
  /** Mode B: Rough Cut Timeline */
  roughCutTimeline?: RoughCutTimeline;
  naturalness_score?: number;
  statistics?: Statistics;
}

/** Word-level transcript */
export interface Word {
  text: string;
  start: number; // 초 단위
  end: number;
  confidence: number; // 0.0 - 1.0
}

/** Transcript */
export interface Transcript {
  words: Word[];
  full_text: string;
  language: string;
  duration: number;
}

/**
 * Cut decision 의 source 식별자.
 * - automatic: 분석 파이프라인이 자동 감지
 * - manual_override: 사용자가 UI 에서 수동 추가
 * - preset_rule: 프리셋 규칙에 의해 강제 적용 (예: hook_first_3sec)
 * - calibration: 사용자 선호 학습 결과 (Phase 2 calibration 시스템)
 */
export type CutDecisionSource =
  | 'automatic'
  | 'manual_override'
  | 'preset_rule'
  | 'calibration';

/**
 * Cut decision 의 정규화된 reason code.
 * UI/통계/필터링용 머신 식별자. 사람이 읽을 메시지는 reasonText 사용.
 */
export type CutDecisionReason =
  | 'silence_over_threshold'  // 무음이 threshold 보다 김
  | 'filler_detected'          // filler word 감지
  | 'duplicate_phrase'         // retake 후보 (중복 발화)
  | 'manual_override'          // 사용자 직접 추가/제거
  | 'preset_rule'              // 프리셋 규칙 적용
  | 'caption_segment';         // 자막 세그먼트 경계 (cut 아님, 표시용)

/** Cut Decision */
export interface CutDecision {
  id: string;
  type: 'silence' | 'filler_word' | 'retake' | 'caption_segment';
  start: number; // 초 단위
  end: number;
  duration: number;
  /** 0.0 ~ 1.0. filler 의 경우 lexicon base_score * context_multiplier 계산값. */
  confidence: number;
  /** 정규화된 reason code (필터링/통계용). */
  reason: CutDecisionReason;
  /** 사람이 읽을 수 있는 제거 사유 (UI 표시용 한 줄 설명). */
  reasonText?: string;
  /** 어디서 만들어진 결정인지 */
  source: CutDecisionSource;
  /**
   * 적용된 프리셋 규칙 식별자.
   * 예: "audio.silence_threshold_db", "filler_words.removal_strength=aggressive"
   * UI 에서 "왜 이게 잘렸는지" 설명할 때 표시.
   */
  presetRule?: string;
  /**
   * confidence 가 review_band 안이라 자동 적용을 보류한 경우 true.
   * UI 의 review queue 에서 사용자가 enable 토글하기 전까지 enabled=false.
   */
  reviewRequired?: boolean;
  metadata?: {
    db_level?: number; // silence일 경우
    filler_text?: string; // filler_word일 경우
    /** filler 분류 레벨 */
    filler_tier?: 'high_confidence' | 'medium_confidence' | 'context_dependent' | 'phrase';
    /** 점수 계산에 적용된 multiplier 라벨 (디버깅/UI) */
    score_factors?: string[];
    retake_group_id?: string; // retake일 경우
    /** caption_segment: 자막 텍스트 */
    caption_text?: string;
    /** word-level 인덱스 (transcript 와 동기화용) */
    word_indices?: number[];
  };
  user_approved?: boolean; // 사용자가 승인했는지
  enabled: boolean; // 활성화 여부 (사용자가 되돌릴 수 있음)
}

/** Caption (자막) */
export interface Caption {
  id: string;
  text: string;
  start: number;
  end: number;
  style?: CaptionStyle;
}

/** Caption Style */
export interface CaptionStyle {
  font_family: string;
  font_size: number;
  font_weight: number;
  text_color: string;
  outline_color: string;
  outline_width: number;
  shadow_enabled: boolean;
  shadow_color?: string;
  shadow_opacity?: number;
  position_vertical: 'top' | 'center' | 'bottom';
  position_offset_percent: number;
}

/** Statistics */
export interface Statistics {
  original_duration: number;
  edited_duration: number;
  silence_removed: number;
  fillers_removed: number;
  retakes_removed: number;
  total_cuts: number;
  cut_frequency: number; // cuts per minute
  naturalness_score: number;
}

/** Preset Types */
export type PresetType = 'ad-short-form' | 'info-talking-head' | 'vlog-style' | 'brand' | 'custom';

/** Audio Parameters */
export interface AudioParams {
  silence_threshold_db: number;
  min_silence_duration_ms: number;
  pre_cut_padding_ms: number;
  post_cut_padding_ms: number;
  reasoning?: string;
}

/** Filler Word Parameters */
export interface FillerWordParams {
  removal_strength: 'conservative' | 'balanced' | 'aggressive';
  context_aware: boolean;
  preserve_natural_pauses: boolean;
  custom_fillers?: string[];
  /**
   * 자동 제거 confidence 임계값 (0~1). 미지정 시 lexicon scoring.default_threshold.
   * 이 값 미만은 reviewRequired=true 로 enabled=false 채로 들어옴.
   */
  confidence_threshold?: number;
  /** 너무 짧은 filler 도 잘라내면 더 부자연스러우므로 최소 제거 길이(ms). */
  min_removable_duration_ms?: number;
  reasoning?: string;
}

/** Caption Parameters */
export interface CaptionParams {
  segmentation_mode: 'by_sentence' | 'by_time' | 'by_breath';
  max_chars_per_line: number;
  max_lines: number;
  line_break_optimization: boolean;
  emphasis_words?: string[];
  reasoning?: string;
}

/** Pacing Parameters */
export interface PacingParams {
  target_tempo: number; // words per minute
  allow_jump_cuts: boolean;
  naturalness_score_min: number;
  hook_first_3sec?: boolean;
  reasoning?: string;
}

/** Effect Parameters */
export interface EffectParams {
  auto_zoom_on_emphasis?: boolean;
  zoom_intensity?: number;
  transition_speed?: 'slow' | 'medium' | 'fast';
}

/** Canvas (영상 비율) Parameters */
export type AspectRatio = '9:16' | '16:9' | '1:1' | '4:5';
export interface CanvasParams {
  aspect_ratio: AspectRatio;
  width: number;
  height: number;
}

/** Preset */
export interface Preset {
  name: string;
  type: PresetType;
  version: string;
  description?: string;
  base_preset?: string; // brand/custom 프리셋일 경우 베이스 프리셋
  /** 편집 모드 (기본: mode-a) */
  editMode?: EditMode;
  canvas: CanvasParams;
  /** Mode A 전용 */
  audio?: AudioParams;
  filler_words?: FillerWordParams;
  captions?: CaptionParams;
  style?: CaptionStyle;
  pacing?: PacingParams;
  effects?: EffectParams;
  /** Mode B 전용 */
  modeBParams?: ModeBPresetParams;
}

/** 한국어 Filler Word Dictionary */
export interface FillerWordDictionary {
  high_confidence: string[];
  medium_confidence: string[];
  context_dependent: string[];
}

/** VAD Result */
export interface VADResult {
  timestamp: number;
  duration: number;
  is_speech: boolean;
  confidence: number;
}

/** Silence Detection Result */
export interface SilenceDetectionResult {
  timestamp: number;
  duration: number;
  confidence: number;
  db_level: number;
}

/** STT Request/Response */
export interface STTRequest {
  action: 'transcribe';
  payload: {
    audio_path: string;
    language: string;
    word_timestamps: boolean;
  };
}

export interface STTResponse {
  success: boolean;
  transcript?: Transcript;
  error?: string;
}

/** VAD Request/Response */
export interface VADRequest {
  action: 'detect_speech';
  payload: {
    audio_path: string;
  };
}

export interface VADResponse {
  success: boolean;
  results?: VADResult[];
  error?: string;
}

/** EDL (Edit Decision List) Entry */
export interface EDLEntry {
  event_number: number;
  reel: string;
  track: string;
  transition: 'C' | 'D'; // C = Cut, D = Dissolve
  source_in: string; // timecode
  source_out: string;
  record_in: string;
  record_out: string;
}

/** CapCut Automation Config */
export interface CapCutConfig {
  version: string;
  ui_positions: {
    import_button?: { x: number; y: number };
    timeline_split?: { x: number; y: number };
  };
  shortcuts: {
    import: string;
    split: string;
    delete: string;
    undo: string;
  };
}

// ============================================================================
// Mode B (Voiceover Crosscut) Types
// ============================================================================

/** Edit Mode */
export type EditMode = 'mode-a' | 'mode-b';

/** Sentence (from STT or script) */
export interface Sentence {
  id: string;
  text: string;
  start: number; // 초 단위 (보이스오버 시작 시점)
  end: number;
  duration: number; // end - start
  words: Word[]; // 원본 word-level transcript (있는 경우)
  metadata?: {
    /** 문장 의미적 태그 (Phase 2/3 용) */
    semantic_tags?: string[];
    /** 사용자가 추가한 키워드 힌트 (수동 매칭) */
    user_keywords?: string[];
  };
}

/** Sentence Timeline (Mode B 입력) */
export interface SentenceTimeline {
  sentences: Sentence[];
  totalDuration: number;
  language: string;
  source: 'stt' | 'script'; // STT로 생성 또는 스크립트 업로드
}

/** Asset (B-roll clip) */
export interface Asset {
  id: string;
  filePath: string;
  fileName: string;
  duration: number; // 초 단위
  metadata: AssetMetadata;
}

/** Asset Metadata */
export interface AssetMetadata {
  /** 파일 해시 (중복 감지용) */
  fileHash: string;
  /** 비디오 해상도 */
  resolution: {
    width: number;
    height: number;
  };
  /** 프레임레이트 */
  fps: number;
  /** 샷 분할 타임스탬프 (Phase 2 이상) */
  shotBoundaries?: number[];
  /** 사용자 입력 키워드 (Phase 1) */
  userKeywords?: string[];
  /** OCR 텍스트 (Phase 2 이상) */
  ocrText?: string;
  /** 이미지 임베딩 벡터 (Phase 3 이상 - CLIP) */
  clipEmbedding?: number[];
  /** 음성 포함 여부 */
  hasAudio?: boolean;
  /** 썸네일 경로 */
  thumbnailPath?: string;
}

/** Asset Index (Mode B 에셋 목록) */
export interface AssetIndex {
  assets: Asset[];
  indexedAt: Date;
  totalDuration: number;
}

/** Clip Candidate (문장에 매칭된 후보 클립) */
export interface ClipCandidate {
  assetId: string;
  score: number; // 0.0 - 1.0
  /** 사용 가능한 최대 길이 (초) */
  maxUsableDuration: number;
  /** 추천 재생 속도 */
  recommendedSpeed: number;
  /** 매칭 근거 */
  matchReason: {
    keywordMatch?: boolean;
    semanticMatch?: boolean;
    visualMatch?: boolean;
    durationFit?: boolean;
  };
}

/** Timeline Clip (타임라인에 배치된 클립) */
export interface TimelineClip {
  id: string;
  sentenceId: string;
  assetId: string;
  /** 타임라인 상 시작 시간 (초) */
  timelineStart: number;
  /** 타임라인 상 종료 시간 (초) */
  timelineEnd: number;
  /** 원본 에셋의 시작 지점 (초) - 트리밍 */
  sourceIn: number;
  /** 원본 에셋의 종료 지점 (초) - 트리밍 */
  sourceOut: number;
  /** 재생 속도 (1.0 = 원속도, 0.5 = 50% 슬로우, 2.0 = 200% 빠르게) */
  playbackSpeed: number;
  /** 매칭 신뢰도 (0.0 - 1.0) */
  confidence: number;
  /** 대체 가능 후보 클립 목록 */
  alternatives: ClipCandidate[];
  /** 조정 전략 */
  adjustmentStrategy?: 'trim' | 'speed' | 'repeat' | 'freeze';
}

/** Track (타임라인 트랙) */
export interface Track {
  id: string;
  type: 'video' | 'audio';
  clips: TimelineClip[];
}

/** Rough Cut Timeline (Mode B 출력) */
export interface RoughCutTimeline {
  tracks: Track[];
  totalDuration: number;
  metadata: {
    sentenceCount: number;
    assetCount: number;
    averageConfidence: number;
    /** 수동 검수 필요 클립 개수 */
    reviewRequiredCount: number;
  };
}

/** Match Config (클립 매칭 설정) */
export interface MatchConfig {
  /** Phase 1: 키워드 기반 매칭 */
  keywordMatching: {
    enabled: boolean;
    /** 최소 키워드 매칭 점수 */
    minScore: number;
  };
  /** Phase 2: 장면 감지 + OCR */
  sceneDetection?: {
    enabled: boolean;
    threshold: number;
  };
  /** Phase 3: CLIP 임베딩 */
  semanticMatching?: {
    enabled: boolean;
    model: string;
  };
  /** 속도 조정 허용 범위 */
  speedAdjustment: {
    min: number; // 예: 0.5 (50% 슬로우)
    max: number; // 예: 1.5 (150% 빠르게)
  };
  /** 클립 재사용 허용 */
  allowRepeat: boolean;
  /** Freeze frame 허용 */
  allowFreeze: boolean;
}

/**
 * Calibration: 사용자가 반복적으로 manual override 한 패턴을 저장해서
 * 다음 작업의 추천값으로 반영한다 (preset calibration 레이어).
 *
 * 예: 광고형 preset 에서 사용자가 "사실" 이라는 단어를 반복적으로 복원하면
 * → 다음 광고형 작업에서 "사실" 의 confidence 를 낮게 매겨 자동 제거 후보에서 빼준다.
 *
 * 우선 로컬 JSON 기반. 나중에 DB 로 옮기기 쉽게 Repository interface 로 감쌈.
 */
export interface PresetCalibration {
  presetId: string;
  /** 사용자가 자주 복원한 filler 단어 (자동 제거 → 사용자가 enabled=false 로 토글) */
  restoredFillers: Record<string, number>;
  /** 사용자가 자주 추가한 manual cut 의 평균 길이 (ms) */
  manualCutAvgMs: number;
  /** 사용자가 직접 만든 manual cut 개수 */
  manualCutCount: number;
  /** 사용자가 선호한 silence threshold dB 평균 */
  preferredSilenceThresholdDb?: number;
  /** 사용자가 선호한 min silence duration ms 평균 */
  preferredMinSilenceMs?: number;
  /** 사용자가 선호한 filler removal strength (가장 자주 선택한 값) */
  preferredFillerStrength?: 'conservative' | 'balanced' | 'aggressive';
  /** 누적된 작업 수 */
  sampleCount: number;
  /** 마지막 업데이트 ISO timestamp */
  lastUpdated: string;
}

/**
 * Calibration repository interface — DB 로 이관하기 쉽도록 추상화.
 */
export interface CalibrationRepository {
  get(presetId: string): Promise<PresetCalibration | null>;
  /** 부분 업데이트. sample count 는 자동 증가. */
  record(
    presetId: string,
    delta: {
      restoredFillerWords?: string[];
      manualCutDurationsMs?: number[];
      silenceThresholdDb?: number;
      minSilenceMs?: number;
      fillerStrength?: 'conservative' | 'balanced' | 'aggressive';
    }
  ): Promise<PresetCalibration>;
  reset(presetId: string): Promise<void>;
  list(): Promise<PresetCalibration[]>;
}

/**
 * Live Analysis 의 threshold 슬라이더가 호출하는 lightweight recompute API.
 *
 * 전체 pipeline (오디오 추출 + STT + spell check) 을 다시 돌리지 않고,
 * 이미 추출된 audioPath / transcript 를 재사용해서 cut decisions 만 빠르게 다시 계산한다.
 *
 * Apply 버튼이 별도로 분리되어 있지 않은 이유: 우리 pipeline 은 ffmpeg 편집을 절대 호출하지
 * 않고 cut decision 만 만든다. 실제 ffmpeg 는 export(EDL/CapCut/render) 단계에서만 호출되므로,
 * recompute 결과를 그대로 timeline 에 반영해도 비파괴적이다.
 */
export interface RecomputeRequest {
  jobId: string;
  audioPath: string;
  /** 캐시된 transcript (filler 재계산에 사용). 비어있으면 filler skip. */
  transcript?: Transcript;
  /** 베이스 프리셋 ID — fallback 으로 빈 필드를 채움 */
  presetId: string;
  /** 사용자 슬라이더로 덮어쓰는 값들 */
  overrides: {
    audio?: Partial<AudioParams>;
    filler_words?: Partial<FillerWordParams>;
  };
}

export interface RecomputeResult {
  success: boolean;
  silenceCuts?: CutDecision[];
  fillerCuts?: CutDecision[];
  /** 어떤 단계가 다시 계산됐는지 (UI 진행 표시용) */
  recomputed: ('silence' | 'filler')[];
  /** 계산 시간 (ms) — preview 빠른지 확인용 */
  durationMs: number;
  error?: string;
}

/** Mode B Preset Parameters */
export interface ModeBPresetParams {
  matchConfig: MatchConfig;
  /** 최소 confidence 로 자동 적용 (이하는 review 필요) */
  autoApplyThreshold: number;
  /** 기본 클립 전환 스타일 */
  transitionStyle?: 'cut' | 'crossfade' | 'dip_to_black';
  /** 전환 지속 시간 (ms) */
  transitionDuration?: number;
}
