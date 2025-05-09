from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
from datetime import datetime
import math

from app.database.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.collaboration import CollaborationRequest, RequestStatus
from app.schemas import (
    CollaborationRequestCreate,
    CollaborationRequestUpdate,
    CollaborationRequestResponse,
    CollaborationRequestList
)
from app.services.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=CollaborationRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_collaboration_request(
    request_data: CollaborationRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new collaboration request."""
    # Check if project exists
    project = db.query(Project).filter(Project.id == request_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if project is active
    if not project.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not active"
        )
    
    # Check if project is completed
    if project.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is already completed"
        )
    
    # Check if user is already a collaborator
    if current_user in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a collaborator on this project"
        )
    
    # Check if user is the project creator
    if project.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot request to collaborate on your own project"
        )
    
    # Check if there's already a pending request
    existing_request = db.query(CollaborationRequest).filter(
        CollaborationRequest.project_id == request_data.project_id,
        CollaborationRequest.user_id == current_user.id,
        CollaborationRequest.status == RequestStatus.PENDING
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending request for this project"
        )
    
    # Create new collaboration request
    db_request = CollaborationRequest(
        user_id=current_user.id,
        project_id=request_data.project_id,
        message=request_data.message,
        role=request_data.role,
        status=RequestStatus.PENDING
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return db_request


@router.get("/sent", response_model=CollaborationRequestList)
async def get_sent_requests(
    skip: int = 0,
    limit: int = 10,
    status: Optional[RequestStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get collaboration requests sent by the current user."""
    # Build query
    query = db.query(CollaborationRequest).filter(CollaborationRequest.user_id == current_user.id)
    
    # Apply status filter if provided
    if status:
        query = query.filter(CollaborationRequest.status == status)
    
    # Count total for pagination
    total = query.count()
    
    # Order by most recent first
    query = query.order_by(desc(CollaborationRequest.created_at))
    
    # Apply pagination and get results
    requests = query.offset(skip).limit(limit).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "requests": requests,
        "total": total,
        "page": current_page,
        "page_size": limit,
        "total_pages": total_pages
    }


@router.get("/received", response_model=CollaborationRequestList)
async def get_received_requests(
    skip: int = 0,
    limit: int = 10,
    status: Optional[RequestStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get collaboration requests for projects created by the current user."""
    # Get projects created by the user
    user_projects = db.query(Project.id).filter(Project.creator_id == current_user.id)
    
    # Build query to get collaboration requests for those projects
    query = db.query(CollaborationRequest).filter(
        CollaborationRequest.project_id.in_(user_projects.scalar_subquery())
    )
    
    # Apply status filter if provided
    if status:
        query = query.filter(CollaborationRequest.status == status)
    
    # Count total for pagination
    total = query.count()
    
    # Order by most recent first
    query = query.order_by(desc(CollaborationRequest.created_at))
    
    # Apply pagination and get results
    requests = query.offset(skip).limit(limit).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "requests": requests,
        "total": total,
        "page": current_page,
        "page_size": limit,
        "total_pages": total_pages
    }


@router.get("/{request_id}", response_model=CollaborationRequestResponse)
async def get_collaboration_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific collaboration request by ID."""
    # Get the request
    collab_request = db.query(CollaborationRequest).filter(CollaborationRequest.id == request_id).first()
    if not collab_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration request not found"
        )
    
    # Check if user is authorized to view this request
    project = db.query(Project).filter(Project.id == collab_request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # User can view request if they are the creator or the requester
    if collab_request.user_id != current_user.id and project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this request"
        )
    
    return collab_request


@router.put("/{request_id}", response_model=CollaborationRequestResponse)
async def update_collaboration_request(
    request_id: int,
    request_update: CollaborationRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a collaboration request (accept or reject)."""
    # Get the request
    collab_request = db.query(CollaborationRequest).filter(CollaborationRequest.id == request_id).first()
    if not collab_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration request not found"
        )
    
    # Get the project
    project = db.query(Project).filter(Project.id == collab_request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is the project creator (only they can update the request status)
    if project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project creator can accept or reject collaboration requests"
        )
    
    # Check if request is already processed
    if collab_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request is already {collab_request.status}"
        )
    
    # Update request status
    collab_request.status = request_update.status
    collab_request.responded_at = datetime.utcnow()
    
    # If request is accepted, add user to project collaborators
    if request_update.status == RequestStatus.ACCEPTED:
        user = db.query(User).filter(User.id == collab_request.user_id).first()
        if user:
            # Add user to collaborators if not already there
            if user not in project.collaborators:
                project.collaborators.append(user)
    
    db.commit()
    db.refresh(collab_request)
    
    return collab_request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collaboration_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete/withdraw a collaboration request (only for pending requests by the request creator)."""
    # Get the request
    collab_request = db.query(CollaborationRequest).filter(CollaborationRequest.id == request_id).first()
    if not collab_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration request not found"
        )
    
    # Check if user is the one who made the request
    if collab_request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to withdraw this request"
        )
    
    # Check if request is still pending
    if collab_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request is already {collab_request.status} and cannot be withdrawn"
        )
    
    # Delete the request
    db.delete(collab_request)
    db.commit()
    
    return None

