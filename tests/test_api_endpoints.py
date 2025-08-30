"""Test API endpoints."""
import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test all public API endpoints."""
    
    def test_about_endpoint(self, client: TestClient, test_data):
        """Test the about endpoint."""
        response = client.get("/api/v1/about/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test"
        assert data["last_name"] == "User"
        assert data["email"] == "test@example.com"
        assert data["language"] == "en"
        assert "available_languages" in data
    
    def test_about_endpoint_spanish(self, client: TestClient, test_data):
        """Test the about endpoint with Spanish language."""
        response = client.get("/api/v1/about/?lang=es")
        assert response.status_code == 200
        
        data = response.json()
        assert data["language"] == "es"
    
    def test_contact_endpoint(self, client: TestClient, test_data):
        """Test the contact endpoint."""
        response = client.get("/api/v1/contact/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == "contact@example.com"
        assert data["contact_form_enabled"] is True
        assert data["language"] == "en"
    
    def test_site_config_endpoint(self, client: TestClient, test_data):
        """Test the site config endpoint."""
        response = client.get("/api/v1/site-config/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["site_title"] == "Test Portfolio"
        assert data["meta_description"] == "Test Description"
        assert data["og_type"] == "website"
    
    def test_skills_endpoint(self, client: TestClient, test_data):
        """Test the skills endpoint."""
        response = client.get("/api/v1/skills/")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        category = data["categories"][0]
        assert category["id"] == "test"
        assert category["label"] == "Test Category"
        assert len(category["skills"]) > 0
        
        skill = category["skills"][0]
        assert skill["name"] == "Test Skill"
    
    def test_projects_endpoint(self, client: TestClient, test_data):
        """Test the projects endpoint."""
        response = client.get("/api/v1/projects/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        project = data[0]
        assert project["title_en"] == "Test Project"
        assert project["title_es"] == "Proyecto de Prueba"
        assert project["technologies"] == ["Python", "FastAPI"]
        assert project["language"] == "en"
    
    def test_experience_endpoint(self, client: TestClient, test_data):
        """Test the experience endpoint."""
        response = client.get("/api/v1/experience/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        experience = data[0]
        assert experience["company"] == "Test Company"
        assert experience["position_en"] == "Test Position"
        assert experience["language"] == "en"
    
    def test_education_endpoint(self, client: TestClient, test_data):
        """Test the education endpoint."""
        response = client.get("/api/v1/education/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        education = data[0]
        assert education["institution"] == "Test University"
        assert education["degree_en"] == "Test Degree"
        assert education["language"] == "en"
    
    def test_invalid_language_defaults_to_english(self, client: TestClient, test_data):
        """Test that invalid language parameter defaults to English."""
        response = client.get("/api/v1/about/?lang=invalid")
        assert response.status_code == 200
        
        data = response.json()
        assert data["language"] == "en"
    
    def test_admin_redirect_without_auth(self, client: TestClient):
        """Test admin redirect when not authenticated."""
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code == 302
        assert "/admin/login" in response.headers["location"]
    
    def test_nonexistent_endpoint_returns_404(self, client: TestClient):
        """Test that non-existent endpoints return 404."""
        response = client.get("/api/v1/nonexistent/")
        assert response.status_code == 404


class TestAPIErrorHandling:
    """Test API error handling."""
    
    def test_about_endpoint_without_data(self, client: TestClient, db_session):
        """Test about endpoint when no data exists."""
        response = client.get("/api/v1/about/")
        assert response.status_code == 404
    
    def test_contact_endpoint_without_data(self, client: TestClient, db_session):
        """Test contact endpoint when no data exists."""
        response = client.get("/api/v1/contact/")
        assert response.status_code == 404
    
    def test_site_config_endpoint_without_data(self, client: TestClient, db_session):
        """Test site config endpoint when no data exists."""
        response = client.get("/api/v1/site-config/")
        assert response.status_code == 404


class TestAPIResponseFormat:
    """Test API response format consistency."""
    
    def test_all_endpoints_return_json(self, client: TestClient, test_data):
        """Test that all endpoints return JSON."""
        endpoints = [
            "/api/v1/about/",
            "/api/v1/contact/",
            "/api/v1/site-config/",
            "/api/v1/skills/",
            "/api/v1/projects/",
            "/api/v1/experience/",
            "/api/v1/education/"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"
    
    def test_multilingual_endpoints_include_language(self, client: TestClient, test_data):
        """Test that multilingual endpoints include language field."""
        multilingual_endpoints = [
            "/api/v1/about/",
            "/api/v1/contact/",
            "/api/v1/projects/",
            "/api/v1/experience/",
            "/api/v1/education/"
        ]
        
        for endpoint in multilingual_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            data = response.json()
            if isinstance(data, list):
                for item in data:
                    assert "language" in item
            else:
                assert "language" in data