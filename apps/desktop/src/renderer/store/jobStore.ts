import { create } from 'zustand';

/** 간소화된 타입 (Renderer용) */
export interface JobInfo {
  id: string;
  videoPath: string;
  presetId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  createdAt: string;
  error?: string;
}

export interface CutDecisionInfo {
  id: string;
  type: 'silence' | 'filler_word' | 'retake';
  start: number;
  end: number;
  duration: number;
  confidence: number;
  metadata?: Record<string, unknown>;
  enabled: boolean;
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

export interface JobResultsInfo {
  transcript: {
    words: TranscriptWord[];
    full_text: string;
    language: string;
    duration: number;
  };
  cutDecisions: CutDecisionInfo[];
  captions: CaptionInfo[];
  statistics: {
    original_duration: number;
    edited_duration: number;
    silence_removed: number;
    fillers_removed: number;
    retakes_removed: number;
    total_cuts: number;
    cut_frequency: number;
    naturalness_score: number;
  };
}

interface JobStore {
  jobs: JobInfo[];
  currentJobId: string | null;
  currentResults: JobResultsInfo | null;
  progressDetail: string;

  setJobs: (jobs: JobInfo[]) => void;
  addJob: (job: JobInfo) => void;
  setCurrentJob: (jobId: string | null) => void;
  setCurrentResults: (results: JobResultsInfo | null) => void;
  updateJobProgress: (jobId: string, progress: number, detail?: string) => void;
  updateJobStatus: (jobId: string, status: JobInfo['status'], error?: string) => void;
  toggleCutDecision: (cutId: string) => void;
}

export const useJobStore = create<JobStore>((set, get) => ({
  jobs: [],
  currentJobId: null,
  currentResults: null,
  progressDetail: '',

  setJobs: (jobs) => set({ jobs }),

  addJob: (job) =>
    set((state) => ({
      jobs: [job, ...state.jobs],
      currentJobId: job.id,
    })),

  setCurrentJob: (jobId) => set({ currentJobId: jobId, currentResults: null }),

  setCurrentResults: (results) => set({ currentResults: results }),

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

  toggleCutDecision: (cutId) =>
    set((state) => {
      if (!state.currentResults) return state;
      return {
        currentResults: {
          ...state.currentResults,
          cutDecisions: state.currentResults.cutDecisions.map((c) =>
            c.id === cutId ? { ...c, enabled: !c.enabled } : c
          ),
        },
      };
    }),
}));
