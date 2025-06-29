import React from 'react';
import { BottomNavigation, BottomNavigationAction, Paper, Box } from '@mui/material';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Dashboard, Person } from '@mui/icons-material';
import AppHeader from './AppHeader';

const NurseLayout: React.FC = () => {
  const location = useLocation();

  const getRouteInfo = () => {
    if (location.pathname.startsWith('/app/dashboard')) {
      return { value: '/app/dashboard', title: 'MAR Dashboard' };
    }
    if (location.pathname.startsWith('/app/profile')) {
      return { value: '/app/profile', title: 'My Profile' };
    }
    // Default route info
    return { value: '/app/dashboard', title: 'MAR Dashboard' };
  };

  const { value, title } = getRouteInfo();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <AppHeader title={title} />
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
        <Outlet />
      </Box>
      <Paper sx={{ position: 'sticky', bottom: 0, left: 0, right: 0 }} elevation={3}>
        <BottomNavigation showLabels value={value}>
          <BottomNavigationAction
            component={Link}
            to="/app/dashboard"
            label="Dashboard"
            value="/app/dashboard"
            icon={<Dashboard />}
          />
          <BottomNavigationAction
            component={Link}
            to="/app/profile"
            label="Profile"
            value="/app/profile"
            icon={<Person />}
          />
        </BottomNavigation>
      </Paper>
    </Box>
  );
};

export default NurseLayout; 