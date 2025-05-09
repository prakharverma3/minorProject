import os
import sys
import re
import importlib.util
from typing import List, Dict, Any, Optional
import logging
from functools import lru_cache
from dotenv import load_dotenv

from app.schemas.recommendation import PaperRecommendation, RecommendationResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the path to the recommendation model
model_path = os.getenv("RECOMMENDATION_MODEL_PATH", "../initialrecomendmodel.py")
max_recommendations = int(os.getenv("MAX_RECOMMENDATIONS", "5"))

# Flag to track if the recommendation model is available
MODEL_AVAILABLE = False

# Add arxiv base URL for paper links
ARXIV_URL_BASE = "https://arxiv.org/abs/"


def load_recommendation_model():
    """
    Load the recommendation model from the specified path.
    
    Returns:
        module: The loaded recommendation model module
    """
    try:
        # Get absolute path to the model file
        abs_model_path = os.path.abspath(model_path)
        logger.info(f"Loading recommendation model from {abs_model_path}")
        
        # Load the module
        spec = importlib.util.spec_from_file_location("recommendation_model", abs_model_path)
        model_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(model_module)
        
        logger.info("Recommendation model loaded successfully")
        return model_module
    except Exception as e:
        logger.error(f"Error loading recommendation model: {str(e)}")
        return None


# Load the model
try:
    model = load_recommendation_model()
    if model:
        MODEL_AVAILABLE = True
        logger.info("Recommendation model initialized successfully")
    else:
        MODEL_AVAILABLE = False
        logger.warning("Recommendation model could not be loaded, service will be disabled")
except Exception as e:
    MODEL_AVAILABLE = False
    logger.warning(f"Error initializing recommendation model: {str(e)}")
    logger.warning("Recommendation services will be disabled but server will continue running")
    model = None


def extract_arxiv_id(title: str) -> Optional[str]:
    """
    Attempt to extract an arXiv ID from a paper title.
    This is a simple heuristic and might need improvement.
    
    Args:
        title: The paper title
        
    Returns:
        str: The extracted arXiv ID, or None if not found
    """
    # Look for patterns like arXiv:1234.56789 or similar in the title
    match = re.search(r'arxiv:(\d+\.\d+)', title.lower())
    if match:
        return match.group(1)
    
    # Alternative patterns might be added here
    return None


@lru_cache(maxsize=100)
def get_paper_recommendations(text: str, max_results: int = max_recommendations) -> RecommendationResponse:
    """
    Get paper recommendations for the given text.
    
    Args:
        text: The text to get recommendations for
        max_results: Maximum number of recommendations to return
        
    Returns:
        RecommendationResponse: The recommendations and metadata
    """
    if not MODEL_AVAILABLE or not model:
        logger.warning("Recommendation model not available or not loaded")
        # Return empty recommendations with explanatory message if model failed to load
        return RecommendationResponse(
            query=text,
            recommendations=[],
            count=0,
            message="Recommendation service is currently unavailable"
        )
    
    try:
        # Use the model's recommend_papers_partial function
        raw_recommendations = model.recommend_papers_partial(text, top_n=max_results)
        
        # Format the recommendations
        recommendations = []
        for title, score in raw_recommendations:
            # Extract arXiv ID if possible
            arxiv_id = extract_arxiv_id(title)
            
            # Create URL if arXiv ID is available
            url = f"{ARXIV_URL_BASE}{arxiv_id}" if arxiv_id else None
            
            # Add to recommendations list
            recommendations.append(
                PaperRecommendation(
                    title=title,
                    score=float(score),  # Ensure score is float
                    arxiv_id=arxiv_id,
                    url=url
                )
            )
        
        # Create and return the response
        return RecommendationResponse(
            query=text,
            recommendations=recommendations,
            count=len(recommendations)
        )
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        # Return empty recommendations in case of error
        return RecommendationResponse(
            query=text,
            recommendations=[],
            count=0,
            message=f"Error processing recommendation: {str(e)}"
        )

