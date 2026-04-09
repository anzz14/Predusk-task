'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted || isLoading) return;

    // Redirect based on auth state
    if (user) {
      router.replace('/dashboard');
    } else {
      router.replace('/login');
    }
  }, [mounted, isLoading, user, router]);

  // Return null during redirect
  return null;
}