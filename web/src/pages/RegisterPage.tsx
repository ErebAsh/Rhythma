import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { friendlyAuthError } from '../api/client';

export function RegisterPage() {
  const { t } = useTranslation();
  const { register } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(username, email, password, fullName);
      navigate('/login', { replace: true });
    } catch (err) {
      setError(friendlyAuthError(err, t('auth.registerError')));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>{t('auth.registerTitle')}</h1>

        {error && <p className="error-text">{error}</p>}

        <label>
          {t('auth.username')}
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </label>

        <label>
          {t('auth.email')}
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        <label>
          {t('auth.fullName')}
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </label>

        <label>
          {t('auth.password')}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? t('auth.registering') : t('auth.registerButton')}
        </button>

        <p>
          {t('auth.haveAccount')} <Link to="/login">{t('auth.loginLink')}</Link>
        </p>
      </form>
    </div>
  );
}
