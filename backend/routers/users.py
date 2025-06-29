from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from dependencies import get_db, get_current_user
import crud
import schemas
from models import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    """
    return current_user


@router.get("/users/me/wards", response_model=List[schemas.WardOut])
def get_my_wards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the list of wards the current user is assigned to.
    """
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    wards = crud.get_wards_for_user(db, user_id=current_user.id)
    return wards 