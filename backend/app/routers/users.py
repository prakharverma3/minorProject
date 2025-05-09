from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from app.database.database import get_db
from app.models.user import User
from app.schemas import UserResponse, UserUpdate
from app.services.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a list of users with pagination and optional search.
    
    Args:
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return
        search: Optional search string for username or full name
    """
    query = db.query(User)
    
    # Apply search filter if provided
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_filter),
                User.full_name.ilike(search_filter)
            )
        )
    
    # Apply pagination and return results
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile information."""
    # Update user fields if they are provided in the request
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    
    if user_update.profile_image_url is not None:
        current_user.profile_image_url = user_update.profile_image_url
    
    # Email changes might require verification in a production app
    if user_update.email is not None and user_update.email != current_user.email:
        # Check if email is already taken
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
        # In a production app, you might set is_verified=False here and send a verification email
    
    # Save changes to database
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/search/", response_model=List[UserResponse])
async def search_users(
    query: str = Query(..., min_length=1),
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search for users by username or full name."""
    search_filter = f"%{query}%"
    users = db.query(User).filter(
        or_(
            User.username.ilike(search_filter),
            User.full_name.ilike(search_filter)
        )
    ).limit(limit).all()
    
    return users

