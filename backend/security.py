import os
import json
import jwt
import requests
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from functools import lru_cache
import logging
from config import settings

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_keycloak_public_key() -> str:
    """
    Fetch the public key from Keycloak JWKS endpoint.
    Cached to avoid repeated requests to Keycloak.
    """
    try:
        response = requests.get(settings.keycloak_jwks_url, timeout=10)
        response.raise_for_status()
        jwks = response.json()
        
        # Extract the first key (assuming single key setup)
        if jwks.get("keys"):
            key_data = jwks["keys"][0]
            # Convert JWK to PEM format
            from jwt.algorithms import RSAAlgorithm
            public_key = RSAAlgorithm.from_jwk(key_data)
            return public_key
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

@lru_cache(maxsize=1)
def get_keycloak_issuer() -> str:
    """
    Get the issuer from Keycloak OpenID Connect configuration.
    """
    try:
        response = requests.get(settings.keycloak_openid_connect_url, timeout=10)
        response.raise_for_status()
        oidc_config = response.json()
        return oidc_config.get("issuer", settings.keycloak_issuer)
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch OIDC config, using default issuer: {e}")
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
        # Get the public key for verification
        public_key = get_keycloak_public_key()
        
        # Get the issuer
        issuer = get_keycloak_issuer()
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.keycloak_client_id,
            issuer=issuer,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True
            }
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidAudienceError:
        logger.warning("Invalid token audience")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience"
        )
    except jwt.InvalidIssuerError:
        logger.warning("Invalid token issuer")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer"
        )
    except jwt.InvalidSignatureError:
        logger.warning("Invalid token signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
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