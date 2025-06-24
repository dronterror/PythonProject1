import { createContext, useContext, ReactNode, useState } from 'react';

// Mock Auth0 user for demo mode
const mockUser = {
  sub: 'demo-user-123',
  email: 'demo@medlog.app',
  name: 'Demo User',
  picture: undefined,
};

const MockAuth0Context = createContext<any>(null);

export const MockAuth0Provider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);

  // Mock Auth0 context value with state
  const mockAuth0Value = {
    user: user,
    isAuthenticated: isAuthenticated,
    isLoading: false,
    error: null,
    loginWithRedirect: () => {
      // Simulate login for demo
      setUser(mockUser);
      setIsAuthenticated(true);
      return Promise.resolve();
    },
    logout: () => {
      setUser(null);
      setIsAuthenticated(false);
    },
    getAccessTokenSilently: () => Promise.resolve('mock-token'),
    getIdTokenClaims: () => Promise.resolve({}),
    handleRedirectCallback: () => Promise.resolve({ appState: {} }),
  };

  return (
    <MockAuth0Context.Provider value={mockAuth0Value}>
      {children}
    </MockAuth0Context.Provider>
  );
};

export const useMockAuth0 = () => {
  return useContext(MockAuth0Context);
}; 