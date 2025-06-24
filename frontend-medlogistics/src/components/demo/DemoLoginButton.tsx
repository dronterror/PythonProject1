import { Button, Typography, Box } from '@mui/material';
import { useAppStore } from '@/stores/useAppStore';
import type { UserProfile } from '@/types';

interface DemoLoginButtonProps {
  onSuccess?: () => void;
}

const DemoLoginButton = ({ onSuccess }: DemoLoginButtonProps) => {
  const { setSession } = useAppStore();

  const handleDemoLogin = () => {
    console.warn('🚀 Demo Mode activated!');
    
    // Create demo user profile
    const demoProfile: UserProfile = {
      sub: 'demo-user-123',
      email: 'demo@medlog.app',
      name: 'Demo User',
      picture: undefined,
      role: 'nurse',
      nurseId: 'demo-user-123',
    };

    // Set session directly in store - this bypasses Auth0 completely
    setSession(demoProfile);
    
    console.warn('Demo session set:', demoProfile);
    
    // Verify store state
    const storeState = useAppStore.getState();
    console.warn('Store state after setting:', {
      isAuthenticated: storeState.isAuthenticated,
      userProfile: storeState.userProfile?.email,
    });
    
    // Call success callback if provided
    if (onSuccess) {
      onSuccess();
    }
    
    // Instead of reload, let's navigate directly to avoid reload issues
    window.location.hash = '#demo-login-success';
    
    // Force page refresh to ensure state changes take effect
    setTimeout(() => {
      window.location.reload();
    }, 200);
  };

  return (
    <Box>
      <Button
        variant="contained"
        color="secondary"
        size="large"
        onClick={handleDemoLogin}
        sx={{ 
          mt: 2, 
          minWidth: 250, 
          backgroundColor: '#4caf50', 
          '&:hover': { backgroundColor: '#388e3c' },
          fontSize: '1.1rem',
          fontWeight: 'bold',
          boxShadow: '0 4px 8px rgba(76, 175, 80, 0.3)'
        }}
      >
        ✅ CLICK HERE FOR DEMO MODE
      </Button>
      
      <Typography variant="body2" color="primary" sx={{ mt: 2, fontWeight: 'bold' }}>
        👆 Click the GREEN button above to test the app!
      </Typography>
    </Box>
  );
};

export default DemoLoginButton; 