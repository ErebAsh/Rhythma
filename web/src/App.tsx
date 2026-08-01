import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { ProviderRoute } from './auth/ProviderRoute';
import { AppLayout } from './components/AppLayout';
import { ProviderLayout } from './components/ProviderLayout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProviderLoginPage } from './pages/ProviderLoginPage';
import { ProviderRegisterPage } from './pages/ProviderRegisterPage';
import { ProviderDashboardPage } from './pages/ProviderDashboardPage';
import { ProviderPatientDetailPage } from './pages/ProviderPatientDetailPage';
import { HomePage } from './pages/HomePage';
import { CyclePage } from './pages/CyclePage';
import { AssistantPage } from './pages/AssistantPage';
import { InsightsPage } from './pages/InsightsPage';
import { ProfilePage } from './pages/ProfilePage';
import { SettingsPage } from './pages/SettingsPage';
import { SharingPage } from './pages/SharingPage';
import { SmsPage } from './pages/SmsPage';
import { CustomCursor } from './components/CustomCursor';
import { ScrollToTopButton } from './components/ScrollToTopButton';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CustomCursor />
        <ScrollToTopButton />

        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/provider/login" element={<ProviderLoginPage />} />
          <Route path="/provider/register" element={<ProviderRegisterPage />} />
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<HomePage />} />
            <Route path="/cycle" element={<CyclePage />} />
            <Route path="/assistant" element={<AssistantPage />} />
            <Route path="/insights" element={<InsightsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/sharing" element={<SharingPage />} />
            <Route path="/sms" element={<SmsPage />} />
          </Route>
          <Route
            element={
              <ProviderRoute>
                <ProviderLayout />
              </ProviderRoute>
            }
          >
            <Route path="/provider" element={<ProviderDashboardPage />} />
            <Route path="/provider/patients/:patientId" element={<ProviderPatientDetailPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}