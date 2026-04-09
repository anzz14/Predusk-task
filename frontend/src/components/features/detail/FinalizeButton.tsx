'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';

interface FinalizeButtonProps {
  documentId: string;
  hasResult: boolean;
  isFinalized: boolean;
  onFinalizeSuccess: () => void;
}

export function FinalizeButton({
  documentId,
  hasResult,
  isFinalized,
  onFinalizeSuccess,
}: FinalizeButtonProps) {
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFinalize = async () => {
    setIsFinalizing(true);
    setError(null);

    try {
      await api.post(`/documents/${documentId}/finalize`);
      onFinalizeSuccess();
    } catch (err: any) {
      const status = err.response?.status;
      const data = err.response?.data;

      if (status === 409) {
        setError('Document is already finalized');
      } else if (status === 400) {
        setError('Cannot finalize: job has been retried. Please refresh and try again.');
      } else {
        setError(data?.detail || 'Failed to finalize document');
      }
    } finally {
      setIsFinalizing(false);
    }
  };

  if (isFinalized) {
    return (
      <div className="rounded border border-green-200 bg-green-50 p-4">
        <p className="text-sm font-medium text-green-900">✓ Document finalized</p>
        <p className="mt-1 text-xs text-green-700">This document has been locked and cannot be edited further.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <Button
        onClick={handleFinalize}
        disabled={!hasResult || isFinalizing || isFinalized}
        className="btn-primary w-full"
      >
        {isFinalizing ? 'Finalizing...' : 'Finalize Document'}
      </Button>

      {!hasResult && (
        <p className="text-xs text-gray-500">Document must be analyzed before finalizing</p>
      )}

      {error && <div className="rounded bg-red-50 p-3 text-xs text-red-700">{error}</div>}
    </div>
  );
}