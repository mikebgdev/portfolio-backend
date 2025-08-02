import pytest
from fastapi.testclient import TestClient

from app.models.content import About, Skill, Project


class TestAboutAPI:
    """Integration tests for About API endpoints."""

    def test_get_about_exists(self, client, db, sample_about_data):
        """Test getting about content when it exists."""
        # Create about record
        about = About(**sample_about_data)
        db.add(about)
        db.commit()
        
        response = client.get("/api/v1/about/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == sample_about_data["content"]
        assert data["photo_url"] == sample_about_data["photo_url"]

    def test_get_about_not_found(self, client):
        """Test getting about content when none exists."""
        response = client.get("/api/v1/about/")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_about_success(self, authenticated_client, mock_current_user):
        """Test updating about content with admin authentication."""
        update_data = {
            "content": "Updated about content",
            "photo_url": "https://example.com/new-photo.jpg"
        }
        
        response = authenticated_client.put("/api/v1/about/", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == update_data["content"]
        assert data["photo_url"] == update_data["photo_url"]

    def test_update_about_unauthorized(self, client, sample_about_data):
        """Test updating about content without authentication."""
        response = client.put("/api/v1/about/", json=sample_about_data)
        
        assert response.status_code == 403

    def test_update_about_partial(self, authenticated_client, mock_current_user, db, sample_about_data):
        """Test partial update of about content."""
        # Create initial about record
        about = About(**sample_about_data)
        db.add(about)
        db.commit()
        
        # Partial update (only content)
        update_data = {"content": "Only content updated"}
        
        response = authenticated_client.put("/api/v1/about/", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Only content updated"
        assert data["photo_url"] == sample_about_data["photo_url"]  # Unchanged


class TestSkillsAPI:
    """Integration tests for Skills API endpoints."""

    def test_get_skills_empty(self, client):
        """Test getting skills when none exist."""
        response = client.get("/api/v1/skills/")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_skills_with_data(self, client, db, sample_skill_data):
        """Test getting skills when they exist."""
        # Create test skills
        skills_data = [
            {"name": "Python", "type": "technical", "level": 5},
            {"name": "JavaScript", "type": "technical", "level": 4},
            {"name": "Communication", "type": "interpersonal", "level": 5}
        ]
        
        for skill_data in skills_data:
            skill = Skill(**skill_data)
            db.add(skill)
        db.commit()
        
        response = client.get("/api/v1/skills/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_skills_filtered_by_type(self, client, db):
        """Test getting skills filtered by type."""
        # Create skills of different types
        skills_data = [
            {"name": "Python", "type": "technical", "level": 5},
            {"name": "Communication", "type": "interpersonal", "level": 5}
        ]
        
        for skill_data in skills_data:
            skill = Skill(**skill_data)
            db.add(skill)
        db.commit()
        
        # Test technical skills filter
        response = client.get("/api/v1/skills/?skill_type=technical")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "technical"
        
        # Test interpersonal skills filter
        response = client.get("/api/v1/skills/?skill_type=interpersonal")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "interpersonal"

    def test_create_skill_success(self, authenticated_client, mock_current_user, sample_skill_data):
        """Test creating a new skill with admin authentication."""
        response = authenticated_client.post("/api/v1/skills/", json=sample_skill_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_skill_data["name"]
        assert data["type"] == sample_skill_data["type"]
        assert data["level"] == sample_skill_data["level"]

    def test_create_skill_unauthorized(self, client, sample_skill_data):
        """Test creating skill without authentication."""
        response = client.post("/api/v1/skills/", json=sample_skill_data)
        
        assert response.status_code == 403

    def test_update_skill_success(self, authenticated_client, mock_current_user, db, sample_skill_data):
        """Test updating an existing skill."""
        # Create skill
        skill = Skill(**sample_skill_data)
        db.add(skill)
        db.commit()
        
        update_data = {"name": "Advanced Python", "level": 5}
        
        response = authenticated_client.put(f"/api/v1/skills/{skill.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Advanced Python"
        assert data["level"] == 5

    def test_update_skill_not_found(self, authenticated_client, mock_current_user):
        """Test updating non-existent skill."""
        update_data = {"name": "Non-existent"}
        
        response = authenticated_client.put("/api/v1/skills/999", json=update_data)
        
        assert response.status_code == 404

    def test_delete_skill_success(self, authenticated_client, mock_current_user, db, sample_skill_data):
        """Test deleting a skill."""
        # Create skill
        skill = Skill(**sample_skill_data)
        db.add(skill)
        db.commit()
        skill_id = skill.id
        
        response = authenticated_client.delete(f"/api/v1/skills/{skill_id}")
        
        assert response.status_code == 204
        
        # Verify deletion
        deleted_skill = db.query(Skill).filter(Skill.id == skill_id).first()
        assert deleted_skill is None

    def test_delete_skill_not_found(self, authenticated_client, mock_current_user):
        """Test deleting non-existent skill."""
        response = authenticated_client.delete("/api/v1/skills/999")
        
        assert response.status_code == 404


class TestProjectsAPI:
    """Integration tests for Projects API endpoints."""

    def test_get_projects_empty(self, client):
        """Test getting projects when none exist."""
        response = client.get("/api/v1/projects/")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_create_project_success(self, authenticated_client, mock_current_user, sample_project_data):
        """Test creating a new project."""
        response = authenticated_client.post("/api/v1/projects/", json=sample_project_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["github_url"] == sample_project_data["github_url"]

    def test_create_project_unauthorized(self, client, sample_project_data):
        """Test creating project without authentication."""
        response = client.post("/api/v1/projects/", json=sample_project_data)
        
        assert response.status_code == 403

    def test_get_project_by_id(self, client, db, sample_project_data):
        """Test getting specific project by ID."""
        # Create project
        project = Project(**sample_project_data)
        db.add(project)
        db.commit()
        
        response = client.get(f"/api/v1/projects/{project.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_project_data["name"]

    def test_get_project_not_found(self, client):
        """Test getting non-existent project."""
        response = client.get("/api/v1/projects/999")
        
        assert response.status_code == 404