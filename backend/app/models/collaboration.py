from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.database import Base

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class CollaborationRequest(Base):
    __tablename__ = "collaboration_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Establish relationship references
    user = relationship("User", back_populates="collaboration_requests")
    project = relationship("Project", back_populates="collaboration_requests")
    
    # Request details
    message = Column(Text)  # Message from the requesting user explaining why they want to collaborate
    role = Column(String(100))  # The role/responsibility the user wants to take in the project
    
    # Request status
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    responded_at = Column(DateTime(timezone=True))  # When the request was accepted/rejected
    
    def __repr__(self):
        return f"<CollaborationRequest {self.id}: {self.user_id} -> {self.project_id} ({self.status})>"

