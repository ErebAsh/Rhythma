import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { fetchDashboard, type DashboardData } from '../api/endpoints';
import { Sparkline } from '../components/charts';

const SYMPTOM_COLORS: Record<string, string> = {
  cramps: '#E07AAD',
  headache: '#E8946A',
  bloating: '#AA3BFF',
  acne: '#52B3B0',
};

function stressLabel(level: number | null, t: (k: string) => string): string {
  if (level == null) return '—';
  if (level <= 2) return t('insights.low');
  if (level <= 3) return t('insights.moderate');
  return t('insights.high');
}

export function InsightsPage() {
  const { t } = useTranslation();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setData(await fetchDashboard());
    } catch {
      setError(t('insights.loadError'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading && !data) {
    return <div className="centered-loader">{t('common.loading')}</div>;
  }

  const lengths = data?.cycleHistory.map((p) => p.cycle_length) ?? [];
  const variability =
    lengths.length >= 2
      ? Math.round(
          lengths.reduce((acc, l) => acc + (l - (data?.cycle.total ?? 0)) ** 2, 0) / lengths.length,
        )
      : null;
  const isHealthy = variability != null && variability <= 3;
  const avgCycle = data?.insights.averageCycleLength ?? null;
  const shortestCycle = data?.insights.shortestCycleLength ?? null;
  const longestCycle = data?.insights.longestCycleLength ?? null;
  const avgBleeding = data?.insights.averageBleedingDuration ?? null;
  const sleep = data?.insights.sleepHours ?? null;
  const stress = stressLabel(data?.recentStressLevel ?? null, t);
  const symptoms = data?.symptomFrequency ?? {};
  const hasSymptoms = Object.keys(symptoms).length > 0;
  const hasEnough = data?.hasEnoughDataForInsights ?? false;

  const recs: { key: string; color: string }[] = [{ key: 'insights.rec1', color: '#E07AAD' }];
  if (sleep && parseFloat(sleep) < 7) recs.push({ key: 'insights.rec2', color: '#AA3BFF' });
  if ((data?.recentStressLevel ?? 0) >= 4) recs.push({ key: 'insights.rec3', color: '#52B3B0' });

  return (
    <div className="page">
      <header className="page-header">
        <h1>{t('insights.title')}</h1>
        <p className="card-sub">{t('insights.subtitle')}</p>
      </header>

      {error ? (
        <div className="error-card">
          <p>{error}</p>
          <button type="button" className="primary-btn" onClick={() => void load()}>
            {t('common.retry')}
          </button>
        </div>
      ) : !hasEnough ? (
        <div className="warning-card">⏳ {t('insights.notEnoughData')}</div>
      ) : null}

      <section className="glass-card mhs-card">
        <div className="mhs-info">
          <p className="card-label">{t('insights.cycleStats')}</p>
          <div className="stat-row">
            <div className="stat-cell">
              <span className="stat-label">{t('insights.avgCycle')}</span>
              <span className="stat-value">{avgCycle == null ? '—' : `${avgCycle}d`}</span>
            </div>
            <div className="stat-cell">
              <span className="stat-label">{t('insights.shortest')}</span>
              <span className="stat-value">{shortestCycle == null ? '—' : `${shortestCycle}d`}</span>
            </div>
            <div className="stat-cell">
              <span className="stat-label">{t('insights.longest')}</span>
              <span className="stat-value">{longestCycle == null ? '—' : `${longestCycle}d`}</span>
            </div>
            <div className="stat-cell">
              <span className="stat-label">{t('insights.avgBleeding')}</span>
              <span className="stat-value">{avgBleeding == null ? '—' : `${avgBleeding}d`}</span>
            </div>
          </div>
          <p className="card-sub">
            {isHealthy ? t('insights.regular') : t('insights.mhsDelta')}
          </p>
        </div>
      </section>

      <section className="mini-stats">
        <MiniStat label={t('insights.variability')} value={variability == null ? '—' : String(variability)} delta={variability == null ? null : variability <= 3 ? t('insights.low') : t('insights.moderate')} color="#52B3B0" arrow={variability == null ? '—' : variability <= 3 ? '↘' : '↗'} />
        <MiniStat label={t('insights.avgCycle')} value={data?.cycle.total != null ? `${data.cycle.total}d` : '—'} delta={t('insights.regular')} color="#AA3BFF" arrow="♥" />
        <MiniStat label={t('insights.sleep')} value={sleep ?? '—'} delta={null} color="#9B72CF" arrow="🌙" />
        <MiniStat label={t('insights.stress')} value={stress} delta={null} color="#E8946A" arrow="📈" />
      </section>

      <section className="glass-card trend-card">
        <div className="trend-heading">
          <div>
            <p className="card-label">{t('insights.trendLabel')}</p>
            <p className="trend-title">{isHealthy ? t('insights.stabilizing') : t('insights.moderateTrend')}</p>
          </div>
          {variability != null ? (
            <span className={`status-pill ${isHealthy ? 'healthy' : 'moderate'}`}>
              {isHealthy ? t('insights.healthy') : t('insights.moderate')}
            </span>
          ) : null}
        </div>
        {lengths.length < 2 ? (
          <p className="empty-note">{t('insights.notEnoughTrendData')}</p>
        ) : (
          <Sparkline points={lengths} color="#AA3BFF" height={80} />
        )}
      </section>

      <section className="glass-card symptom-card">
        <p className="card-label">{t('insights.symptomsLabel')}</p>
        {!hasSymptoms ? (
          <p className="empty-note">{t('insights.noSymptomsYet')}</p>
        ) : (
          <div className="symptom-bars">
            {Object.entries(symptoms).map(([key, fraction]) => (
              <div key={key} className="symptom-bar">
                <span className="symptom-label">{t(`cycle.${key}`)}</span>
                <div className="symptom-track">
                  <div
                    className="symptom-fill"
                    style={{
                      width: `${Math.round((fraction as number) * 100)}%`,
                      background: SYMPTOM_COLORS[key] ?? '#AA3BFF',
                    }}
                  />
                </div>
                <span className="symptom-pct">{Math.round((fraction as number) * 100)}%</span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="section-title">{t('insights.wellness')}</h2>
        {recs.map((rec, i) => (
          <div key={i} className="glass-card rec-card">
            <span className="rec-icon" style={{ background: rec.color }}>
              💗
            </span>
            <p>{t(rec.key)}</p>
          </div>
        ))}
      </section>
    </div>
  );
}

interface MiniStatProps {
  label: string;
  value: string;
  delta: string | null;
  color: string;
  arrow: string;
}

function MiniStat({ label, value, delta, color, arrow }: MiniStatProps) {
  return (
    <div className="glass-card mini-stat">
      <span className="mini-stat-icon" style={{ background: `${color}22`, color }}>
        {arrow}
      </span>
      <p className="mini-stat-label">{label}</p>
      <p className="mini-stat-value">{value}</p>
      {delta ? <p className="mini-stat-delta">{delta}</p> : null}
    </div>
  );
}
