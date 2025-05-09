from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any
from datetime import datetime

from app.schemas.auth import UserResponse


class ProjectBase(BaseModel):
    """Base schema for project data."""
    title: str
    summary: str = Field(..., max_length=200)
    description: str
    category: str
    github_link: Optional[str] = None
    skills_needed: Optional[str] = None
    tags: Optional[List[str]] = []


class ProjectCreate(ProjectBase):
    """Schema for project creation."""
    
    @validator('tags', pre=True)
    def parse_tags(cls, v):
        """Convert tags to list if they're provided as comma-separated string."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v


class ProjectUpdate(BaseModel):
    """Schema for project update."""
    title: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    github_link: Optional[str] = None
    skills_needed: Optional[str] = None
    tags: Optional[List[str]] = None
    progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_completed: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @validator('tags', pre=True)
    def parse_tags(cls, v):
        """Convert tags to list if they're provided as comma-separated string."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v


class ProjectCollaborator(BaseModel):
    """Schema for project collaborator."""
    id: int
    username: str
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    
    class Config:
        orm_mode = True


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    creator_id: int
    creator: UserResponse
    progress: float
    is_completed: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    collaborators: List[ProjectCollaborator] = []
    
    @validator('tags', pre=True)
    def split_tags(cls, v):
        """Convert tags from comma-separated string to list."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v or []
    
    class Config:
        orm_mode = True


class ProjectList(BaseModel):
    """Schema for list of projects response."""
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProjectCreateResponse(BaseModel):
    """Schema for project creation response with success message."""
    project: ProjectResponse
    message: str
    success: bool = True

