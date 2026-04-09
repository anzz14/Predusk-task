'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { RegisterForm } from '@/components/features/auth/RegisterForm';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function RegisterPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted || isLoading) return;
    if (user) {
      router.replace('/dashboard');
    }
  }, [mounted, isLoading, user, router]);

  if (!mounted || isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="space-y-4 text-center">
          <div className="flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-800 border-t-transparent"></div>
          </div>
          <p className="text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="grid min-h-screen lg:grid-cols-2">
        <div className="relative hidden overflow-hidden border-r border-gray-200 bg-black text-white lg:flex lg:flex-col lg:justify-between">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.16),_transparent_34%),radial-gradient(circle_at_bottom_left,_rgba(255,255,255,0.08),_transparent_32%)]" />
          <div className="relative z-10 p-10 xl:p-14">
            <Badge variant="outline" className="border-white/20 bg-white/5 text-white">
              Signup
            </Badge>
            <div className="mt-8 max-w-md space-y-5">
              <h1 className="text-4xl font-semibold tracking-tight xl:text-5xl">
                Create your account and start analyzing.
              </h1>
              <p className="text-sm leading-6 text-white/70 xl:text-base">
                Set up in seconds, then upload content, inspect metrics, and export the results.
              </p>
            </div>
          </div>

          <div className="relative z-10 p-10 xl:p-14">
            <div className="space-y-3 text-sm text-white/80">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
                Simple onboarding with one account per workspace
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
                Black and white, minimal, and focused on the form
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-center px-4 py-10 sm:px-6 lg:px-8">
          <div className="w-full max-w-md space-y-6">
            <div className="lg:hidden">
              <Badge variant="outline" className="border-gray-200 bg-white text-black">
                Signup
              </Badge>
            </div>

            <Card className="border-gray-200 shadow-none">
              <CardHeader className="space-y-2 pb-4">
                <CardTitle className="text-3xl tracking-tight text-black">Create account</CardTitle>
                <CardDescription className="text-sm text-gray-600">
                  Enter your details below to get started.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <RegisterForm />
                <p className="text-center text-sm text-gray-600">
                  Already have an account?{' '}
                  <a href="/login" className="font-medium text-black underline-offset-4 hover:underline">
                    Sign in
                  </a>
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}