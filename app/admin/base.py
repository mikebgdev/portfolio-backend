"""Base admin configuration and authentication."""

from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.config import settings
from app.database import engine


class AdminAuth(AuthenticationBackend):
    """Authentication backend for SQLAdmin."""

    async def login(self, request: Request) -> bool:
        """Handle admin login."""
        form = await request.form()
        username, password = form["username"], form["password"]

        # Use the same authentication as API
        from app.auth.oauth import AuthService
        from app.database import SessionLocal
        from app.models.user import User

        auth_service = AuthService()
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == username).first()
            if (
                user
                and user.is_active
                and auth_service.verify_password(str(password), str(user.password_hash))
            ):
                # Store user info in session
                request.session.update(
                    {
                        "user_id": user.id,
                        "user_email": user.email,
                        "user_role": user.role,
                        "authenticated": True,
                    }
                )
                return True
        finally:
            db.close()
        return False

    async def logout(self, request: Request) -> bool:
        """Handle admin logout."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        """Check if user is authenticated."""
        return request.session.get("authenticated", False)


# Create authentication backend
authentication_backend = AdminAuth(secret_key=settings.secret_key)


def create_admin(app):
    """Create and configure SQLAdmin instance."""
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="Portfolio Admin Panel",
        logo_url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
        templates_dir="templates",
        # Fix for Coolify deployment - ensure proper static file serving
        debug=settings.debug,
    )
    return admin
