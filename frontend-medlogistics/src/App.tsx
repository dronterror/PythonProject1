import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { Box, CircularProgress, Typography, Button, Container, Card, CardContent } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useAppStore, useActiveWard } from '@/stores/useAppStore';
import { setAuthToken, clearAuthToken } from '@/lib/apiClient';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import TokenManager from '@/components/auth/TokenManager';
import WardSelectorPage from '@/components/ward/WardSelectorPage';
import NurseLayout from '@/components/layout/NurseLayout';
import DashboardPage from '@/pages/DashboardPage';
import PatientsPage from '@/pages/PatientsPage';
import type { UserProfile } from '@/types';

const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
  padding: theme.spacing(3),
}));

const LoginContainer = styled(Container)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}));

const LoginCard = styled(Card)(({ theme }) => ({
  padding: theme.spacing(4),
  textAlign: 'center',
  maxWidth: 400,
  width: '100%',
}));

// Loading component
const AppLoading: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => {
  return (
    <LoadingContainer>
      <CircularProgress size={48} thickness={4} />
      <Typography variant="h6" sx={{ mt: 2 }} color="textSecondary">
        {message}
      </Typography>
    </LoadingContainer>
  );
};

// Login page component
const LoginPage: React.FC = () => {
  const { loginWithRedirect } = useAuth0();

  const handleLogin = () => {
    loginWithRedirect({
      appState: {
        returnTo: window.location.pathname,
      },
    });
  };

  return (
    <Box>
      <LoginContainer maxWidth="sm">
        <LoginCard>
          <CardContent>
            <Typography variant="h4" component="h1" gutterBottom color="primary">
              MedLog Nurse
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              Professional medication management for nurses
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Please sign in to access your dashboard and manage patient medications.
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={handleLogin}
              sx={{ mt: 2, minWidth: 200 }}
            >
              Sign In
            </Button>
          </CardContent>
        </LoginCard>
      </LoginContainer>
      
      {/* Development Token Manager */}
      <TokenManager />
    </Box>
  );
};

// Main App component
const App: React.FC = () => {
  // const navigate = useNavigate();
  const { 
    isLoading: authLoading, 
    isAuthenticated, 
    user, 
    getAccessTokenSilently,
    error: authError 
  } = useAuth0();
  
  const { 
    setSession, 
    clearSession, 
    // userProfile, 
    isAuthenticated: storeAuthenticated 
  } = useAppStore();
  
  const { wardId } = useActiveWard();

  // Handle authentication state changes
  useEffect(() => {
    const handleAuth = async () => {
      if (isAuthenticated && user) {
        try {
          // Get access token and store it
          const token = await getAccessTokenSilently();
          setAuthToken(token);

          // Create user profile from Auth0 user
          const profile: UserProfile = {
            sub: user.sub!,
            email: user.email!,
            name: user.name!,
            picture: user.picture,
            role: 'nurse', // Default role - this could come from user metadata
            nurseId: user.sub,
          };

          // Set session in store
          setSession(profile);
        } catch (error) {
          console.error('Error setting up authentication:', error);
          clearSession();
          clearAuthToken();
        }
      } else if (!isAuthenticated && storeAuthenticated) {
        // User logged out
        clearSession();
        clearAuthToken();
      }
    };

    handleAuth();
  }, [isAuthenticated, user, getAccessTokenSilently, setSession, clearSession, storeAuthenticated]);

  // Show loading while Auth0 is initializing
  if (authLoading) {
    return <AppLoading message="Initializing application..." />;
  }

  // Show error if authentication failed
  if (authError) {
    return (
      <LoadingContainer>
        <Typography variant="h6" color="error" gutterBottom>
          Authentication Error
        </Typography>
        <Typography variant="body2" color="textSecondary" paragraph>
          {authError.message}
        </Typography>
        <Button variant="contained" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </LoadingContainer>
    );
  }

  // Not authenticated - show login page
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // Authenticated but no ward selected - show ward selector
  if (isAuthenticated && !wardId) {
    return (
      <ProtectedRoute>
        <WardSelectorPage />
      </ProtectedRoute>
    );
  }

  // Fully authenticated with ward selected - show main app
  return (
    <ProtectedRoute>
      <Routes>
        {/* Redirect root to dashboard */}
        <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
        
        {/* Main app routes with layout */}
        <Route path="/app" element={<NurseLayout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="patients" element={<PatientsPage />} />
          <Route path="medications" element={<div>Medications Page (Coming Soon)</div>} />
          <Route path="profile" element={<div>Profile Page (Coming Soon)</div>} />
          <Route path="settings" element={<div>Settings Page (Coming Soon)</div>} />
          <Route path="notifications" element={<div>Notifications Page (Coming Soon)</div>} />
        </Route>

        {/* Ward selector route (in case user needs to change ward) */}
        <Route path="/select-ward" element={<WardSelectorPage />} />

        {/* Catch all - redirect to dashboard */}
        <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
      </Routes>
    </ProtectedRoute>
  );
};

export default App; 