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

// ─── Provider Dashboard & Data Sharing (issue #267) ────────────────────────

export interface Consent {
  id: string;
  patient_id: string;
  provider_id: string;
  provider_email: string;
  provider_name: string;
  status: 'active' | 'revoked';
  created_at?: string | null;
  updated_at?: string | null;
  revoked_at?: string | null;
  /**
   * How many times this provider has opened the patient's data, and when
   * she last did (issue #350). Folded into the consent list by the
   * backend so the sharing screen needs no second request.
   *
   * Optional so the page keeps rendering against a backend that predates
   * the field, rather than showing "0 views" — which would be a claim,
   * not a gap.
   */
  viewCount?: number;
  lastAccessedAt?: string | null;
}

/** One recorded read of the patient's data by a provider (issue #350). */
export interface AccessLogEntry {
  id: string;
  providerId: string;
  providerName: string | null;
  /** `patient_list` (dashboard card) or `patient_detail` (full record). */
  view: 'patient_list' | 'patient_detail';
  consentId: string | null;
  accessedAt: string | null;
}

/**
 * Where a page of access history sits. Mirrors the `page` object the
 * cycle-history endpoint returns (#331); declared separately rather than
 * shared so the two can diverge without one silently changing the other.
 */
export interface AccessLogPageInfo {
  limit: number;
  offset: number;
  count: number;
  hasMore: boolean;
  nextOffset: number | null;
}

export interface AccessLogPage {
  entries: AccessLogEntry[];
  page: AccessLogPageInfo;
}

export interface ProviderPatientSummary {
  patient_id: string;
  name: string;
  age?: number | null;
  city?: string | null;
  state?: string | null;
  sharedSince?: string | null;
  loggedCycleCount: number;
  mhs?: number | null;
  cvi?: string | null;
  hasEnoughDataForInsights: boolean;
}

export interface ProviderPatientDetail {
  patient: {
    id: string;
    name: string;
    age?: number | null;
    city?: string | null;
    state?: string | null;
    cycle_length?: number | null;
    period_duration?: number | null;
    cycle_regular?: boolean | null;
    last_period?: string | null;
  };
  summary: {
    mhs?: number | null;
    cvi?: string | null;
    cvi_raw?: number | null;
    loggedCycleCount: number;
    hasEnoughDataForInsights: boolean;
    avgSleepHours?: number | null;
  };
  cycleLogs: Array<{
    id: string;
    start_date?: string | null;
    end_date?: string | null;
    flow_intensity?: string | null;
    mood?: string | null;
    symptoms?: string[] | null;
    sleep_hours?: number | null;
    stress_level?: number | null;
    notes?: string | null;
  }>;
  consent: { grantedAt?: string | null; status: string };
}

export interface ProviderProfile {
  id: string;
  email: string;
  username?: string | null;
  full_name?: string | null;
  specialty?: string | null;
  license_number?: string | null;
  role: string;
}

export async function grantConsent(providerEmail: string): Promise<Consent> {
  const response = await apiClient.post<Consent>('/provider/consents', {
    provider_email: providerEmail,
  });
  return response.data;
}

export async function fetchConsents(): Promise<Consent[]> {
  const response = await apiClient.get<{ consents: Consent[] }>('/provider/consents');
  return response.data.consents;
}

export async function revokeConsent(consentId: string): Promise<Consent> {
  const response = await apiClient.delete<Consent>(`/provider/consents/${consentId}`);
  return response.data;
}

export async function fetchProviderProfile(): Promise<ProviderProfile> {
  const response = await apiClient.get<ProviderProfile>('/provider/me');
  return response.data;
}

export async function fetchProviderPatients(): Promise<ProviderPatientSummary[]> {
  const response = await apiClient.get<{ patients: ProviderPatientSummary[] }>(
    '/provider/patients',
  );
  return response.data.patients;
}

/**
 * The patient's own record of who has viewed her data, newest first.
 *
 * Patient-only on the server: a provider cannot read this, because her
 * side of the relationship is the thing being recorded.
 */
export async function fetchAccessLog(limit = 20, offset = 0): Promise<AccessLogPage> {
  const response = await apiClient.get<AccessLogPage>('/provider/access-log', {
    params: { limit, offset },
  });
  return response.data;
}

export async function fetchProviderPatientDetail(
  patientId: string,
): Promise<ProviderPatientDetail> {
  const response = await apiClient.get<ProviderPatientDetail>(
    `/provider/patients/${patientId}`,
  );
  return response.data;
}
