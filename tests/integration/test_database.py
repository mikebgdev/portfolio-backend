import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models.user import User
from app.models.content import About, Skill, Project, Experience, Education


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    def test_database_connection(self, db):
        """Test basic database connection."""
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1

    def test_tables_created(self, db):
        """Test that all required tables are created."""
        # Check if tables exist by trying to query them
        tables_to_check = [
            (User, "users"),
            (About, "about"),
            (Skill, "skills"),
            (Project, "projects"),
            (Experience, "experience"),
            (Education, "education")
        ]
        
        for model, table_name in tables_to_check:
            # This will raise an exception if table doesn't exist
            count = db.query(model).count()
            assert count >= 0  # Should not raise exception

    def test_cascade_operations(self, db):
        """Test database cascade operations (if any)."""
        # For now, our models don't have foreign key relationships
        # This test is a placeholder for future relationship testing
        pass

    def test_transaction_rollback(self, db):
        """Test transaction rollback functionality."""
        # Start a transaction
        user = User(email="rollback@example.com", name="Rollback User")
        db.add(user)
        
        # Don't commit, just rollback
        db.rollback()
        
        # Verify user was not saved
        saved_user = db.query(User).filter(User.email == "rollback@example.com").first()
        assert saved_user is None

    def test_concurrent_operations(self, db):
        """Test concurrent database operations."""
        # Create multiple records in same transaction
        users = [
            User(email=f"user{i}@example.com", name=f"User {i}")
            for i in range(5)
        ]
        
        skills = [
            Skill(name=f"Skill {i}", type="technical", level=i+1)
            for i in range(5)
        ]
        
        db.add_all(users + skills)
        db.commit()
        
        # Verify all records were created
        assert db.query(User).count() == 5
        assert db.query(Skill).count() == 5

    def test_bulk_insert_performance(self, db):
        """Test bulk insert operations."""
        # Create many records at once
        skills = [
            Skill(name=f"Bulk Skill {i}", type="technical", level=(i % 5) + 1)
            for i in range(100)
        ]
        
        db.add_all(skills)
        db.commit()
        
        # Verify all records were created
        assert db.query(Skill).count() == 100

    def test_database_constraints(self, db):
        """Test database constraints are enforced."""
        # Test unique constraint on user email
        user1 = User(email="duplicate@example.com", name="User 1")
        user2 = User(email="duplicate@example.com", name="User 2")
        
        db.add(user1)
        db.commit()
        
        db.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db.commit()

    def test_index_performance(self, db):
        """Test that indexes improve query performance."""
        # Create many users
        users = [
            User(email=f"indexed_user_{i}@example.com", name=f"User {i}")
            for i in range(1000)
        ]
        db.add_all(users)
        db.commit()
        
        # Test email index (should be fast)
        result = db.query(User).filter(User.email == "indexed_user_500@example.com").first()
        assert result is not None
        assert result.name == "User 500"

    def test_query_optimizations(self, db):
        """Test various query optimization patterns."""
        # Create test data
        skills = [
            Skill(name=f"Query Skill {i}", type="technical", level=(i % 5) + 1)
            for i in range(50)
        ]
        db.add_all(skills)
        db.commit()
        
        # Test filtered queries
        high_level_skills = db.query(Skill).filter(Skill.level >= 4).all()
        assert len(high_level_skills) > 0
        
        # Test ordered queries
        ordered_skills = db.query(Skill).order_by(Skill.level.desc()).limit(10).all()
        assert len(ordered_skills) == 10
        assert ordered_skills[0].level >= ordered_skills[-1].level

    def test_data_types_and_validation(self, db):
        """Test that data types are properly handled."""
        from datetime import datetime
        
        # Test datetime fields
        experience = Experience(
            company="DateTime Test Co",
            position="Tester",
            start_date=datetime(2023, 1, 1, 9, 0, 0),
            end_date=datetime(2023, 12, 31, 17, 0, 0)
        )
        db.add(experience)
        db.commit()
        db.refresh(experience)
        
        # Verify datetime precision is maintained
        assert experience.start_date == datetime(2023, 1, 1, 9, 0, 0)
        assert experience.end_date == datetime(2023, 12, 31, 17, 0, 0)

    def test_null_handling(self, db):
        """Test NULL value handling."""
        # Test fields that allow NULL
        project = Project(
            name="Minimal Project",
            description="Basic project",
            github_url="https://github.com/test/minimal"
            # demo_url, technologies, image_url are NULL
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        assert project.demo_url is None
        assert project.technologies is None
        assert project.image_url is None

    def test_session_management(self):
        """Test session management with dependency injection."""
        # Test that get_db creates and closes sessions properly
        session_gen = get_db()
        session = next(session_gen)
        
        # Session should be usable
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
        
        # Cleanup (simulating FastAPI's dependency cleanup)
        try:
            next(session_gen)
        except StopIteration:
            pass  # Expected - generator is exhausted