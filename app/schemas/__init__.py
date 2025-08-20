"""Schemas package - centralized imports."""

# Individual domain schemas
from .about import AboutResponse
from .contact import ContactResponse
from .education import EducationResponse
from .experience import ExperienceResponse
from .projects import ProjectResponse
from .skills import (
    SkillCategoryResponse,
    SkillResponse,
    SkillsGroupedResponse,
    SkillNestedResponse,
    CategoryWithSkillsResponse
)
from .site_config import SiteConfigResponse

__all__ = [
    "AboutResponse",
    "ContactResponse",
    "EducationResponse",
    "ExperienceResponse", 
    "ProjectResponse",
    "SkillCategoryResponse",
    "SkillResponse",
    "SkillsGroupedResponse",
    "SkillNestedResponse",
    "CategoryWithSkillsResponse",
    "SiteConfigResponse"
]