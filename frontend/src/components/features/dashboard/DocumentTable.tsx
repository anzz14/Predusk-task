'use client';

import React from 'react';
import Link from 'next/link';
import { useDocumentStore } from '@/store/documentStore';
import { api } from '@/lib/api';
import type { DocumentResponse } from '@/types/document';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { StatusBadge } from './StatusBadge';
import { JobProgressBar } from './JobProgressBar';
import { formatDate, formatBytes } from '@/lib/utils';

interface DocumentTableProps {
  documents: DocumentResponse[];
  isLoading: boolean;
  onRefetch: () => void;
}

export function DocumentTable({ documents, isLoading, onRefetch }: DocumentTableProps) {
  const { page, pageSize, total, setPage } = useDocumentStore();
  const [retrying, setRetrying] = React.useState<string | null>(null);

  const handleRetry = async (jobId: string) => {
    setRetrying(jobId);
    try {
      await api.post(`/jobs/${jobId}/retry`);
      onRefetch();
    } catch (error) {
      console.error('Retry failed:', error);
    } finally {
      setRetrying(null);
    }
  };

  const handleExport = async (documentId: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/export`, {
        params: { format: 'json' },
      });
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `export-${documentId}.json`;
      a.click();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="mb-4 inline-block">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-gray-900"></div>
          </div>
          <p className="text-sm text-gray-600">Loading documents...</p>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="rounded border border-gray-200 bg-white p-8 text-center">
        <p className="text-gray-600">No documents found. Start by uploading a file above.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded border border-gray-200">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-gray-200 bg-gray-50">
              <TableHead className="px-6 py-3 text-left text-xs font-semibold text-gray-900">Filename</TableHead>
              <TableHead className="px-6 py-3 text-left text-xs font-semibold text-gray-900">Size</TableHead>
              <TableHead className="px-6 py-3 text-left text-xs font-semibold text-gray-900">Uploaded</TableHead>
              <TableHead className="px-6 py-3 text-left text-xs font-semibold text-gray-900">Status</TableHead>
              <TableHead className="px-6 py-3 text-left text-xs font-semibold text-gray-900">Progress</TableHead>
              <TableHead className="px-6 py-3 text-left text-xs font-semibold text-gray-900">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((doc) => {
              const job = doc.job;
              return (
                <TableRow key={doc.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <TableCell className="px-6 py-4 text-sm text-gray-900">
                    <Link href={`/documents/${doc.id}`} className="text-blue-600 hover:underline">
                      {doc.original_filename}
                    </Link>
                  </TableCell>
                  <TableCell className="px-6 py-4 text-sm text-gray-600">{formatBytes(doc.file_size)}</TableCell>
                  <TableCell className="px-6 py-4 text-sm text-gray-600">{formatDate(doc.upload_timestamp)}</TableCell>
                  <TableCell className="px-6 py-4">
                    {job ? <StatusBadge status={job.status} /> : <StatusBadge status="queued" />}
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    {job ? <JobProgressBar jobId={job.id} status={job.status} /> : <div className="text-xs text-gray-400">–</div>}
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="flex gap-2">
                      {/* View Button */}
                      <Link href={`/documents/${doc.id}`}>
                        <Button size="sm" variant="outline" className="border border-gray-300">
                          View
                        </Button>
                      </Link>

                      {/* Retry Button */}
                      {job?.status === 'failed' && (
                        <Button
                          size="sm"
                          onClick={() => handleRetry(job.id)}
                          disabled={retrying === job.id}
                          variant="outline"
                          className="border border-gray-300"
                        >
                          {retrying === job.id ? 'Retrying...' : 'Retry'}
                        </Button>
                      )}

                      {/* Export Button */}
                      {job?.status === 'finalized' && doc.extracted_result && (
                        <Button
                          size="sm"
                          onClick={() => handleExport(doc.id)}
                          variant="outline"
                          className="border border-gray-300"
                        >
                          Export
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Page {page} of {totalPages} ({total} total documents)
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setPage(page - 1)}
            disabled={page <= 1}
            variant="outline"
            className="border border-gray-300"
          >
            Previous
          </Button>
          <Button
            onClick={() => setPage(page + 1)}
            disabled={page >= totalPages}
            variant="outline"
            className="border border-gray-300"
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}