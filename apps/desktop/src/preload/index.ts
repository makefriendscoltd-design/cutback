import { contextBridge, ipcRenderer } from 'electron';

/**
 * IPC 채널 상수 (인라인)
 * Electron preload 샌드박스에서는 workspace 패키지를 resolve할 수 없으므로
 * @cutback/shared 대신 직접 정의
 */
const IPC = {
  JOB_CREATE: 'job:create',
  JOB_CANCEL: 'job:cancel',
  JOB_DELETE: 'job:delete',
  JOB_LIST: 'job:list',
  JOB_GET: 'job:get',
  JOB_PROGRESS: 'job:progress',
  JOB_COMPLETED: 'job:completed',
  JOB_ERROR: 'job:error',
  JOB_PARTIAL: 'job:partial',
  AUDIO_PEAKS: 'audio:peaks',
  VIDEO_PREVIEW: 'video:preview',
  CUT_RECOMPUTE: 'cut:recompute',
  CALIBRATION_GET: 'calibration:get',
  CALIBRATION_RECORD: 'calibration:record',
  CALIBRATION_LIST: 'calibration:list',
  CALIBRATION_RESET: 'calibration:reset',
  PRESET_LOAD: 'preset:load',
  PRESET_LIST: 'preset:list',
  PRESET_SAVE: 'preset:save',
  PRESET_DELETE: 'preset:delete',
  EXPORT_EDL: 'export:edl',
  EXPORT_CAPCUT: 'export:capcut',
  EXPORT_SRT: 'export:srt',
  EXPORT_VIDEO: 'export:video',
  SETTINGS_GET: 'settings:get',
  SETTINGS_SET: 'settings:set',
  HEALTH_GET: 'health:get',
  HEALTH_CHANGED: 'health:changed',
  UPDATE_CHECK: 'update:check',
  UPDATE_STATUS: 'update:status',
  UPDATE_INSTALL: 'update:install',
} as const;

/**
 * Preload Script
 * Renderer에서 안전하게 Main Process와 통신할 수 있도록
 * contextBridge로 API를 노출
 */
contextBridge.exposeInMainWorld('api', {
  // --- Job Management ---
  createJob: (params: {
    videoPath: string;
    presetId: string;
    editMode?: 'mode-a' | 'mode-b';
    assetPaths?: string[];
  }) => ipcRenderer.invoke(IPC.JOB_CREATE, params),

  listJobs: () => ipcRenderer.invoke(IPC.JOB_LIST),

  getJob: (jobId: string) => ipcRenderer.invoke(IPC.JOB_GET, jobId),

  cancelJob: (jobId: string) =>
    ipcRenderer.invoke(IPC.JOB_CANCEL, jobId),

  deleteJob: (jobId: string) =>
    ipcRenderer.invoke(IPC.JOB_DELETE, jobId),

  toggleCut: (cutId: string, enabled: boolean) =>
    ipcRenderer.invoke('cut:toggle', { cutId, enabled }),

  // --- Job Events ---
  onJobProgress: (
    callback: (data: {
      jobId: string;
      stage: string;
      progress: number;
      detail?: string;
    }) => void
  ) => {
    const handler = (_event: Electron.IpcRendererEvent, data: unknown) =>
      callback(data as Parameters<typeof callback>[0]);
    ipcRenderer.on(IPC.JOB_PROGRESS, handler);
    return () => ipcRenderer.removeListener(IPC.JOB_PROGRESS, handler);
  },

  onJobCompleted: (
    callback: (data: { jobId: string; results: unknown }) => void
  ) => {
    const handler = (_event: Electron.IpcRendererEvent, data: unknown) =>
      callback(data as Parameters<typeof callback>[0]);
    ipcRenderer.on(IPC.JOB_COMPLETED, handler);
    return () => ipcRenderer.removeListener(IPC.JOB_COMPLETED, handler);
  },

  onJobError: (
    callback: (data: { jobId: string; error: string }) => void
  ) => {
    const handler = (_event: Electron.IpcRendererEvent, data: unknown) =>
      callback(data as Parameters<typeof callback>[0]);
    ipcRenderer.on(IPC.JOB_ERROR, handler);
    return () => ipcRenderer.removeListener(IPC.JOB_ERROR, handler);
  },

  /**
   * Live Analysis Timeline 용. 파이프라인 단계별 부분 결과 스트리밍.
   * partial 의 키 (silenceCuts, transcript, fillerCuts, retakeCuts, captionSegments,
   * audioPath) 는 단계마다 다르게 들어옴.
   */
  onJobPartial: (
    callback: (data: { jobId: string; stage: string; partial: unknown }) => void
  ) => {
    const handler = (_event: Electron.IpcRendererEvent, data: unknown) =>
      callback(data as Parameters<typeof callback>[0]);
    ipcRenderer.on(IPC.JOB_PARTIAL, handler);
    return () => ipcRenderer.removeListener(IPC.JOB_PARTIAL, handler);
  },

  /** 오디오 파형 peaks 데이터 추출 (waveform 표시용) */
  audioPeaks: (audioPath: string, bucketCount?: number) =>
    ipcRenderer.invoke(IPC.AUDIO_PEAKS, { audioPath, bucketCount }),

  /**
   * Browser-playable preview MP4 (H.264 + AAC, 480p) 생성.
   * HEVC/H.265 등 Chromium 이 디코드 못 하는 영상을 BeforeAfterPreview 에서 보기 위해.
   * 두 번째 호출부터는 캐시 hit (즉시 리턴).
   */
  generateVideoPreview: (sourcePath: string) =>
    ipcRenderer.invoke(IPC.VIDEO_PREVIEW, { sourcePath }),

  onVideoPreviewProgress: (
    callback: (data: { sourcePath: string; current: number; total: number }) => void
  ) => {
    const handler = (_e: Electron.IpcRendererEvent, data: unknown) =>
      callback(data as Parameters<typeof callback>[0]);
    ipcRenderer.on('video:preview-progress', handler);
    return () => ipcRenderer.removeListener('video:preview-progress', handler);
  },

  /** Threshold 슬라이더 preview — silence/filler 만 빠르게 다시 계산 */
  recomputeCuts: (req: {
    jobId: string;
    audioPath: string;
    transcript?: unknown;
    presetId: string;
    overrides: {
      audio?: Record<string, unknown>;
      filler_words?: Record<string, unknown>;
    };
  }) => ipcRenderer.invoke(IPC.CUT_RECOMPUTE, req),

  /** Calibration: preset 별 학습값 조회/기록 */
  getCalibration: (presetId: string) =>
    ipcRenderer.invoke(IPC.CALIBRATION_GET, presetId),
  recordCalibration: (
    presetId: string,
    delta: {
      restoredFillerWords?: string[];
      manualCutDurationsMs?: number[];
      silenceThresholdDb?: number;
      minSilenceMs?: number;
      fillerStrength?: 'conservative' | 'balanced' | 'aggressive';
    }
  ) =>
    ipcRenderer.invoke(IPC.CALIBRATION_RECORD, { presetId, delta }),
  listCalibrations: () => ipcRenderer.invoke(IPC.CALIBRATION_LIST),
  resetCalibration: (presetId: string) =>
    ipcRenderer.invoke(IPC.CALIBRATION_RESET, presetId),

  // --- Presets ---
  listPresets: () => ipcRenderer.invoke(IPC.PRESET_LIST),

  loadPreset: (presetId: string) =>
    ipcRenderer.invoke(IPC.PRESET_LOAD, presetId),

  savePreset: (id: string, preset: unknown) =>
    ipcRenderer.invoke(IPC.PRESET_SAVE, { id, preset }),

  deletePreset: (presetId: string) =>
    ipcRenderer.invoke(IPC.PRESET_DELETE, presetId),

  // --- File Dialog ---
  openVideoDialog: () => ipcRenderer.invoke('dialog:openVideo'),
  openVoiceoverDialog: () => ipcRenderer.invoke('dialog:openVoiceover'),
  openMultipleVideosDialog: () =>
    ipcRenderer.invoke('dialog:openMultipleVideos') as Promise<string[]>,

  // --- Export ---
  exportEDL: (jobId: string) =>
    ipcRenderer.invoke(IPC.EXPORT_EDL, { jobId }),

  exportSRT: (jobId: string) =>
    ipcRenderer.invoke(IPC.EXPORT_SRT, { jobId }),

  exportCapCut: (jobId: string) =>
    ipcRenderer.invoke(IPC.EXPORT_CAPCUT, { jobId }),

  renderVideo: (jobId: string) =>
    ipcRenderer.invoke(IPC.EXPORT_VIDEO, { jobId }),

  // --- CapCut Automation ---
  getCapCutStatus: () =>
    ipcRenderer.invoke('capcut:status'),

  applyToCapCut: (jobId: string) =>
    ipcRenderer.invoke('capcut:apply', { jobId }),

  // --- Mode C: Shorts Composer ---
  listShortsFonts: () => ipcRenderer.invoke('shorts:fonts'),

  previewShortsSubtitles: (params: {
    script?: string;
    voiceoverPath?: string;
    chunkMode?: 'syllable' | 'sentence';
    chunkSyllables?: number;
    maxLineSyllables?: number;
    syllablesPerSecond?: number;
  }) => ipcRenderer.invoke('shorts:previewSubtitles', params),

  composeShorts: (spec: ShortsComposeParams) =>
    ipcRenderer.invoke('shorts:compose', spec),

  onShortsProgress: (
    callback: (data: { stage: string; progress: number; message: string }) => void
  ) => {
    const handler = (_event: Electron.IpcRendererEvent, data: unknown) =>
      callback(data as Parameters<typeof callback>[0]);
    ipcRenderer.on('shorts:progress', handler);
    return () => ipcRenderer.removeListener('shorts:progress', handler);
  },

  // --- Health / Preflight ---
  getHealth: (force?: boolean) =>
    ipcRenderer.invoke(IPC.HEALTH_GET, force ? { force: true } : undefined),

  // --- Auto Update ---
  checkUpdates: () => ipcRenderer.invoke(IPC.UPDATE_CHECK),
  getUpdateStatus: () => ipcRenderer.invoke(IPC.UPDATE_STATUS),
  installUpdate: () => ipcRenderer.invoke(IPC.UPDATE_INSTALL),
  onUpdateStatus: (callback: (status: UpdateStatus) => void) => {
    const handler = (_event: Electron.IpcRendererEvent, data: unknown) =>
      callback(data as UpdateStatus);
    ipcRenderer.on(IPC.UPDATE_STATUS, handler);
    return () => ipcRenderer.removeListener(IPC.UPDATE_STATUS, handler);
  },
});

// 검수/수정된 자막 이벤트 하나
export interface ShortsSubtitleEvent {
  text: string;
  start: number;
  end: number;
}

// Mode C compose 파라미터 (outputPath 는 main 의 저장 다이얼로그에서 결정)
export interface ShortsComposeParams {
  clips: string[];
  clipDuration?: { min: number; max: number };
  script?: string;
  voiceoverPath?: string;
  bgmPath?: string;
  resolution?: 'fhd' | '4k';
  /** 사용자가 검수/수정한 자막 이벤트. 있으면 script 대신 이걸 사용 */
  events?: ShortsSubtitleEvent[];
  /** 자막 출력 방식. 기본 'burn' */
  subtitleMode?: 'burn' | 'srt' | 'both';
  subtitle?: {
    fontId?: string;
    chunkMode?: 'syllable' | 'sentence';
    chunkSyllables?: number;
    maxLineSyllables?: number;
    syllablesPerSecond?: number;
    position?: 'center' | 'bottom';
  };
}

export interface ShortsFontInfo {
  id: string;
  family: string;
  license: string;
  available: boolean;
}

// 업데이트 상태 타입 (renderer 도 사용)
export type UpdateStatus =
  | { phase: 'idle' }
  | { phase: 'checking' }
  | { phase: 'available'; version: string; releaseNotes?: string }
  | { phase: 'not-available'; version: string }
  | { phase: 'downloading'; percent: number; transferred: number; total: number }
  | { phase: 'downloaded'; version: string }
  | { phase: 'error'; message: string };

// 타입 선언 (Renderer에서 window.api 사용 시)
export interface CutbackAPI {
  createJob: (params: {
    videoPath: string;
    presetId: string;
    editMode?: 'mode-a' | 'mode-b';
    assetPaths?: string[];
  }) => Promise<{ success: boolean; job?: unknown; error?: string }>;
  listJobs: () => Promise<unknown[]>;
  getJob: (
    jobId: string
  ) => Promise<{ job: unknown; results: unknown | null }>;
  cancelJob: (jobId: string) => Promise<{ success: boolean }>;
  deleteJob: (
    jobId: string
  ) => Promise<{ success: boolean; error?: string }>;
  toggleCut: (
    cutId: string,
    enabled: boolean
  ) => Promise<{ success: boolean }>;
  onJobProgress: (
    callback: (data: {
      jobId: string;
      stage: string;
      progress: number;
      detail?: string;
    }) => void
  ) => () => void;
  onJobCompleted: (
    callback: (data: { jobId: string; results: unknown }) => void
  ) => () => void;
  onJobError: (
    callback: (data: { jobId: string; error: string }) => void
  ) => () => void;
  onJobPartial: (
    callback: (data: { jobId: string; stage: string; partial: unknown }) => void
  ) => () => void;
  audioPeaks: (
    audioPath: string,
    bucketCount?: number
  ) => Promise<{
    success: boolean;
    peaks?: number[];
    duration?: number;
    sampleRate?: number;
    error?: string;
  }>;
  generateVideoPreview: (sourcePath: string) => Promise<{
    success: boolean;
    previewPath?: string;
    fromCache?: boolean;
    durationMs?: number;
    error?: string;
  }>;
  onVideoPreviewProgress: (
    callback: (data: { sourcePath: string; current: number; total: number }) => void
  ) => () => void;
  recomputeCuts: (req: {
    jobId: string;
    audioPath: string;
    transcript?: unknown;
    presetId: string;
    overrides: {
      audio?: Record<string, unknown>;
      filler_words?: Record<string, unknown>;
    };
  }) => Promise<{
    success: boolean;
    silenceCuts?: unknown[];
    fillerCuts?: unknown[];
    recomputed: ('silence' | 'filler')[];
    durationMs: number;
    error?: string;
  }>;
  getCalibration: (
    presetId: string
  ) => Promise<{ success: boolean; calibration?: unknown; error?: string }>;
  recordCalibration: (
    presetId: string,
    delta: {
      restoredFillerWords?: string[];
      manualCutDurationsMs?: number[];
      silenceThresholdDb?: number;
      minSilenceMs?: number;
      fillerStrength?: 'conservative' | 'balanced' | 'aggressive';
    }
  ) => Promise<{ success: boolean; calibration?: unknown; error?: string }>;
  listCalibrations: () => Promise<{
    success: boolean;
    calibrations?: unknown[];
    error?: string;
  }>;
  resetCalibration: (
    presetId: string
  ) => Promise<{ success: boolean; error?: string }>;
  listPresets: () => Promise<unknown[]>;
  loadPreset: (presetId: string) => Promise<unknown>;
  savePreset: (id: string, preset: unknown) => Promise<{ success: boolean }>;
  deletePreset: (presetId: string) => Promise<{ success: boolean }>;
  openVideoDialog: () => Promise<string | null>;
  openVoiceoverDialog: () => Promise<string | null>;
  openMultipleVideosDialog: () => Promise<string[]>;
  exportEDL: (
    jobId: string
  ) => Promise<{ success: boolean; path?: string; error?: string }>;
  exportSRT: (
    jobId: string
  ) => Promise<{ success: boolean; path?: string; error?: string }>;
  exportCapCut: (
    jobId: string
  ) => Promise<{ success: boolean; path?: string; error?: string; message?: string }>;
  renderVideo: (
    jobId: string
  ) => Promise<{ success: boolean; path?: string; error?: string }>;
  getCapCutStatus: () => Promise<{ running: boolean; projectsPath: string | null }>;
  applyToCapCut: (
    jobId: string
  ) => Promise<{ success: boolean; applied?: number; skipped?: number; error?: string }>;
  listShortsFonts: () => Promise<ShortsFontInfo[]>;
  previewShortsSubtitles: (params: {
    script?: string;
    voiceoverPath?: string;
    chunkMode?: 'syllable' | 'sentence';
    chunkSyllables?: number;
    maxLineSyllables?: number;
    syllablesPerSecond?: number;
  }) => Promise<{
    success: boolean;
    events?: ShortsSubtitleEvent[];
    source?: 'stt' | 'script' | 'none';
    sttError?: string;
    error?: string;
  }>;
  composeShorts: (spec: ShortsComposeParams) => Promise<{
    success: boolean;
    outputPath?: string;
    durationSec?: number;
    segmentCount?: number;
    subtitleEventCount?: number;
    width?: number;
    height?: number;
    srtPath?: string;
    error?: string;
  }>;
  onShortsProgress: (
    callback: (data: { stage: string; progress: number; message: string }) => void
  ) => () => void;
  getHealth: (force?: boolean) => Promise<{
    generatedAt: string;
    overall: 'ok' | 'warn' | 'fail';
    checks: Array<{
      id: string;
      label: string;
      status: 'ok' | 'warn' | 'fail';
      detail: string;
      fixes?: string[];
    }>;
  }>;
  checkUpdates: () => Promise<UpdateStatus>;
  getUpdateStatus: () => Promise<UpdateStatus>;
  installUpdate: () => Promise<{ success: boolean }>;
  onUpdateStatus: (callback: (status: UpdateStatus) => void) => () => void;
}

declare global {
  interface Window {
    api: CutbackAPI;
  }
}
