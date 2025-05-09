import logging
import sqlite3
import os
from sqlalchemy import inspect
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file directly
load_dotenv()

# Get DATABASE_URL from environment directly
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

from app.database.database import engine, Base, SessionLocal
from app.models.user import User

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_sqlite_structure():
    """Check database structure using SQLite directly"""
    logger.info("Checking database structure using SQLite...")
    
    # Parse database URL to get the correct path
    logger.info(f"DATABASE_URL from environment: {DATABASE_URL}")
    
    if DATABASE_URL.startswith("sqlite:///"):
        # Extract the path part from the URL
        db_path_str = DATABASE_URL[10:]  # Remove 'sqlite:///'
        
        # Handle relative paths
        if db_path_str.startswith('./'):
            # Relative to current directory
            db_path = Path.cwd() / db_path_str[2:]
            logger.info(f"Relative path detected, resolved to: {db_path}")
        elif db_path_str.startswith('/'):
            # Absolute path
            db_path = Path(db_path_str)
            logger.info(f"Absolute path detected: {db_path}")
        else:
            # Default case
            db_path = Path.cwd() / db_path_str
            logger.info(f"Default path resolution: {db_path}")
    else:
        logger.error(f"Non-SQLite database URL or unsupported format: {DATABASE_URL}")
        return False
    
    # Check if file exists
    logger.info(f"Checking for database file at: {db_path.absolute()}")
    if not db_path.exists():
        logger.error(f"Database file not found at {db_path.absolute()}")
        
        # Additional checks to help troubleshoot
        parent_dir = db_path.parent
        logger.info(f"Parent directory: {parent_dir}")
        if parent_dir.exists():
            logger.info(f"Parent directory exists. Contents:")
            for item in parent_dir.iterdir():
                logger.info(f"  - {item.name} ({'directory' if item.is_dir() else 'file'})")
        else:
            logger.error(f"Parent directory does not exist: {parent_dir}")
            
        return False
    
    logger.info(f"Found database at {db_path.absolute()}")
    logger.info(f"File size: {db_path.stat().st_size} bytes")
    
    try:
        # Connect to the SQLite database using the correct path
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        logger.info(f"Tables in database: {table_names}")
        
        # Check if users table exists
        if 'users' not in table_names:
            logger.error("Users table not found in database")
            return False
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        logger.info("Users table structure:")
        column_names = []
        for col in columns:
            column_names.append(col[1])  # Column name is at index 1
            logger.info(f"  Column: {col}")
        
        # Check for hashed_password column
        if 'hashed_password' not in column_names:
            logger.error("hashed_password column not found in users table")
            return False
        
        logger.info("hashed_password column found in users table")
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error checking SQLite structure: {str(e)}")
        return False

def check_sqlalchemy_mapping():
    """Check SQLAlchemy model mapping"""
    logger.info("Checking SQLAlchemy model mapping...")
    
    try:
        # Get User model inspector
        inspector = inspect(User)
        
        # Get mapped columns
        columns = [column.key for column in inspector.columns]
        logger.info(f"User model mapped columns: {columns}")
        
        # Check if hashed_password is mapped
        if 'hashed_password' not in columns:
            logger.error("hashed_password not mapped in User model")
            return False
        
        logger.info("User model is properly mapped with hashed_password column")
        
        # Verify we can query the database
        db = SessionLocal()
        try:
            # Just do a simple count query to verify connectivity
            count = db.query(User).count()
            logger.info(f"Database contains {count} users")
            
            # Try to get first user if exists
            if count > 0:
                first_user = db.query(User).first()
                logger.info(f"First user ID: {first_user.id}, Username: {first_user.username}")
                logger.info(f"First user has hashed_password: {'Yes' if first_user.hashed_password else 'No'}")
            
            return True
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            return False
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error checking SQLAlchemy mapping: {str(e)}")
        return False

def verify_database():
    """Verify database schema and model mapping"""
    logger.info("Starting database verification...")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    sqlite_ok = check_sqlite_structure()
    sqlalchemy_ok = check_sqlalchemy_mapping()
    
    if sqlite_ok and sqlalchemy_ok:
        logger.info("Database verification completed successfully!")
        return True
    else:
        logger.error("Database verification failed!")
        return False

if __name__ == "__main__":
    verify_database()

