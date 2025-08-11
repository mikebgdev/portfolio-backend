from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import engine
from app.models.user import User
from app.models.content import About, Skill, Project, Experience, Education


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        
        # Use the same authentication as API
        from app.database import SessionLocal
        from app.models.user import User
        from app.auth.oauth import auth_service
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == username).first()
            if user and user.is_active and auth_service.verify_password(password, user.password_hash):
                # Store user info in session
                request.session.update({
                    "user_id": user.id,
                    "user_email": user.email,
                    "user_role": user.role,
                    "authenticated": True
                })
                return True
        finally:
            db.close()
        return False

    async def logout(self, request: Request) -> bool:
        # Clear session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("authenticated", False)


authentication_backend = AdminAuth(secret_key="your-admin-secret-key")

# Create admin instance - we'll initialize it in main.py
def create_admin(app):
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="Portfolio Admin Panel",
        logo_url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    )
    return admin


# User Admin View
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.name, User.role, User.is_active, User.created_at]
    column_searchable_list = [User.email, User.name]
    column_sortable_list = [User.id, User.email, User.name, User.created_at]
    column_details_exclude_list = [User.created_at, User.updated_at]
    can_delete = False  # Prevent accidental user deletion
    
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


# About Admin View
class AboutAdmin(ModelView, model=About):
    column_list = [About.id, About.content, About.photo_url, About.updated_at]
    column_details_exclude_list = [About.updated_at]
    form_columns = [About.content, About.photo_url]
    
    name = "About"
    name_plural = "About"
    icon = "fa-solid fa-info-circle"


# Skill Admin View
class SkillAdmin(ModelView, model=Skill):
    column_list = [Skill.id, Skill.name, Skill.type, Skill.level, Skill.created_at]
    column_searchable_list = [Skill.name, Skill.type]
    column_sortable_list = [Skill.id, Skill.name, Skill.type, Skill.level, Skill.created_at]
    column_details_exclude_list = [Skill.created_at]
    form_columns = [Skill.name, Skill.type, Skill.level]
    
    name = "Skill"
    name_plural = "Skills"
    icon = "fa-solid fa-cog"


# Project Admin View
class ProjectAdmin(ModelView, model=Project):
    column_list = [Project.id, Project.name, Project.description, Project.github_url, Project.created_at]
    column_searchable_list = [Project.name, Project.description, Project.technologies]
    column_sortable_list = [Project.id, Project.name, Project.created_at]
    column_details_exclude_list = [Project.created_at]
    form_columns = [Project.name, Project.description, Project.github_url, Project.demo_url, Project.technologies, Project.image_url]
    
    name = "Project"
    name_plural = "Projects" 
    icon = "fa-solid fa-folder"


# Experience Admin View
class ExperienceAdmin(ModelView, model=Experience):
    column_list = [Experience.id, Experience.company, Experience.position, Experience.start_date, Experience.end_date]
    column_searchable_list = [Experience.company, Experience.position, Experience.location]
    column_sortable_list = [Experience.id, Experience.company, Experience.start_date, Experience.created_at]
    column_details_exclude_list = [Experience.created_at]
    form_columns = [Experience.company, Experience.position, Experience.description, Experience.start_date, Experience.end_date, Experience.location]
    
    name = "Experience"
    name_plural = "Experience"
    icon = "fa-solid fa-briefcase"


# Education Admin View  
class EducationAdmin(ModelView, model=Education):
    column_list = [Education.id, Education.institution, Education.degree, Education.start_date, Education.end_date]
    column_searchable_list = [Education.institution, Education.degree, Education.field_of_study]
    column_sortable_list = [Education.id, Education.institution, Education.start_date, Education.created_at]
    column_details_exclude_list = [Education.created_at]
    form_columns = [Education.institution, Education.degree, Education.field_of_study, Education.description, Education.start_date, Education.end_date, Education.location, Education.gpa]
    
    name = "Education"
    name_plural = "Education"
    icon = "fa-solid fa-graduation-cap"


def register_admin_views(admin):
    """Register all admin views with the admin instance."""
    admin.add_view(UserAdmin)
    admin.add_view(AboutAdmin)
    admin.add_view(SkillAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(ExperienceAdmin)
    admin.add_view(EducationAdmin)