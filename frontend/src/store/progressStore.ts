import { create } from 'zustand';

export interface ProgressEvent {
  stage: string;
  percentage: number;
  message: string;
}

export interface ProgressStore {
  // State: Record of job progress keyed by jobId
  progress: Record<string, ProgressEvent>;

  // Actions
  updateJobProgress: (jobId: string, event: ProgressEvent) => void;
  clearJobProgress: (jobId: string) => void;
  reset: () => void;
}

export const useProgressStore = create<ProgressStore>((set) => ({
  // Initial state
  progress: {},

  // Actions
  updateJobProgress: (jobId, event) =>
    set((state) => ({
      progress: {
        ...state.progress,
        [jobId]: event,
      },
    })),

  clearJobProgress: (jobId) =>
    set((state) => {
      const newProgress = { ...state.progress };
      delete newProgress[jobId];
      return { progress: newProgress };
    }),

  reset: () => set({ progress: {} }),
}));