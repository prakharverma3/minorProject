from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

# Many-to-many relationship table for project collaborators
project_collaborators = Table(
    "project_collaborators",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic project information
    title = Column(String(255), nullable=False, index=True)
    summary = Column(String(200), nullable=False)  # Short summary (max 100 chars as in the form)
    description = Column(Text, nullable=False)     # Detailed description
    category = Column(String(50), nullable=False)  # e.g., Technology, Healthcare, etc.
    
    # Additional information
    github_link = Column(String(255))  # Optional GitHub repository URL
    skills_needed = Column(Text)       # Skills needed for the project
    
    # Tags will be stored as text
    tags = Column(Text)  # Storing as comma-separated values, we'll handle conversion in API
    
    # Project status and progress
    progress = Column(Float, default=0.0)  # Progress as percentage (0-100)
    is_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="projects")
    
    # Many-to-many relationship with collaborators
    collaborators = relationship(
        "User", 
        secondary=project_collaborators,
        back_populates="collaborated_projects"
    )
    
    # One-to-many relationship with collaboration requests
    collaboration_requests = relationship("CollaborationRequest", back_populates="project")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Project {self.title}>"

