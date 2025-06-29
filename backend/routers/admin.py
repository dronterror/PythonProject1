import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
import uuid

from dependencies import get_db, require_roles, require_role
import crud
import schemas
import models
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

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
        raise HTTPException(status_code=400, detail="Failed to create hospital")


@router.get("/hospitals", response_model=List[schemas.HospitalOut])
def get_hospitals(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """Get all hospitals (Super Admin only)"""
    return crud.get_hospitals(db=db)


# Ward Management Endpoints

@router.post("/hospitals/{hospital_id}/wards", response_model=schemas.WardOut)
def create_ward(
    hospital_id: str,
    ward: schemas.WardCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin", "hospital_admin"]))
):
    """Create a new ward in a hospital"""
    try:
        # Verify hospital exists
        hospital = crud.get_hospital(db=db, hospital_id=hospital_id)
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        return crud.create_ward(db=db, ward=ward, hospital_id=hospital_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create ward: {e}")
        raise HTTPException(status_code=400, detail="Failed to create ward")


@router.get("/hospitals/{hospital_id}/wards", response_model=List[schemas.WardOut])
def get_hospital_wards(
    hospital_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin", "hospital_admin"]))
):
    """Get all wards in a hospital"""
    # Verify hospital exists
    hospital = crud.get_hospital(db=db, hospital_id=hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    return crud.get_hospital_wards(db=db, hospital_id=hospital_id)


# User Management Endpoints

@router.get("/users", response_model=List[schemas.UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin", "hospital_admin"]))
):
    """Get all users (Admin only)"""
    return crud.get_users(db=db)


@router.post("/users/invite", response_model=schemas.UserOut)
def invite_user(
    user_data: schemas.UserInvite,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin", "hospital_admin"]))
):
    """
    Invite a new user to the system.
    Creates user in database with placeholder Keycloak ID.
    Admin must manually create the user in Keycloak Admin Console.
    """
    try:
        # Check if user already exists
        existing_user = crud.get_user_by_email(db=db, email=user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Verify hospital and ward exist
        if user_data.hospital_id:
            hospital = crud.get_hospital(db=db, hospital_id=user_data.hospital_id)
            if not hospital:
                raise HTTPException(status_code=404, detail="Hospital not found")
        
        if user_data.ward_id:
            ward = crud.get_ward(db=db, ward_id=user_data.ward_id)
            if not ward:
                raise HTTPException(status_code=404, detail="Ward not found")
        
        # Create user with placeholder auth provider ID
        user_create = schemas.UserCreate(
            email=user_data.email,
            role=user_data.role,
            hospital_id=user_data.hospital_id,
            ward_id=user_data.ward_id,
            auth_provider_id=f"pending-{uuid.uuid4()}"  # Placeholder until user logs in
        )
        
        user = crud.create_user(db=db, user=user_create)
        
        logger.info(f"User invited: {user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to invite user: {e}")
        raise HTTPException(status_code=400, detail="Failed to invite user")


# User Permission Management

@router.get("/users/{user_id}/permissions")
def get_user_permissions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin", "hospital_admin"]))
):
    """Get user permissions and assignments"""
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "hospital_id": user.hospital_id,
        "ward_id": user.ward_id,
        "permissions": crud.get_user_permissions(db=db, user_id=user_id)
    }


@router.put("/users/{user_id}/permissions")
def update_user_permissions(
    user_id: str,
    permissions_data: schemas.UserWardPermissionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin", "hospital_admin"]))
):
    """Update user permissions and assignments"""
    try:
        user = crud.get_user(db=db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user permissions
        updated_user = crud.update_user_permissions(
            db=db, 
            user_id=user_id, 
            permissions_data=permissions_data
        )
        
        return {"message": "User permissions updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user permissions: {e}")
        raise HTTPException(status_code=400, detail="Failed to update user permissions")


@router.delete("/users/{user_id}/permissions")
def revoke_user_permissions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """Revoke all user permissions (Super Admin only)"""
    try:
        crud.revoke_user_permissions(db=db, user_id=user_id)
        return {"message": "User permissions revoked successfully"}
    except Exception as e:
        logger.error(f"Failed to revoke user permissions: {e}")
        raise HTTPException(status_code=400, detail="Failed to revoke user permissions")


# Ward Management (additional endpoint)

@router.get("/wards", response_model=List[schemas.WardOut])
def get_all_wards(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["super_admin"]))
):
    """Get all wards across all hospitals (Super Admin only)"""
    return crud.get_all_wards(db=db) 