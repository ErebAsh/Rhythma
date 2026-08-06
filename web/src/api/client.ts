// `AxiosHeaders` is a value — it is constructed below. The other two are
// types only, and `verbatimModuleSyntax` is on in tsconfig, so importing a
// type through a value import is a build error (TS1484).
import axios, { AxiosHeaders } from 'axios';
import type { AxiosError, InternalAxiosRequestConfig } from 'axios';

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

// ─── Auto-Refresh Token Logic ─────────────────────────────────────────────

/// Endpoints that should never trigger token refresh or retry logic.
const PUBLIC_ENDPOINTS = new Set([
  '/auth/login',
  '/auth/register',
  '/auth/firebase-login',
  '/auth/refresh',
  '/auth/logout',
  '/auth/password-requirements',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/auth/verify-email',
  '/auth/resend-verification',
  '/assistant/languages',
  '/health',
]);

function isPublicEndpoint(path: string): boolean {
  for (const publicPath of PUBLIC_ENDPOINTS) {
    if (path === publicPath || path.endsWith(publicPath)) return true;
  }
  return false;
}

/// Shared in-flight refresh promise so concurrent 401s do not spawn
/// multiple refresh requests.
let refreshPromise: Promise<boolean> | null = null;

async function performRefresh(): Promise<boolean> {
  // If a refresh is already in flight, reuse it.
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      // The refresh cookie is sent automatically via withCredentials.
      // We use a plain axios call (not apiClient) to avoid recursion.
      await axios.post(`${BASE_URL}/auth/refresh`, {}, { withCredentials: true });
      // On success the backend rotated the HttpOnly cookies; no local
      // storage needed.
      return true;
    } catch {
      return false;
    }
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

// ─── Request Interceptor ──────────────────────────────────────────────────

apiClient.interceptors.request.use(
  (config) => {
    // Mark retried requests so the response interceptor can break loops.
    return config;
  },
  (error) => Promise.reject(error),
);

// ─── Response Interceptor ─────────────────────────────────────────────────

apiClient.interceptors.response.use(
  (response) => {
    recordRequestId(response.headers);
    return response;
  },
  async (error: AxiosError) => {
    recordRequestId(error.response?.headers);

    const status = error.response?.status;
    const config = error.config as InternalAxiosRequestConfig | undefined;
    const url = config?.url ?? '';

    // Not a 401 — pass through unchanged.
    if (status !== 401) {
      return Promise.reject(error);
    }

    // Public endpoints should not trigger refresh.
    if (isPublicEndpoint(url)) {
      onUnauthorized?.();
      return Promise.reject(error);
    }

    // Prevent infinite retry loops: if this request was already retried
    // after a refresh, force logout.
    if (config?.headers?.['X-Retry-After-Refresh'] === '1') {
      onUnauthorized?.();
      return Promise.reject(error);
    }

    // Attempt to refresh using the HttpOnly cookie.
    const refreshed = await performRefresh();

    if (!refreshed) {
      // Refresh failed — clear session and redirect.
      onUnauthorized?.();
      return Promise.reject(error);
    }

    // Retry the original request once with the new cookies (auto-sent).
    //
    // The marker goes on a real `AxiosHeaders`, not a plain object cast to
    // one. `InternalAxiosRequestConfig.headers` is an `AxiosHeaders`, which
    // carries `set`/`get`/`has` and a normalized key map; a bare
    // `Record<string, string>` satisfies none of that, and the `as` was
    // asserting a lie the compiler correctly refused (TS2322). Downstream
    // axios internals call methods on this object.
    const headers = AxiosHeaders.from(config?.headers);
    headers.set('X-Retry-After-Refresh', '1');

    const retryConfig = {
      ...config,
      headers,
    } as InternalAxiosRequestConfig;

    // `apiClient.request(...)` rather than `apiClient(...)`. They run the
    // same code — the instance *is* a bound `request` — but only the named
    // form is a property lookup, so it is the one a caller can observe.
    return apiClient.request(retryConfig);
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
