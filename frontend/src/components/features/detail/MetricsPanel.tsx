'use client';

interface MetricsPanelProps {
  wordCount: number;
  readabilityScore: number;
}

function getFleschLabel(score: number): string {
  if (score >= 90) return 'Very Easy (5th grade)';
  if (score >= 80) return 'Easy (6th grade)';
  if (score >= 70) return 'Fairly Easy (7th grade)';
  if (score >= 60) return 'Standard (8th-9th grade)';
  if (score >= 50) return 'Fairly Difficult (10th-12th grade)';
  if (score >= 30) return 'Difficult (College level)';
  return 'Very Difficult (College graduate)';
}

export function MetricsPanel({ wordCount, readabilityScore }: MetricsPanelProps) {
  const scoreColor =
    readabilityScore >= 70
      ? 'text-green-700'
      : readabilityScore >= 50
        ? 'text-yellow-700'
        : 'text-red-700';

  return (
    <div className="grid grid-cols-2 gap-6 rounded border border-gray-200 bg-white p-6">
      <div>
        <div className="text-sm font-medium text-gray-600">Word Count</div>
        <div className="mt-2 text-3xl font-bold text-gray-900">{wordCount.toLocaleString()}</div>
        <div className="mt-1 text-xs text-gray-500">words</div>
      </div>

      <div>
        <div className="text-sm font-medium text-gray-600">Readability Score</div>
        <div className={`mt-2 text-3xl font-bold ${scoreColor}`}>{readabilityScore.toFixed(1)}</div>
        <div className="mt-1 text-xs text-gray-500">{getFleschLabel(readabilityScore)}</div>
      </div>
    </div>
  );
}