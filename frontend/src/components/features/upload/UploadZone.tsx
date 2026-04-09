'use client';

import React, { useState, useRef } from 'react';
import { useSSE } from '@/hooks/useSSE';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { UploadProgress } from './UploadProgress';

interface UploadResponse {
  document_id: string;
  job_id: string;
}

export function UploadZone() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedJobIds, setUploadedJobIds] = useState<string[]>([]);

  // Start SSE for each uploaded job
  uploadedJobIds.forEach((jobId) => {
    useSSE(jobId);
  });

  const validateFiles = (files: File[]): { valid: File[]; errors: string[] } => {
    const errors: string[] = [];
    const valid: File[] = [];
    const MAX_SIZE = 5242880; // 5MB

    files.forEach((file) => {
      if (file.type !== 'text/plain') {
        errors.push(`${file.name}: Only .txt files are allowed`);
      } else if (file.size > MAX_SIZE) {
        errors.push(`${file.name}: File exceeds 5MB limit`);
      } else {
        valid.push(file);
      }
    });

    return { valid, errors };
  };

  const handleFiles = async (files: File[]) => {
    setError(null);
    const { valid, errors } = validateFiles(Array.from(files));

    if (errors.length > 0) {
      setError(errors.join('; '));
      return;
    }

    const formData = new FormData();
    valid.forEach((file) => {
      formData.append('files', file);
    });

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const response = await api.post<UploadResponse[]>('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        },
      });

      // Extract job IDs from response and trigger SSE connections
      const jobIds = response.data.map((item) => item.job_id);
      setUploadedJobIds(jobIds);

      // Reset form
      setUploadProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(Array.from(e.dataTransfer.files));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  return (
    <div className="w-full space-y-4">
      {isUploading && <UploadProgress progress={uploadProgress} />}

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
          isDragging ? 'border-gray-900 bg-gray-50' : 'border-gray-300 bg-white'
        }`}
      >
        <div className="space-y-3">
          <div className="text-sm text-gray-600">Drag and drop .txt files here, or click to select</div>
          <Button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="btn-primary"
          >
            Select Files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".txt"
            onChange={handleInputChange}
            disabled={isUploading}
            className="hidden"
          />
        </div>
      </div>

      {error && <div className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>}
    </div>
  );
}