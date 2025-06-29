import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Database Configuration
    database_url: str = "postgresql://valmed:valmedpass@localhost:5432/valmed"
    
    # Keycloak OIDC Configuration
    keycloak_server_url: str = "http://keycloak:8080"  # Use Docker service name for internal communication
    keycloak_realm: str = "medlog-realm"
    keycloak_client_id: str = "medlog-clients"
    
    # Application Settings
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Security Settings
    secret_key: str = "your-secret-key-change-me-in-production"
    algorithm: str = "HS256"
    
    # Legacy Auth0 Settings (deprecated, for backward compatibility during migration)
    auth0_domain: Optional[str] = None
    auth0_api_audience: Optional[str] = None
    auth0_algorithm: str = "RS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    @property
    def keycloak_openid_connect_url(self) -> str:
        """Construct the OpenID Connect discovery URL for Keycloak."""
        return f"{self.keycloak_server_url}/realms/{self.keycloak_realm}/.well-known/openid_configuration"
    
    @property
    def keycloak_jwks_url(self) -> str:
        """Construct the JWKS URL for Keycloak."""
        return f"{self.keycloak_server_url}/realms/{self.keycloak_realm}/protocol/openid-connect/certs"
    
    @property
    def keycloak_issuer(self) -> str:
        """Construct the issuer URL for Keycloak."""
        # Use the external URL for issuer validation since that's what tokens contain
        return f"https://keycloak.medlog.local/realms/{self.keycloak_realm}"


# Create a global settings instance
settings = Settings() 