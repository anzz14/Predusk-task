'use client';

import React, { useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useDocumentDetail } from '@/hooks/useDocumentDetail';
import { useSSE } from '@/hooks/useSSE';
import { MetricsPanel } from '@/components/features/detail/MetricsPanel';
import { KeywordsTable } from '@/components/features/detail/KeywordsTable';
import { SummaryEditor } from '@/components/features/detail/SummaryEditor';
import { FinalizeButton } from '@/components/features/detail/FinalizeButton';
import { ExportButtons } from '@/components/features/export/ExportButtons';
import { StatusBadge } from '@/components/features/dashboard/StatusBadge';
import { JobProgressBar } from '@/components/features/dashboard/JobProgressBar';
import { formatDate, formatBytes } from '@/lib/utils';

export default function DocumentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const documentId = params.id as string;

  const { user, isLoading: authLoading } = useAuth();
  const { document, job, result, isLoading, refetch } = useDocumentDetail(documentId);
  const [mounted, setMounted] = React.useState(false);

  // Start SSE if job is processing
  const jobId = job?.id || null;
  useSSE(jobId);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect if not authenticated
  useEffect(() => {
    if (!mounted || authLoading) return;
    if (!user) {
      router.replace('/login');
    }
  }, [mounted, authLoading, user, router]);

  if (!mounted || authLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="space-y-4 text-center">
          <div className="flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-800 border-t-transparent"></div>
          </div>
          <p className="text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Redirecting...
  }

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="space-y-4 text-center">
          <div className="flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-800 border-t-transparent"></div>
          </div>
          <p className="text-sm text-gray-600">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="min-h-screen bg-white">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-black">Document Not Found</h1>
            <p className="mt-2 text-gray-600">This document does not exist or you do not have permission to view it.</p>
            <button
              onClick={() => router.push('/dashboard')}
              className="mt-4 inline-flex items-center rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-black">{document.original_filename}</h1>
                <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                  <span>Size: {formatBytes(document.file_size)}</span>
                  <span className="text-gray-400">•</span>
                  <span>Uploaded: {formatDate(document.created_at)}</span>
                </div>
              </div>
              {job && <StatusBadge status={job.status} />}
            </div>
            {jobId && <JobProgressBar jobId={jobId} status={job?.status || 'pending'} />}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-3">
          {/* Left Column - Metrics & Keywords */}
          <div className="space-y-8 lg:col-span-2">
            {result ? (
              <>
                <MetricsPanel wordCount={result.word_count} readabilityScore={result.readability_score} />
                <KeywordsTable keywords={result.primary_keywords} />
              </>
            ) : job?.status === 'completed' ? (
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
                <p className="text-gray-600">No analysis results available</p>
              </div>
            ) : (
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
                <p className="text-gray-600">Analysis in progress. Results will appear here shortly.</p>
              </div>
            )}
          </div>

          {/* Right Column - Actions */}
          <div className="space-y-4 lg:sticky lg:top-4">
            {result && (
              <>
                <SummaryEditor
                  documentId={documentId}
                  autoSummary={result.auto_summary}
                  userEditedSummary={result.user_edited_summary}
                  isFinalized={result.is_finalized}
                  onSaveSuccess={() => refetch()}
                />
                <FinalizeButton
                  documentId={documentId}
                  hasResult={!!result}
                  isFinalized={result.is_finalized}
                  onFinalizeSuccess={() => refetch()}
                />
                <ExportButtons
                  documentId={documentId}
                  isFinalized={result.is_finalized}
                />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}