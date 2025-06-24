import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { 
  Box, 
  Typography, 
  Avatar, 
  Card, 
  CardContent,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import { Person, Email, Badge } from '@mui/icons-material';

const Profile: React.FC = () => {
  const { user, isLoading, error } = useAuth0();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load profile: {error.message}
      </Alert>
    );
  }

  if (!user) {
    return (
      <Alert severity="warning">
        No user information available
      </Alert>
    );
  }

  const userRoles = user['https://api.medlogistics.com/roles'] || [];

  return (
    <Card sx={{ maxWidth: 500, mx: 'auto', mt: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={3}>
          <Avatar 
            src={user.picture} 
            alt={user.name}
            sx={{ width: 80, height: 80, mr: 2 }}
          >
            <Person />
          </Avatar>
          <Box>
            <Typography variant="h5" component="h2" gutterBottom>
              {user.name || 'Unknown User'}
            </Typography>
            <Typography variant="body1" color="text.secondary" display="flex" alignItems="center">
              <Email sx={{ mr: 1, fontSize: 18 }} />
              {user.email}
            </Typography>
          </Box>
        </Box>

        <Box mb={2}>
          <Typography variant="h6" gutterBottom display="flex" alignItems="center">
            <Badge sx={{ mr: 1 }} />
            Roles
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {userRoles.length > 0 ? (
              userRoles.map((role: string) => (
                <Chip 
                  key={role} 
                  label={role} 
                  variant="outlined" 
                  color="primary"
                  size="small"
                />
              ))
            ) : (
              <Typography variant="body2" color="text.secondary">
                No roles assigned
              </Typography>
            )}
          </Box>
        </Box>

        <Box>
          <Typography variant="body2" color="text.secondary">
            <strong>User ID:</strong> {user.sub}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Last Updated:</strong> {new Date(user.updated_at || '').toLocaleString()}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default Profile; 