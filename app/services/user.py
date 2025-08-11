from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.auth.oauth import auth_service
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
        user_dict = user_data.model_dump()
        # Hash password if provided
        if 'password' in user_dict:
            user_dict['password_hash'] = auth_service.get_password_hash(user_dict.pop('password'))
        
        db_user = User(**user_dict)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_user_with_password(self, db: Session, email: str, name: str, password: str, role: str = "admin") -> User:
        """Create user with password."""
        db_user = User(
            email=email,
            name=name,
            password_hash=auth_service.get_password_hash(password),
            role=role,
            is_active=True
        )
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