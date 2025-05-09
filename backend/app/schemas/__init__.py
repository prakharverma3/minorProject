# Authentication schemas
from app.schemas.auth import (
    Token,
    TokenPayload,
    LoginRequest,
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse
)

# Project schemas
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectCollaborator,
    ProjectResponse,
    ProjectList,
    ProjectCreateResponse
)

# Collaboration schemas
from app.schemas.collaboration import (
    RequestStatusEnum,
    CollaborationRequestBase,
    CollaborationRequestCreate,
    CollaborationRequestUpdate,
    ProjectMinimal,
    CollaborationRequestResponse,
    CollaborationRequestList
)

# Recommendation schemas
from app.schemas.recommendation import (
    RecommendationRequest,
    PaperRecommendation,
    RecommendationResponse
)

