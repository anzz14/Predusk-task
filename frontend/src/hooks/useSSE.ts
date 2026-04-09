'use client';

import { useEffect } from 'react';
import { useProgressStore } from '@/store/progressStore';
import { getAuthToken } from '@/lib/api';

/**
 * Hook to connect to Server-Sent Events stream for job progress
 * Opens EventSource connection to /api/v1/jobs/{jobId}/progress/stream
 * Updates progressStore on each event and refetches documentStore on terminal event
 */
export function useSSE(jobId: string | null) {
  const updateJobProgress = useProgressStore((state) => state.updateJobProgress);
  const clearJobProgress = useProgressStore((state) => state.clearJobProgress);

  useEffect(() => {
    if (!jobId) return;

    const token = getAuthToken();
    if (!token) return;

    // Build URL with token as query param (EventSource doesn't support custom headers)
    const url = `${process.env.NEXT_PUBLIC_API_URL}/jobs/${jobId}/progress/stream?token=${encodeURIComponent(token)}`;

    let eventSource: EventSource | null = null;

    try {
      eventSource = new EventSource(url);

      // Handle incoming messages
      eventSource.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          updateJobProgress(jobId, {
            stage: data.stage,
            percentage: data.progress,
            message: data.message || '',
          });

          // Check if this is a terminal event
          if (data.stage === 'job_completed' || data.stage === 'job_failed') {
            eventSource?.close();
            clearJobProgress(jobId);
            // Trigger a refetch of the document list
            // This is handled by the 5s polling in useDocuments hook
          }
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
        }
      });

      // Handle connection errors
      eventSource.onerror = () => {
        console.error('SSE connection error');
        eventSource?.close();
        clearJobProgress(jobId);
      };
    } catch (error) {
      console.error('Failed to create EventSource:', error);
    }

    // Cleanup on unmount or jobId change
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [jobId, updateJobProgress, clearJobProgress]);
}
