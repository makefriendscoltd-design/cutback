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
  videoPath: string;
  presetId: string;
  status: JobStatus;
  progress: number; // 0-100
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
  results?: JobResults;
}

/** 작업 결과 */
export interface JobResults {
  transcript: Transcript;
  cutDecisions: CutDecision[];
  captions: Caption[];
  naturalness_score: number;
  statistics: Statistics;
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

/** Cut Decision */
export interface CutDecision {
  id: string;
  type: 'silence' | 'filler_word' | 'retake';
  start: number; // 초 단위
  end: number;
  duration: number;
  /** 0.0 ~ 1.0. filler 의 경우 lexicon base_score * context_multiplier 계산값. */
  confidence: number;
  /** 사람이 읽을 수 있는 제거 사유 (UI 표시용). */
  reason?: string;
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
  canvas: CanvasParams;
  audio: AudioParams;
  filler_words: FillerWordParams;
  captions: CaptionParams;
  style: CaptionStyle;
  pacing: PacingParams;
  effects?: EffectParams;
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
