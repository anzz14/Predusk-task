'use client';

import { Progress } from '@/components/ui/progress';

interface UploadProgressProps {
  progress: number;
}

export function UploadProgress({ progress }: UploadProgressProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium text-gray-900">Uploading...</div>
        <div className="text-sm text-gray-600">{Math.round(progress)}%</div>
      </div>
      <Progress value={progress} className="h-2" />
    </div>
  );
}