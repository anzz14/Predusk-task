'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useDocuments } from '@/hooks/useDocuments';
import { UploadZone } from '@/components/features/upload/UploadZone';
import { FilterBar } from '@/components/features/dashboard/FilterBar';
import { DocumentTable } from '@/components/features/dashboard/DocumentTable';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const { documents, isLoading, error, refetch } = useDocuments();
  const [mounted, setMounted] = React.useState(false);

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
    return null;
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-black">Dashboard</h1>
              <p className="mt-1 text-sm text-gray-600">Manage and analyze your documents</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-black">{user.email}</p>
                <p className="text-xs text-gray-600">Signed in</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="space-y-12">
          {/* Upload Section */}
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-black">Upload Documents</h2>
              <p className="text-sm text-gray-600">Upload text files to analyze</p>
            </div>
            <UploadZone />
          </div>

          {/* Filter Section */}
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-black">Filter & Search</h2>
              <p className="text-sm text-gray-600">Find your documents</p>
            </div>
            <FilterBar />
          </div>

          {/* Documents Table */}
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-black">Your Documents</h2>
              <p className="text-sm text-gray-600">View and manage your analysis results</p>
            </div>
            {error ? (
              <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-700">
                <p className="text-sm font-medium">Failed to load documents</p>
                <p className="mt-1 text-xs">Please try refreshing the page</p>
              </div>
            ) : (
              <DocumentTable documents={documents} isLoading={isLoading} onRefetch={refetch} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}