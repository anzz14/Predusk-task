'use client';

import { Badge } from '@/components/ui/badge';

type JobStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'finalized';

interface StatusBadgeProps {
  status: JobStatus;
}

const statusConfig: Record<JobStatus, { label: string; className: string }> = {
  queued: {
    label: 'Queued',
    className: 'bg-gray-100 text-gray-800 border border-gray-300',
  },
  processing: {
    label: 'Processing',
    className: 'bg-blue-50 text-blue-800 border border-blue-300',
  },
  completed: {
    label: 'Completed',
    className: 'bg-green-50 text-green-800 border border-green-300',
  },
  failed: {
    label: 'Failed',
    className: 'bg-red-50 text-red-800 border border-red-300',
  },
  finalized: {
    label: 'Finalized',
    className: 'bg-green-100 text-green-900 border border-green-400',
  },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status];
  return (
    <Badge variant="outline" className={`${config.className} font-medium`}>
      {config.label}
    </Badge>
  );
}