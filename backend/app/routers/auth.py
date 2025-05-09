from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import timedelta
import logging
import traceback
from pydantic import BaseModel

from app.database.database import get_db
from app.models.user import User
from app.schemas import (
    UserCreate,
    UserResponse,
    Token,
    LoginRequest
)
from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

router = APIRouter()


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    token: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    logging.info(f"Registration attempt for username: {user_data.username}, email: {user_data.email}")
    
    try:
        # Check if username already exists
        if db.query(User).filter(User.username == user_data.username).first():
            logging.warning(f"Registration failed: Username '{user_data.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if db.query(User).filter(User.email == user_data.email).first():
            logging.warning(f"Registration failed: Email '{user_data.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user with hashed password
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            bio=user_data.bio,
            profile_image_url=user_data.profile_image_url,
            is_active=True,
            is_verified=False  # User starts unverified, could add email verification later
        )
        
        try:
            # Begin database transaction
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # Verify that all required fields are present for serialization
            if not hasattr(db_user, 'id') or not db_user.id:
                logging.error("User created but missing ID field")
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to register user. Missing ID field."
                )
            
            # Verify created_at is present for serialization
            if not hasattr(db_user, 'created_at') or not db_user.created_at:
                logging.warning("User created but missing created_at timestamp")
            
            logging.info(f"User registered successfully: {db_user.username}, ID: {db_user.id}")
            
            # Return the user model for serialization - convert to a proper response model
            user_response = UserResponse.model_validate(db_user)
            return user_response
            
        except IntegrityError as e:
            # Handle database integrity errors
            db.rollback()
            logging.error(f"Database integrity error during registration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register. Integrity constraint violation."
            )
        except SQLAlchemyError as e:
            # Handle other SQLAlchemy errors
            db.rollback()
            logging.error(f"Database error during registration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register. Database error occurred."
            )
            
    except HTTPException:
        # Re-raise HTTPExceptions to preserve status codes
        raise
    except Exception as e:
        # Catch any other unexpected errors
        logging.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register. Please try again."
        )


@router.post("/login", response_model=Token)
async def login(request: Request, form_data: LoginRequest, db: Session = Depends(get_db)):
    """Generate access and refresh tokens for user authentication."""
    client_ip = request.client.host if request.client else "unknown"
    logging.info(f"Login attempt for username: {form_data.username} from IP: {client_ip}")
    
    try:
        # Find user by username
        user = db.query(User).filter(User.username == form_data.username).first()
        
        # Check if user exists
        if not user:
            logging.warning(f"Failed login attempt - user not found: {form_data.username} from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Check if password is correct
        if not verify_password(form_data.password, user.hashed_password):
            logging.warning(f"Failed login attempt - incorrect password for user: {form_data.username} from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            logging.warning(f"Login attempt for inactive user: {form_data.username} from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create token payload
        token_data = {"sub": user.id}

        logging.info(f"User successfully authenticated: {user.username} from IP: {client_ip}")
        
        # Generate tokens with explicit expiration times
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Generate tokens
        try:
            access_token = create_access_token(
                token_data, expires_delta=access_token_expires)
            refresh_token = create_refresh_token(token_data)
            
            return {
                "access_token": access_token, 
                "refresh_token": refresh_token, 
                "token_type": "bearer"
            }
        except Exception as e:
            logging.error(f"Token generation failed for user {user.username}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error",
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error during login: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, refresh_request: RefreshTokenRequest = Body(...), db: Session = Depends(get_db)):
    """Generate a new access token using a refresh token.
    
    The token should be provided in the request body as a JSON object: {"token": "your-refresh-token"}
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        logging.info(f"Attempting to refresh token from IP: {client_ip}")
        
        # Get token from request
        token = refresh_request.token
        
        # Validate token is present
        if not token:
            logging.error(f"Empty token provided in refresh request from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is required",
            )
            
        try:
            # Use the token_type parameter to explicitly verify this is a refresh token
            payload = decode_token(token, token_type="refresh")
        except HTTPException as e:
            # Pass through HTTP exceptions from token validation
            logging.error(f"Token validation failed during refresh from IP: {client_ip}: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Failed to decode refresh token from IP: {client_ip}: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if user_id is None:
            logging.error("Token missing user ID (sub)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Find user in database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logging.error(f"User with ID {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user.is_active:
            logging.error(f"User with ID {user_id} is inactive")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        logging.info(f"Token refresh successful for user ID: {user.id}")
        
        # Create token data with a unique nonce to ensure new tokens
        # This guarantees the tokens will be different even if created in the same second
        import time
        import random
        
        token_data = {
            "sub": user.id,
            # Add a unique nonce value to ensure tokens are always different
            "nonce": f"{time.time()}-{random.randint(1000, 9999)}"
        }
        
        # Force a slightly different expiration time to ensure token uniqueness
        # Add a small random offset to standard expiration time
        random_minutes_offset = random.uniform(0.1, 0.9)  # Between 0.1 and 0.9 minutes
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES + random_minutes_offset)
        
        # Create tokens with the new data and expiration
        access_token = create_access_token(
            token_data, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(token_data)
        
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status code and details
        raise
    except Exception as e:
        logging.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    """Get current user information from token."""
    client_ip = request.client.host if request.client else "unknown"
    logging.info(f"User {current_user.username} (ID: {current_user.id}) accessed profile data from IP: {client_ip}")
    
    # Collect user information for the response
    try:
        return current_user
    except Exception as e:
        logging.error(f"Error retrieving user profile for {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )

