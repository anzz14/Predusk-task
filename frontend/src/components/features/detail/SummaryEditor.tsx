'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

interface SummaryEditorProps {
  documentId: string;
  autoSummary: string;
  userEditedSummary: string | null;
  isFinalized: boolean;
  onSaveSuccess: () => void;
}

export function SummaryEditor({
  documentId,
  autoSummary,
  userEditedSummary,
  isFinalized,
  onSaveSuccess,
}: SummaryEditorProps) {
  const [value, setValue] = useState(userEditedSummary || autoSummary);
  const [initialValue] = useState(userEditedSummary || autoSummary);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const isDirty = value !== initialValue;

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await api.patch(`/documents/${documentId}/result`, {
        user_edited_summary: value,
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      onSaveSuccess();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save summary';
      setError(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4 rounded border border-gray-200 bg-white p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Summary</h3>
        {isFinalized && <span className="text-xs font-medium text-gray-500">Finalized — read only</span>}
      </div>

      <Textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={isFinalized}
        className="min-h-32"
        placeholder="Edit the summary..."
      />

      {!isFinalized && (
        <div className="flex items-center gap-3">
          <Button
            onClick={handleSave}
            disabled={!isDirty || isSaving}
            className="btn-primary"
          >
            {isSaving ? 'Saving...' : 'Save Draft'}
          </Button>
          {success && <span className="text-xs text-green-700">✓ Saved successfully</span>}
          {error && <span className="text-xs text-red-700">✗ {error}</span>}
        </div>
      )}
    </div>
  );
}