import { useEffect, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import {
  fetchConsents,
  grantConsent,
  revokeConsent,
  type Consent,
} from '../api/endpoints';

function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString();
}

export function SharingPage() {
  const { t } = useTranslation();

  const [consents, setConsents] = useState<Consent[]>([]);
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    try {
      setConsents(await fetchConsents());
    } catch {
      setError(t('sharing.loadError'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setNotice('');
    setSubmitting(true);
    try {
      const consent = await grantConsent(email.trim());
      setEmail('');
      setNotice(t('sharing.added', { name: consent.provider_name }));
      await load();
    } catch (err) {
      if (
        err &&
        typeof err === 'object' &&
        'response' in err &&
        (err as { response?: { status?: number } }).response?.status === 404
      ) {
        setError(t('sharing.notFound'));
      } else {
        setError(t('sharing.loadError'));
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevoke = async (consent: Consent) => {
    if (!window.confirm(t('sharing.revokeConfirm', { name: consent.provider_name }))) return;
    setError('');
    setNotice('');
    try {
      await revokeConsent(consent.id);
      setNotice(t('sharing.revokedMsg'));
      await load();
    } catch {
      setError(t('sharing.loadError'));
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h1>{t('sharing.title')}</h1>
      </header>

      <p className="card-sub" style={{ marginTop: -6 }}>
        {t('sharing.subtitle')}
      </p>

      {error && <p className="error-text">{error}</p>}
      {notice && <p className="card-sub">{notice}</p>}

      <section className="glass-card list-card detail-section">
        <h2>{t('sharing.addTitle')}</h2>
        <form className="auth-form" onSubmit={handleAdd} style={{ marginTop: 8 }}>
          <label>
            {t('sharing.providerEmail')}
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={submitting || !email.trim()}>
            {submitting ? t('sharing.adding') : t('sharing.addButton')}
          </button>
        </form>
        <p className="empty-note">{t('sharing.intro')}</p>
      </section>

      <section className="glass-card list-card detail-section">
        {loading ? (
          <p>{t('common.loading')}</p>
        ) : consents.length === 0 ? (
          <p className="empty-note">{t('sharing.empty')}</p>
        ) : (
          consents.map((consent) => (
            <div key={consent.id} className="list-row">
              <div className="list-row-main">
                <span className="list-row-title">{consent.provider_name}</span>
                <span className="list-row-sub">{consent.provider_email}</span>
                <span className="list-row-sub">
                  {t('sharing.grantedOn', { date: formatDate(consent.created_at) })}
                </span>
              </div>
              <span className={`badge ${consent.status}`}>
                {consent.status === 'active' ? t('sharing.active') : t('sharing.revoked')}
              </span>
              {consent.status === 'active' && (
                <button
                  type="button"
                  className="ghost-btn"
                  onClick={() => void handleRevoke(consent)}
                >
                  {t('sharing.revoke')}
                </button>
              )}
            </div>
          ))
        )}
      </section>
    </div>
  );
}
