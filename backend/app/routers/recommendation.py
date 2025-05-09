from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from app.database.database import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas import (
    RecommendationRequest,
    RecommendationResponse
)
from app.services.auth import get_current_active_user
from app.services.recommendation import get_paper_recommendations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get paper recommendations based on text input.
    
    Args:
        request: The recommendation request containing text and optional max_results
    """
    try:
        # Get recommendations from the service
        recommendations = get_paper_recommendations(
            text=request.text,
            max_results=request.max_results
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=RecommendationResponse)
async def get_project_recommendations(
    project_id: int,
    max_results: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get paper recommendations for a specific project.
    
    Args:
        project_id: The ID of the project to get recommendations for
        max_results: Maximum number of recommendations to return
    """
    # Get the project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Combine project title, summary, and description for better recommendations
    project_text = f"{project.title}. {project.summary}. {project.description}"
    
    try:
        # Get recommendations from the service
        recommendations = get_paper_recommendations(
            text=project_text,
            max_results=max_results
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error getting project recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/background", status_code=status.HTTP_202_ACCEPTED)
async def get_recommendations_background(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """
    Queue recommendation generation as a background task.
    This is useful for long-running recommendation generation.
    
    Args:
        request: The recommendation request
        background_tasks: FastAPI background tasks handler
    """
    # This is a placeholder for a more sophisticated background task system
    # In a production app, this might use Celery, Redis Queue, etc.
    background_tasks.add_task(get_paper_recommendations, request.text, request.max_results)
    
    return {"message": "Recommendation generation queued"}

