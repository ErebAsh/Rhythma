import { beforeEach, describe, expect, it, vi } from 'vitest';

// Mock the client module rather than the network. These tests are about
// *which URL and payload* each function sends — the exact class of bug
// (#259) that type-checks, lints, builds, and then fails at runtime.
vi.mock('./client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
  setUnauthorizedHandler: vi.fn(),
  friendlyAuthError: vi.fn(),
}));

import { apiClient } from './client';
import {
  deleteAccount,
  deleteCycleLog,
  fetchCycleHistory,
  fetchDashboard,
  fetchObservations,
  fetchProfile,
  fetchSmsSettings,
  fetchSupportedLanguages,
  patchProfile,
  saveSmsSettings,
  sendChatMessage,
  sendSmsSummary,
  submitCycleLog,
} from './endpoints';
import { dashboardFixture, observationsFixture } from '../test/utils';

const mockClient = apiClient as unknown as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  patch: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe('dashboard', () => {
  it('GETs /dashboard and unwraps the body', async () => {
    mockClient.get.mockResolvedValue({ data: dashboardFixture() });

    const data = await fetchDashboard();

    expect(mockClient.get).toHaveBeenCalledWith('/dashboard');
    expect(data.user.name).toBe('Asha');
  });

  it('propagates a failure rather than returning a partial object', async () => {
    mockClient.get.mockRejectedValue(new Error('500'));
    await expect(fetchDashboard()).rejects.toThrow();
  });
});

describe('cycle tracking', () => {
  it('POSTs a log to /cycle/log with the payload untouched', async () => {
    mockClient.post.mockResolvedValue({ data: { id: 'log-1', message: 'ok' } });
    const log = { start_date: '2026-05-01', flow_intensity: 'light' };

    await submitCycleLog(log);

    expect(mockClient.post).toHaveBeenCalledWith('/cycle/log', log);
  });

  it('GETs history for a user id with the limit as a query param', async () => {
    mockClient.get.mockResolvedValue({ data: { message: 'ok', entries: [] } });

    await fetchCycleHistory('user-1', 30);

    expect(mockClient.get).toHaveBeenCalledWith('/cycle/user-1/history', {
      params: { limit: 30 },
    });
  });

  it('defaults the history limit to 90 days', async () => {
    mockClient.get.mockResolvedValue({ data: { message: 'ok', entries: [] } });

    await fetchCycleHistory('user-1');

    expect(mockClient.get).toHaveBeenCalledWith('/cycle/user-1/history', {
      params: { limit: 90 },
    });
  });

  it('returns the entries array, not the envelope', async () => {
    mockClient.get.mockResolvedValue({
      data: { message: 'ok', entries: [{ id: 'a', start_date: '2026-05-01' }] },
    });

    await expect(fetchCycleHistory('user-1')).resolves.toHaveLength(1);
  });

  it('DELETEs a log by id', async () => {
    mockClient.delete.mockResolvedValue({ data: {} });

    await deleteCycleLog('log-42');

    expect(mockClient.delete).toHaveBeenCalledWith('/cycle/log-42');
  });
});

describe('assistant', () => {
  it('POSTs message, language and history to /assistant/chat', async () => {
    mockClient.post.mockResolvedValue({
      data: { response: 'hi', language: 'en', disclaimer: 'not medical advice' },
    });
    const history = [{ role: 'user' as const, content: 'hello' }];

    await sendChatMessage('hello', 'hi', history);

    expect(mockClient.post).toHaveBeenCalledWith('/assistant/chat', {
      message: 'hello',
      language: 'hi',
      history,
    });
  });

  it('GETs the supported language list', async () => {
    mockClient.get.mockResolvedValue({ data: [{ code: 'en', name: 'English' }] });

    await fetchSupportedLanguages();

    expect(mockClient.get).toHaveBeenCalledWith('/assistant/languages');
  });
});

describe('sms', () => {
  it('GETs settings', async () => {
    mockClient.get.mockResolvedValue({ data: { phoneNumber: '+91', enabled: true } });

    await expect(fetchSmsSettings()).resolves.toEqual({
      phoneNumber: '+91',
      enabled: true,
    });
    expect(mockClient.get).toHaveBeenCalledWith('/sms/settings');
  });

  it('treats a 404 as "never configured" rather than an error', async () => {
    // A first-run user has no settings document; surfacing that as an
    // error would show a red banner on a perfectly normal screen.
    mockClient.get.mockRejectedValue({ response: { status: 404 } });

    await expect(fetchSmsSettings()).resolves.toEqual({
      phoneNumber: '',
      enabled: false,
    });
  });

  it('still throws on a non-404 failure', async () => {
    mockClient.get.mockRejectedValue({ response: { status: 500 } });
    await expect(fetchSmsSettings()).rejects.toBeDefined();
  });

  it('still throws when the request never reached the server', async () => {
    mockClient.get.mockRejectedValue(new Error('network'));
    await expect(fetchSmsSettings()).rejects.toBeDefined();
  });

  it('POSTs settings', async () => {
    const settings = { phoneNumber: '+919876543210', enabled: true };
    mockClient.post.mockResolvedValue({ data: settings });

    await saveSmsSettings(settings);

    expect(mockClient.post).toHaveBeenCalledWith('/sms/settings', settings);
  });

  it('POSTs a summary with snake_case keys the backend expects', async () => {
    // The SMSRequest model uses phone_number; sending phoneNumber here
    // would 422 at runtime while type-checking cleanly.
    mockClient.post.mockResolvedValue({ data: { message: 'ok', sid: 'SM1' } });

    await sendSmsSummary('+919876543210', 'Your cycle summary');

    expect(mockClient.post).toHaveBeenCalledWith('/sms/send-summary', {
      phone_number: '+919876543210',
      message: 'Your cycle summary',
    });
  });
});

describe('profile', () => {
  it('GETs /auth/profile', async () => {
    mockClient.get.mockResolvedValue({ data: { id: 'u1' } });

    await fetchProfile();

    expect(mockClient.get).toHaveBeenCalledWith('/auth/profile');
  });

  it('PATCHes /auth/profile with only the changed fields', async () => {
    // PATCH semantics matter: the backend writes only non-None fields, so
    // sending a full object with nulls would clobber unrelated data.
    mockClient.patch.mockResolvedValue({ data: { id: 'u1', age: 30 } });

    await patchProfile({ age: 30 });

    expect(mockClient.patch).toHaveBeenCalledWith('/auth/profile', { age: 30 });
  });

  it('DELETEs /auth/me to close the account', async () => {
    mockClient.delete.mockResolvedValue({ data: {} });

    await deleteAccount();

    expect(mockClient.delete).toHaveBeenCalledWith('/auth/me');
  });
});

describe('insights observations', () => {
  it('GETs /insights/{userId}/observations and unwraps the body', async () => {
    mockClient.get.mockResolvedValue({ data: observationsFixture() });

    const data = await fetchObservations('user-1');

    expect(mockClient.get).toHaveBeenCalledWith('/insights/user-1/observations');
    expect(data.cycleConsistency).toBe('slightly_variable');
    expect(data.observations).toHaveLength(2);
  });

  it('propagates a failure rather than returning a partial object', async () => {
    mockClient.get.mockRejectedValue(new Error('500'));
    await expect(fetchObservations('user-1')).rejects.toThrow();
  });
});

describe('endpoint paths as a contract', () => {
  it('never calls a path outside the routers the backend registers', async () => {
    // main.py mounts auth, health, assistant, cycle, insights, sms and the
    // dashboard. A call to anything else is a client/server mismatch, which
    // is exactly how the /auth/token bug shipped.
    const mounted = [
      '/auth',
      '/health',
      '/assistant',
      '/cycle',
      '/insights',
      '/sms',
      '/dashboard',
    ];

    mockClient.get.mockResolvedValue({ data: dashboardFixture() });
    mockClient.post.mockResolvedValue({ data: {} });
    mockClient.patch.mockResolvedValue({ data: {} });
    mockClient.delete.mockResolvedValue({ data: {} });

    await fetchDashboard();
    await fetchCycleHistory('u1');
    await fetchProfile();
    await fetchSupportedLanguages();
    await submitCycleLog({ start_date: '2026-05-01' });
    await deleteCycleLog('log-1');
    await deleteAccount();

    const calledPaths = [
      ...mockClient.get.mock.calls,
      ...mockClient.post.mock.calls,
      ...mockClient.patch.mock.calls,
      ...mockClient.delete.mock.calls,
    ].map((call) => String(call[0]));

    expect(calledPaths.length).toBeGreaterThan(0);
    for (const path of calledPaths) {
      expect(
        mounted.some((prefix) => path.startsWith(prefix)),
        `${path} is not under a router the backend mounts`,
      ).toBe(true);
    }
  });
});
