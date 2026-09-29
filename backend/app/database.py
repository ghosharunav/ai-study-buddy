"""
Single source of truth for the DB connection.

Base   -> every ORM model inherits from this so SQLAlchemy knows about them
engine -> the actual connection to the SQLite file
get_db -> a FastAPI dependency that hands routes a DB session and always
          closes it afterward, even if the request raises an error
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# check_same_thread=False is required for SQLite when used with FastAPI's
# threaded request handling — SQLite otherwise refuses connections from a
# thread other than the one that created them.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: `db: Session = Depends(get_db)` in any route."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
