import { create } from 'zustand';
import type { DocumentResponse } from '@/types/document';

export interface DocumentFilters {
  search: string;
  status: string;
  sortBy: string;
  sortOrder: string;
}

export interface DocumentStore {
  // State
  documents: DocumentResponse[];
  total: number;
  page: number;
  pageSize: number;
  filters: DocumentFilters;
  isLoading: boolean;
  error: string | null;

  // Actions
  setDocuments: (documents: DocumentResponse[], total: number) => void;
  setFilters: (filters: Partial<DocumentFilters>) => void;
  setPage: (page: number) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const defaultFilters: DocumentFilters = {
  search: '',
  status: '',
  sortBy: 'created_at',
  sortOrder: 'desc',
};

export const useDocumentStore = create<DocumentStore>((set) => ({
  // Initial state
  documents: [],
  total: 0,
  page: 1,
  pageSize: 10,
  filters: defaultFilters,
  isLoading: false,
  error: null,

  // Actions
  setDocuments: (documents, total) => set({ documents, total }),

  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
      page: 1, // Reset to first page when filters change
    })),

  setPage: (page) => set({ page }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  reset: () =>
    set({
      documents: [],
      total: 0,
      page: 1,
      pageSize: 10,
      filters: defaultFilters,
      isLoading: false,
      error: null,
    }),
}));