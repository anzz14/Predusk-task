'use client';

import { useContext } from 'react';
import { AuthContext } from '@/context/AuthContext';
import type { AuthContextType } from '@/types/auth';

/**
 * Hook to access auth context
 * Provides user, isLoading, login, logout, register
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}