import requests
import logging
import json
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_registration():
    """
    Test user registration endpoint
    1. Attempt to register with provided credentials
    2. Log API response details
    3. Verify database state after registration
    """
    # API endpoint
    BASE_URL = "http://127.0.0.1:8000"
    REGISTER_URL = f"{BASE_URL}/api/auth/register"
    
    # User credentials for registration
    user_data = {
        "username": "prakhar.verma003",
        "email": "vermaprakhar85@gmail.com",
        "password": "Test123456",
        "full_name": "Prakhar Verma",
        "bio": None,
        "profile_image_url": None
    }
    
    logger.info(f"Attempting registration with username: {user_data['username']}")
    logger.info(f"Request URL: {REGISTER_URL}")
    
    try:
        # Step 1: Make registration request
        response = requests.post(
            REGISTER_URL,
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Step 2: Log response details
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        
        try:
            # Try to parse JSON response
            response_data = response.json()
            logger.info(f"Response body: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            # Log raw response if not JSON
            logger.warning(f"Non-JSON response: {response.text}")
        
        # Step 3: Verify database state
        verify_database(user_data["username"])
        
        if response.status_code == 201:
            logger.info("Registration successful!")
            return True
        else:
            logger.error(f"Registration failed with status code: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

def verify_database(username):
    """
    Verify that user exists in the database after registration
    """
    logger.info(f"Verifying database state for username: {username}")
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Query for the user
            user = db.query(User).filter(User.username == username).first()
            
            if user:
                logger.info(f"User found in database:")
                logger.info(f"  ID: {user.id}")
                logger.info(f"  Username: {user.username}")
                logger.info(f"  Email: {user.email}")
                logger.info(f"  Full Name: {user.full_name}")
                logger.info(f"  Active: {user.is_active}")
                logger.info(f"  Verified: {user.is_verified}")
                logger.info(f"  Created At: {user.created_at}")
                return True
            else:
                logger.error(f"User '{username}' not found in database!")
                
                # Log other users in the database for debugging
                users = db.query(User).all()
                logger.info(f"Total users in database: {len(users)}")
                logger.info("Existing users:")
                for u in users:
                    logger.info(f"  {u.id}: {u.username} ({u.email})")
                
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database verification error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_registration()
    logger.info(f"Test completed. Success: {success}")

