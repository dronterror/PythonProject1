import React from 'react';
import ReactDOM from 'react-dom/client';
import { HashRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { KeycloakAuthProvider } from '@/components/auth/KeycloakAuthContext';
import App from './App';
import { theme } from './theme';

// Create a client
const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <KeycloakAuthProvider>
          <HashRouter>
            <App />
          </HashRouter>
        </KeycloakAuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </React.StrictMode>
); 