from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.schemas.auth import UserResponse


class RequestStatusEnum(str, Enum):
    """Enum for collaboration request status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class CollaborationRequestBase(BaseModel):
    """Base schema for collaboration request data."""
    message: Optional[str] = None
    role: Optional[str] = None


class CollaborationRequestCreate(CollaborationRequestBase):
    """Schema for creating a collaboration request."""
    project_id: int


class CollaborationRequestUpdate(BaseModel):
    """Schema for updating a collaboration request."""
    status: RequestStatusEnum
    response_message: Optional[str] = None


class ProjectMinimal(BaseModel):
    """Minimal project information for collaboration response."""
    id: int
    title: str
    category: str
    
    class Config:
        orm_mode = True


class CollaborationRequestResponse(CollaborationRequestBase):
    """Schema for collaboration request response."""
    id: int
    user_id: int
    project_id: int
    status: RequestStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    
    # Include the related user and project information
    user: Optional[UserResponse] = None
    project: Optional[ProjectMinimal] = None
    
    class Config:
        orm_mode = True


class CollaborationRequestList(BaseModel):
    """Schema for list of collaboration requests response."""
    requests: List[CollaborationRequestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

