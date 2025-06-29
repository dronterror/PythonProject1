import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Keycloak Configuration
const getKeycloakUrl = () => {
  const url = import.meta.env.VITE_KEYCLOAK_URL;
  if (!url) {
    console.error("VITE_KEYCLOAK_URL is not set. Please check your .env file.");
    // Fallback for safety, but this should be configured.
    return 'http://localhost:8081';
  }
  return url;
};

const KEYCLOAK_CONFIG = {
  url: getKeycloakUrl(),
  realm: 'medflow-realm',
  clientId: 'medflow-backend',
};

// Add debug logging - FORCE UPDATE
console.log('Keycloak Config (UPDATED):', KEYCLOAK_CONFIG);

// Types
interface User {
  id: string;
  email: string;
  name?: string;
  roles: string[];
  sub: string;
}

interface AuthContextType {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  getAccessToken: () => string | null;
  hasRole: (role: string) => boolean;
  error: string | null;
}

// Create Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth Provider Component
export const KeycloakAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('keycloak_token');
    if (storedToken) {
      try {
        const userData = parseJWT(storedToken);
        if (userData && !isTokenExpired(storedToken)) {
          setToken(storedToken);
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          // Token expired, clear it
          localStorage.removeItem('keycloak_token');
        }
      } catch (err) {
        console.error('Error parsing stored token:', err);
        localStorage.removeItem('keycloak_token');
      }
    }
    setIsLoading(false);
  }, []);

  // Parse JWT token to extract user data
  const parseJWT = (token: string): User | null => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        id: payload.sub,
        sub: payload.sub,
        email: payload.email || payload.preferred_username || 'unknown@example.com',
        name: payload.name || payload.preferred_username || 'Unknown User',
        roles: payload.realm_access?.roles || [],
      };
    } catch (error) {
      console.error('Error parsing JWT:', error);
      return null;
    }
  };

  // Check if token is expired
  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp < currentTime;
    } catch {
      return true;
    }
  };

  // Login function with improved error handling
  const login = async (username: string, password: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const tokenUrl = `${KEYCLOAK_CONFIG.url}/realms/${KEYCLOAK_CONFIG.realm}/protocol/openid-connect/token`;
      
      console.log('Attempting login to:', tokenUrl);
      
      const response = await fetch(tokenUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          client_id: KEYCLOAK_CONFIG.clientId,
          username,
          password,
          grant_type: 'password',
        }),
      });

      console.log('Login response status:', response.status);

      if (!response.ok) {
        let errorMessage = 'Login failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.error_description || errorData.error || 'Login failed';
        } catch (e) {
          // If we can't parse error response, check status
          if (response.status === 401) {
            errorMessage = 'Invalid username or password';
          } else if (response.status >= 500) {
            errorMessage = 'Keycloak server error. Please try again later.';
          } else if (response.status === 404) {
            errorMessage = 'Keycloak server not found. Please check your configuration.';
          } else {
            errorMessage = `Login failed with status: ${response.status}`;
          }
        }
        throw new Error(errorMessage);
      }

      const tokenData = await response.json();
      const accessToken = tokenData.access_token;

      if (!accessToken) {
        throw new Error('No access token received from Keycloak');
      }

      // Parse user data from token
      const userData = parseJWT(accessToken);
      if (!userData) {
        throw new Error('Invalid token received');
      }

      console.log('Login successful for user:', userData.email);

      // Store token and update state
      localStorage.setItem('keycloak_token', accessToken);
      setToken(accessToken);
      setUser(userData);
      setIsAuthenticated(true);
      
    } catch (err) {
      console.error('Login error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('keycloak_token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  };

  // Get access token
  const getAccessToken = (): string | null => {
    if (token && !isTokenExpired(token)) {
      return token;
    }
    return null;
  };

  // Check if user has specific role
  const hasRole = (role: string): boolean => {
    return user?.roles.includes(role) || false;
  };

  const value: AuthContextType = {
    isLoading,
    isAuthenticated,
    user,
    token,
    login,
    logout,
    getAccessToken,
    hasRole,
    error,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useKeycloakAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useKeycloakAuth must be used within a KeycloakAuthProvider');
  }
  return context;
};

// Compatibility hook for existing Auth0 code
export const useAuth0 = () => {
  const keycloakAuth = useKeycloakAuth();
  
  return {
    isLoading: keycloakAuth.isLoading,
    isAuthenticated: keycloakAuth.isAuthenticated,
    user: keycloakAuth.user,
    getAccessTokenSilently: async () => keycloakAuth.getAccessToken() || '',
    loginWithRedirect: () => {
      // This will be handled by a custom login component
      console.log('Login redirect - use custom login form');
    },
    logout: keycloakAuth.logout,
  };
}; 