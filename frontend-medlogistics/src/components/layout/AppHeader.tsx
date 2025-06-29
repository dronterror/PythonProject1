import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Chip, Tooltip } from '@mui/material';
import { ArrowBack, Logout } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useKeycloakAuth } from '@/components/auth/KeycloakAuthContext';
import { useActiveWard, useAppStore } from '@/stores/useAppStore';

interface AppHeaderProps {
  title: string;
}

const AppHeader: React.FC<AppHeaderProps> = ({ title }) => {
  const navigate = useNavigate();
  const { logout } = useKeycloakAuth();
  const activeWard = useActiveWard();
  const { clearSession } = useAppStore();

  const handleGoToWardSelection = () => {
    // We only clear the active ward, not the whole session
    useAppStore.setState({ activeWard: null });
    navigate('/select-ward');
  };

  const handleLogout = () => {
    logout();
    clearSession(); // Ensure all app state is cleared on logout
  };

  return (
    <AppBar position="sticky" color="primary">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {title}
        </Typography>

        {activeWard && (
          <Tooltip title="Change Ward">
            <Chip
              icon={<ArrowBack />}
              label={activeWard.name}
              onClick={handleGoToWardSelection}
              color="secondary"
              sx={{ mr: 2, cursor: 'pointer' }}
            />
          </Tooltip>
        )}

        <Tooltip title="Logout">
          <IconButton color="inherit" onClick={handleLogout}>
            <Logout />
          </IconButton>
        </Tooltip>
      </Toolbar>
    </AppBar>
  );
};

export default AppHeader; 