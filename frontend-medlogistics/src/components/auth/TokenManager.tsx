import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Chip,
} from '@mui/material';
import { setAuthToken } from '@/lib/apiClient';

// Fresh JWT tokens from the real backend (2-hour expiration)
const TEST_TOKENS = {
  doctor: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoMHw4MmYzYzI4NDdjNmM0ZDdiOWY3OGNjY2UiLCJlbWFpbCI6ImRvY3RvcjFAdmFsbWVkLmNvbSIsInJvbGUiOiJkb2N0b3IiLCJpYXQiOjE3NTA3OTgwNDMsImlzcyI6Imh0dHBzOi8vZGV2LW1lZGxvZy10ZXN0LnVzLmF1dGgwLmNvbS8iLCJhdWQiOiJodHRwczovL2FwaS5tZWRsb2cuYXBwIiwiZXhwIjoxNzUwODA1MjQzfQ.mtVbZOElSt3uiUbqxR9vL0HJxL2T55JQD0q81Tj6qpk',
  nurse: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoMHxlNTNhOTk0ZDNiMzg0ZTQ2ODUzOGNjZjUiLCJlbWFpbCI6Im51cnNlMkB2YWxtZWQuY29tIiwicm9sZSI6Im51cnNlIiwiaWF0IjoxNzUwNzk4MDQzLCJpc3MiOiJodHRwczovL2Rldi1tZWRsb2ctdGVzdC51cy5hdXRoMC5jb20vIiwiYXVkIjoiaHR0cHM6Ly9hcGkubWVkbG9nLmFwcCIsImV4cCI6MTc1MDgwNTI0M30.3hPgu-I8REPR1Ad8wb0BNcBq788SE70Zq0qyEOxlxWk',
  pharmacist: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoMHwwN2Y0NWQ5MTgxYzY0NmVjYTI2Zjc1NTkiLCJlbWFpbCI6InBoYXJtYWNpc3QxQHZhbG1lZC5jb20iLCJyb2xlIjoicGhhcm1hY2lzdCIsImlhdCI6MTc1MDc5ODA0MywiaXNzIjoiaHR0cHM6Ly9kZXYtbWVkbG9nLXRlc3QudXMuYXV0aDAuY29tLyIsImF1ZCI6Imh0dHBzOi8vYXBpLm1lZGxvZy5hcHAiLCJleHAiOjE3NTA4MDUyNDN9.d3E-gQ5iHQ8G6Ei7Nd4fDHNh6u4qN0QJJ7DJfgpjU1U',
};

const TokenManager: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState<string>('nurse');
  const [customToken, setCustomToken] = useState<string>('');
  const [currentToken, setCurrentToken] = useState<string>(
    localStorage.getItem('medlog_jwt_token') || ''
  );

  const handleSetTestToken = () => {
    const token = TEST_TOKENS[selectedRole as keyof typeof TEST_TOKENS];
    localStorage.setItem('medlog_jwt_token', token);
    setAuthToken(token);
    setCurrentToken(token);
  };

  const handleSetCustomToken = () => {
    if (customToken.trim()) {
      localStorage.setItem('medlog_jwt_token', customToken.trim());
      setAuthToken(customToken.trim());
      setCurrentToken(customToken.trim());
      setCustomToken('');
    }
  };

  const handleClearToken = () => {
    localStorage.removeItem('medlog_jwt_token');
    localStorage.removeItem('auth0_token');
    setCurrentToken('');
  };

  const getTokenInfo = () => {
    if (!currentToken) return null;
    
    try {
      const payload = JSON.parse(atob(currentToken.split('.')[1]));
      return {
        email: payload.email,
        role: payload.role,
        exp: new Date(payload.exp * 1000).toLocaleString(),
      };
    } catch (error) {
      return { error: 'Invalid token format' };
    }
  };

  const tokenInfo = getTokenInfo();

  return (
    <Card sx={{ m: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          JWT Token Manager (Development)
        </Typography>
        
        <Alert severity="info" sx={{ mb: 2 }}>
          Use this to test the real backend connection with JWT tokens
        </Alert>

        {/* Current Token Status */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Current Token Status:
          </Typography>
          {currentToken ? (
            <Box>
              <Chip 
                label={`Active: ${tokenInfo?.email || 'Unknown'} (${tokenInfo?.role || 'Unknown'})`} 
                color="success" 
                sx={{ mb: 1 }}
              />
              {tokenInfo?.exp && (
                <Typography variant="caption" display="block">
                  Expires: {tokenInfo.exp}
                </Typography>
              )}
            </Box>
          ) : (
            <Chip label="No Token Set" color="error" />
          )}
        </Box>

        {/* Test Token Selection */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Set Test Token:
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1 }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Role</InputLabel>
              <Select
                value={selectedRole}
                label="Role"
                onChange={(e) => setSelectedRole(e.target.value)}
              >
                <MenuItem value="nurse">Nurse</MenuItem>
                <MenuItem value="doctor">Doctor</MenuItem>
                <MenuItem value="pharmacist">Pharmacist</MenuItem>
              </Select>
            </FormControl>
            <Button 
              variant="contained" 
              onClick={handleSetTestToken}
              size="small"
            >
              Set {selectedRole} Token
            </Button>
          </Box>
        </Box>

        {/* Custom Token Input */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Set Custom Token:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="Paste JWT token here..."
              value={customToken}
              onChange={(e) => setCustomToken(e.target.value)}
              multiline
              rows={2}
            />
            <Button 
              variant="outlined" 
              onClick={handleSetCustomToken}
              disabled={!customToken.trim()}
              size="small"
            >
              Set Token
            </Button>
          </Box>
        </Box>

        {/* Clear Token */}
        <Button 
          variant="outlined" 
          color="error" 
          onClick={handleClearToken}
          size="small"
        >
          Clear All Tokens
        </Button>
      </CardContent>
    </Card>
  );
};

export default TokenManager; 