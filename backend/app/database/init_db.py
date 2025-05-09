import logging
from sqlalchemy.exc import SQLAlchemyError
import os
import sys
from passlib.context import CryptContext

# Add the parent directory to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database configuration and models
from app.database.database import engine, Base, SessionLocal
from app.models import User, Project, CollaborationRequest, RequestStatus

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Create database tables if they don't exist."""
    try:
        # Create all tables defined in models
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def create_test_data():
    """Create initial test data for development."""
    db = SessionLocal()
    try:
        # Check if we already have users
        if db.query(User).first():
            logger.info("Test data already exists, skipping...")
            return
        
        logger.info("Creating test data...")
        
        # Create test users
        users = [
            User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("password123"),
                full_name="Admin User",
                bio="I am the administrator of the platform.",
                is_verified=True
            ),
            User(
                username="researcher1",
                email="researcher1@example.com",
                hashed_password=pwd_context.hash("password123"),
                full_name="Research User 1",
                bio="AI researcher interested in machine learning projects.",
                is_verified=True
            ),
            User(
                username="developer1",
                email="developer1@example.com",
                hashed_password=pwd_context.hash("password123"),
                full_name="Developer User 1",
                bio="Software developer with experience in web applications.",
                is_verified=True
            )
        ]
        db.add_all(users)
        db.commit()
        
        # Create test projects
        projects = [
            Project(
                title="AI-Powered Crop Optimization System",
                summary="A machine learning system for optimizing farming yields in challenging environments",
                description="Developing a machine learning system that analyzes soil conditions, weather patterns, and crop data to optimize farming yields in challenging environments.",
                category="Environment",
                progress=65,
                tags="machine-learning,agriculture,sustainability",
                skills_needed="Machine learning, agricultural knowledge, data analysis",
                creator_id=2  # researcher1
            ),
            Project(
                title="Decentralized Education Platform",
                summary="Blockchain-based platform for educational credential verification",
                description="Creating a blockchain-based platform for educational credential verification and skill certification that works across borders.",
                category="Education",
                progress=40,
                tags="blockchain,education,verification",
                skills_needed="Blockchain, education policy, frontend development",
                creator_id=3  # developer1
            )
        ]
        db.add_all(projects)
        db.commit()
        
        # Create test collaboration requests
        collab_requests = [
            CollaborationRequest(
                user_id=3,  # developer1
                project_id=1,  # AI-Powered Crop Optimization
                message="I can help with the web interface for visualizing crop data.",
                role="Frontend Developer",
                status=RequestStatus.PENDING
            ),
            CollaborationRequest(
                user_id=2,  # researcher1
                project_id=2,  # Decentralized Education Platform
                message="I have experience with educational credential systems and ML.",
                role="AI Specialist",
                status=RequestStatus.ACCEPTED
            )
        ]
        db.add_all(collab_requests)
        db.commit()
        
        logger.info("Test data created successfully!")
    except SQLAlchemyError as e:
        logger.error(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    success = init_db()
    if success and "--with-testdata" in sys.argv:
        create_test_data()

