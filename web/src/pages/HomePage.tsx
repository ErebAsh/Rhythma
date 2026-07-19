import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';

// Deliberately minimal. Issue #47's scope is scaffold + auth only, not
// feature parity with the Flutter app — this just proves a protected
// route renders after a real login.
export function HomePage() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();

  return (
    <div className="home-page">
      <h1>{t('home.welcome', { name: user?.username ?? '' })}</h1>
      <button onClick={logout}>{t('home.logout')}</button>
    </div>
  );
}
