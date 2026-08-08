import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/useAuth';
import { deleteAccount, fetchSupportedLanguages, patchProfile, type SupportedLanguage } from '../api/endpoints';
import { useDocumentMeta } from '../lib/useDocumentMeta';

const FALLBACK_LANGUAGES: SupportedLanguage[] = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'Hindi' },
  { code: 'mr', name: 'Marathi' },
  { code: 'ta', name: 'Tamil' },
  { code: 'te', name: 'Telugu' },
  { code: 'kn', name: 'Kannada' },
  { code: 'ml', name: 'Malayalam' },
];

const LANGUAGE_KEY: Record<string, string> = {
  en: 'settings.english',
  hi: 'settings.hindi',
  mr: 'settings.marathi',
  ta: 'settings.tamil',
  te: 'settings.telugu',
  kn: 'settings.kannada',
  ml: 'settings.malayalam',
};

export function SettingsPage() {
  useDocumentMeta('meta.settings.title', 'meta.settings.description');
  const { t, i18n } = useTranslation();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [languages, setLanguages] = useState<SupportedLanguage[]>(FALLBACK_LANGUAGES);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchSupportedLanguages().then(setLanguages).catch(() => undefined);
  }, []);

  const changeLanguage = async (code: string) => {
    await i18n.changeLanguage(code);
    // Best-effort sync so the preference follows the user across devices.
    patchProfile({ language: code }).catch(() => undefined);
  };

  const handleDelete = async () => {
    if (!window.confirm(t('settings.deleteAccount'))) return;
    setDeleting(true);
    try {
      await deleteAccount();
    } catch {
      // Best-effort: the account is still signed out locally below.
    } finally {
      await logout();
      navigate('/login', { replace: true });
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h1>{t('settings.title')}</h1>
      </header>

      <section className="menu-list">
        <div className="menu-item glass-card">
          <span>🌐</span>
          <div className="menu-item-body">
            <span>{t('settings.language')}</span>
            <span className="card-sub">{t('settings.languageSubtitle')}</span>
          </div>
        </div>
        <div className="language-list">
          {languages.map((lang) => (
            <button
              key={lang.code}
              type="button"
              className={`chip${i18n.language === lang.code ? ' active' : ''}`}
              onClick={() => void changeLanguage(lang.code)}
            >
              {LANGUAGE_KEY[lang.code] ? t(LANGUAGE_KEY[lang.code]) : lang.name}
            </button>
          ))}
        </div>

        <Link to="/sharing" className="menu-item glass-card">
          <span>🩺</span>
          <div className="menu-item-body">
            <span>{t('settings.sharing')}</span>
            <span className="card-sub">{t('settings.sharingSubtitle')}</span>
          </div>
          <span className="chevron">›</span>
        </Link>

        <Link to="/sms" className="menu-item glass-card">
          <span>📱</span>
          <div className="menu-item-body">
            <span>{t('settings.sms')}</span>
            <span className="card-sub">{t('settings.smsSubtitle')}</span>
          </div>
          <span className="chevron">›</span>
        </Link>

        <a href="mailto:support@rhythma.com" className="menu-item glass-card">
          <span>💬</span>
          <div className="menu-item-body">
            <span>{t('settings.contactUs')}</span>
          </div>
          <span className="chevron">›</span>
        </a>
      </section>

      <section className="menu-list">
        <button type="button" className="menu-item glass-card" onClick={() => void logout()}>
          <span>🚪</span>
          <span>{t('settings.logOut')}</span>
          <span className="chevron">›</span>
        </button>
        <button type="button" className="menu-item glass-card danger" disabled={deleting} onClick={() => void handleDelete()}>
          <span>🗑️</span>
          <span>{t('settings.deleteAccount')}</span>
          <span className="chevron">›</span>
        </button>
      </section>
    </div>
  );
}
