import { NavLink, Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/useAuth';

export function ProviderLayout() {
  const { t } = useTranslation();
  const { logout } = useAuth();

  return (
    <div className="app-layout">
      <header className="app-header">
        <span className="app-brand" aria-hidden>
          Rhythma
        </span>
        <button
          type="button"
          className="ghost-btn"
          onClick={() => void logout('/provider/login')}
        >
          {t('providerNav.logout')}
        </button>
      </header>

      <nav className="app-nav" aria-label="Provider">
        <NavLink
          to="/provider"
          end
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          {t('providerNav.dashboard')}
        </NavLink>
      </nav>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
