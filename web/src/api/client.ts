import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

// Set by the auth provider once the router is mounted, so a 401 anywhere
// can redirect to /login without this module needing to import React.
let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

export const apiClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // send cookies with requests to the backend
  headers: { 'X-Client-Platform': 'web' }, // for the backend to know which client is making requests 
});

// The id the backend stamped on the most recent response, success or
// failure. `core/middleware.py` returns it as X-Request-ID and #268
// exposed it to JavaScript so the client could surface it; the error
// boundary shows it, which is what turns "the app broke" in a bug report
// into a specific line in the server log.
const REQUEST_ID_HEADER = 'x-request-id';
let lastRequestId: string | null = null;

export function getLastRequestId(): string | null {
  return lastRequestId;
}

function recordRequestId(headers: unknown) {
  if (!headers || typeof headers !== 'object') return;
  const value = (headers as Record<string, unknown>)[REQUEST_ID_HEADER];
  if (typeof value === 'string' && value) lastRequestId = value;
}

// A 401 anywhere means the token is invalid or expired: clear it and
// redirect to /login, same as the Flutter app's global onUnauthorized.
// Modified: No more request interceptor attaching Authorization — the cookie
// rides along automatically.
apiClient.interceptors.response.use(
  (response) => {
    recordRequestId(response.headers);
    return response;
  },
  (error) => {
    recordRequestId(error.response?.headers);
    if (error.response?.status === 401) {
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
