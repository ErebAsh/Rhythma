import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { fetchProviderProfile, fetchProviderPatients, type ProviderPatientSummary } from '../api/endpoints';

function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString();
}

export function ProviderDashboardPage() {
  const { t } = useTranslation();

  const [name, setName] = useState('');
  const [patients, setPatients] = useState<ProviderPatientSummary[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [profile, list] = await Promise.all([
          fetchProviderProfile(),
          fetchProviderPatients(),
        ]);
        if (cancelled) return;
        setName(profile.full_name || profile.username || profile.email);
        setPatients(list);
      } catch {
        if (!cancelled) setError(t('providerDashboard.loadError'));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [t]);

  return (
    <div className="page">
      <header className="page-header">
        <h1>{t('providerDashboard.title')}</h1>
      </header>

      <p className="card-sub" style={{ marginTop: -6 }}>
        {name ? t('providerDashboard.welcome', { name }) : ''}
      </p>

      {error && <p className="error-text">{error}</p>}
      {loading && <p>{t('common.loading')}</p>}

      {!loading && patients.length === 0 && (
        <div className="glass-card provider-card">
          <span>{t('providerDashboard.empty')}</span>
        </div>
      )}

      <div className="provider-grid">
        {patients.map((patient) => (
          <div key={patient.patient_id} className="glass-card provider-card">
            <span className="list-row-title">{patient.name}</span>
            <span className="list-row-sub">
              {[patient.age != null ? `${patient.age} yr` : null, patient.city, patient.state]
                .filter(Boolean)
                .join(' · ')}
            </span>
            <div className="stat-row">
              <div className="stat-cell">
                <span className="stat-label">{t('providerDashboard.cyclesLogged', { count: patient.loggedCycleCount })}</span>
                <span className="stat-value">{patient.loggedCycleCount}</span>
              </div>
              <div className="stat-cell">
                <span className="stat-label">{t('providerDashboard.mhs')}</span>
                <span className="stat-value">{patient.mhs ?? '—'}</span>
              </div>
              <div className="stat-cell">
                <span className="stat-label">{t('providerDashboard.cvi')}</span>
                <span className="stat-value">{patient.cvi ?? '—'}</span>
              </div>
            </div>
            <span className="list-row-sub">
              {t('providerPatient.grantedOn', { date: formatDate(patient.sharedSince) })}
            </span>
            <Link to={`/provider/patients/${patient.patient_id}`}>
              {t('providerDashboard.viewPatient')} →
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
