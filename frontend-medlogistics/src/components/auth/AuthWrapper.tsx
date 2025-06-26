import { ReactNode } from 'react';
import { KeycloakAuthProvider } from './KeycloakAuthContext';

interface AuthWrapperProps {
  children: ReactNode;
}

const AuthWrapper = ({ children }: AuthWrapperProps) => {
  // Always use Keycloak provider
  return (
    <KeycloakAuthProvider>
      {children}
    </KeycloakAuthProvider>
  );
};

export default AuthWrapper; 