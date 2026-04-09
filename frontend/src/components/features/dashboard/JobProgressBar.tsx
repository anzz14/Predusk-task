'use client';

import { useProgressStore } from '@/store/progressStore';
import { Progress } from '@/components/ui/progress';

interface JobProgressBarProps {
  jobId: string;
  status: string;
}

export function JobProgressBar({ jobId, status }: JobProgressBarProps) {
  const progress = useProgressStore((state) => state.progress[jobId]);

  if (status !== 'processing' || !progress) {
    return <div className="text-xs text-gray-400">–</div>;
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="truncate text-xs text-gray-600">{progress.message || progress.stage}</div>
        <div className="ml-2 text-xs font-medium text-gray-900">{progress.percentage}%</div>
      </div>
      <Progress value={progress.percentage} className="h-1.5" />
    </div>
  );
}