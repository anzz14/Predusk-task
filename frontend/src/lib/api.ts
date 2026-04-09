import axios, { AxiosInstance, AxiosError } from 'axios';

/**
 * Module-level reference to the current auth token
 * Updated by AuthContext on login/logout
 */
let currentToken: string | null = null;

/**
 * Set the current auth token (called by AuthContext)
 */
export function setAuthToken(token: string | null) {
  currentToken = token;
}

/**
 * Get the current auth token
 */
export function getAuthToken(): string | null {
  return currentToken;
}

/**
 * Create and configure the API client
 */
const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor: Add Bearer token to all requests
 */
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor: Handle 401 errors and trigger logout
 */
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle 401 Unauthorized (token expired or invalid)
    if (error.response?.status === 401) {
      // Clear the stored token
      setAuthToken(null);
      
      // Trigger logout and redirect to login
      // This will be handled by triggering a custom event that AuthContext listens to
      const event = new CustomEvent('auth:logout', { detail: { reason: 'token_expired' } });
      window.dispatchEvent(event);
      
      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
export { api };