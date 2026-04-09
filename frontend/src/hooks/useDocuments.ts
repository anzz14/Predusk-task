'use client';

import { useEffect, useCallback, useRef } from 'react';
import { useDocumentStore } from '@/store/documentStore';
import api from '@/lib/api';
import type { DocumentListResponse } from '@/types/document';

/**
 * Hook to fetch paginated document list
 * Watches filters and page, fetches data, sets up 5s polling interval
 * Exposes refetch() for manual refresh triggers
 */
export function useDocuments() {
  const store = useDocumentStore();
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  /**
   * Fetch documents from the API
   */
  const fetchDocuments = useCallback(async () => {
    if (!isMountedRef.current) return;

    try {
      store.setLoading(true);
      store.setError(null);

      const params = {
        search: store.filters.search,
        status: store.filters.status,
        sort_by: store.filters.sortBy,
        sort_order: store.filters.sortOrder,
        page: store.page,
        page_size: store.pageSize,
      };

      const response = await api.get<DocumentListResponse>('/documents', {
        params,
      });

      if (isMountedRef.current) {
        store.setDocuments(response.data.items, response.data.total);
      }
    } catch (error) {
      if (isMountedRef.current) {
        store.setError(
          error instanceof Error ? error.message : 'Failed to fetch documents'
        );
      }
    } finally {
      if (isMountedRef.current) {
        store.setLoading(false);
      }
    }
  }, [store]);

  /**
   * Manual refetch trigger
   */
  const refetch = useCallback(async () => {
    await fetchDocuments();
  }, [fetchDocuments]);

  /**
   * Watch filters and page changes
   */
  useEffect(() => {
    fetchDocuments();
  }, [store.filters, store.page, fetchDocuments]);

  /**
   * Set up 5-second polling for coarse status updates
   */
  useEffect(() => {
    pollingIntervalRef.current = setInterval(() => {
      if (isMountedRef.current) {
        fetchDocuments();
      }
    }, 5000);

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [fetchDocuments]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  return {
    documents: store.documents,
    total: store.total,
    page: store.page,
    setPage: store.setPage,
    filters: store.filters,
    setFilters: store.setFilters,
    isLoading: store.isLoading,
    error: store.error,
    refetch,
  };
}
