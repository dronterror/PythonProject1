import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  TextField,
  Alert,
  Chip,
} from '@mui/material';
import { useKeycloakAuth } from './KeycloakAuthContext';

const TokenManager: React.FC = () => {
  const [customToken, setCustomToken] = useState<string>('');
  const { token, user, logout, isAuthenticated } = useKeycloakAuth();

  const handleSetCustomToken = () => {
    if (customToken.trim()) {
      localStorage.setItem('keycloak_token', customToken.trim());
      setCustomToken('');
      window.location.reload(); // Refresh to load new token
    }
  };

  const handleClearToken = () => {
    logout();
  };

  const getTokenInfo = () => {
    if (!token) return null;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        email: payload.email || payload.preferred_username || 'Unknown',
        roles: payload.realm_access?.roles || [],
        exp: new Date(payload.exp * 1000).toLocaleString(),
        iss: payload.iss,
        sub: payload.sub,
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
          Keycloak Token Manager (Development)
        </Typography>
        
        <Alert severity="info" sx={{ mb: 2 }}>
          Current authentication uses Keycloak with JWT tokens
        </Alert>

        {/* Current Token Status */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Current Authentication Status:
          </Typography>
          {isAuthenticated && user ? (
            <Box>
              <Chip 
                label={`Authenticated: ${user.email} (${user.roles.join(', ')})`} 
                color="success" 
                sx={{ mb: 1 }}
              />
              {tokenInfo?.exp && (
                <Typography variant="caption" display="block">
                  Token Expires: {tokenInfo.exp}
                </Typography>
              )}
              {tokenInfo?.iss && (
                <Typography variant="caption" display="block">
                  Issuer: {tokenInfo.iss}
                </Typography>
              )}
            </Box>
          ) : (
            <Chip label="Not Authenticated" color="error" />
          )}
        </Box>

        {/* Token Details */}
        {tokenInfo && !tokenInfo.error && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Token Details:
            </Typography>
            <Typography variant="caption" display="block">
              Subject: {tokenInfo.sub}
            </Typography>
            <Typography variant="caption" display="block">
              Roles: {tokenInfo.roles.join(', ') || 'None'}
            </Typography>
          </Box>
        )}

        {/* Custom Token Input */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Set Custom Keycloak Token:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="Paste Keycloak JWT token here..."
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
          <Typography variant="caption" color="text.secondary">
            Get tokens from Keycloak at: http://keycloak.medlog.local
          </Typography>
        </Box>

        {/* Logout Button */}
        {isAuthenticated && (
          <Button 
            variant="outlined" 
            color="error" 
            onClick={handleClearToken}
            size="small"
          >
            Logout
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

export default TokenManager; 