from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendationRequest(BaseModel):
    """Schema for requesting paper recommendations."""
    text: str = Field(..., min_length=1, description="The text to generate recommendations for")
    max_results: Optional[int] = Field(5, ge=1, le=20, description="Maximum number of recommendations to return")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Machine learning approaches for natural language processing",
                "max_results": 5
            }
        }


class PaperRecommendation(BaseModel):
    """Schema for a single paper recommendation."""
    title: str
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                "score": 0.92,
                "arxiv_id": "1810.04805",
                "url": "https://arxiv.org/abs/1810.04805"
            }
        }


class RecommendationResponse(BaseModel):
    """Schema for paper recommendation response."""
    query: str
    recommendations: List[PaperRecommendation]
    count: int
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Machine learning approaches for natural language processing",
                "recommendations": [
                    {
                        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                        "score": 0.92,
                        "arxiv_id": "1810.04805",
                        "url": "https://arxiv.org/abs/1810.04805"
                    },
                    {
                        "title": "Attention Is All You Need",
                        "score": 0.89,
                        "arxiv_id": "1706.03762",
                        "url": "https://arxiv.org/abs/1706.03762"
                    }
                ],
                "count": 2
            }
        }

