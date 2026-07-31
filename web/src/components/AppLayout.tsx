import { NavLink, Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';

interface NavLinkDef {
  to: string;
  key: string;
  end?: boolean;
}

const LINKS: NavLinkDef[] = [
  { to: '/', key: 'nav.home', end: true },
  { to: '/cycle', key: 'nav.cycle' },
  { to: '/assistant', key: 'nav.assistant' },
  { to: '/insights', key: 'nav.insights' },
  { to: '/profile', key: 'nav.profile' },
  { to: '/settings', key: 'nav.settings' },
];

export function AppLayout() {
  const { t } = useTranslation();
  const { logout } = useAuth();

  return (
    <div className="app-layout">
      <header className="app-header">
        <span className="app-brand" aria-hidden>
          Rhythma
        </span>
        <button type="button" className="ghost-btn" onClick={() => void logout()}>
          {t('nav.logout')}
        </button>
      </header>

      <nav className="app-nav" aria-label="Main">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            {t(link.key)}
          </NavLink>
        ))}
      </nav>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
