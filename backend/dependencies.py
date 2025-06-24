from fastapi import Security, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, UserRole
from security import verify_token, get_auth0_user_id, extract_user_roles
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security), 
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current user from Auth0 JWT token.
    
    Args:
        credentials: JWT token from the Authorization header
        db: Database session
        
    Returns:
        User object from the database
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Verify the JWT token
    payload = verify_token(credentials.credentials)
    
    # Extract Auth0 user ID
    auth0_user_id = get_auth0_user_id(payload)
    
    # Find the user in our database
    user = db.query(User).filter(User.auth0_user_id == auth0_user_id).first()
    if not user:
        logger.warning(f"User with Auth0 ID {auth0_user_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not found in system"
        )
    
    return user

def get_token_payload(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """
    Get the decoded JWT token payload without database lookup.
    Useful for admin operations that need token roles.
    """
    return verify_token(credentials.credentials)

def require_role(role_name: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role.value != role_name:
            logger.warning(f"User {current_user.email} tried to access {role_name}-only endpoint.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return role_dependency

def require_roles(allowed_roles: list[str]):
    """
    Dependency factory that accepts a list of allowed roles for more flexible access control.
    Checks both the user's database role and Auth0 token roles.
    
    Args:
        allowed_roles: List of role names that are allowed to access the endpoint
        
    Returns:
        A dependency function that checks if the current user's role is in the allowed list
    """
    def role_checker(
        current_user: User = Depends(get_current_user),
        token_payload: Dict[str, Any] = Depends(get_token_payload)
    ):
        # Check database role
        user_db_role = current_user.role.value
        
        # Check Auth0 token roles
        token_roles = extract_user_roles(token_payload)
        
        # User has access if they have the role in either location
        has_db_role = user_db_role in allowed_roles
        has_token_role = any(role in allowed_roles for role in token_roles)
        
        if not (has_db_role or has_token_role):
            logger.warning(
                f"User {current_user.email} with database role {user_db_role} "
                f"and token roles {token_roles} tried to access endpoint requiring roles: {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker