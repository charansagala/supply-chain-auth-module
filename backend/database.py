"""
database.py
-----------
This file sets up the connection to the database using SQLAlchemy.

It provides:
- `engine`      : the object that actually talks to the database
- `SessionLocal` : a factory that creates new database sessions
- `Base`         : the base class that all our ORM models (tables) inherit from
- `get_db()`     : a FastAPI dependency that gives each request its own DB session
                    and closes it automatically when the request is done
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from the .env file (DATABASE_URL, JWT_SECRET_KEY, etc.)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Did you create a .env file from .env.example?"
    )

# The engine manages the actual connection pool to the database.
# pool_pre_ping=True checks that a connection is alive before using it.
# connect_args check_same_thread=False is required for SQLite + FastAPI:
# SQLite by default only allows the thread that created the connection to
# use it, but FastAPI uses multiple threads. This flag disables that check.
# (This setting is ignored and harmless for non-SQLite databases like MySQL.)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

# SessionLocal is a "session factory". Every request will call SessionLocal()
# to get its own independent database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all our SQLAlchemy models will inherit from.
# SQLAlchemy uses this to know which classes map to which database tables.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session to each request.

    Usage in a route:
        def some_route(db: Session = Depends(get_db)):
            ...

    The 'yield' pattern makes sure the session is always closed after the
    request finishes, even if an error happens.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
