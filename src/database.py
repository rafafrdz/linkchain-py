import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
import time
from sqlalchemy import text

# Database connection parameters
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME = os.getenv("POSTGRES_DB", "vectordb")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# SQLAlchemy setup
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Document model
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384))  # Dimension depends on the model, 384 for all-MiniLM-L6-v2

def get_db_session():
    """
    Get a database session
    """
    return SessionLocal()

def init_db():
    """
    Initialize the database, create tables and pgvector extension
    """
    # Wait for PostgreSQL to be ready
    max_retries = 10
    retry_interval = 5

    for i in range(max_retries):
        try:
            # Try to connect to the database
            conn = engine.connect()
            conn.close()
            break
        except Exception as e:
            if i < max_retries - 1:
                print(f"Database not ready yet, retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                raise Exception(f"Could not connect to database after {max_retries} attempts: {str(e)}")

    # Create pgvector extension if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")
