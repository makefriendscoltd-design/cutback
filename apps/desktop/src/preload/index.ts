import { contextBridge, ipcRenderer } from 'electron';

/**
 * IPC 채널 상수 (인라인)
 * Electron preload 샌드박스에서는 workspace 패키지를 resolve할 수 없으므로
 * @cutback/shared 대신 직접 정의
 */
const IPC = {
  JOB_CREATE: 'job:create',
  JOB_CANCEL: 'job:cancel',
  JOB_LIST: 'job:list',
  JOB_GET: 'job:get',
  JOB_PROGRESS: 'job:progress',
  JOB_COMPLETED: 'job:completed',
  JOB_ERROR: 'job:error',
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
  createJob: (params: { videoPath: string; presetId: string }) =>
    ipcRenderer.invoke(IPC.JOB_CREATE, params),

  listJobs: () => ipcRenderer.invoke(IPC.JOB_LIST),

  getJob: (jobId: string) => ipcRenderer.invoke(IPC.JOB_GET, jobId),

  cancelJob: (jobId: string) =>
    ipcRenderer.invoke(IPC.JOB_CANCEL, jobId),

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
  }) => Promise<{ success: boolean; job?: unknown; error?: string }>;
  listJobs: () => Promise<unknown[]>;
  getJob: (
    jobId: string
  ) => Promise<{ job: unknown; results: unknown | null }>;
  cancelJob: (jobId: string) => Promise<{ success: boolean }>;
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
  listPresets: () => Promise<unknown[]>;
  loadPreset: (presetId: string) => Promise<unknown>;
  savePreset: (id: string, preset: unknown) => Promise<{ success: boolean }>;
  deletePreset: (presetId: string) => Promise<{ success: boolean }>;
  openVideoDialog: () => Promise<string | null>;
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
