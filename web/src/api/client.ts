import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

const TOKEN_KEY = 'rhythma_token';

export const tokenStorage = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

// Set by the auth provider once the router is mounted, so a 401 anywhere
// can redirect to /login without this module needing to import React.
let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

export const apiClient = axios.create({
  baseURL: BASE_URL,
});

// Attach the stored token to every request, mirroring api_client.dart's
// interceptor.
apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.get();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A 401 anywhere means the token is invalid or expired: clear it and
// redirect to /login, same as the Flutter app's global onUnauthorized.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      tokenStorage.clear();
      onUnauthorized?.();
    }
    return Promise.reject(error);
  },
);

/**
 * Turns an auth-flow error into an accurate message instead of always
 * blaming bad credentials. A request that never reaches the server (e.g.
 * blocked by CORS, or the backend isn't running) throws with no
 * `error.response` at all — previously this was shown as "Invalid
 * username or password", which was actively misleading and made a CORS
 * misconfiguration look like a login bug.
 */
export function friendlyAuthError(error: unknown, fallback: string): string {
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosErr = error as {
      response?: { status?: number; data?: { detail?: string } };
    };
    if (!axiosErr.response) {
      return "Couldn't reach the server. Check your connection, that the backend is running, and that this origin is allowed by its CORS settings.";
    }
    const status = axiosErr.response.status;
    if (status === 401) return 'Invalid username or password.';
    if (status === 429) {
      return (
        axiosErr.response.data?.detail ||
        'Too many attempts. Please wait a few minutes and try again.'
      );
    }
    if (axiosErr.response.data?.detail) return axiosErr.response.data.detail;
  }
  return fallback;
}
