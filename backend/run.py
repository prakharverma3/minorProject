#!/usr/bin/env python
import os
import argparse
import uvicorn
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(".")

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Main entry point for running the FastAPI server.
    """
    parser = argparse.ArgumentParser(description="Run the IdeaForge API server")
    
    # Define command line arguments
    parser.add_argument(
        "--host", 
        type=str, 
        default=os.getenv("API_HOST", "0.0.0.0"),
        help="Host to run the server on"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("API_PORT", "8000")),
        help="Port to run the server on"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        default=os.getenv("DEBUG", "true").lower() == "true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--init-db", 
        action="store_true",
        help="Initialize the database before starting"
    )
    parser.add_argument(
        "--with-testdata", 
        action="store_true",
        help="Load test data into the database (only used with --init-db)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize database if requested
    if args.init_db:
        print("Initializing database...")
        from app.database.init_db import init_db, create_test_data
        
        success = init_db()
        if success:
            print("Database initialized successfully!")
            
            if args.with_testdata:
                print("Loading test data...")
                create_test_data()
                print("Test data loaded successfully!")
        else:
            print("Failed to initialize database. Exiting.")
            sys.exit(1)
    
    # Run the server
    print(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()

