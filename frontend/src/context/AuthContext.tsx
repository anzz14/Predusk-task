'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import * as jose from 'jose';
import api, { setAuthToken } from '@/lib/api';
import type { User, LoginRequest, RegisterRequest, AuthContextType } from '@/types/auth';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Initialize auth state on mount by reading JWT from session cookie
   */
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Get the JWT token from the session endpoint
        const response = await fetch('/api/auth/session', {
          method: 'GET',
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          if (data.token) {
            // Decode JWT payload client-side (without verification - just to read claims)
            try {
              const decoded = jose.decodeJwt(data.token);
              const storedEmail = sessionStorage.getItem('user_email') || '';
              const userData: User = {
                id: decoded.sub || '',
                email: storedEmail,
                is_active: true,
                created_at: new Date().toISOString(),
              };
              setUser(userData);
              setAuthToken(data.token);
            } catch (error) {
              console.error('Failed to decode JWT:', error);
              setUser(null);
              setAuthToken(null);
            }
          }
        } else {
          setUser(null);
          setAuthToken(null);
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        setUser(null);
        setAuthToken(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();

    // Listen for logout events from API interceptor
    const handleLogout = () => {
      sessionStorage.removeItem('user_email');
      setUser(null);
      setAuthToken(null);
    };

    window.addEventListener('auth:logout', handleLogout as EventListener);
    return () => {
      window.removeEventListener('auth:logout', handleLogout as EventListener);
    };
  }, []);

  /**
   * Login with email and password
   */
  const login = useCallback(async (email: string, password: string) => {
    try {
      setIsLoading(true);

      // Call backend login endpoint
      const loginResponse = await api.post('/auth/login', {
        email,
        password,
      } as LoginRequest);

      const token = loginResponse.data.access_token;

      // Store token in httpOnly cookie via session endpoint
      const sessionResponse = await fetch('/api/auth/session', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      if (!sessionResponse.ok) {
        throw new Error('Failed to set session cookie');
      }

      // Decode and set user state
      const decoded = jose.decodeJwt(token);
      const userData: User = {
        id: decoded.sub || '',
        email,
        is_active: true,
        created_at: new Date().toISOString(),
      };

      sessionStorage.setItem('user_email', email);
      setUser(userData);
      setAuthToken(token);
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  /**
   * Register new user and auto-login
   */
  const register = useCallback(async (email: string, password: string) => {
    try {
      setIsLoading(true);

      // Call backend register endpoint
      await api.post('/auth/register', {
        email,
        password,
      } as RegisterRequest);

      // Auto-login after successful registration
      await login(email, password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [login]);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      // Clear httpOnly cookie via session endpoint
      await fetch('/api/auth/session', {
        method: 'DELETE',
        credentials: 'include',
      });

      sessionStorage.removeItem('user_email');
      setUser(null);
      setAuthToken(null);
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // Still clear local state even if cookie clear fails
      sessionStorage.removeItem('user_email');
      setUser(null);
      setAuthToken(null);
      router.push('/login');
    }
  }, [router]);

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    register,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use auth context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}