import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useKeycloakAuth } from './KeycloakAuthContext';
import KeycloakLogin from './KeycloakLogin';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const { isLoading, isAuthenticated, hasRole } = useKeycloakAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Loading...
        </Typography>
      </Box>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <KeycloakLogin />;
  }

  // Check role requirements
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <Typography variant="h6" color="error">
          Access Denied
        </Typography>
        <Typography variant="body2" color="text.secondary">
          You don't have permission to access this resource.
          Required role: {requiredRole}
        </Typography>
      </Box>
    );
  }

  // Render protected content
  return <>{children}</>;
};

export default ProtectedRoute; 