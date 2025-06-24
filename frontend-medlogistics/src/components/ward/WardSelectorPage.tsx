import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Alert,
  Container,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import {
  LocalHospital as WardIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useAuth0 } from '@auth0/auth0-react';
import { styled } from '@mui/material/styles';
import { useQuery } from '@tanstack/react-query';
import { useAppStore } from '@/stores/useAppStore';
import { api } from '@/lib/apiClient';
// import type { Ward } from '@/types';

const StyledContainer = styled(Container)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.default,
  paddingTop: theme.spacing(2),
  paddingBottom: theme.spacing(2),
}));

const WelcomeCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
  color: theme.palette.primary.contrastText,
}));

const WardCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  '&:hover': {
    boxShadow: theme.shadows[4],
    transform: 'translateY(-2px)',
    transition: 'all 0.2s ease-in-out',
  },
}));

const WardSelectorPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth0();
  const { setActiveWard, userProfile } = useAppStore();

  // Fetch available wards
  const {
    data: wards,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['wards'],
    queryFn: () => api.getWards(),
    retry: 3,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const handleWardSelection = async (ward: any) => {
    try {
      // Set the active ward in the store
      setActiveWard(ward.id, ward.name);
      
      // Navigate to the main dashboard
      navigate('/app/dashboard');
    } catch (error) {
      console.error('Error selecting ward:', error);
    }
  };

  const handleLogout = () => {
    logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
  };

  if (isLoading) {
    return (
      <StyledContainer maxWidth="sm">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <Box textAlign="center">
            <CircularProgress size={48} />
            <Typography variant="h6" sx={{ mt: 2 }}>
              Loading wards...
            </Typography>
          </Box>
        </Box>
      </StyledContainer>
    );
  }

  if (error) {
    return (
      <StyledContainer maxWidth="sm">
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          action={
            <IconButton color="inherit" size="small" onClick={() => refetch()}>
              Retry
            </IconButton>
          }
        >
          Failed to load wards. Please check your connection and try again.
        </Alert>
      </StyledContainer>
    );
  }

  return (
    <>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Select Ward
          </Typography>
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <StyledContainer maxWidth="sm">
        <WelcomeCard>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <PersonIcon sx={{ mr: 2, fontSize: 40 }} />
              <Box>
                <Typography variant="h5" component="h1">
                  Welcome, {user?.name || userProfile?.name}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  {userProfile?.role || 'Nurse'}
                </Typography>
              </Box>
            </Box>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>
              Please select the ward you&apos;ll be working in today
            </Typography>
          </CardContent>
        </WelcomeCard>

        <Typography variant="h6" gutterBottom>
          Available Wards
        </Typography>

        {wards && Array.isArray(wards) && wards.length > 0 ? (
          <List sx={{ p: 0 }}>
            {wards.map((ward) => (
              <WardCard key={ward.id}>
                <ListItem disablePadding>
                  <ListItemButton
                    onClick={() => handleWardSelection(ward)}
                    sx={{ p: 2 }}
                  >
                    <ListItemIcon>
                      <WardIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={ward.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            {ward.description}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Capacity: {ward.currentOccupancy}/{ward.capacity} patients
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItemButton>
                </ListItem>
              </WardCard>
            ))}
          </List>
        ) : (
          <Alert severity="info">
            No wards are currently available. Please contact your administrator.
          </Alert>
        )}
      </StyledContainer>
    </>
  );
};

export default WardSelectorPage; 