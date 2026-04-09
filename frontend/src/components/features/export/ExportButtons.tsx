'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';

interface ExportButtonsProps {
  documentId: string;
  isFinalized: boolean;
}

export function ExportButtons({ documentId, isFinalized }: ExportButtonsProps) {
  const [isExporting, setIsExporting] = useState<'json' | 'csv' | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async (format: 'json' | 'csv') => {
    if (!isFinalized) {
      setError('Document must be finalized before export');
      return;
    }

    setIsExporting(format);
    setError(null);

    try {
      const response = await api.get(`/documents/${documentId}/export`, {
        params: { format },
        responseType: 'blob',
      });

      const blob = new Blob([response.data], {
        type: format === 'json' ? 'application/json' : 'text/csv',
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `export-${documentId}.${format === 'json' ? 'json' : 'csv'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to export as ${format.toUpperCase()}`;
      setError(errorMessage);
    } finally {
      setIsExporting(null);
    }
  };

  return (
    <div className="space-y-3 rounded border border-gray-200 bg-white p-6">
      <h3 className="text-lg font-semibold text-gray-900">Export</h3>

      <div className="flex gap-3">
        <Button
          onClick={() => handleExport('json')}
          disabled={!isFinalized || isExporting !== null}
          variant="outline"
          className="border border-gray-300 flex-1"
        >
          {isExporting === 'json' ? 'Downloading JSON...' : 'Download JSON'}
        </Button>
        <Button
          onClick={() => handleExport('csv')}
          disabled={!isFinalized || isExporting !== null}
          variant="outline"
          className="border border-gray-300 flex-1"
        >
          {isExporting === 'csv' ? 'Downloading CSV...' : 'Download CSV'}
        </Button>
      </div>

      {!isFinalized && (
        <p className="text-xs text-gray-500">Document must be finalized before export</p>
      )}

      {error && <div className="rounded bg-red-50 p-3 text-xs text-red-700">{error}</div>}
    </div>
  );
}