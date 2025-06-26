import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useKeycloakAuth } from '@/components/auth/KeycloakAuthContext';
import { Box, CircularProgress, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useAppStore, useActiveWard } from '@/stores/useAppStore';
import { setAuthToken, clearAuthToken } from '@/lib/apiClient';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import TokenManager from '@/components/auth/TokenManager';
import KeycloakLogin from '@/components/auth/KeycloakLogin';
import RoleSelector from '@/components/RoleSelector';
import WardSelectorPage from '@/components/ward/WardSelectorPage';
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

// Main App component
const App: React.FC = () => {
  // Use Keycloak authentication
  const { 
    isLoading: authLoading, 
    isAuthenticated, 
    user, 
    getAccessToken,
    error: authError 
  } = useKeycloakAuth();
  
  const { 
    setSession, 
    clearSession, 
    setSelectedRole,
    hasSelectedRole,
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
          const token = getAccessToken();
          if (token) {
            setAuthToken(token);

            // Create user profile from Keycloak user
            const profile: UserProfile = {
              sub: user.sub,
              email: user.email,
              name: user.name || user.email,
              picture: undefined, // Keycloak might not have pictures
              role: user.roles.includes('super-admin') ? 'super_admin' : 
                    user.roles.includes('doctor') ? 'doctor' :
                    user.roles.includes('pharmacist') ? 'pharmacist' :
                    user.roles.includes('nurse') ? 'nurse' : 'nurse', // Default to nurse
              nurseId: user.sub,
            };

            // Set session in store
            setSession(profile);
          }
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
  }, [isAuthenticated, user, getAccessToken, setSession, clearSession, storeAuthenticated]);

  // Show loading state while checking authentication
  if (authLoading) {
    return <AppLoading message="Checking authentication..." />;
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return (
      <Box>
        <KeycloakLogin />
        {/* Development Token Manager */}
        <TokenManager />
      </Box>
    );
  }

  // Show authentication error
  if (authError) {
    return (
      <LoadingContainer>
        <Typography variant="h6" color="error" gutterBottom>
          Authentication Error
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {authError}
        </Typography>
      </LoadingContainer>
    );
  }

  // Role selection logic
  const handleRoleSelect = (role: string) => {
    setSelectedRole(role);
  };

  const getLayoutForRole = () => {
    if (!hasSelectedRole) return null;
    
    switch (useAppStore.getState().selectedRole) {
      case 'nurse':
        return <NurseLayout />;
      case 'doctor':
        return <DoctorLayout />;
      case 'pharmacist':
        return <PharmacistLayout />;
      case 'super-admin':
        return <AdminLayout />;
      default:
        return <NurseLayout />; // Fallback
    }
  };

  // Show role selector if user hasn't selected a role yet
  if (!hasSelectedRole) {
    return (
      <ProtectedRoute>
        <RoleSelector 
          onRoleSelect={handleRoleSelect}
        />
      </ProtectedRoute>
    );
  }

  // Show ward selector if role needs ward selection and no ward is selected
  if (roleNeedsWard() && !wardId) {
    return (
      <ProtectedRoute>
        <WardSelectorPage />
      </ProtectedRoute>
    );
  }

  // Main application routes
  return (
    <ProtectedRoute>
      <Routes>
        {/* Dashboard Routes */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        
        {/* Nurse Routes */}
        <Route path="/patients" element={<PatientsPage />} />
        
        {/* Doctor Routes */}
        <Route path="/prescribe" element={<PrescribePage />} />
        <Route path="/my-orders" element={<MyOrdersPage />} />
        
        {/* Pharmacist Routes */}
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        
        {/* Admin Routes */}
        <Route path="/admin" element={<AdminDashboardPage />} />
        <Route path="/admin/hospitals" element={<HospitalManagementPage />} />
        <Route path="/admin/users" element={<UserManagementPage />} />
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
      
      {/* Role-specific layout wrapper */}
      {getLayoutForRole()}
    </ProtectedRoute>
  );
};

export default App; 