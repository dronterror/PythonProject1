"""
Test Security Module for JWT Authentication
Handles HS256 tokens for testing purposes
"""

import os
import jwt
from typing import Dict, Any
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# JWT Configuration for testing (matches token generator)
JWT_SECRET_KEY = "your-super-secret-jwt-key-change-in-production"
JWT_ALGORITHM = "HS256"

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a test JWT token using HS256.
    
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
        # Verify and decode the token using HS256
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            audience="https://api.medlog.app",
            issuer="https://dev-medlog-test.us.auth0.com/"
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
    Extract user roles from the token payload.
    For test tokens, the role is stored directly in the 'role' field.
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        List of user roles
    """
    role = payload.get("role")
    return [role] if role else []

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