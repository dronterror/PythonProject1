import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Container,
} from '@mui/material';
import { styled } from '@mui/material/styles';

// Role interface for the roles array
interface Role {
  id: string;
  title: string;
  icon: string;
  description: string;
  color: string;
}

interface RoleSelectorProps {
  onRoleSelect: (roleId: string) => void;
}

const roles: Role[] = [
  {
    id: 'nurse',
    title: 'Nurse',
    icon: '👩‍⚕️',
    description: 'Medication administration and patient care',
    color: '#ffc107',
  },
  {
    id: 'doctor',
    title: 'Doctor',
    icon: '🩺',
    description: 'Prescription management and patient orders',
    color: '#4caf50',
  },
  {
    id: 'pharmacist',
    title: 'Pharmacist',
    icon: '💊',
    description: 'Inventory management and stock alerts',
    color: '#2196f3',
  },
  {
    id: 'super_admin',
    title: 'Super Admin',
    icon: '⚙️',
    description: 'System administration and user management',
    color: '#f44336',
  },
];

const BackgroundContainer = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  padding: theme.spacing(4),
  textAlign: 'center',
}));

const RoleCard = styled(Card)(({ theme }) => ({
  minHeight: 200,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  transition: 'all 0.2s ease-in-out',
  borderRadius: theme.spacing(3),
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: theme.shadows[10],
  },
  position: 'relative',
  overflow: 'visible',
}));

const ColorBar = styled(Box)<{ roleColor: string }>(({ roleColor }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  height: 6,
  backgroundColor: roleColor,
  borderRadius: '24px 24px 0 0',
}));

const RoleSelector = ({ onRoleSelect }: RoleSelectorProps) => {
  return (
    <BackgroundContainer>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h2" component="h1" sx={{ 
          fontWeight: 'bold', 
          color: 'white', 
          mb: 2,
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
        }}>
          🏥 MedLogistics
        </Typography>
        <Typography variant="h4" component="h2" sx={{ 
          fontWeight: 'bold', 
          color: 'white', 
          mb: 1,
          textShadow: '1px 1px 2px rgba(0,0,0,0.3)'
        }}>
          Select Your Role
        </Typography>
        <Typography variant="h6" sx={{ 
          color: 'rgba(255,255,255,0.9)', 
          maxWidth: 400, 
          mx: 'auto' 
        }}>
          Choose your role to access the appropriate medication management interface
        </Typography>
      </Box>

      <Container maxWidth="lg">
        <Grid container spacing={3} justifyContent="center">
          {roles.map((role) => (
            <Grid item xs={12} sm={6} md={3} key={role.id}>
              <RoleCard onClick={() => onRoleSelect(role.id)}>
                <ColorBar roleColor={role.color} />
                <CardContent sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  textAlign: 'center',
                  py: 4
                }}>
                  <Typography variant="h2" component="div" sx={{ mb: 2 }}>
                    {role.icon}
                  </Typography>
                  <Typography variant="h5" component="h3" sx={{ 
                    fontWeight: 'bold', 
                    mb: 1,
                    color: 'text.primary'
                  }}>
                    {role.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {role.description}
                  </Typography>
                  <Typography variant="h5" sx={{ 
                    color: 'primary.main',
                    fontWeight: 'bold'
                  }}>
                    →
                  </Typography>
                </CardContent>
              </RoleCard>
            </Grid>
          ))}
        </Grid>
      </Container>

      <Box sx={{ mt: 6, color: 'rgba(255,255,255,0.8)' }}>
        <Typography variant="body2">
          ValMed Medication Logistics PWA
        </Typography>
        <Typography variant="body2">
          Mobile-first medication management system
        </Typography>
      </Box>
    </BackgroundContainer>
  );
};

export default RoleSelector; 