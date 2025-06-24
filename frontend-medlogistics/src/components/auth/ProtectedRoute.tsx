import React from 'react';
import { withAuthenticationRequired } from '@auth0/auth0-react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.default,
}));

const LoadingContent = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: theme.spacing(3),
}));

// Loading component shown while authentication is being verified
const AuthenticationLoading: React.FC = () => {
  return (
    <LoadingContainer>
      <LoadingContent>
        <CircularProgress size={48} thickness={4} />
        <Typography variant="h6" color="textSecondary" align="center">
          Verifying authentication...
        </Typography>
        <Typography variant="body2" color="textSecondary" align="center">
          Please wait while we securely log you in
        </Typography>
      </LoadingContent>
    </LoadingContainer>
  );
};

// Higher-order component that protects routes with Auth0 authentication
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const ProtectedComponent = withAuthenticationRequired(
    () => <>{children}</>,
    {
      onRedirecting: () => <AuthenticationLoading />,
      returnTo: window.location.pathname,
    }
  );

  return <ProtectedComponent />;
};

export default ProtectedRoute; 