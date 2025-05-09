from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Import routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.projects import router as projects_router
from app.routers.collaborations import router as collaborations_router
from app.routers.recommendation import router as recommendation_router
# Load environment variables
load_dotenv()

# API configuration from environment variables
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_PREFIX = os.getenv("API_PREFIX", "/api")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# CORS settings from environment variables
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:8080").split(",")

# Create FastAPI app
app = FastAPI(
    title="IdeaForge API",
    description="API for the IdeaForge research collaboration platform",
    version="0.1.0",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
    debug=DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint - API health check
@app.get("/")
async def root():
    return {"status": "online", "message": "IdeaForge API is running"}

# Include routers

app.include_router(auth_router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(users_router, prefix=f"{API_PREFIX}/users", tags=["Users"])
app.include_router(projects_router, prefix=f"{API_PREFIX}/projects", tags=["Projects"])
app.include_router(collaborations_router, prefix=f"{API_PREFIX}/collaborations", tags=["Collaborations"])
app.include_router(recommendation_router, prefix=f"{API_PREFIX}/recommendations", tags=["Recommendations"])
if __name__ == "__main__":
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=DEBUG)

