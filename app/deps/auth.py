from sqlalchemy.orm import Session
from typing import Generator
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Database dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()