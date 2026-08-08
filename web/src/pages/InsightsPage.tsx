import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/useAuth';
import {
  fetchObservations,
  type CycleConsistency,
  type Observation,
  type ObservationsResponse,
} from '../api/endpoints';

// No MHS/CVI score here — this page is built entirely against the factual
// /insights/{user_id}/observations endpoint (issue #320). Every number and
// sentence below comes straight from the user's own logged data.

const SEVERITY_ICON: Record<Observation['severity'], string> = {
  info: 'ℹ️',
  attention: '💡',
  seek_care: '💗',
};

const CONSISTENCY_STYLE: Record<CycleConsistency, string> = {
  unknown: 'neutral',
  consistent: 'healthy',
  slightly_variable: 'moderate',
  variable: 'attention',
};

export function InsightsPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [data, setData] = useState<ObservationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError('');
    try {
      setData(await fetchObservations(user.id));
    } catch {
      setError(t('insights.loadError'));
    } finally {
      setLoading(false);
    }
  }, [t, user]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading && !data) {
    return <div className="centered-loader">{t('common.loading')}</div>;
  }

  const totalCycleDays = data?.cycle?.total;
  const variability =
    lengths.length >= 2 && totalCycleDays != null && totalCycleDays > 0
      ? Math.round(
          lengths.reduce((acc, l) => acc + (l - totalCycleDays) ** 2, 0) / lengths.length,
        )
      : null;
  const isHealthy = variability != null && variability <= 3;
  const mhs = data?.insights.mhs ?? null;
  const cvi = data?.insights.cvi ?? null;
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
      ) : isInsufficient ? (
        <div className="warning-card">⏳ {t('insights.notEnoughData')}</div>
      ) : null}

      <section className="glass-card">
        <p className="card-label">{t('insights.cycleStatsLabel')}</p>
        <div className="mini-stats">
          <div className="glass-card mini-stat">
            <span className="mini-stat-icon" style={{ background: '#AA3BFF22', color: '#AA3BFF' }}>
              ♥
            </span>
            <p className="mini-stat-label">{t('insights.avgCycleLength')}</p>
            <p className="mini-stat-value">{avgCycleLength != null ? `${avgCycleLength}d` : '—'}</p>
          </div>
          <div className="glass-card mini-stat">
            <span className="mini-stat-icon" style={{ background: '#52B3B022', color: '#52B3B0' }}>
              #
            </span>
            <p className="mini-stat-label">{t('insights.cyclesAnalyzed')}</p>
            <p className="mini-stat-value">{analyzedCount}</p>
          </div>
        </div>
      </section>

      <section className="glass-card">
        <div className="trend-heading">
          <p className="card-label">{t('insights.consistencyLabel')}</p>
          <span className={`status-pill ${CONSISTENCY_STYLE[consistency]}`}>
            {t(`insights.consistency.${consistency}.pill`)}
          </span>
        </div>
        <p className="card-sub">{t(`insights.consistency.${consistency}.description`)}</p>
      </section>

      {!isInsufficient ? (
        <section>
          <h2 className="section-title">{t('insights.observationsLabel')}</h2>
          {displayObservations.length === 0 ? (
            <div className="glass-card empty-note">{t('insights.noObservations')}</div>
          ) : (
            displayObservations.map((observation) => (
              <ObservationCard key={observation.code} observation={observation} />
            ))
          )}
        </section>
      ) : null}

      <p className="disclaimer">{t(disclaimerKey)}</p>
    </div>
  );
}

function ObservationCard({ observation }: { observation: Observation }) {
  const { t } = useTranslation();
  return (
    <div className={`glass-card observation-card severity-${observation.severity}`}>
      <div className="observation-heading">
        <span className="observation-icon" aria-hidden="true">
          {SEVERITY_ICON[observation.severity] ?? 'ℹ️'}
        </span>
        <div>
          <p className="observation-severity-label">{t(`insights.severity.${observation.severity}`)}</p>
          <p className="observation-title">{observation.title}</p>
        </div>
      </div>
      <p className="observation-body">{observation.body}</p>
    </div>
  );
}
