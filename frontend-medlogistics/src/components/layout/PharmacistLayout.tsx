import React from 'react';
import { BottomNavigation, BottomNavigationAction, Paper, Box } from '@mui/material';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Inventory, NotificationsActive } from '@mui/icons-material';
import AppHeader from './AppHeader';

const PharmacistLayout: React.FC = () => {
  const location = useLocation();

  const getRouteInfo = () => {
    if (location.pathname.startsWith('/app/inventory')) {
      return { value: '/app/inventory', title: 'Ward Inventory' };
    }
    if (location.pathname.startsWith('/app/alerts')) {
      return { value: '/app/alerts', title: 'Low Stock Alerts' };
    }
    // Default route info
    return { value: '/app/inventory', title: 'Ward Inventory' };
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
            to="/app/inventory"
            label="Inventory"
            value="/app/inventory"
            icon={<Inventory />}
          />
          <BottomNavigationAction
            component={Link}
            to="/app/alerts"
            label="Alerts"
            value="/app/alerts"
            icon={<NotificationsActive />}
          />
        </BottomNavigation>
      </Paper>
    </Box>
  );
};

export default PharmacistLayout; 