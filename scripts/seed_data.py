#!/usr/bin/env python3
"""
Seed script to populate initial data for the portfolio backend.
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.models.content import About, Skill, Project


def create_initial_data():
    """Create initial data for the portfolio."""
    db: Session = SessionLocal()
    try:
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            name="Portfolio Admin",
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        
        # Create initial about content
        about = About(
            content="Welcome to my portfolio! I'm a passionate developer...",
            photo_url="https://example.com/photo.jpg"
        )
        db.add(about)
        
        # Create initial skills
        skills = [
            Skill(name="Python", type="technical", level=5),
            Skill(name="FastAPI", type="technical", level=4),
            Skill(name="PostgreSQL", type="technical", level=4),
            Skill(name="JavaScript", type="technical", level=4),
            Skill(name="React", type="technical", level=3),
            Skill(name="Team Leadership", type="interpersonal", level=4),
            Skill(name="Communication", type="interpersonal", level=5),
        ]
        
        for skill in skills:
            db.add(skill)
        
        # Create sample project
        project = Project(
            name="Portfolio Backend",
            description="A robust FastAPI backend for portfolio management",
            github_url="https://github.com/example/portfolio-backend",
            demo_url="https://portfolio-api.example.com",
            technologies='["Python", "FastAPI", "PostgreSQL", "Docker"]',
            image_url="https://example.com/project-image.jpg"
        )
        db.add(project)
        
        db.commit()
        print("✅ Initial data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating initial data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_data()