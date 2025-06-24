import os
import json
import jwt
import requests
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Auth0 configuration from environment variables
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
AUTH0_ALGORITHM = "RS256"

if not AUTH0_DOMAIN or not AUTH0_API_AUDIENCE:
    raise ValueError("AUTH0_DOMAIN and AUTH0_API_AUDIENCE environment variables must be set")

@lru_cache(maxsize=1)
def get_jwks() -> Dict[str, Any]:
    """
    Fetch the JSON Web Key Set from Auth0.
    Cached to avoid repeated requests to Auth0.
    """
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch JWKS from Auth0: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify authentication tokens"
        )

def get_rsa_key(token: str) -> Dict[str, Any]:
    """
    Extract the RSA key from JWKS for token verification.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = get_jwks()
        
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                return {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
    except Exception as e:
        logger.error(f"Failed to extract RSA key: {e}")
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to find appropriate key for token verification"
    )

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode an Auth0 JWT token.
    
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
        # Get the RSA key for verification
        rsa_key = get_rsa_key(token)
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[AUTH0_ALGORITHM],
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
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

def extract_user_roles(payload: Dict[str, Any]) -> list[str]:
    """
    Extract user roles from the Auth0 token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        List of user roles
    """
    # Auth0 custom claims are typically namespaced
    roles_claim = "https://api.medlogistics.com/roles"
    return payload.get(roles_claim, [])

def get_auth0_user_id(payload: Dict[str, Any]) -> str:
    """
    Extract the Auth0 user ID from the token payload.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        Auth0 user ID (sub claim)
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    return user_id 