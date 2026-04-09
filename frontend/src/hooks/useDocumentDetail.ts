'use client';

import { useEffect, useCallback, useRef, useState } from 'react';
import api from '@/lib/api';
import type { DocumentResponse, ProcessingJob, ExtractedResult } from '@/types/document';

export interface UseDocumentDetailReturn {
  document: DocumentResponse | null;
  job: ProcessingJob | null;
  result: ExtractedResult | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch a single document with its job and result data
 * Accepts documentId and optionally refetches on demand
 * Exposes document, job, result, isLoading, and refetch function
 */
export function useDocumentDetail(documentId: string | null): UseDocumentDetailReturn {
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isMountedRef = useRef(true);

  /**
   * Fetch document details from the API
   */
  const fetchDocument = useCallback(async () => {
    if (!documentId) {
      setDocument(null);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const response = await api.get<DocumentResponse>(`/documents/${documentId}`);

      if (isMountedRef.current) {
        setDocument(response.data);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err instanceof Error ? err.message : 'Failed to fetch document');
      }
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [documentId]);

  /**
   * Fetch on mount and when documentId changes
   */
  useEffect(() => {
    fetchDocument();
  }, [documentId, fetchDocument]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Extract latest job and result from document
  const job = document?.processing_jobs?.[0] || null;
  const result = document?.extracted_result || null;

  return {
    document,
    job,
    result,
    isLoading,
    error,
    refetch: fetchDocument,
  };
}
