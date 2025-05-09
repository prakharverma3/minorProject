import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import jwt
import os
from unittest.mock import patch, MagicMock

from app.main import app
from app.database.database import Base, get_db
from app.models.user import User
from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    SECRET_KEY,
    ALGORITHM
)

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test client
client = TestClient(app)

# Test user data
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "bio": "Test user bio",
    "profile_image_url": None
}


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client_with_db(test_db):
    """Create a test client with a dependency override for the database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def registered_user(client_with_db, test_db):
    """Create a test user in the database."""
    # Register a test user
    response = client_with_db.post("/api/auth/register", json=test_user)
    assert response.status_code == 201
    
    # Get the user from the database
    db_user = test_db.query(User).filter(User.username == test_user["username"]).first()
    assert db_user is not None
    
    return db_user


@pytest.fixture
def auth_tokens(client_with_db, registered_user):
    """Get authentication tokens for the test user."""
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client_with_db.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    return tokens


# Test password hashing and verification
def test_password_hashing():
    """Test that password hashing and verification work correctly."""
    password = "test_password"
    hashed = get_password_hash(password)
    
    # Ensure hashed password is not the same as the original
    assert hashed != password
    
    # Verify the password
    assert verify_password(password, hashed) is True
    
    # Verify incorrect password fails
    assert verify_password("wrong_password", hashed) is False


# Test registration
def test_user_registration(client_with_db):
    """Test user registration process."""
    # Register a new user
    response = client_with_db.post("/api/auth/register", json=test_user)
    assert response.status_code == 201
    
    # Check response format
    user_data = response.json()
    assert user_data["username"] == test_user["username"]
    assert user_data["email"] == test_user["email"]
    assert "id" in user_data
    assert "hashed_password" not in user_data  # Password should not be returned


def test_duplicate_username_registration(client_with_db, registered_user):
    """Test registration with duplicate username is rejected."""
    # Try to register with the same username
    duplicate_user = test_user.copy()
    duplicate_user["email"] = "different@example.com"  # Different email
    
    response = client_with_db.post("/api/auth/register", json=duplicate_user)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_duplicate_email_registration(client_with_db, registered_user):
    """Test registration with duplicate email is rejected."""
    # Try to register with the same email
    duplicate_user = test_user.copy()
    duplicate_user["username"] = "differentuser"  # Different username
    
    response = client_with_db.post("/api/auth/register", json=duplicate_user)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


# Test login
def test_user_login(client_with_db, registered_user):
    """Test user login process."""
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    response = client_with_db.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    # Check tokens are returned
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_with_wrong_password(client_with_db, registered_user):
    """Test login with incorrect password is rejected."""
    login_data = {
        "username": test_user["username"],
        "password": "wrong_password"
    }
    
    response = client_with_db.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_with_nonexistent_user(client_with_db):
    """Test login with non-existent user is rejected."""
    login_data = {
        "username": "nonexistentuser",
        "password": "somepassword"
    }
    
    response = client_with_db.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


# Test token refresh
def test_token_refresh(client_with_db, auth_tokens):
    """Test refreshing an access token with a refresh token."""
    refresh_data = {
        "token": auth_tokens["refresh_token"]
    }
    
    response = client_with_db.post("/api/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    
    # Check new tokens are returned
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["token_type"] == "bearer"
    
    # Verify tokens are different
    assert new_tokens["access_token"] != auth_tokens["access_token"]
    assert new_tokens["refresh_token"] != auth_tokens["refresh_token"]


def test_refresh_with_access_token(client_with_db, auth_tokens):
    """Test that using an access token for refresh is rejected."""
    refresh_data = {
        "token": auth_tokens["access_token"]  # Using access token instead of refresh token
    }
    
    response = client_with_db.post("/api/auth/refresh", json=refresh_data)
    assert response.status_code == 401
    assert "Invalid token type" in response.json()["detail"]


def test_refresh_with_invalid_token(client_with_db):
    """Test that using an invalid token for refresh is rejected."""
    refresh_data = {
        "token": "invalid_token"
    }
    
    response = client_with_db.post("/api/auth/refresh", json=refresh_data)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_refresh_with_expired_token(client_with_db, registered_user):
    """Test that using an expired refresh token is rejected."""
    # Create an expired refresh token
    token_data = {"sub": registered_user.id, "type": "refresh"}
    expire = datetime.utcnow() - timedelta(days=1)  # Token expired 1 day ago
    token_data.update({"exp": expire})
    expired_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    refresh_data = {
        "token": expired_token
    }
    
    response = client_with_db.post("/api/auth/refresh", json=refresh_data)
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]


# Test protected endpoint access
def test_get_me_endpoint(client_with_db, auth_tokens):
    """Test accessing the /me endpoint with valid token."""
    headers = {
        "Authorization": f"Bearer {auth_tokens['access_token']}"
    }
    
    response = client_with_db.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    
    # Check response data
    user_data = response.json()
    assert user_data["username"] == test_user["username"]
    assert user_data["email"] == test_user["email"]
    assert "hashed_password" not in user_data


def test_get_me_without_token(client_with_db):
    """Test accessing the /me endpoint without a token."""
    response = client_with_db.get("/api/auth/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_me_with_invalid_token(client_with_db):
    """Test accessing the /me endpoint with an invalid token."""
    headers = {
        "Authorization": "Bearer invalid_token"
    }
    
    response = client_with_db.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_get_me_with_refresh_token(client_with_db, auth_tokens):
    """Test that using a refresh token for accessing /me is rejected."""
    headers = {
        "Authorization": f"Bearer {auth_tokens['refresh_token']}"
    }
    
    response = client_with_db.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "Invalid token type" in response.json()["detail"]


# Additional edge cases
def test_nonexistent_user_in_token(client_with_db, registered_user):
    """Test using a token with a non-existent user ID."""
    # Create a token with a non-existent user ID
    non_existent_id = registered_user.id + 999  # Assuming this ID doesn't exist
    token_data = {"sub": non_existent_id, "type": "access"}
    expire = datetime.utcnow() + timedelta(minutes=30)
    token_data.update({"exp": expire})
    invalid_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    headers = {
        "Authorization": f"Bearer {invalid_token}"
    }
    
    response = client_with_db.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "User not found" in response.json()["detail"]


def test_login_with_inactive_user(client_with_db, registered_user, test_db):
    """Test login with an inactive user is rejected."""
    # Deactivate the user
    registered_user.is_active = False
    test_db.commit()
    
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    response = client_with_db.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Account is inactive" in response.json()["detail"]

