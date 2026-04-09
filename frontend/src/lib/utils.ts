import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges Tailwind CSS classes intelligently, handling conflicts
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formats a date string to a human-readable format (e.g., "Jan 15, 2026")
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Formats a date string to include time (e.g., "Jan 15, 2026 2:30 PM")
 */
export function formatDateTime(dateString: string | null | undefined): string {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Formats bytes to human-readable format (e.g., "1.5 MB")
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Truncates a string to a maximum length, appending ellipsis if needed
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Converts a camelCase string to Title Case
 */
export function toTitleCase(str: string): string {
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (char) => char.toUpperCase())
    .trim();
}

/**
 * Converts a status string to a human-readable label
 */
export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    queued: 'Queued',
    processing: 'Processing',
    completed: 'Completed',
    failed: 'Failed',
    finalized: 'Finalized',
  };
  return labels[status] ?? toTitleCase(status);
}