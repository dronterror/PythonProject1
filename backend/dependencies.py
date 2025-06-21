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
    for u in db.query(User).all():
        if secrets.compare_digest(u.api_key, api_key):
            return u
    logger.warning("Invalid API Key")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

def require_role(role_name: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role.value != role_name:
            logger.warning(f"User {current_user.email} tried to access {role_name}-only endpoint.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return role_dependency 