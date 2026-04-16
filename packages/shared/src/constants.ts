/** 앱 전역 상수 */

/**
 * 한국어 Filler Word Dictionary
 *
 * 주의: 매칭 시 filler-detector가 문장부호/공백 제거 + 반복 자모 축약을 적용한다.
 * 따라서 여기엔 "정규화된 베이스 형태"만 넣는다.
 *   - "어..." / "어," / "어~" → 모두 "어"로 정규화되어 매칭됨
 *   - "어어어" / "어어어어" → "어어"로 축약되어 매칭됨
 */
export const KOREAN_FILLER_WORDS = {
  high_confidence: [
    // 순수 감탄/머뭇거림
    '어',
    '음',
    '어어',
    '음음',
    '에에',
    '으',
    '으음',
    '아',
    '에',
    '엄',
    '엥',
    '응',
    '으응',
    '아아',
    // 추임새
    '뭐랄까',
    '뭐냐면',
    '뭐였더라',
  ],
  medium_confidence: [
    '약간',
    '뭔가',
    '좀',
    '되게',
    '진짜',
    '완전',
    '엄청',
    '막',
    '뭐',
    '그',
    '이',
    '저',
    '인제',
    '그게',
    '저기',
    '저기요',
  ],
  context_dependent: [
    '사실',
    '그니까',
    '근데',
    '이제',
    '그래서',
    '그럼',
    '일단',
    '아무튼',
    '어쨌든',
    '그러니까',
    '하여튼',
    '뭐든',
  ],
};

/** Python 서비스 포트 */
export const PYTHON_SERVICES = {
  STT_PORT: 5555,
  VAD_PORT: 5556,
  // Whisper base 모델로 6분 영상 transcription = CPU에서 1-5분 소요.
  // 타임아웃을 넉넉하게 잡고 재시도 최소화 (재시도 시 서버 상태 꼬임 방지).
  TIMEOUT_MS: 600000, // 10분
  RETRY_ATTEMPTS: 1,
  RETRY_DELAY_MS: 2000,
};

/** 오디오 처리 기본값 */
export const AUDIO_DEFAULTS = {
  SAMPLE_RATE: 16000, // Whisper 권장
  CHANNELS: 1, // mono
  FORMAT: 'wav',
  SILENCE_THRESHOLD_DB: -35,
  MIN_SILENCE_DURATION_MS: 500,
};

/** 자막 처리 기본값 */
export const CAPTION_DEFAULTS = {
  MAX_CHARS_PER_LINE: 18,
  MAX_LINES: 2,
  DEFAULT_DURATION_SEC: 3,
  MIN_DURATION_SEC: 1,
  MAX_DURATION_SEC: 7,
};

/** 파일 경로 */
export const PATHS = {
  PRESETS_DIR: 'presets',
  TEMP_DIR: 'temp',
  LOGS_DIR: 'logs',
  DB_FILE: 'cutback.db',
};

/** 로그 레벨 */
export const LOG_LEVELS = ['error', 'warn', 'info', 'debug'] as const;

/** IPC 채널 */
export const IPC_CHANNELS = {
  // Job Management
  JOB_CREATE: 'job:create',
  JOB_CANCEL: 'job:cancel',
  JOB_LIST: 'job:list',
  JOB_GET: 'job:get',

  // Job Events (Main → Renderer)
  JOB_PROGRESS: 'job:progress',
  JOB_COMPLETED: 'job:completed',
  JOB_ERROR: 'job:error',

  // Preset Management
  PRESET_LOAD: 'preset:load',
  PRESET_LIST: 'preset:list',
  PRESET_SAVE: 'preset:save',
  PRESET_DELETE: 'preset:delete',

  // Export
  EXPORT_EDL: 'export:edl',
  EXPORT_CAPCUT: 'export:capcut',
  EXPORT_SRT: 'export:srt',
  EXPORT_VIDEO: 'export:video',

  // Settings
  SETTINGS_GET: 'settings:get',
  SETTINGS_SET: 'settings:set',

  // Health / Preflight
  HEALTH_GET: 'health:get',
  HEALTH_CHANGED: 'health:changed',

  // Auto Update
  UPDATE_CHECK: 'update:check',
  UPDATE_STATUS: 'update:status',
  UPDATE_INSTALL: 'update:install',
} as const;

/** 자연스러움 점수 임계값 */
export const NATURALNESS_THRESHOLDS = {
  EXCELLENT: 0.9,
  GOOD: 0.75,
  ACCEPTABLE: 0.6,
  POOR: 0.5,
};

/** CapCut 기본 설정 */
export const CAPCUT_DEFAULTS = {
  EXECUTABLE_NAME: 'CapCut.exe',
  PROCESS_NAME: 'CapCut',
  DEFAULT_SHORTCUTS: {
    import: 'ctrl+i',
    split: 's',
    delete: 'delete',
    undo: 'ctrl+z',
  },
};
