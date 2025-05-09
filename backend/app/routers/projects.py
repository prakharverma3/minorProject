from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
import math

from app.database.database import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse, 
    ProjectList,
    ProjectCreateResponse
)
from app.services.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=ProjectCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new project."""
    # Convert tags from list to comma-separated string
    tags_string = ",".join(project_data.tags) if project_data.tags else ""
    
    # Create new project
    db_project = Project(
        title=project_data.title,
        summary=project_data.summary,
        description=project_data.description,
        category=project_data.category,
        github_link=project_data.github_link,
        skills_needed=project_data.skills_needed,
        tags=tags_string,
        creator_id=current_user.id,
        progress=0.0,  # Initial progress is 0%
        is_completed=False,
        is_active=True
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Return project data with success message
    return {
        "project": db_project,
        "message": f"Project '{db_project.title}' created successfully!",
        "success": True
    }


@router.get("/", response_model=ProjectList)
async def get_projects(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a list of projects with filtering and pagination.
    
    Args:
        skip: Number of projects to skip (for pagination)
        limit: Maximum number of projects to return
        search: Optional search string for title or description
        category: Optional category filter
        tags: Optional comma-separated tags to filter by
        active_only: Only show active projects if True
    """
    # Build the query with filters
    query = db.query(Project)
    
    # Filter by active status if requested
    if active_only:
        query = query.filter(Project.is_active == True)
    
    # Apply category filter if provided
    if category:
        query = query.filter(Project.category == category)
    
    # Apply tags filter if provided
    if tags:
        # Split into list
        tag_list = [tag.strip() for tag in tags.split(",")]
        
        # Build tag filter condition for each tag (using LIKE)
        tag_filters = []
        for tag in tag_list:
            # Look for the tag in the tags field, surrounded by commas or at the start/end
            tag_pattern = f"%{tag}%"
            tag_filters.append(Project.tags.ilike(tag_pattern))
        
        # Combine filters with OR (any tag matches)
        if tag_filters:
            query = query.filter(or_(*tag_filters))
    
    # Apply search filter if provided
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Project.title.ilike(search_filter),
                Project.description.ilike(search_filter),
                Project.summary.ilike(search_filter)
            )
        )
    
    # Count total for pagination
    total = query.count()
    
    # Order by most recent first
    query = query.order_by(desc(Project.created_at))
    
    # Apply pagination and get results
    projects = query.offset(skip).limit(limit).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "projects": projects,
        "total": total,
        "page": current_page,
        "page_size": limit,
        "total_pages": total_pages
    }


@router.get("/my-projects", response_model=ProjectList)
async def get_my_projects(
    skip: int = 0,
    limit: int = 10,
    include_collaborations: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get projects created by the current user.
    
    Args:
        skip: Number of projects to skip (for pagination)
        limit: Maximum number of projects to return
        include_collaborations: Include projects where the user is a collaborator
    """
    # Start with projects created by the user
    if include_collaborations:
        # Include projects where user is a collaborator using the many-to-many relationship
        base_query = db.query(Project).filter(
            or_(
                Project.creator_id == current_user.id,
                Project.collaborators.any(id=current_user.id)
            )
        )
    else:
        # Only include projects created by the user
        base_query = db.query(Project).filter(Project.creator_id == current_user.id)
    
    # Count total for pagination
    total = base_query.count()
    
    # Order by most recent first
    query = base_query.order_by(desc(Project.created_at))
    
    # Apply pagination and get results
    projects = query.offset(skip).limit(limit).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "projects": projects,
        "total": total,
        "page": current_page,
        "page_size": limit,
        "total_pages": total_pages
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a project."""
    # Get the project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is the creator
    if project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this project"
        )
    
    # Update the project fields if they are provided
    if project_update.title is not None:
        project.title = project_update.title
    
    if project_update.summary is not None:
        project.summary = project_update.summary
    
    if project_update.description is not None:
        project.description = project_update.description
    
    if project_update.category is not None:
        project.category = project_update.category
    
    if project_update.github_link is not None:
        project.github_link = project_update.github_link
    
    if project_update.skills_needed is not None:
        project.skills_needed = project_update.skills_needed
    
    if project_update.tags is not None:
        project.tags = ",".join(project_update.tags)
    
    if project_update.progress is not None:
        project.progress = project_update.progress
    
    if project_update.is_completed is not None:
        project.is_completed = project_update.is_completed
    
    if project_update.is_active is not None:
        project.is_active = project_update.is_active
    
    # Save changes to database
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a project."""
    # Get the project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is the creator
    if project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this project"
        )
    
    # Delete the project (actually just mark as inactive for data retention)
    project.is_active = False
    db.commit()
    
    return None


@router.post("/{project_id}/collaborators/{user_id}", response_model=ProjectResponse)
async def add_collaborator(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a collaborator to a project."""
    # Get the project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is the creator
    if project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project creator can add collaborators"
        )
    
    # Get the user to add as collaborator
    user_to_add = db.query(User).filter(User.id == user_id).first()
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is already a collaborator
    if user_to_add in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a collaborator on this project"
        )
    
    # Add the user as a collaborator
    project.collaborators.append(user_to_add)
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}/collaborators/{user_id}", response_model=ProjectResponse)
async def remove_collaborator(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a collaborator from a project."""
    # Get the project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is the creator or the collaborator being removed
    if project.creator_id != current_user.id and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove this collaborator"
        )
    
    # Get the user to remove
    user_to_remove = db.query(User).filter(User.id == user_id).first()
    if not user_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is a collaborator
    if user_to_remove not in project.collaborators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a collaborator on this project"
        )
    
    # Remove the user as a collaborator
    project.collaborators.remove(user_to_remove)
    db.commit()
    db.refresh(project)
    
    return project

