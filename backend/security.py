import os
import json
import requests
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status, Depends
from functools import lru_cache
import logging
from config import settings
from fastapi.security import OAuth2AuthorizationCodeBearer, OpenIdConnect
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from pydantic import ValidationError

logger = logging.getLogger(__name__)

def get_keycloak_public_key() -> dict:
    """
    Fetch the public key from Keycloak JWKS endpoint.
    """
    try:
        # Use the configured JWKS URL from settings
        jwks_url = settings.keycloak_jwks_url
        logger.debug(f"Attempting to fetch JWKS from: {jwks_url}")
        
        # For development, we may need to skip SSL verification
        verify_ssl = not settings.debug
        response = requests.get(jwks_url, timeout=10, verify=verify_ssl)
        response.raise_for_status()
        jwks = response.json()
        
        # Return the JWKS data instead of a single key
        # We'll select the right key based on the token's kid later
        if jwks.get("keys"):
            return jwks
        else:
            raise Exception("No keys found in JWKS response")
            
    except requests.RequestException as e:
        logger.error(f"Failed to fetch JWKS from Keycloak: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify authentication tokens - Keycloak unavailable"
        )
    except Exception as e:
        logger.error(f"Failed to process JWKS from Keycloak: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process authentication keys"
        )

def get_keycloak_issuer() -> str:
    """
    Get the issuer from Keycloak OpenID Connect configuration.
    Since the well-known endpoint has issues, use the default issuer.
    """
    # Use the default issuer since OIDC discovery endpoint is not working
    return settings.keycloak_issuer

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a Keycloak JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        The decoded token payload
        
    Raises:
        HTTPException: For invalid, expired, or malformed tokens
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is required"
        )
    
    try:
        # Get the JWKS data
        jwks = get_keycloak_public_key()
        
        # Get the token header to find the key ID
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        # Find the matching key in JWKS
        public_key_data = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                public_key_data = key
                break
        
        if not public_key_data:
            # This case should now be rare since we are not caching,
            # but it's kept for robustness.
            logger.error(f"No matching key found for kid: {kid}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key. Could not find a matching public key."
            )
        
        # Get the issuer
        issuer = get_keycloak_issuer()
        
        # Verify and decode the token using JWKS
        # For python-jose, we need to pass the JWKS as the key parameter
        payload = jwt.decode(
            token,
            jwks,  # Pass the entire JWKS, jose will find the right key by kid
            algorithms=["RS256"],
            audience=None,  # Skip audience verification
            issuer=issuer,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": False,  # Skip audience verification, check azp instead
                "verify_iss": True
            }
        )
        
        # Manually verify the authorized party (client ID)
        azp = payload.get("azp")
        if azp != settings.keycloak_client_id:
            logger.warning(f"Invalid authorized party: {azp}, expected: {settings.keycloak_client_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client"
            )
        
        return payload
        
    except HTTPException:
        raise # Re-raise custom HTTPExceptions
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTClaimsError as e:
        logger.warning(f"Invalid token claims (e.g., issuer or audience): {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )
    except JWTError as e:
        logger.warning(f"Invalid token signature or structure: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}, type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed",
        )

def extract_user_roles(payload: Dict[str, Any]) -> List[str]:
    """
    Extract user roles from the Keycloak token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        List of user roles
    """
    # Keycloak stores realm roles in realm_access.roles
    realm_access = payload.get("realm_access", {})
    roles = realm_access.get("roles", [])
    
    # Filter out Keycloak default roles to only return application roles
    app_roles = [role for role in roles if role in ["super-admin", "pharmacist", "doctor", "nurse"]]
    
    return app_roles

def get_keycloak_user_id(payload: Dict[str, Any]) -> str:
    """
    Extract the Keycloak user ID from the token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        Keycloak user ID (sub claim)
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    return user_id

def get_user_email(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extract the user email from the token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        User email if available
    """
    return payload.get("email")

def get_user_preferred_username(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extract the preferred username from the token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        Preferred username if available
    """
    return payload.get("preferred_username")

def get_jwks():
    """
    Retrieves the JSON Web Key Set (JWKS) from the OIDC provider.
    The keys are cached to avoid fetching them for every request.
    """
    # ... existing code ... 