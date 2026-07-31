import { apiClient } from './client';

// ─── Dashboard ──────────────────────────────────────────────────────────────

export interface DashboardCycle {
  day: number | null;
  total: number;
  nextPeriodDays: number | null;
}

export interface DashboardInsights {
  mhs: number | null;
  cvi: string | null;
  sleepHours: string | null;
}

export interface CycleHistoryPoint {
  start_date: string;
  cycle_length: number;
}

export interface SymptomFrequency {
  cramps: number;
  headache: number;
  bloating: number;
  acne: number;
}

export interface DashboardData {
  user: { name: string };
  cycle: DashboardCycle;
  insights: DashboardInsights;
  hasEnoughDataForInsights: boolean;
  loggedCycleCount: number;
  cycleHistory: CycleHistoryPoint[];
  symptomFrequency: SymptomFrequency | Record<string, never>;
  recentStressLevel: number | null;
}

export async function fetchDashboard(): Promise<DashboardData> {
  const response = await apiClient.get<DashboardData>('/dashboard');
  return response.data;
}

// ─── Cycle Tracking ─────────────────────────────────────────────────────────

export interface CycleLogInput {
  start_date: string;
  end_date?: string | null;
  flow_intensity?: string | null;
  mood?: string | null;
  symptoms?: string[] | null;
  sleep_hours?: number | null;
  stress_level?: number | null;
  notes?: string | null;
}

export interface CycleLogEntry extends CycleLogInput {
  id: string;
}

export interface CycleHistory {
  message: string;
  entries: CycleLogEntry[];
}

export async function submitCycleLog(log: CycleLogInput) {
  const response = await apiClient.post<{ id: string; message: string; data: CycleLogInput }>(
    '/cycle/log',
    log,
  );
  return response.data;
}

export async function fetchCycleHistory(userId: string, limit = 90): Promise<CycleLogEntry[]> {
  const response = await apiClient.get<CycleHistory>(`/cycle/${userId}/history`, {
    params: { limit },
  });
  return response.data.entries;
}

export async function deleteCycleLog(logId: string) {
  await apiClient.delete(`/cycle/${logId}`);
}

// ─── AI Assistant ───────────────────────────────────────────────────────────

export interface ChatMessage {
  role: 'user' | 'model';
  content: string;
}

export interface ChatResult {
  response: string;
  language: string;
  disclaimer: string;
}

export interface SupportedLanguage {
  code: string;
  name: string;
}

export async function sendChatMessage(
  message: string,
  language: string,
  history: ChatMessage[],
): Promise<ChatResult> {
  const response = await apiClient.post<ChatResult>('/assistant/chat', {
    message,
    language,
    history,
  });
  return response.data;
}

export async function fetchSupportedLanguages(): Promise<SupportedLanguage[]> {
  const response = await apiClient.get<SupportedLanguage[]>('/assistant/languages');
  return response.data;
}

// ─── SMS ────────────────────────────────────────────────────────────────────

export interface SmsSettings {
  phoneNumber: string;
  enabled: boolean;
}

export async function fetchSmsSettings(): Promise<SmsSettings> {
  try {
    const response = await apiClient.get<SmsSettings>('/sms/settings');
    return response.data;
  } catch (error) {
    // 404 means the user has never saved settings — a normal first run.
    if (error && typeof error === 'object' && 'response' in error) {
      const status = (error as { response?: { status?: number } }).response?.status;
      if (status === 404) return { phoneNumber: '', enabled: false };
    }
    throw error;
  }
}

export async function saveSmsSettings(settings: SmsSettings): Promise<SmsSettings> {
  const response = await apiClient.post<SmsSettings>('/sms/settings', settings);
  return response.data;
}

export async function sendSmsSummary(phone_number: string, message: string) {
  const response = await apiClient.post<{ message: string; sid: string }>('/sms/send-summary', {
    phone_number,
    message,
  });
  return response.data;
}

// ─── Profile ────────────────────────────────────────────────────────────────

export interface Profile {
  id?: string;
  phone?: string | null;
  username?: string | null;
  email?: string | null;
  full_name?: string | null;
  age?: number | null;
  height_cm?: number | null;
  weight_kg?: number | null;
  avatar?: string | null;
  language?: string | null;
  last_period?: string | null;
  last_period_is_approximate?: boolean | null;
  cycle_length?: number | null;
  period_duration?: number | null;
  cycle_regular?: boolean | null;
  notifications_enabled?: boolean | null;
  city?: string | null;
  state?: string | null;
}

export type ProfileUpdate = Partial<Pick<
  Profile,
  | 'full_name'
  | 'age'
  | 'height_cm'
  | 'weight_kg'
  | 'avatar'
  | 'language'
  | 'last_period'
  | 'last_period_is_approximate'
  | 'cycle_length'
  | 'period_duration'
  | 'cycle_regular'
  | 'notifications_enabled'
  | 'phone'
  | 'city'
  | 'state'
>>;

export async function fetchProfile(): Promise<Profile> {
  const response = await apiClient.get<Profile>('/auth/profile');
  return response.data;
}

export async function patchProfile(updates: ProfileUpdate): Promise<Profile> {
  const response = await apiClient.patch<Profile>('/auth/profile', updates);
  return response.data;
}

export async function deleteAccount() {
  await apiClient.delete('/auth/me');
}
