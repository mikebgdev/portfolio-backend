"""Services package - centralized imports."""

# Individual domain services
from .about import about_service
from .contact import contact_service
from .education import education_service
from .experience import experience_service
from .projects import project_service
from .site_config import site_config_service
from .skills import skill_category_service, skill_service

__all__ = [
    "about_service",
    "contact_service",
    "education_service",
    "experience_service",
    "project_service",
    "skill_service",
    "skill_category_service",
    "site_config_service",
]
