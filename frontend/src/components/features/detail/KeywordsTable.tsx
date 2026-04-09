'use client';

import { useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

interface Keyword {
  keyword: string;
  count: number;
  density_percentage: number;
}

interface KeywordsTableProps {
  keywords: Keyword[];
}

type SortBy = 'count' | 'density' | 'keyword';
type SortOrder = 'asc' | 'desc';

export function KeywordsTable({ keywords }: KeywordsTableProps) {
  const [sortBy, setSortBy] = useState<SortBy>('density');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const handleSort = (column: SortBy) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const sortedKeywords = [...keywords].sort((a, b) => {
    let aVal: number | string = 0;
    let bVal: number | string = 0;

    if (sortBy === 'count') {
      aVal = a.count;
      bVal = b.count;
    } else if (sortBy === 'density') {
      aVal = a.density_percentage;
      bVal = b.density_percentage;
    } else {
      aVal = a.keyword;
      bVal = b.keyword;
    }

    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }

    const numA = typeof aVal === 'number' ? aVal : 0;
    const numB = typeof bVal === 'number' ? bVal : 0;
    return sortOrder === 'asc' ? numA - numB : numB - numA;
  });

  const SortIndicator = ({ column }: { column: SortBy }) => {
    if (sortBy !== column) return <span className="text-gray-300 ml-1">⇅</span>;
    return <span className="text-gray-900 ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>;
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Keywords</h3>
      <div className="overflow-x-auto rounded border border-gray-200">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-gray-200 bg-gray-50">
              <TableHead
                className="cursor-pointer px-6 py-3 text-left text-xs font-semibold text-gray-900 hover:bg-gray-100"
                onClick={() => handleSort('keyword')}
              >
                Keyword <SortIndicator column="keyword" />
              </TableHead>
              <TableHead
                className="cursor-pointer px-6 py-3 text-left text-xs font-semibold text-gray-900 hover:bg-gray-100"
                onClick={() => handleSort('count')}
              >
                Count <SortIndicator column="count" />
              </TableHead>
              <TableHead
                className="cursor-pointer px-6 py-3 text-left text-xs font-semibold text-gray-900 hover:bg-gray-100"
                onClick={() => handleSort('density')}
              >
                Density % <SortIndicator column="density" />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedKeywords.map((kw, idx) => (
              <TableRow key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                <TableCell className="px-6 py-3 text-sm font-medium text-gray-900">{kw.keyword}</TableCell>
                <TableCell className="px-6 py-3 text-sm text-gray-600">{kw.count}</TableCell>
                <TableCell className="px-6 py-3 text-sm text-gray-600">{kw.density_percentage.toFixed(2)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}