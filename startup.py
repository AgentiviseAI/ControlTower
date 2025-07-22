#!/usr/bin/env python3
"""
Startup script for the AI Platform Portal Backend
Handles database initialization and starts the server
"""
import os
import sys
import time
from sqlalchemy import text
from app.core.database import engine, create_tables
from scripts.init_data import initialize_sample_data


def wait_for_database(max_retries=30, delay=2):
    """Wait for database to be available"""
    print("Waiting for database connection...")
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"❌ Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
    
    print("❌ Failed to connect to database after maximum retries")
    return False


def initialize_database():
    """Initialize database tables and sample data"""
    try:
        print("Creating database tables...")
        # Import models to ensure they're registered with Base
        import app.models
        create_tables()
        print("✅ Database tables created successfully!")
        
        print("Initializing sample data...")
        initialize_sample_data()
        print("✅ Sample data initialized successfully!")
        
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def startup_with_db_wait():
    """Startup function that waits for database - use this for Docker"""
    print("🚀 Starting AI Platform Portal Backend...")
    
    # Check environment variables
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("⚠️ DATABASE_URL not set, using default SQLite database")
        # Set SQLite for local development
        os.environ["DATABASE_URL"] = "sqlite:///./ai_platform.db"
    else:
        print(f"📊 Using database: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    # For SQLite, skip waiting for database connection
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        print("✅ Using SQLite database - no connection wait needed")
    else:
        # Wait for database (PostgreSQL)
        if not wait_for_database():
            sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    print("✅ Backend startup completed successfully!")
    print("🌐 Starting FastAPI server...")
    return True


def main():
    """Main startup function"""
    return startup_with_db_wait()


if __name__ == "__main__":
    main()
