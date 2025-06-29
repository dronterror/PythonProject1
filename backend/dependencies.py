from fastapi import Security, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, UserRole
from security import verify_token, get_keycloak_user_id, extract_user_roles, get_user_email
import logging
from typing import Dict, Any
import uuid

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
    Get the current user from Keycloak JWT token.
    Auto-creates user in database if they don't exist but have valid token.
    
    Args:
        credentials: JWT token from the Authorization header
        db: Database session
        
    Returns:
        User object from the database
        
    Raises:
        HTTPException: If token is invalid
    """
    # Verify the JWT token
    payload = verify_token(credentials.credentials)
    
    # Extract Keycloak user ID and email
    keycloak_user_id = get_keycloak_user_id(payload)
    user_email = get_user_email(payload) or "unknown@example.com"
    
    # Find the user in our database
    user = db.query(User).filter(User.auth_provider_id == keycloak_user_id).first()
    
    if not user:
        # Auto-create user on first login
        logger.info(f"Auto-creating user with Keycloak ID {keycloak_user_id} and email {user_email}")
        
        # Extract roles from Keycloak token
        token_roles = extract_user_roles(payload)
        
        # Determine user role (default to 'nurse' if no specific role found)
        user_role = UserRole.nurse  # Default role
        if "super-admin" in token_roles:
            user_role = UserRole.super_admin
        elif "pharmacist" in token_roles:
            user_role = UserRole.pharmacist
        elif "doctor" in token_roles:
            user_role = UserRole.doctor
        elif "nurse" in token_roles:
            user_role = UserRole.nurse
        
        # Create new user
        user = User(
            id=uuid.uuid4(),
            email=user_email,
            role=user_role,
            auth_provider_id=keycloak_user_id
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Successfully created user {user.email} with role {user.role.value}")
    
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
    Checks both the user's database role and Keycloak token roles.
    
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
        
        # Check Keycloak token roles
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