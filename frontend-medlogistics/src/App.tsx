import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useKeycloakAuth } from '@/components/auth/KeycloakAuthContext';
import { Box, CircularProgress, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useAppStore, useUser, useActiveWard } from '@/stores/useAppStore';
import { apiClient } from '@/lib/apiClient';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import KeycloakLogin from '@/components/auth/KeycloakLogin';
import WardSelectorPage from '@/components/ward/WardSelectorPage';
import AppDispatcher from '@/pages/AppDispatcher';
import MyOrdersPage from '@/pages/doctor/MyOrdersPage';
import PrescribePage from '@/pages/doctor/PrescribePage';
import InventoryPage from '@/pages/pharmacist/InventoryPage';
import AlertsPage from '@/pages/pharmacist/AlertsPage';
import NurseDashboardPage from '@/pages/nurse/DashboardPage';
import { UserProfile } from '@/types';
import { jwtDecode } from 'jwt-decode';

const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
  padding: theme.spacing(3),
}));

const AppLoading: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => (
  <LoadingContainer>
    <CircularProgress size={48} thickness={4} />
    <Typography variant="h6" sx={{ mt: 2 }} color="textSecondary">
      {message}
    </Typography>
  </LoadingContainer>
);

const App: React.FC = () => {
  const { isAuthenticated, isLoading, token, logout } = useKeycloakAuth();
  const { setSession, clearSession } = useAppStore();
  const user = useUser();
  const activeWard = useActiveWard();

  useEffect(() => {
    const setupSession = async () => {
      if (isAuthenticated && token) {
        try {
          const decodedToken: any = jwtDecode(token);
          const roles = decodedToken.realm_access?.roles || [];

          // Fetch user profile from backend
          const response = await apiClient.get<UserProfile>('/users/me');
          
          setSession(response.data, roles);
        } catch (error) {
          console.error('Failed to set up session:', error);
          logout();
        }
      } else {
        clearSession();
      }
    };

    if (!isLoading) {
      setupSession();
    }
  }, [isAuthenticated, token, isLoading, setSession, clearSession, logout]);

  if (isLoading) {
    return <AppLoading message="Initializing..." />;
  }

  if (!isAuthenticated) {
    return <KeycloakLogin />;
  }

  if (!user) {
    return <AppLoading message="Loading user profile..." />;
  }

  if (!activeWard) {
    return <WardSelectorPage />;
  }

  return (
    <Routes>
      <Route path="/login" element={<KeycloakLogin />} />
      <Route path="/select-ward" element={<WardSelectorPage />} />

      <Route path="/app" element={<ProtectedRoute><AppDispatcher /></ProtectedRoute>}>
        {/* Doctor Routes */}
        <Route path="my-orders" element={<MyOrdersPage />} />
        <Route path="prescribe" element={<PrescribePage />} />

        {/* Pharmacist Routes */}
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="alerts" element={<AlertsPage />} />

        {/* Nurse Routes */}
        <Route path="dashboard" element={<NurseDashboardPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/app" replace />} />
    </Routes>
  );
};

export default App; 