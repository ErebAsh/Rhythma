import { describe, expect, it } from 'vitest';
import {
  PHASE_COLORS,
  addMonths,
  cycleDayFor,
  daysBetween,
  isSameDay,
  parseISODate,
  phaseFor,
  startOfMonth,
  toISODate,
} from './dates';

// These are local-time helpers with no library behind them, so the failure
// modes are the classic ones: UTC drift, month rollover, and leap days.
// All fixtures are fixed dates — nothing here reads the clock.

describe('toISODate', () => {
  it('pads month and day', () => {
    expect(toISODate(new Date(2026, 0, 5))).toBe('2026-01-05');
  });

  it('uses local components, not UTC', () => {
    // `toISOString()` would report the previous day for anywhere west of
    // Greenwich late in the evening — the bug this helper exists to avoid.
    const lateEvening = new Date(2026, 4, 1, 23, 30);
    expect(toISODate(lateEvening)).toBe('2026-05-01');
  });

  it('handles the last day of a year', () => {
    expect(toISODate(new Date(2026, 11, 31))).toBe('2026-12-31');
  });

  it('handles a leap day', () => {
    expect(toISODate(new Date(2024, 1, 29))).toBe('2024-02-29');
  });
});

describe('parseISODate', () => {
  it('round-trips with toISODate', () => {
    for (const iso of ['2026-01-01', '2024-02-29', '2026-12-31', '2026-07-04']) {
      expect(toISODate(parseISODate(iso))).toBe(iso);
    }
  });

  it('produces a local midnight, not a UTC one', () => {
    const parsed = parseISODate('2026-05-01');
    expect(parsed.getHours()).toBe(0);
    expect(parsed.getDate()).toBe(1);
  });
});

describe('startOfMonth', () => {
  it('returns the first of the month', () => {
    expect(toISODate(startOfMonth(new Date(2026, 4, 17)))).toBe('2026-05-01');
  });

  it('is idempotent', () => {
    const first = startOfMonth(new Date(2026, 4, 17));
    expect(toISODate(startOfMonth(first))).toBe('2026-05-01');
  });
});

describe('addMonths', () => {
  it('moves forward', () => {
    expect(toISODate(addMonths(new Date(2026, 4, 15), 1))).toBe('2026-06-01');
  });

  it('rolls over the year boundary going forward', () => {
    expect(toISODate(addMonths(new Date(2026, 11, 15), 1))).toBe('2027-01-01');
  });

  it('rolls over the year boundary going back', () => {
    expect(toISODate(addMonths(new Date(2026, 0, 15), -1))).toBe('2025-12-01');
  });

  it('does not overflow from a 31-day month into the wrong month', () => {
    // Normalising to the 1st is what makes this safe; a naive
    // setMonth(+1) on Jan 31 lands in March.
    expect(toISODate(addMonths(new Date(2026, 0, 31), 1))).toBe('2026-02-01');
  });
});

describe('isSameDay', () => {
  it('ignores the time of day', () => {
    expect(isSameDay(new Date(2026, 4, 1, 0, 1), new Date(2026, 4, 1, 23, 59))).toBe(true);
  });

  it('distinguishes the same day in different months', () => {
    expect(isSameDay(new Date(2026, 4, 1), new Date(2026, 5, 1))).toBe(false);
  });

  it('distinguishes the same date in different years', () => {
    expect(isSameDay(new Date(2025, 4, 1), new Date(2026, 4, 1))).toBe(false);
  });
});

describe('daysBetween', () => {
  it('counts forward', () => {
    expect(daysBetween(new Date(2026, 4, 1), new Date(2026, 4, 8))).toBe(7);
  });

  it('counts backward as a negative', () => {
    expect(daysBetween(new Date(2026, 4, 8), new Date(2026, 4, 1))).toBe(-7);
  });

  it('is zero for the same day at different times', () => {
    expect(daysBetween(new Date(2026, 4, 1, 1), new Date(2026, 4, 1, 23))).toBe(0);
  });

  it('crosses a month boundary', () => {
    expect(daysBetween(new Date(2026, 3, 28), new Date(2026, 4, 2))).toBe(4);
  });

  it('counts a leap day', () => {
    expect(daysBetween(new Date(2024, 1, 28), new Date(2024, 2, 1))).toBe(2);
  });

  it('survives a DST transition', () => {
    // A naive (b - a) / 86400000 without rounding returns 30.958… across a
    // spring-forward, which floors to the wrong day count.
    expect(daysBetween(new Date(2026, 2, 1), new Date(2026, 3, 1))).toBe(31);
  });
});

describe('cycleDayFor', () => {
  it('is day 1 on the period start date', () => {
    expect(cycleDayFor(new Date(2026, 4, 1), '2026-05-01')).toBe(1);
  });

  it('counts inclusively from the start', () => {
    expect(cycleDayFor(new Date(2026, 4, 15), '2026-05-01')).toBe(15);
  });

  it('falls back to the day of the month with no last period', () => {
    expect(cycleDayFor(new Date(2026, 4, 17), null)).toBe(17);
    expect(cycleDayFor(new Date(2026, 4, 17))).toBe(17);
  });

  it('falls back rather than returning a non-positive day for an earlier date', () => {
    expect(cycleDayFor(new Date(2026, 3, 20), '2026-05-01')).toBe(20);
  });
});

describe('phaseFor', () => {
  it.each([
    ['2026-05-01', 'period'],
    ['2026-05-05', 'period'],
    ['2026-05-06', 'follicular'],
    ['2026-05-13', 'follicular'],
    ['2026-05-14', 'ovulation'],
    ['2026-05-16', 'ovulation'],
    ['2026-05-17', 'luteal'],
  ])('maps %s to %s', (iso, expected) => {
    expect(phaseFor(parseISODate(iso), '2026-05-01')).toBe(expected);
  });

  it('has a colour for every phase', () => {
    for (const phase of ['period', 'follicular', 'ovulation', 'luteal'] as const) {
      expect(PHASE_COLORS[phase]).toMatch(/^#[0-9A-Fa-f]{6}$/);
    }
  });

  it('keeps reporting luteal well past a normal cycle length', () => {
    // Documents current behaviour rather than endorsing it: the day count
    // is not wrapped by cycle length, so a stale last_period pins the user
    // in luteal indefinitely. Same shortcoming as the Flutter provider.
    expect(phaseFor(parseISODate('2026-07-15'), '2026-05-01')).toBe('luteal');
  });
});
