from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any

from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWSError
import os
import logging
import bcrypt
import random
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User

# Load environment variables
load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7))

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        # Convert password to bytes if it's a string
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        
        # Convert hashed password to bytes if it's a string
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
            
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        logging.error(f"Password verification failed: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    try:
        # Convert password to bytes if it's a string
        if isinstance(password, str):
            password = password.encode('utf-8')
            
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)
        
        # Return the hashed password as a string
        return hashed_password.decode('utf-8')
    except Exception as e:
        logging.error(f"Password hashing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password processing error"
        )

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    
    # Ensure sub is a string
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    # Always use current time as the base
    current_time = datetime.utcnow()
    
    # Add a unique timestamp component to ensure tokens are unique
    # Add a small random component to the expiration time (milliseconds)
    # This ensures each token created has a unique expiration time
    random_milliseconds = random.randint(1, 999) / 1000.0
    
    if expires_delta:
        expire = current_time + expires_delta + timedelta(seconds=random_milliseconds)
    else:
        expire = current_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES, seconds=random_milliseconds)
    
    # Add issued at time to ensure token uniqueness
    to_encode.update({
        "exp": expire, 
        "type": "access",
        "iat": current_time,
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a new JWT refresh token with longer expiry."""
    to_encode = data.copy()
    
    # Ensure sub is a string
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
        
    # Always use current time as the base
    current_time = datetime.utcnow()
    
    # Add a unique timestamp component to ensure tokens are unique
    # Add a small random component to the expiration time (milliseconds)
    random_milliseconds = random.randint(1, 999) / 1000.0
    
    expire = current_time + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS, seconds=random_milliseconds)
    
    # Add issued at time to ensure token uniqueness
    to_encode.update({
        "exp": expire, 
        "type": "refresh",
        "iat": current_time,
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str, token_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Decode a JWT token and return the payload.
    Optionally verify the token is of a specific type (access or refresh).
    """
    if not SECRET_KEY:
        logging.error("JWT_SECRET environment variable is not set")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication system configuration error",
        )
        
    try:
        # First try to decode without verification to check token type
        # This helps provide better error messages for type mismatches
        try:
            unverified_payload = jwt.decode(
                token, 
                SECRET_KEY,
                options={"verify_signature": False, "verify_exp": False},
                algorithms=[ALGORITHM]
            )
            
            # Check token type first if specified
            if token_type and unverified_payload.get("type") != token_type:
                token_type_found = unverified_payload.get("type", "unknown")
                logging.warning(f"Token type mismatch. Expected: {token_type}, got: {token_type_found}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type} token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except (JWTError, JWSError):
            # If we can't decode without verification, it may be an invalid token format
            # Let the next step handle the error with full verification
            pass
            
        # Full verification
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Ensure sub is a string
        if "sub" in payload and not isinstance(payload["sub"], str):
            payload["sub"] = str(payload["sub"])
            
        # Check token type again after full decode
        if token_type and payload.get("type") != token_type:
            token_type_found = payload.get("type", "unknown")
            logging.warning(f"Token type mismatch. Expected: {token_type}, got: {token_type_found}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type} token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
    except ExpiredSignatureError:
        logging.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTClaimsError as e:
        # Special handling for subject claim errors - these could be from using a token with non-existent user ID
        if "Subject" in str(e):
            logging.error(f"Invalid subject claim in token: {str(e)}")
            if token_type == "access":
                # For access tokens, this likely means a non-existent user ID
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                # For other token types
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token claims",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            logging.error(f"Invalid token claims: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, JWSError) as e:
        logging.error(f"Failed to decode token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current user from a JWT access token."""
    try:
        # Explicitly verify this is an access token
        try:
            payload = decode_token(token, token_type="access")
        except HTTPException as e:
            # Pass through specific errors from decode_token
            # Make sure to check if this is a "User not found" error from decode_token
            if e.detail == "User not found":
                logging.warning("Token contains non-existent user ID")
                raise
            # Otherwise, re-raise the exception
            raise
            
        user_id = payload.get("sub")
        if user_id is None:
            logging.warning("Token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token content: missing user identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Convert user_id to int if it's stored as string
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            logging.error(f"Invalid user_id format in token: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identifier format",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions from decode_token
        raise
    except Exception as e:
        logging.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logging.warning(f"User with ID {user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logging.error(f"Database error when retrieving user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Check if the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

