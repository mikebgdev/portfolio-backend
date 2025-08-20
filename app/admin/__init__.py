"""Admin package for SQLAdmin configuration."""
from .base import create_admin
from .views import register_admin_views

__all__ = ["create_admin", "register_admin_views"]