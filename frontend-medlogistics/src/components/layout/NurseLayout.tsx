import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  BottomNavigation,
  BottomNavigationAction,
  Paper,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PatientsIcon,
  Medication as MedicationIcon,
  Person as ProfileIcon,
  Notifications as NotificationsIcon,
  MoreVert as MoreIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useAuth0 } from '@auth0/auth0-react';
import { styled } from '@mui/material/styles';
import { useAppStore, useActiveWard, useUserProfile } from '@/stores/useAppStore';

const LayoutContainer = styled(Box)({
  display: 'flex',
  flexDirection: 'column',
  minHeight: '100vh',
});

const MainContent = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  paddingTop: theme.spacing(1),
  paddingBottom: theme.spacing(10), // Space for bottom navigation
  backgroundColor: theme.palette.background.default,
  minHeight: 'calc(100vh - 56px - 70px)', // AppBar height - BottomNav height
}));

const StyledBottomNavigation = styled(BottomNavigation)(({ theme }) => ({
  position: 'fixed',
  bottom: 0,
  left: 0,
  right: 0,
  zIndex: theme.zIndex.appBar,
  borderTop: `1px solid ${theme.palette.divider}`,
}));

const WardChip = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.secondary.main,
  color: theme.palette.secondary.contrastText,
  padding: theme.spacing(0.5, 1),
  borderRadius: theme.spacing(1),
  fontSize: '0.75rem',
  fontWeight: 500,
}));

interface NavigationItem {
  label: string;
  value: string;
  icon: React.ReactElement;
  path: string;
}

const navigationItems: NavigationItem[] = [
  {
    label: 'Dashboard',
    value: 'dashboard',
    icon: <DashboardIcon />,
    path: '/app/dashboard',
  },
  {
    label: 'Patients',
    value: 'patients', 
    icon: <PatientsIcon />,
    path: '/app/patients',
  },
  {
    label: 'Medications',
    value: 'medications',
    icon: <MedicationIcon />,
    path: '/app/medications',
  },
  {
    label: 'Profile',
    value: 'profile',
    icon: <ProfileIcon />,
    path: '/app/profile',
  },
];

const NurseLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth0();
  const { wardName } = useActiveWard();
  const userProfile = useUserProfile();
  const { clearSession } = useAppStore();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationCount] = useState(3); // This would come from a notifications store

  // Get current navigation value based on pathname
  const getCurrentNavValue = () => {
    const path = location.pathname;
    const currentItem = navigationItems.find(item => path.startsWith(item.path));
    return currentItem?.value || 'dashboard';
  };

  const handleNavigationChange = (_event: React.SyntheticEvent, newValue: string) => {
    const item = navigationItems.find(nav => nav.value === newValue);
    if (item) {
      navigate(item.path);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    clearSession();
    logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
    handleMenuClose();
  };

  const handleSettings = () => {
    navigate('/app/settings');
    handleMenuClose();
  };

  return (
    <LayoutContainer>
      {/* Top App Bar */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
            <Typography variant="h6" component="div" sx={{ mr: 2 }}>
              MedLog Nurse
            </Typography>
            {wardName && (
              <WardChip>
                {wardName}
              </WardChip>
            )}
          </Box>

          {/* Notifications */}
          <IconButton
            color="inherit"
            onClick={() => navigate('/app/notifications')}
            sx={{ mr: 1 }}
          >
            <Badge badgeContent={notificationCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* Profile Menu */}
          <IconButton
            color="inherit"
            onClick={handleMenuOpen}
            sx={{ p: 0 }}
          >
            {user?.picture ? (
              <Avatar
                src={user.picture}
                alt={user.name}
                sx={{ width: 32, height: 32 }}
              />
            ) : (
              <MoreIcon />
            )}
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem disabled>
              <ListItemText
                primary={user?.name || userProfile?.name}
                secondary={userProfile?.role || 'Nurse'}
              />
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleSettings}>
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Settings</ListItemText>
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Logout</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Main Content Area */}
      <MainContent>
        <Outlet />
      </MainContent>

      {/* Bottom Navigation */}
      <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
        <StyledBottomNavigation
          value={getCurrentNavValue()}
          onChange={handleNavigationChange}
          showLabels
        >
          {navigationItems.map((item) => (
            <BottomNavigationAction
              key={item.value}
              label={item.label}
              value={item.value}
              icon={item.icon}
            />
          ))}
        </StyledBottomNavigation>
      </Paper>
    </LayoutContainer>
  );
};

export default NurseLayout; 