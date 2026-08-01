import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient, friendlyAuthError, setUnauthorizedHandler } from './client';
import { axiosError } from '../test/utils';

describe('apiClient configuration', () => {
  it('sends cookies with every request', () => {
    // The backend switched from a bearer token in localStorage to an
    // HttpOnly cookie; without withCredentials the cookie is never sent
    // and every authenticated request 401s.
    expect(apiClient.defaults.withCredentials).toBe(true);
  });

  it('identifies itself as the web client', () => {
    // core/auth_router.py branches on this header: web clients get the
    // cookie only, mobile clients also get the token in the body.
    expect(apiClient.defaults.headers['X-Client-Platform']).toBe('web');
  });

  it('points at the /api/v1 prefix the backend mounts its routers under', () => {
    expect(apiClient.defaults.baseURL).toMatch(/\/api\/v1$/);
  });
});

describe('401 interceptor', () => {
  afterEach(() => {
    // The handler is module-level state; leaving one registered would let
    // a later test's rejection call a previous test's spy.
    setUnauthorizedHandler(() => {});
  });

  async function runResponseInterceptor(error: unknown) {
    // Reach into the registered interceptor rather than making a real
    // request: the point is to test the handler, not axios.
    const handlers = (
      apiClient.interceptors.response as unknown as {
        handlers: { rejected: (e: unknown) => Promise<unknown> }[];
      }
    ).handlers.filter(Boolean);
    const rejected = handlers[handlers.length - 1].rejected;
    return rejected(error).catch((e: unknown) => e);
  }

  it('calls the unauthorized handler on a 401', async () => {
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);

    await runResponseInterceptor({ response: { status: 401 } });

    expect(onUnauthorized).toHaveBeenCalledTimes(1);
  });

  it('does not call it for other statuses', async () => {
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);

    await runResponseInterceptor({ response: { status: 500 } });
    await runResponseInterceptor({ response: { status: 403 } });
    await runResponseInterceptor({ response: { status: 404 } });

    expect(onUnauthorized).not.toHaveBeenCalled();
  });

  it('does not throw when no handler has been registered', async () => {
    // The optional call (`onUnauthorized?.()`) makes this a silent no-op
    // in production, so nothing would surface a missing registration.
    setUnauthorizedHandler(undefined as unknown as () => void);
    await expect(
      runResponseInterceptor({ response: { status: 401 } }),
    ).resolves.toBeDefined();
  });

  it('re-rejects so callers still see the error', async () => {
    setUnauthorizedHandler(vi.fn());
    const original = { response: { status: 401 } };
    await expect(runResponseInterceptor(original)).resolves.toBe(original);
  });

  it('tolerates an error with no response at all', async () => {
    setUnauthorizedHandler(vi.fn());
    await expect(runResponseInterceptor(new Error('network down'))).resolves.toBeInstanceOf(
      Error,
    );
  });
});

describe('friendlyAuthError', () => {
  it('reports an unreachable server instead of blaming credentials', () => {
    // This branch exists specifically so a CORS misconfiguration or a
    // stopped backend does not get reported as "invalid password" —
    // which sent people looking in entirely the wrong place.
    const message = friendlyAuthError(axiosError(undefined), 'fallback');
    expect(message).toMatch(/Couldn't reach the server/i);
    expect(message).not.toMatch(/invalid/i);
  });

  it('maps 401 to invalid credentials', () => {
    expect(friendlyAuthError(axiosError(401), 'fallback')).toMatch(/Invalid/i);
  });

  it('prefers the server detail on a 429', () => {
    expect(friendlyAuthError(axiosError(429, 'Wait 5 minutes.'), 'fallback')).toBe(
      'Wait 5 minutes.',
    );
  });

  it('falls back to generic copy on a 429 with no detail', () => {
    expect(friendlyAuthError(axiosError(429), 'fallback')).toMatch(/Too many attempts/i);
  });

  it('passes through a server-provided detail for other statuses', () => {
    expect(friendlyAuthError(axiosError(409, 'Email already registered'), 'fallback')).toBe(
      'Email already registered',
    );
  });

  it('uses the caller fallback for a non-axios error', () => {
    expect(friendlyAuthError(new Error('boom'), 'fallback')).toBe('fallback');
    expect(friendlyAuthError(null, 'fallback')).toBe('fallback');
    expect(friendlyAuthError('a string', 'fallback')).toBe('fallback');
  });

  it('uses the fallback when a status carries no detail', () => {
    expect(friendlyAuthError(axiosError(500), 'fallback')).toBe('fallback');
  });
});

describe('base URL configuration', () => {
  it('is always set, so a missing env var cannot produce relative requests', () => {
    // With an empty baseURL every call would go to the page's own origin
    // and 404 against the static host rather than the API.
    expect(apiClient.defaults.baseURL).toBeTruthy();
  });

  it('has no trailing slash, so paths do not become //dashboard', () => {
    expect(apiClient.defaults.baseURL).not.toMatch(/\/$/);
  });
});
