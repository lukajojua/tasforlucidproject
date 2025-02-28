import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# loads env variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Provides a database session for a request.

    This function is used by FastAPI to inject a database session into
    route handlers. The session is automatically closed after the request
    is processed to free resources.

    Yields:
        Session: A SQLAlchemy Session instance.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
