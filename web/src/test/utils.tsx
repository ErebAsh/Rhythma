import type { ReactElement, ReactNode } from 'react';
import { render, type RenderOptions, type RenderResult } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import { AuthProvider } from '../auth/AuthContext';

/**
 * Render a component inside the providers the real app mounts it under.
 *
 * Without this, every page test would repeat the same three wrappers, and
 * a test that forgot one would fail with "useAuth must be used within an
 * AuthProvider" rather than telling you anything about the component.
 */
interface RenderWithProvidersOptions extends Omit<RenderOptions, 'wrapper'> {
  /** Initial history entries for MemoryRouter, e.g. ['/login']. */
  route?: string;
  /** Set false to test a component that must not be wrapped in AuthProvider. */
  withAuth?: boolean;
}

export function renderWithProviders(
  ui: ReactElement,
  { route = '/', withAuth = true, ...options }: RenderWithProvidersOptions = {},
): RenderResult {
  function Wrapper({ children }: { children: ReactNode }) {
    const withinRouter = withAuth ? <AuthProvider>{children}</AuthProvider> : children;
    return (
      <I18nextProvider i18n={i18n}>
        <MemoryRouter initialEntries={[route]}>{withinRouter}</MemoryRouter>
      </I18nextProvider>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

/**
 * A minimal axios-shaped error.
 *
 * `friendlyAuthError` branches on `isAxiosError` and on the presence of
 * `response`, so tests need to be able to build both a "server replied
 * with a status" error and a "request never reached the server" error.
 */
export function axiosError(status?: number, detail?: string) {
  return {
    isAxiosError: true,
    response:
      status === undefined
        ? undefined
        : { status, data: detail === undefined ? {} : { detail } },
  };
}

/** A dashboard payload matching the backend's DashboardResponse model. */
export function dashboardFixture(overrides: Record<string, unknown> = {}) {
  return {
    user: { name: 'Asha' },
    cycle: { day: 12, total: 28, nextPeriodDays: 16 },
    insights: { mhs: 78, cvi: 'Low', sleepHours: '7.4h' },
    hasEnoughDataForInsights: true,
    loggedCycleCount: 6,
    cycleHistory: [
      { start_date: '2026-04-01', cycle_length: 28 },
      { start_date: '2026-04-29', cycle_length: 29 },
    ],
    symptomFrequency: { cramps: 0.5, headache: 0.2, bloating: 0.3, acne: 0.1 },
    recentStressLevel: 3,
    ...overrides,
  };
}
