'use client';

import React, { useState } from 'react';
import { useDocumentStore } from '@/store/documentStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

type JobStatus = 'all' | 'queued' | 'processing' | 'completed' | 'failed' | 'finalized';
type SortBy = 'uploaded' | 'created_at';
type SortOrder = 'asc' | 'desc';

export function FilterBar() {
  const { filters, setFilters } = useDocumentStore();
  const [search, setSearch] = useState(filters.search || '');
  const [status, setStatus] = useState<JobStatus>((filters.status || 'all') as JobStatus);
  const [sortBy, setSortBy] = useState<SortBy>((filters.sortBy || 'uploaded') as SortBy);
  const [sortOrder, setSortOrder] = useState<SortOrder>((filters.sortOrder || 'desc') as SortOrder);

  const handleApplyFilters = () => {
    setFilters({
      search: search || undefined,
      status: status === 'all' ? undefined : status,
      sortBy,
      sortOrder,
    });
  };

  const handleReset = () => {
    setSearch('');
    setStatus('all');
    setSortBy('uploaded');
    setSortOrder('desc');
    setFilters({
      search: undefined,
      status: undefined,
      sortBy: 'uploaded',
      sortOrder: 'desc',
    });
  };

  return (
    <div className="space-y-4 rounded border border-gray-200 bg-white p-4">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Search Input */}
        <div>
          <label className="block text-sm font-medium text-gray-900">Search Filename</label>
          <Input
            type="text"
            placeholder="Filter by filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-clean mt-1"
          />
        </div>

        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-900">Status</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as JobStatus)}
            className="input-clean mt-1 block w-full"
          >
            <option value="all">All Statuses</option>
            <option value="queued">Queued</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="finalized">Finalized</option>
          </select>
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium text-gray-900">Sort By</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortBy)}
            className="input-clean mt-1 block w-full"
          >
            <option value="uploaded">Upload Date</option>
            <option value="created_at">Created Date</option>
          </select>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-gray-900">Order</label>
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value as SortOrder)}
            className="input-clean mt-1 block w-full"
          >
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button onClick={handleApplyFilters} className="btn-primary">
          Apply Filters
        </Button>
        <Button onClick={handleReset} variant="outline" className="border border-gray-300">
          Reset
        </Button>
      </div>
    </div>
  );
}