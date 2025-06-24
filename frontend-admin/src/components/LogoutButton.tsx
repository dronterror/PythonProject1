import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@mui/material';
import { Logout } from '@mui/icons-material';

const LogoutButton: React.FC = () => {
  const { logout } = useAuth0();

  return (
    <Button
      variant="outlined"
      color="primary"
      startIcon={<Logout />}
      onClick={() => logout({ 
        logoutParams: { 
          returnTo: window.location.origin 
        }
      })}
      sx={{ 
        minWidth: 120,
        fontWeight: 600
      }}
    >
      Sign Out
    </Button>
  );
};

export default LogoutButton; 