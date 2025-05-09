#!/usr/bin/env python
import sys
import os
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_test")

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import app components
try:
    from app.database.database import engine, SessionLocal
    from app.models.user import User
    from app.schemas import UserCreate, UserResponse
    from app.services.auth import get_password_hash
    
    logger.info("Successfully imported required modules")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def test_db_connection():
    """Test the database connection"""
    logger.info("Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"Database connection successful: {result.fetchone()}")
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False

def inspect_users_table():
    """Inspect the users table structure"""
    logger.info("Inspecting users table...")
    try:
        inspector = inspect(engine)
        
        # Check if the users table exists
        tables = inspector.get_table_names()
        if "users" not in tables:
            logger.error("Users table does not exist!")
            return False
            
        # Get column information
        columns = inspector.get_columns("users")
        logger.info("Users table structure:")
        for column in columns:
            logger.info(f"  {column['name']}: {column['type']}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to inspect users table: {e}")
        return False

def test_user_creation():
    """Test creating a user in the database"""
    logger.info("Testing user creation...")
    
    # Create a test user with a unique username
    test_user = UserCreate(
        username=f"testuser_{os.urandom(4).hex()}",
        email=f"test_{os.urandom(4).hex()}@example.com",
        password="Password123!",
        full_name="Test User",
        bio="Test user for debugging",
        profile_image_url=None
    )
    
    logger.info(f"Attempting to create user: {test_user.username} / {test_user.email}")
    
    db = SessionLocal()
    try:
        # Check if username already exists
        if db.query(User).filter(User.username == test_user.username).first():
            logger.error(f"Username {test_user.username} already exists")
            return False
        
        # Check if email already exists
        if db.query(User).filter(User.email == test_user.email).first():
            logger.error(f"Email {test_user.email} already exists")
            return False
        
        # Create new user
        db_user = User(
            username=test_user.username,
            email=test_user.email,
            hashed_password=get_password_hash(test_user.password),
            full_name=test_user.full_name,
            bio=test_user.bio,
            profile_image_url=test_user.profile_image_url,
            is_active=True,
            is_verified=False
        )
        
        # Start transaction
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User created successfully: ID={db_user.id}")
        
        # Try to create a UserResponse object
        try:
            # Log all user attributes to check for missing fields
            logger.info("User attributes:")
            for attr_name in dir(db_user):
                if not attr_name.startswith('_') and attr_name != 'metadata':
                    attr_value = getattr(db_user, attr_name)
                    if not callable(attr_value):
                        logger.info(f"  {attr_name}: {attr_value}")
            
            # Try to create the response
            user_response = UserResponse.from_orm(db_user)
            logger.info(f"Successfully created UserResponse: {user_response}")
            return True
        except ValidationError as e:
            logger.error(f"Failed to create UserResponse: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating UserResponse: {e}")
            return False
            
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during user creation: {e}")
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during user creation: {e}")
        return False
    finally:
        db.close()

def run_tests():
    """Run all diagnostic tests"""
    logger.info("Starting database and registration tests")
    
    # Test database connection
    if not test_db_connection():
        logger.error("Database connection test failed. Stopping tests.")
        return False
    
    # Inspect users table
    if not inspect_users_table():
        logger.warning("Users table inspection failed. Continuing with other tests.")
    
    # Test user creation
    if not test_user_creation():
        logger.error("User creation test failed.")
        return False
    
    logger.info("All tests completed successfully")
    return True

if __name__ == "__main__":
    success = run_tests()
    if not success:
        logger.error("Database and registration tests failed.")
        sys.exit(1)
    else:
        logger.info("Database and registration tests passed!")

