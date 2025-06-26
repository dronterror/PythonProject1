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

# Note: With Keycloak, user management is typically done through the Keycloak Admin Console
# This endpoint will create placeholder users that need to be manually created in Keycloak
# by the administrator, or you can implement Keycloak Admin API integration here.

def create_keycloak_user_placeholder(email: str) -> str:
    """
    Create a placeholder user ID for Keycloak integration.
    
    In a full implementation, this would use Keycloak Admin API to create users.
    For now, it returns a placeholder ID that needs to be updated when the user
    is created in Keycloak.
    """
    import uuid
    # Generate a placeholder ID that will be replaced with actual Keycloak user ID
    return f"placeholder-{uuid.uuid4()}"

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
    1. Creates a placeholder user record in our database
    2. Assigns the user to the specified ward with the specified role
    3. Returns instructions for manually creating the user in Keycloak
    
    Note: With Keycloak, you must manually create the user in the Keycloak Admin Console
    and then update the auth_provider_id field in the database with the actual Keycloak user ID.
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
        # Create placeholder user (Keycloak user must be created manually)
        keycloak_user_id = create_keycloak_user_placeholder(email=user_invite.email)
        
        # Create user in our database
        user_create = schemas.UserCreate(
            email=user_invite.email,
            role=user_invite.role,
            auth_provider_id=keycloak_user_id
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
            message=f"User placeholder created successfully. Please create the user '{user_invite.email}' in Keycloak Admin Console and update the auth_provider_id field.",
            user_id=db_user.id,
            keycloak_user_id=keycloak_user_id,
            keycloak_instructions="1. Go to Keycloak Admin Console\n2. Create user with email: " + user_invite.email + "\n3. Assign realm roles\n4. Update auth_provider_id in database with actual Keycloak user ID"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to invite user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite user"
        )

# User Permission Management Endpoints

@router.get("/users/{user_id}/permissions", response_model=List[schemas.UserWardPermissionOut])
def get_user_permissions(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("super_admin"))
):
    """Get all ward permissions for a specific user (Super Admin only)"""
    # Verify user exists
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.get_user_ward_permissions(db=db, user_id=user_id)

@router.post("/users/{user_id}/permissions", response_model=schemas.UserWardPermissionOut)
def create_user_permission(
    user_id: uuid.UUID,
    permission: schemas.UserWardPermissionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("super_admin"))
):
    """Create a new ward permission for a user (Super Admin only)"""
    # Verify user exists
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify ward exists
    ward = crud.get_ward(db=db, ward_id=permission.ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    
    # Check if permission already exists
    existing_permission = crud.get_user_ward_permission(
        db=db, user_id=user_id, ward_id=permission.ward_id, role=permission.role
    )
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this permission for this ward"
        )
    
    try:
        return crud.create_user_ward_permission(
            db=db, user_id=user_id, ward_id=permission.ward_id, role=permission.role
        )
    except Exception as e:
        logger.error(f"Failed to create user permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user permission"
        )

@router.delete("/users/{user_id}/permissions")
def delete_user_permission(
    user_id: uuid.UUID,
    permission: schemas.UserWardPermissionDelete,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("super_admin"))
):
    """Remove a specific ward permission from a user (Super Admin only)"""
    # Verify user exists
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find and delete the permission
    existing_permission = crud.get_user_ward_permission(
        db=db, user_id=user_id, ward_id=permission.ward_id, role=permission.role
    )
    if not existing_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    try:
        crud.delete_user_ward_permission(db=db, permission_id=existing_permission.id)
        return {"message": "Permission deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete user permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete user permission"
        )

# Ward listing endpoint for dropdowns
@router.get("/wards", response_model=List[schemas.WardOut])
def get_all_wards(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("super_admin"))
):
    """Get all wards across all hospitals (Super Admin only)"""
    return crud.get_all_wards(db=db) 