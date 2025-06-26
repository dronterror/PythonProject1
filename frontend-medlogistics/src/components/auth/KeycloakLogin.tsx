import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
} from '@mui/material';
import { useKeycloakAuth } from './KeycloakAuthContext';

const KeycloakLogin: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error } = useKeycloakAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (username && password) {
      try {
        await login(username, password);
        // Success - user will be redirected by the parent component
      } catch (err) {
        // Error is handled by the auth context
        console.error('Login failed:', err);
      }
    }
  };

  const handleQuickLogin = (role: 'admin' | 'doctor' | 'nurse' | 'pharmacist') => {
    const credentials = {
      admin: { username: 'admin', password: 'admin' },
      doctor: { username: 'doctor', password: 'doctor' },
      nurse: { username: 'nurse', password: 'nurse' },
      pharmacist: { username: 'pharmacist', password: 'pharmacist' },
    };

    const cred = credentials[role];
    setUsername(cred.username);
    setPassword(cred.password);
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom align="center">
              MedLogistics
            </Typography>
            <Typography variant="h6" gutterBottom align="center" color="text.secondary">
              Sign in to continue
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                margin="normal"
                required
                autoComplete="username"
                autoFocus
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
                required
                autoComplete="current-password"
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={isLoading || !username || !password}
              >
                {isLoading ? <CircularProgress size={24} /> : 'Sign In'}
              </Button>
            </Box>

            {/* Quick Login for Development */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom color="text.secondary">
                Quick Login (Development):
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => handleQuickLogin('admin')}
                  disabled={isLoading}
                >
                  Admin
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => handleQuickLogin('doctor')}
                  disabled={isLoading}
                >
                  Doctor
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => handleQuickLogin('nurse')}
                  disabled={isLoading}
                >
                  Nurse
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => handleQuickLogin('pharmacist')}
                  disabled={isLoading}
                >
                  Pharmacist
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default KeycloakLogin; 