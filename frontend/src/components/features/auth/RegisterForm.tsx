'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

export function RegisterForm() {
  const router = useRouter();
  const { register, isLoading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Client-side validation
    if (!email || !password || !confirmPassword) {
      setError('All fields are required');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      await register(email, password);
      router.push('/dashboard');
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Registration failed. Please try again.';
      setError(errorMessage);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <label htmlFor="email" className="block text-sm font-medium text-gray-900">
          Email
        </label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
          className={cn('input-clean')}
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="password" className="block text-sm font-medium text-gray-900">
          Password
        </label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isLoading}
          className={cn('input-clean')}
          autoComplete="new-password"
        />
        <p className="text-xs text-gray-500">At least 8 characters</p>
      </div>

      <div className="space-y-2">
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-900">
          Confirm Password
        </label>
        <Input
          id="confirmPassword"
          type="password"
          placeholder="••••••••"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          disabled={isLoading}
          className={cn('input-clean')}
          autoComplete="new-password"
        />
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <Button
        type="submit"
        disabled={isLoading}
        className={cn('btn-primary w-full')}
      >
        {isLoading ? 'Creating account...' : 'Sign up'}
      </Button>

      <div className="text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{' '}
          <a href="/login" className="font-medium text-gray-900 hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </form>
  );
}