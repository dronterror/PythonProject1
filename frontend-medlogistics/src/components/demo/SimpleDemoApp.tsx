import { useState } from 'react';
import { Box, Button, Typography, Container, Card, CardContent } from '@mui/material';
import { styled } from '@mui/material/styles';
import RoleSelector from '@/components/RoleSelector';

import { useAppStore } from '@/stores/useAppStore';
import type { UserProfile } from '@/types';

const WelcomeCard = styled(Card)(({ theme }) => ({
  textAlign: 'center',
  padding: theme.spacing(4),
  marginBottom: theme.spacing(3),
  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
  color: theme.palette.primary.contrastText,
}));

const SimpleDemoApp = () => {
  const [currentView, setCurrentView] = useState<'login' | 'roles' | 'ward' | 'dashboard'>('login');
  const { setSession, setSelectedRole, setActiveWard } = useAppStore();

  const handleDemoStart = () => {
    console.warn('🚀 Simple Demo Mode activated!');
    
    // Create demo user profile
    const demoProfile: UserProfile = {
      sub: 'demo-user-123',
      email: 'demo@medlog.app',
      name: 'Demo User',
      picture: undefined,
      role: 'nurse',
      nurseId: 'demo-user-123',
    };

    // Set session in store
    setSession(demoProfile);
    
    console.warn('Demo session set, moving to role selection');
    setCurrentView('roles');
  };

  const handleRoleSelect = (role: string) => {
    console.warn('Role selected:', role);
    setSelectedRole(role);
    setCurrentView('ward');
  };

  const handleWardSelect = (wardId: string, wardName: string) => {
    console.warn('Ward selected:', wardId, wardName);
    setActiveWard(wardId, wardName);
    setCurrentView('dashboard');
  };

  if (currentView === 'login') {
    return (
      <Container maxWidth="sm" sx={{ mt: 8 }}>
        <WelcomeCard>
          <CardContent>
            <Typography variant="h3" gutterBottom>
              🏥 MedLogistics
            </Typography>
            <Typography variant="h5" gutterBottom>
              Demo Mode
            </Typography>
            <Typography variant="body1" paragraph>
              Experience the complete medication management system
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={handleDemoStart}
              sx={{
                mt: 2,
                backgroundColor: '#4caf50',
                '&:hover': { backgroundColor: '#388e3c' },
                fontSize: '1.2rem',
                fontWeight: 'bold',
                px: 4,
                py: 2,
              }}
            >
              ✅ Start Demo
            </Button>
          </CardContent>
        </WelcomeCard>
      </Container>
    );
  }

  if (currentView === 'roles') {
    return <RoleSelector onRoleSelect={handleRoleSelect} />;
  }

  if (currentView === 'ward') {
    return (
      <Box>
        <Typography variant="h4" sx={{ p: 3, textAlign: 'center' }}>
          Select Your Ward
        </Typography>
        <Container maxWidth="sm">
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Button
                fullWidth
                variant="contained"
                onClick={() => handleWardSelect('ward-1', 'General Medicine')}
                sx={{ mb: 1 }}
              >
                🏥 General Medicine Ward
              </Button>
              <Button
                fullWidth
                variant="contained"
                onClick={() => handleWardSelect('ward-2', 'Emergency')}
                sx={{ mb: 1 }}
              >
                🚨 Emergency Ward
              </Button>
              <Button
                fullWidth
                variant="contained"
                onClick={() => handleWardSelect('ward-3', 'Pediatrics')}
              >
                👶 Pediatrics Ward
              </Button>
            </CardContent>
          </Card>
        </Container>
      </Box>
    );
  }

  // Dashboard view
  return (
    <Box>
      <Typography variant="h4" sx={{ p: 3, textAlign: 'center', backgroundColor: 'primary.main', color: 'white' }}>
        🏥 MedLogistics Dashboard - Demo Mode
      </Typography>
      <Container maxWidth="lg" sx={{ mt: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Welcome to the Demo!
            </Typography>
            <Typography variant="body1" paragraph>
              This is a simplified demo of the MedLogistics system. In the full version, you would see:
            </Typography>
            <Box component="ul" sx={{ ml: 2 }}>
              <li>Patient medication schedules</li>
              <li>Medication administration records</li>
              <li>Drug inventory management</li>
              <li>Real-time notifications</li>
              <li>Comprehensive reporting</li>
            </Box>
            <Button
              variant="contained"
              onClick={() => {
                setCurrentView('login');
                // Clear demo data
                const { clearSession } = useAppStore.getState();
                clearSession();
              }}
              sx={{ mt: 2 }}
            >
              🔄 Reset Demo
            </Button>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default SimpleDemoApp; 