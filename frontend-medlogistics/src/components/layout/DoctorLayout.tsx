import React from 'react';
import { BottomNavigation, BottomNavigationAction, Paper, Box } from '@mui/material';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { ListAlt, Create } from '@mui/icons-material';
import AppHeader from './AppHeader';

const DoctorLayout: React.FC = () => {
  const location = useLocation();

  const getRouteInfo = () => {
    if (location.pathname.startsWith('/app/prescribe')) {
      return { value: '/app/prescribe', title: 'Prescribe Medication' };
    }
    if (location.pathname.startsWith('/app/my-orders')) {
      return { value: '/app/my-orders', title: 'My Orders' };
    }
    // Default route info
    return { value: '/app/my-orders', title: 'My Orders' };
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
            to="/app/my-orders"
            label="My Orders"
            value="/app/my-orders"
            icon={<ListAlt />}
          />
          <BottomNavigationAction
            component={Link}
            to="/app/prescribe"
            label="Prescribe"
            value="/app/prescribe"
            icon={<Create />}
          />
        </BottomNavigation>
      </Paper>
    </Box>
  );
};

export default DoctorLayout; 