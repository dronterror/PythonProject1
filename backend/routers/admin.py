import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
import uuid

from dependencies import get_db, require_roles
import crud
import schemas
import models

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Auth0 Management API configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_MANAGEMENT_CLIENT_ID = os.getenv("AUTH0_MANAGEMENT_CLIENT_ID")
AUTH0_MANAGEMENT_CLIENT_SECRET = os.getenv("AUTH0_MANAGEMENT_CLIENT_SECRET")

def get_auth0_management_token():
    """Get an access token for Auth0 Management API"""
    if not all([AUTH0_DOMAIN, AUTH0_MANAGEMENT_CLIENT_ID, AUTH0_MANAGEMENT_CLIENT_SECRET]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth0 Management API credentials not configured"
        )
    
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    headers = {"Content-Type": "application/json"}
    data = {
        "client_id": AUTH0_MANAGEMENT_CLIENT_ID,
        "client_secret": AUTH0_MANAGEMENT_CLIENT_SECRET,
        "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.RequestException as e:
        logger.error(f"Failed to get Auth0 management token: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to Auth0 Management API"
        )

def create_auth0_user(email: str, send_email: bool = True):
    """Create a user in Auth0 and return the user ID"""
    management_token = get_auth0_management_token()
    
    url = f"https://{AUTH0_DOMAIN}/api/v2/users"
    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/json"
    }
    
    # Generate a temporary password (user will be prompted to reset)
    import secrets
    temp_password = secrets.token_urlsafe(16) + "A1!"
    
    data = {
        "email": email,
        "password": temp_password,
        "connection": "Username-Password-Authentication",
        "verify_email": send_email,
        "email_verified": not send_email  # If we're not sending email, mark as verified
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        user_data = response.json()
        return user_data["user_id"]
    except requests.RequestException as e:
        logger.error(f"Failed to create Auth0 user: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to create user in Auth0"
        )

# Hospital Management Endpoints

@router.post("/hospitals", response_model=schemas.HospitalOut)
def create_hospital(
    hospital: schemas.HospitalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """Create a new hospital (Super Admin only)"""
    try:
        return crud.create_hospital(db=db, hospital=hospital)
    except Exception as e:
        logger.error(f"Failed to create hospital: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create hospital"
        )

@router.get("/hospitals", response_model=List[schemas.HospitalOut])
def get_hospitals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """Get all hospitals (Super Admin only)"""
    return crud.get_hospitals(db=db, skip=skip, limit=limit)

# Ward Management Endpoints

@router.post("/hospitals/{hospital_id}/wards", response_model=schemas.WardOut)
def create_ward(
    hospital_id: uuid.UUID,
    ward: schemas.WardCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """Create a new ward in a hospital (Super Admin only)"""
    # Verify hospital exists
    hospital = crud.get_hospital(db=db, hospital_id=hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Ensure the ward is being created for the correct hospital
    ward.hospital_id = hospital_id
    
    try:
        return crud.create_ward(db=db, ward=ward)
    except Exception as e:
        logger.error(f"Failed to create ward: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create ward"
        )

@router.get("/hospitals/{hospital_id}/wards", response_model=List[schemas.WardOut])
def get_wards_by_hospital(
    hospital_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """Get all wards for a hospital (Super Admin only)"""
    # Verify hospital exists
    hospital = crud.get_hospital(db=db, hospital_id=hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    return crud.get_wards_by_hospital(db=db, hospital_id=hospital_id)

# User Management Endpoints

@router.get("/users", response_model=List[schemas.UserOut])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """Get all users (Super Admin only)"""
    return crud.get_users(db=db, skip=skip, limit=limit)

@router.post("/users/invite", response_model=schemas.UserInviteResponse)
def invite_user(
    user_invite: schemas.UserInvite,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """
    Invite a new user to the system (Super Admin only)
    
    This endpoint:
    1. Creates a user in Auth0
    2. Creates a corresponding user record in our database
    3. Assigns the user to the specified ward with the specified role
    """
    # Verify hospital and ward exist
    hospital = crud.get_hospital(db=db, hospital_id=user_invite.hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    ward = crud.get_ward(db=db, ward_id=user_invite.ward_id)
    if not ward or ward.hospital_id != user_invite.hospital_id:
        raise HTTPException(status_code=404, detail="Ward not found in specified hospital")
    
    # Check if user already exists
    existing_user = crud.get_user_by_email(db=db, email=user_invite.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    try:
        # Create user in Auth0
        auth0_user_id = create_auth0_user(
            email=user_invite.email,
            send_email=user_invite.send_email
        )
        
        # Create user in our database
        user_create = schemas.UserCreate(
            email=user_invite.email,
            role=user_invite.role,
            auth0_user_id=auth0_user_id
        )
        db_user = crud.create_user(db=db, user=user_create)
        
        # Create user-ward permission
        crud.create_user_ward_permission(
            db=db,
            user_id=db_user.id,
            ward_id=user_invite.ward_id,
            role=user_invite.role
        )
        
        return schemas.UserInviteResponse(
            message=f"User invited successfully {'and email sent' if user_invite.send_email else ''}",
            user_id=db_user.id,
            auth0_user_id=auth0_user_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (Auth0 errors, etc.)
        raise
    except Exception as e:
        logger.error(f"Failed to invite user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite user"
        ) 