import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { useMockAuth0 } from '@/components/auth/MockAuth0Context';
import { Box, CircularProgress, Typography, Button, Container, Card, CardContent } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useAppStore, useActiveWard } from '@/stores/useAppStore';
import { setAuthToken, clearAuthToken } from '@/lib/apiClient';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import TokenManager from '@/components/auth/TokenManager';
import RoleSelector from '@/components/RoleSelector';
import WardSelectorPage from '@/components/ward/WardSelectorPage';
import DemoLoginButton from '@/components/demo/DemoLoginButton';
import SimpleDemoApp from '@/components/demo/SimpleDemoApp';
import NurseLayout from '@/components/layout/NurseLayout';
import { AdminLayout } from '@/components/layout/AdminLayout';
import DashboardPage from '@/pages/DashboardPage';
import PatientsPage from '@/pages/PatientsPage';
import AdminDashboardPage from '@/pages/admin/AdminDashboardPage';
import HospitalManagementPage from '@/pages/admin/HospitalManagementPage';
import UserManagementPage from '@/pages/admin/UserManagementPage';
import DoctorLayout from '@/components/layout/DoctorLayout';
import PharmacistLayout from '@/components/layout/PharmacistLayout';
import MyOrdersPage from '@/pages/doctor/MyOrdersPage';
import PrescribePage from '@/pages/doctor/PrescribePage';
import InventoryPage from '@/pages/pharmacist/InventoryPage';
import AlertsPage from '@/pages/pharmacist/AlertsPage';
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
              MedLogistics
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              Medication Management Platform
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Please sign in to access your dashboard and manage patient medications.
            </Typography>
            
            {/* DEMO MODE BUTTON - Now using dedicated component */}
            <DemoLoginButton />
            
            {/* Simple Demo Mode (fallback) */}
            <Button
              variant="outlined"
              size="medium"
              onClick={() => {
                // Render simple demo app instead
                const simpleDemoContainer = document.getElementById('root');
                if (simpleDemoContainer) {
                  window.location.hash = '#simple-demo';
                  window.location.reload();
                }
              }}
              sx={{ mt: 2, minWidth: 200, backgroundColor: '#ff9800', color: 'white', '&:hover': { backgroundColor: '#f57c00' } }}
            >
              🔧 Simple Demo (Fallback)
            </Button>
            
            {/* Less prominent Auth0 button */}
            <Button
              variant="outlined"
              size="small"
              onClick={handleLogin}
              sx={{ mt: 3, minWidth: 150, opacity: 0.6 }}
            >
              Sign In (Auth0 - Not Working)
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
  // Check if we should show simple demo app
  if (window.location.hash.includes('simple-demo')) {
    return <SimpleDemoApp />;
  }

  // Check if we're using real Auth0 or mock for demo
  const hasValidAuth0Config = Boolean(
    import.meta.env.VITE_AUTH0_DOMAIN && 
    import.meta.env.VITE_AUTH0_DOMAIN !== 'your-auth0-domain.auth0.com' &&
    import.meta.env.VITE_AUTH0_CLIENT_ID &&
    import.meta.env.VITE_AUTH0_CLIENT_ID !== 'your-auth0-client-id'
  );
  
  // Use real Auth0 or mock based on configuration
  const realAuth0 = useAuth0();
  const mockAuth0 = useMockAuth0();
  
  const { 
    isLoading: authLoading, 
    isAuthenticated, 
    user, 
    getAccessTokenSilently,
    error: authError 
  } = hasValidAuth0Config ? realAuth0 : mockAuth0;
  
  const { 
    setSession, 
    clearSession, 
    setSelectedRole,
    hasSelectedRole,
    isSuperAdmin,
    roleNeedsWard,
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

  // Debug authentication state
  if (import.meta.env.DEV || window.location.hash.includes('demo')) {
    console.warn('Auth state check:', {
      isAuthenticated,
      storeAuthenticated,
      hasValidAuth0Config,
      userProfile: useAppStore.getState().userProfile?.email,
    });
  }

  // Prioritize store authentication for demo mode
  // Not authenticated - show login page
  if (!storeAuthenticated && !isAuthenticated) {
    return <LoginPage />;
  }

  // Handle role selection callback
  const handleRoleSelect = (role: string) => {
    setSelectedRole(role);
  };

  // Get the appropriate layout based on role
  const getLayoutForRole = () => {
    const { isDoctor, isPharmacist, isNurse } = useAppStore.getState();
    
    if (isDoctor()) return DoctorLayout;
    if (isPharmacist()) return PharmacistLayout;
    if (isNurse()) return NurseLayout;
    return NurseLayout; // Default fallback
  };

  // Authenticated but no role selected - show role selector
  if ((isAuthenticated || storeAuthenticated) && !hasSelectedRole()) {
    return (
      <ProtectedRoute>
        <RoleSelector onRoleSelect={handleRoleSelect} />
      </ProtectedRoute>
    );
  }

  // Role selected but needs ward and no ward selected - show ward selector
  if ((isAuthenticated || storeAuthenticated) && hasSelectedRole() && roleNeedsWard() && !wardId) {
    return (
      <ProtectedRoute>
        <WardSelectorPage />
      </ProtectedRoute>
    );
  }

  // Super admin - show admin interface (no ward needed)
  if ((isAuthenticated || storeAuthenticated) && isSuperAdmin()) {
    return (
      <ProtectedRoute>
        <Routes>
          {/* Redirect root to admin dashboard */}
          <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
          
          {/* Admin routes */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<AdminDashboardPage />} />
            <Route path="users" element={<UserManagementPage />} />
            <Route path="hospitals" element={<HospitalManagementPage />} />
          </Route>
          
          {/* Role selector route (in case user needs to change role) */}
          <Route path="/select-role" element={<RoleSelector onRoleSelect={handleRoleSelect} />} />

          {/* Catch all - redirect to admin dashboard */}
          <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
        </Routes>
      </ProtectedRoute>
    );
  }

  // Get the appropriate layout component
  const LayoutComponent = getLayoutForRole();
  const { isDoctor, isPharmacist, isNurse } = useAppStore.getState();

  // Fully authenticated with role and ward selected - show role-specific app
  return (
    <ProtectedRoute>
      <Routes>
        {/* Redirect root to dashboard */}
        <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
        
        {/* Main app routes with role-specific layout */}
        <Route path="/app" element={<LayoutComponent />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          
          {/* Doctor-specific routes */}
          {isDoctor() && (
            <>
              <Route path="orders" element={<MyOrdersPage />} />
              <Route path="prescribe" element={<PrescribePage />} />
            </>
          )}
          
          {/* Pharmacist-specific routes */}
          {isPharmacist() && (
            <>
              <Route path="inventory" element={<InventoryPage />} />
              <Route path="alerts" element={<AlertsPage />} />
            </>
          )}
          
          {/* Nurse-specific routes */}
          {isNurse() && (
            <>
              <Route path="patients" element={<PatientsPage />} />
              <Route path="medications" element={<div>Medications Page (Coming Soon)</div>} />
            </>
          )}
          
          {/* Common routes */}
          <Route path="profile" element={<div>Profile Page (Coming Soon)</div>} />
          <Route path="settings" element={<div>Settings Page (Coming Soon)</div>} />
          <Route path="notifications" element={<div>Notifications Page (Coming Soon)</div>} />
        </Route>

        {/* Ward selector route (in case user needs to change ward) */}
        <Route path="/select-ward" element={<WardSelectorPage />} />
        
        {/* Role selector route (in case user needs to change role) */}
        <Route path="/select-role" element={<RoleSelector onRoleSelect={handleRoleSelect} />} />

        {/* Catch all - redirect to dashboard */}
        <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
      </Routes>
    </ProtectedRoute>
  );
};

export default App; 