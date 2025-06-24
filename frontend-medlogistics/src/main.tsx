import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import AuthWrapper from './components/auth/AuthWrapper';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import App from './App.tsx';
import { theme } from './theme';
import ErrorBoundary from './components/ErrorBoundary';

// Create QueryClient with optimized settings for mobile
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes (formerly cacheTime)
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Auth0 configuration - only used if proper credentials are provided
const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN || 'localhost',
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID || 'demo-client-id',
  authorizationParams: {
    redirect_uri: window.location.origin,
    audience: import.meta.env.VITE_AUTH0_AUDIENCE || 'https://api.medlog.app',
  },
  useRefreshTokens: true,
  cacheLocation: 'localstorage' as const,
};

// Check if we have valid Auth0 configuration
const hasValidAuth0Config = Boolean(
  import.meta.env.VITE_AUTH0_DOMAIN && 
  import.meta.env.VITE_AUTH0_DOMAIN !== 'your-auth0-domain.auth0.com' &&
  import.meta.env.VITE_AUTH0_CLIENT_ID &&
  import.meta.env.VITE_AUTH0_CLIENT_ID !== 'your-auth0-client-id'
);

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <AuthWrapper auth0Config={auth0Config} hasValidAuth0Config={hasValidAuth0Config}>
          <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <App />
              {/* {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />} */}
            </ThemeProvider>
          </QueryClientProvider>
        </AuthWrapper>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
); 