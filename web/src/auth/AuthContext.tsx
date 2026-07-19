import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient, setUnauthorizedHandler, tokenStorage } from '../api/client';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  // Starts true: on first load we don't yet know if a stored token is
  // still valid, so protected routes should wait rather than flash
  // the login page.
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setUser(null);
      navigate('/login', { replace: true });
    });
  }, [navigate]);

  // On load, confirm any stored token is genuinely still valid by calling
  // /auth/me (not just checking that it exists) — same approach as the
  // Flutter app's splash-screen session validation.
  useEffect(() => {
    const validate = async () => {
      if (!tokenStorage.get()) {
        setLoading(false);
        return;
      }
      try {
        const response = await apiClient.get('/auth/me');
        setUser(response.data);
      } catch {
        // 401 is already handled by the response interceptor (clears
        // token). Any other failure (e.g. offline) just leaves the user
        // logged out for this session rather than guessing.
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    validate();
  }, []);

  const login = async (username: string, password: string) => {
    const form = new URLSearchParams();
    form.set('username', username);
    form.set('password', password);
    const response = await apiClient.post('/auth/token', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    tokenStorage.set(response.data.access_token);
    const me = await apiClient.get('/auth/me');
    setUser(me.data);
  };

  const register = async (
    username: string,
    email: string,
    password: string,
    fullName?: string,
  ) => {
    await apiClient.post('/auth/register', {
      username,
      email,
      password,
      full_name: fullName || null,
    });
  };

  const logout = () => {
    tokenStorage.clear();
    setUser(null);
    navigate('/login', { replace: true });
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
