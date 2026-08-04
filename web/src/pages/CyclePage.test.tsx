import { beforeEach, describe, expect, it, vi } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// The Cycle page was the largest page with no test at all, which is how
// #349 shipped: it asked the history endpoint for `limit=365`, the server
// caps at 100 and answers 422, and the page's `catch` turned that into an
// empty Map — rendering exactly like a brand-new account. Nothing in the
// UI or the console said a request had failed.
//
// The endpoints module is mocked rather than axios, so these tests are
// about what the *page* asks for and what it does with the answer.
vi.mock('../api/endpoints', () => ({
  fetchCycleHistoryRange: vi.fn(),
  fetchProfile: vi.fn(),
  submitCycleLog: vi.fn(),
  deleteCycleLog: vi.fn(),
}));

vi.mock('../auth/useAuth', () => ({
  useAuth: () => ({ user: { id: 'user-1', username: 'asha' } }),
}));

import {
  deleteCycleLog,
  fetchCycleHistoryRange,
  fetchProfile,
  submitCycleLog,
} from '../api/endpoints';
import { CyclePage } from './CyclePage';
import { renderWithProviders } from '../test/utils';
import { toISODate } from '../lib/dates';

const mockRange = fetchCycleHistoryRange as unknown as ReturnType<typeof vi.fn>;
const mockProfile = fetchProfile as unknown as ReturnType<typeof vi.fn>;
const mockSubmit = submitCycleLog as unknown as ReturnType<typeof vi.fn>;
const mockDelete = deleteCycleLog as unknown as ReturnType<typeof vi.fn>;

const TODAY = new Date();
const TODAY_ISO = toISODate(TODAY);

function logFixture(overrides: Record<string, unknown> = {}) {
  return {
    id: `user-1_${TODAY_ISO}`,
    start_date: TODAY_ISO,
    flow_intensity: 'medium',
    ...overrides,
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  mockRange.mockResolvedValue([]);
  mockProfile.mockResolvedValue({ last_period: TODAY_ISO });
  mockSubmit.mockResolvedValue({ id: 'log-1', message: 'ok' });
  mockDelete.mockResolvedValue(undefined);
});

describe('loading history', () => {
  it('fetches a date window rather than a fixed number of entries', async () => {
    renderWithProviders(<CyclePage />);

    await waitFor(() => expect(mockRange).toHaveBeenCalled());

    const [userId, start, end] = mockRange.mock.calls[0];
    expect(userId).toBe('user-1');
    expect(start).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(end).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(start < end).toBe(true);
  });

  it('asks for a window that contains the displayed month', async () => {
    renderWithProviders(<CyclePage />);
    await waitFor(() => expect(mockRange).toHaveBeenCalled());

    const [, start, end] = mockRange.mock.calls[0];
    const firstOfMonth = toISODate(new Date(TODAY.getFullYear(), TODAY.getMonth(), 1));
    const lastOfMonth = toISODate(new Date(TODAY.getFullYear(), TODAY.getMonth() + 1, 0));

    expect(start <= firstOfMonth).toBe(true);
    expect(end >= lastOfMonth).toBe(true);
  });

  it('marks days that have a log', async () => {
    mockRange.mockResolvedValue([logFixture()]);

    const { container } = renderWithProviders(<CyclePage />);

    await waitFor(() => {
      expect(container.querySelectorAll('.log-dot').length).toBeGreaterThan(0);
    });
  });

  it('renders no log dots when the user genuinely has none', async () => {
    mockRange.mockResolvedValue([]);

    const { container } = renderWithProviders(<CyclePage />);

    await waitFor(() => expect(mockRange).toHaveBeenCalled());
    expect(container.querySelectorAll('.log-dot')).toHaveLength(0);
  });

  it('tolerates an entry with no start_date instead of throwing', async () => {
    // `entry.start_date.slice(0, 10)` on a partial document would throw
    // inside the loop and land in the same catch, blanking the calendar
    // for one malformed row.
    mockRange.mockResolvedValue([{ id: 'broken' }, logFixture()]);

    const { container } = renderWithProviders(<CyclePage />);

    await waitFor(() => {
      expect(container.querySelectorAll('.log-dot').length).toBe(1);
    });
    expect(screen.queryByRole('alert')).toBeNull();
  });
});

describe('a failed load is not silence', () => {
  it('says the load failed instead of rendering an empty calendar', async () => {
    mockRange.mockRejectedValue(new Error('422'));

    renderWithProviders(<CyclePage />);

    // The regression this file exists for: before #349 this state was
    // indistinguishable from "no logs yet".
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });

  it('offers a retry that re-requests the same window', async () => {
    mockRange.mockRejectedValueOnce(new Error('network'));
    mockRange.mockResolvedValue([logFixture()]);

    const { container } = renderWithProviders(<CyclePage />);
    const alert = await screen.findByRole('alert');

    await userEvent.click(within(alert).getByRole('button'));

    await waitFor(() => {
      expect(container.querySelectorAll('.log-dot').length).toBeGreaterThan(0);
    });
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('does not treat a missing profile as a failed load', async () => {
    // `fetchProfile` is already `.catch`-ed to null in the page; a user
    // with no profile yet must still see her calendar.
    mockProfile.mockRejectedValue(new Error('404'));
    mockRange.mockResolvedValue([logFixture()]);

    const { container } = renderWithProviders(<CyclePage />);

    await waitFor(() => {
      expect(container.querySelectorAll('.log-dot').length).toBeGreaterThan(0);
    });
    expect(screen.queryByRole('alert')).toBeNull();
  });
});

describe('changing month', () => {
  it('re-fetches for the new month', async () => {
    renderWithProviders(<CyclePage />);
    await waitFor(() => expect(mockRange).toHaveBeenCalledTimes(1));

    await userEvent.click(screen.getByLabelText('Previous month'));

    await waitFor(() => expect(mockRange).toHaveBeenCalledTimes(2));
    const firstWindow = mockRange.mock.calls[0][1];
    const secondWindow = mockRange.mock.calls[1][1];
    expect(secondWindow < firstWindow).toBe(true);
  });

  it('fetches forward when paging to the next month', async () => {
    renderWithProviders(<CyclePage />);
    await waitFor(() => expect(mockRange).toHaveBeenCalledTimes(1));

    await userEvent.click(screen.getByLabelText('Next month'));

    await waitFor(() => expect(mockRange).toHaveBeenCalledTimes(2));
    expect(mockRange.mock.calls[1][1] > mockRange.mock.calls[0][1]).toBe(true);
  });

  it('shows logs from a month other than the current one', async () => {
    // Before this change the page fetched once and never again, so any
    // month outside the initial fetch was blank regardless of the limit.
    const lastMonth = new Date(TODAY.getFullYear(), TODAY.getMonth() - 1, 15);
    mockRange.mockResolvedValueOnce([]);
    mockRange.mockResolvedValueOnce([
      logFixture({ id: 'older', start_date: toISODate(lastMonth) }),
    ]);

    const { container } = renderWithProviders(<CyclePage />);
    await waitFor(() => expect(mockRange).toHaveBeenCalledTimes(1));

    await userEvent.click(screen.getByLabelText('Previous month'));

    await waitFor(() => {
      expect(container.querySelectorAll('.log-dot').length).toBe(1);
    });
  });
});

describe('saving', () => {
  it('reloads the current window after a successful save', async () => {
    renderWithProviders(<CyclePage />);
    await waitFor(() => expect(mockRange).toHaveBeenCalledTimes(1));

    await userEvent.click(screen.getByText('Light'));
    await userEvent.click(screen.getByText('Save Log'));

    await waitFor(() => expect(mockSubmit).toHaveBeenCalled());
    await waitFor(() => expect(mockRange).toHaveBeenCalledTimes(2));
  });

  it('sends only the selected fields', async () => {
    renderWithProviders(<CyclePage />);
    await waitFor(() => expect(mockRange).toHaveBeenCalled());

    await userEvent.click(screen.getByText('Heavy'));
    await userEvent.click(screen.getByText('Save Log'));

    await waitFor(() => expect(mockSubmit).toHaveBeenCalled());
    expect(mockSubmit).toHaveBeenCalledWith({
      start_date: TODAY_ISO,
      flow_intensity: 'heavy',
    });
  });

  it('keeps the save button disabled until something is selected', async () => {
    renderWithProviders(<CyclePage />);
    await waitFor(() => expect(mockRange).toHaveBeenCalled());

    expect(screen.getByText('Save Log')).toBeDisabled();
  });
});
