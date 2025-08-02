from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional


class UserService:
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email address."""
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        db_user = User(**user_data.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_user_from_oauth(self, db: Session, email: str, name: str) -> User:
        """Create user from OAuth data."""
        user_data = UserCreate(
            email=email,
            name=name,
            role="admin",
            is_active=True
        )
        return self.create_user(db, user_data)

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update existing user."""
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return db_user


# Global service instance
user_service = UserService()