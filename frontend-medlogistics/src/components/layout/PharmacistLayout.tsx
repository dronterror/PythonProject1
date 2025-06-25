import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Avatar,
  Divider,
  Badge,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Dashboard as DashboardIcon,
  Inventory as InventoryIcon,
  Warning as AlertsIcon,
  Person as ProfileIcon,
  ExitToApp as LogoutIcon,
  LocalHospital as WardIcon,
} from '@mui/icons-material';
import { useAuth0 } from '@auth0/auth0-react';
import { useAppStore, useActiveWard, useUserProfile } from '@/stores/useAppStore';

const PharmacistLayout: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { logout } = useAuth0();
  const { clearSession } = useAppStore();
  const { wardName } = useActiveWard();
  const userProfile = useUserProfile();

  const navigationItems = [
    {
      label: 'Dashboard',
      path: '/app/dashboard',
      icon: DashboardIcon,
    },
    {
      label: 'Inventory',
      path: '/app/inventory',
      icon: InventoryIcon,
    },
    {
      label: 'Alerts',
      path: '/app/alerts',
      icon: AlertsIcon,
      badge: 0, // Could be populated with low stock count
    },
    {
      label: 'Profile',
      path: '/app/profile',
      icon: ProfileIcon,
    },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };

  const handleLogout = () => {
    clearSession();
    logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
  };

  const handleChangeWard = () => {
    navigate('/select-ward');
  };

  const drawerContent = (
    <Box sx={{ width: 280, height: '100%' }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          MedLogistics
        </Typography>
        {isMobile && (
          <IconButton
            color="inherit"
            onClick={() => setDrawerOpen(false)}
            edge="end"
          >
            <CloseIcon />
          </IconButton>
        )}
      </Toolbar>
      <Divider />
      
      {/* User Info */}
      <Box sx={{ p: 2 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar
            src={userProfile?.picture}
            sx={{ width: 40, height: 40, mr: 2 }}
          >
            {userProfile?.name?.charAt(0)}
          </Avatar>
          <Box>
            <Typography variant="subtitle2" noWrap>
              {userProfile?.name}
            </Typography>
            <Typography variant="body2" color="textSecondary" noWrap>
              Pharmacist
            </Typography>
          </Box>
        </Box>
        
        {/* Active Ward */}
        <Box
          display="flex"
          alignItems="center"
          sx={{
            p: 1,
            bgcolor: 'primary.light',
            borderRadius: 1,
            cursor: 'pointer',
          }}
          onClick={handleChangeWard}
        >
          <WardIcon color="primary" sx={{ mr: 1 }} />
          <Box>
            <Typography variant="body2" color="primary">
              {wardName || 'Select Ward'}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Click to change
            </Typography>
          </Box>
        </Box>
      </Box>
      
      <Divider />
      
      {/* Navigation */}
      <List>
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: theme.palette.primary.light,
                    '&:hover': {
                      backgroundColor: theme.palette.primary.light,
                    },
                  },
                }}
              >
                <ListItemIcon>
                  {item.badge ? (
                    <Badge badgeContent={item.badge} color="error">
                      <Icon color={isActive ? 'primary' : 'inherit'} />
                    </Badge>
                  ) : (
                    <Icon color={isActive ? 'primary' : 'inherit'} />
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary={item.label}
                  primaryTypographyProps={{
                    color: isActive ? 'primary' : 'inherit',
                    fontWeight: isActive ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      
      <Box sx={{ flexGrow: 1 }} />
      
      {/* Logout */}
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText primary="Sign Out" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          ...(isMobile && {
            backgroundColor: theme.palette.primary.main,
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(true)}
            sx={{ mr: 2, ...((!isMobile) && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            MedLogistics - Pharmacy
          </Typography>
          
          {/* Ward indicator in header */}
          {wardName && (
            <Box
              display="flex"
              alignItems="center"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.15)',
                borderRadius: 1,
                px: 2,
                py: 0.5,
                cursor: 'pointer',
              }}
              onClick={handleChangeWard}
            >
              <WardIcon sx={{ mr: 1, fontSize: 20 }} />
              <Typography variant="body2">
                {wardName}
              </Typography>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? drawerOpen : true}
        onClose={() => setDrawerOpen(false)}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
            ...(isMobile && {
              width: '100%',
              maxWidth: 280,
            }),
          },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 0,
          ...((!isMobile) && {
            ml: '280px',
          }),
        }}
      >
        <Toolbar /> {/* Spacer for AppBar */}
        <Outlet />
      </Box>
    </Box>
  );
};

export default PharmacistLayout; 