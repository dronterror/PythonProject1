import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Button, CircularProgress } from '@mui/material';
import { Login } from '@mui/icons-material';

const LoginButton: React.FC = () => {
  const { loginWithRedirect, isLoading } = useAuth0();

  return (
    <Button
      variant="contained"
      color="primary"
      size="large"
      startIcon={isLoading ? <CircularProgress size={20} /> : <Login />}
      onClick={() => loginWithRedirect()}
      disabled={isLoading}
      sx={{ 
        minWidth: 200,
        height: 50,
        fontSize: '1.1rem',
        fontWeight: 600
      }}
    >
      {isLoading ? 'Signing in...' : 'Sign In'}
    </Button>
  );
};

export default LoginButton; 