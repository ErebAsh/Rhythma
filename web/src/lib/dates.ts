// Local-time date helpers (no external date library).

export function toISODate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function parseISODate(iso: string): Date {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}

export function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

export function addMonths(date: Date, months: number): Date {
  return new Date(date.getFullYear(), date.getMonth() + months, 1);
}

export function endOfMonth(date: Date): Date {
  // Day 0 of the *next* month is the last day of this one, which avoids
  // hardcoding month lengths or a leap-year rule.
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

export function addDays(date: Date, days: number): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days);
}

/**
 * The inclusive date window the calendar needs loaded to render `month`.
 *
 * Wider than the month itself. A user paging back and forth re-fetches
 * constantly at exact-month granularity, and a log written on the 1st or
 * the 31st sits right on the boundary. A few days of margin each side
 * makes paging feel steadier and costs nothing — the whole window is
 * still comfortably inside a single page.
 */
export function monthWindow(month: Date, marginDays = 7): { start: string; end: string } {
  return {
    start: toISODate(addDays(startOfMonth(month), -marginDays)),
    end: toISODate(addDays(endOfMonth(month), marginDays)),
  };
}

export function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

export function daysBetween(a: Date, b: Date): number {
  const ms = new Date(b.getFullYear(), b.getMonth(), b.getDate()).getTime() -
    new Date(a.getFullYear(), a.getMonth(), a.getDate()).getTime();
  return Math.round(ms / 86400000);
}

export function cycleDayFor(date: Date, lastPeriodIso?: string | null): number {
  if (lastPeriodIso) {
    const day = daysBetween(parseISODate(lastPeriodIso), date) + 1;
    if (day >= 1) return day;
  }
  // Fallback matches the Flutter app: day-of-month when no last period set.
  return date.getDate();
}

export type CyclePhase = 'period' | 'follicular' | 'ovulation' | 'luteal';

export function phaseFor(date: Date, lastPeriodIso?: string | null): CyclePhase {
  const day = cycleDayFor(date, lastPeriodIso);
  if (day <= 5) return 'period';
  if (day <= 13) return 'follicular';
  if (day <= 16) return 'ovulation';
  return 'luteal';
}

export const PHASE_COLORS: Record<CyclePhase, string> = {
  period: '#E07AAD',
  follicular: '#AA3BFF',
  ovulation: '#52B3B0',
  luteal: '#E8946A',
};

export function formatMonthYear(date: Date): string {
  return date.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
}

export function formatDayMonth(date: Date): string {
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}
