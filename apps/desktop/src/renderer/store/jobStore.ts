import { create } from 'zustand';

/** 간소화된 타입 (Renderer용) */
export interface JobInfo {
  id: string;
  videoPath: string;
  presetId: string;
  /** Mode A (단일 영상) 또는 Mode B (보이스오버 + B-roll). 미지정시 mode-a. */
  editMode?: 'mode-a' | 'mode-b';
  /** Mode B 전용: B-roll 클립 경로 */
  assetPaths?: string[];
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  createdAt: string;
  error?: string;
}

export interface CutDecisionInfo {
  id: string;
  type: 'silence' | 'filler_word' | 'retake' | 'caption_segment';
  start: number;
  end: number;
  duration: number;
  confidence: number;
  reason: string;
  reasonText?: string;
  source: string;
  presetRule?: string;
  metadata?: Record<string, unknown>;
  enabled: boolean;
  reviewRequired?: boolean;
}

export interface TranscriptWord {
  text: string;
  start: number;
  end: number;
  confidence: number;
}

export interface CaptionInfo {
  id: string;
  text: string;
  start: number;
  end: number;
}

/** Mode B: 문장 단위 타임라인 항목 */
export interface SentenceInfo {
  id: string;
  text: string;
  start: number;
  end: number;
  duration: number;
}

/** Mode B: B-roll 에셋 메타 */
export interface AssetInfo {
  id: string;
  filePath: string;
  fileName: string;
  duration: number;
  metadata?: {
    userKeywords?: string[];
    resolution?: { width: number; height: number };
    fps?: number;
  };
}

/** Mode B: 타임라인에 배치된 클립 (문장 1개 = 클립 1개) */
export interface TimelineClipInfo {
  id: string;
  sentenceId: string;
  assetId: string;
  timelineStart: number;
  timelineEnd: number;
  sourceIn: number;
  sourceOut: number;
  playbackSpeed: number;
  confidence: number;
  adjustmentStrategy?: 'trim' | 'speed' | 'repeat' | 'freeze';
  alternatives?: { assetId: string; score: number }[];
}

export interface JobResultsInfo {
  // Mode A 필드 (Mode B 작업이면 undefined)
  transcript?: {
    words: TranscriptWord[];
    full_text: string;
    language: string;
    duration: number;
  };
  cutDecisions?: CutDecisionInfo[];
  captions?: CaptionInfo[];
  statistics?: {
    original_duration: number;
    edited_duration: number;
    silence_removed: number;
    fillers_removed: number;
    retakes_removed: number;
    total_cuts: number;
    cut_frequency: number;
    naturalness_score: number;
  };

  // Mode B 필드 (Mode A 작업이면 undefined)
  sentenceTimeline?: {
    sentences: SentenceInfo[];
    totalDuration: number;
    language: string;
    source: 'stt' | 'script';
  };
  assetIndex?: {
    assets: AssetInfo[];
    totalDuration: number;
  };
  roughCutTimeline?: {
    tracks: { id: string; type: 'video' | 'audio'; clips: TimelineClipInfo[] }[];
    totalDuration: number;
    metadata: {
      sentenceCount: number;
      assetCount: number;
      averageConfidence: number;
      reviewRequiredCount: number;
    };
  };
}

interface JobStore {
  jobs: JobInfo[];
  currentJobId: string | null;
  currentResults: JobResultsInfo | null;
  progressDetail: string;
  /**
   * Undo/redo 스택. 사용자가 transcript 에서 단어를 cut/복원할 때마다
   * 직전 cutDecisions snapshot 이 past 에 push 된다.
   */
  cutHistory: { past: CutDecisionInfo[][]; future: CutDecisionInfo[][] };

  setJobs: (jobs: JobInfo[]) => void;
  addJob: (job: JobInfo) => void;
  removeJob: (jobId: string) => void;
  setCurrentJob: (jobId: string | null) => void;
  setCurrentResults: (results: JobResultsInfo | null) => void;
  updateJobProgress: (jobId: string, progress: number, detail?: string) => void;
  updateJobStatus: (jobId: string, status: JobInfo['status'], error?: string) => void;
  /**
   * cut 의 enabled 상태를 토글한다.
   * `enabled` 인자를 명시하면 그 값으로 set, 생략하면 현재 값을 뒤집는다.
   * (Live timeline 과 review transcript 가 같은 객체를 참조하므로 어느 쪽에서 바꿔도 즉시 반영됨.)
   */
  toggleCutDecision: (cutId: string, enabled?: boolean) => void;
  /**
   * transcript 에서 사용자가 임의 구간을 비활성화 (manual cut) 한다.
   * 기존 cut 안에 들어있는 단어면 그 cut 을 enable 토글하고,
   * 아무 cut 에도 안 속하는 구간이면 새 manual_override cut 을 만든다.
   */
  addManualCut: (cut: {
    start: number;
    end: number;
    text: string;
  }) => CutDecisionInfo | null;
  undoCutChange: () => void;
  redoCutChange: () => void;
}

// 간단한 uuid (브라우저용; renderer 는 crypto.randomUUID 가 안전)
function newId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `manual-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export const useJobStore = create<JobStore>((set, get) => ({
  jobs: [],
  currentJobId: null,
  currentResults: null,
  progressDetail: '',
  cutHistory: { past: [], future: [] },

  setJobs: (jobs) => set({ jobs }),

  addJob: (job) =>
    set((state) => ({
      jobs: [job, ...state.jobs],
      currentJobId: job.id,
      cutHistory: { past: [], future: [] },
    })),

  removeJob: (jobId) =>
    set((state) => ({
      jobs: state.jobs.filter((j) => j.id !== jobId),
      currentJobId: state.currentJobId === jobId ? null : state.currentJobId,
      currentResults: state.currentJobId === jobId ? null : state.currentResults,
    })),

  setCurrentJob: (jobId) =>
    set({
      currentJobId: jobId,
      currentResults: null,
      cutHistory: { past: [], future: [] },
    }),

  setCurrentResults: (results) =>
    set({ currentResults: results, cutHistory: { past: [], future: [] } }),

  updateJobProgress: (jobId, progress, detail) =>
    set((state) => ({
      jobs: state.jobs.map((j) =>
        j.id === jobId ? { ...j, progress, status: 'processing' as const } : j
      ),
      progressDetail: detail || state.progressDetail,
    })),

  updateJobStatus: (jobId, status, error) =>
    set((state) => ({
      jobs: state.jobs.map((j) =>
        j.id === jobId ? { ...j, status, error, progress: status === 'completed' ? 100 : j.progress } : j
      ),
    })),

  toggleCutDecision: (cutId, enabled) =>
    set((state) => {
      // Mode B 결과에는 cutDecisions 가 없음
      if (!state.currentResults?.cutDecisions) return state;
      const prev = state.currentResults.cutDecisions;
      const next = prev.map((c) =>
        c.id === cutId
          ? { ...c, enabled: typeof enabled === 'boolean' ? enabled : !c.enabled }
          : c
      );
      return {
        currentResults: { ...state.currentResults, cutDecisions: next },
        cutHistory: {
          past: [...state.cutHistory.past, prev].slice(-50),
          future: [],
        },
      };
    }),

  addManualCut: (cut) => {
    const state = get();
    if (!state.currentResults?.cutDecisions) return null;
    // 기존 cut 안에 완전히 들어가면 그걸 토글하는 게 맞음
    const overlapping = state.currentResults.cutDecisions.find(
      (c) => c.start <= cut.start && c.end >= cut.end
    );
    if (overlapping) {
      // 이미 cut 이 있으면 enabled=true 로 만들기 (없애면 이미 cut 됨)
      const newDecision: CutDecisionInfo = { ...overlapping, enabled: true };
      const prev = state.currentResults.cutDecisions;
      set({
        currentResults: {
          ...state.currentResults,
          cutDecisions: prev.map((c) => (c.id === overlapping.id ? newDecision : c)),
        },
        cutHistory: {
          past: [...state.cutHistory.past, prev].slice(-50),
          future: [],
        },
      });
      return newDecision;
    }
    const id = newId();
    const newCut: CutDecisionInfo = {
      id,
      type: 'filler_word', // 임의 구간 → 색상은 filler 와 동일하게 표시
      start: cut.start,
      end: cut.end,
      duration: cut.end - cut.start,
      confidence: 1.0,
      reason: 'manual_override',
      reasonText: cut.text ? `수동 제거 "${cut.text}"` : '수동 제거',
      source: 'manual_override',
      enabled: true,
      metadata: { filler_text: cut.text },
    };
    const prev = state.currentResults.cutDecisions;
    set({
      currentResults: {
        ...state.currentResults,
        cutDecisions: [...prev, newCut],
      },
      cutHistory: {
        past: [...state.cutHistory.past, prev].slice(-50),
        future: [],
      },
    });
    return newCut;
  },

  undoCutChange: () =>
    set((state) => {
      if (!state.currentResults?.cutDecisions) return state;
      const past = state.cutHistory.past;
      if (past.length === 0) return state;
      const previous = past[past.length - 1];
      const newPast = past.slice(0, -1);
      return {
        currentResults: { ...state.currentResults, cutDecisions: previous },
        cutHistory: {
          past: newPast,
          future: [state.currentResults.cutDecisions, ...state.cutHistory.future],
        },
      };
    }),

  redoCutChange: () =>
    set((state) => {
      if (!state.currentResults?.cutDecisions) return state;
      const future = state.cutHistory.future;
      if (future.length === 0) return state;
      const next = future[0];
      const newFuture = future.slice(1);
      return {
        currentResults: { ...state.currentResults, cutDecisions: next },
        cutHistory: {
          past: [...state.cutHistory.past, state.currentResults.cutDecisions],
          future: newFuture,
        },
      };
    }),
}));
