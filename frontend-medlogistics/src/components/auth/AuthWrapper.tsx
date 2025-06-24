import { ReactNode } from 'react';
import { Auth0Provider } from '@auth0/auth0-react';
import { MockAuth0Provider } from './MockAuth0Context';

interface AuthWrapperProps {
  children: ReactNode;
  auth0Config: any;
  hasValidAuth0Config: boolean;
}

const AuthWrapper = ({ children, auth0Config, hasValidAuth0Config }: AuthWrapperProps) => {
  if (hasValidAuth0Config) {
    // Use real Auth0 provider when valid config is available
    return (
      <Auth0Provider {...auth0Config}>
        {children}
      </Auth0Provider>
    );
  }

  // Use mock provider for demo mode
  return (
    <MockAuth0Provider>
      {children}
    </MockAuth0Provider>
  );
};

export default AuthWrapper; 