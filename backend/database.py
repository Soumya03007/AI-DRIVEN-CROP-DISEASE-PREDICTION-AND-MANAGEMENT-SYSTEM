from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Get the database URI from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure that DATABASE_URL is defined
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a sessionmaker factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Dependency to get DB session in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optionally, create all tables (if you are using this from database.py)
def init_db():
    # Import all models here (so that they are registered with Base.metadata)
    from models import User, Report  # Ensure all models are imported before creating the tables
    
    logging.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)