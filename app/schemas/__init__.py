"""Schemas package - centralized imports."""

# Individual domain schemas
from .about import AboutResponse
from .contact import ContactResponse
from .education import EducationResponse
from .experience import ExperienceResponse
from .projects import ProjectResponse
from .site_config import SiteConfigResponse
from .skills import (
    CategoryWithSkillsResponse,
    SkillCategoryResponse,
    SkillNestedResponse,
    SkillResponse,
    SkillsGroupedResponse,
)

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
    "SiteConfigResponse",
]
