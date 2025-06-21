from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, UserRole
import secrets
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    if not api_key:
        logger.warning("Missing API Key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")
    
    # Use efficient database query instead of loading all users
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        logger.warning("Invalid API Key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    
    return user

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
    
    Args:
        allowed_roles: List of role names that are allowed to access the endpoint
        
    Returns:
        A dependency function that checks if the current user's role is in the allowed list
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in allowed_roles:
            logger.warning(f"User {current_user.email} with role {current_user.role.value} tried to access endpoint requiring roles: {allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker 