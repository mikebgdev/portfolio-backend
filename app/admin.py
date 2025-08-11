from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from wtforms import SelectField, BooleanField
from wtforms.validators import DataRequired
from app.database import engine
from app.models.user import User
from app.models.content import About, Skill, Project, Experience, Education, Contact


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
    
    # Custom labels for better UX
    column_labels = {
        "email": "Email",
        "name": "Nombre",
        "role": "Rol",
        "is_active": "Activo",
        "created_at": "Fecha Creación",
        "updated_at": "Fecha Actualización"
    }
    
    name = "Usuario"
    name_plural = "Usuarios"
    icon = "fa-solid fa-user"


# About Admin View
class AboutAdmin(ModelView, model=About):
    column_list = [About.id, About.name, About.last_name, About.email, About.location, About.birth_month, About.birth_year, About.created_at]
    column_details_exclude_list = [About.updated_at, About.created_at]
    
    # Format datetime columns
    column_formatters = {
        About.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else "",
        About.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M") if m.updated_at else "",
    }
    form_columns = [
        # Personal info
        About.name, About.last_name, About.birth_month, About.birth_year, 
        About.email, About.location, About.photo_url,
        # Nationality (English & Spanish)
        About.nationality_en, About.nationality_es,
        # Bio (English & Spanish)  
        About.bio_en, About.bio_es,
        # Extra content (English & Spanish)
        About.extra_content_en, About.extra_content_es
    ]
    column_searchable_list = [About.name, About.email, About.location]
    
    # Custom labels for better UX
    column_labels = {
        "name": "Nombre",
        "last_name": "Apellidos", 
        "birth_month": "Mes Nacimiento",
        "birth_year": "Año Nacimiento",
        "email": "Email",
        "location": "Ubicación",
        "photo_url": "Foto URL",
        "nationality_en": "Nacionalidad (Inglés)",
        "nationality_es": "Nacionalidad (Español)",
        "bio_en": "Biografía (Inglés)",
        "bio_es": "Biografía (Español)",
        "extra_content_en": "Contenido Extra (Inglés)",
        "extra_content_es": "Contenido Extra (Español)",
        "created_at": "Fecha Creación"
    }
    
    name = "Acerca de"
    name_plural = "Acerca de"
    icon = "fa-solid fa-info-circle"


# Skill Admin View
class SkillAdmin(ModelView, model=Skill):
    column_list = [Skill.id, Skill.name, Skill.category, Skill.display_order, Skill.activa, Skill.is_in_progress]
    column_searchable_list = [Skill.name, Skill.category]
    column_sortable_list = [Skill.id, Skill.name, Skill.category, Skill.display_order, Skill.created_at]
    column_details_exclude_list = [Skill.created_at]
    
    # Format datetime columns
    column_formatters = {
        Skill.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else "",
    }
    form_columns = [
        # Working fields
        Skill.name,
        Skill.category,
        Skill.display_order,
        # Boolean fields - let's try to include them
        Skill.is_in_progress,
        Skill.activa
    ]
    
    # Custom form overrides for boolean fields using SelectField
    form_overrides = {
        "is_in_progress": SelectField,
        "activa": SelectField
    }
    
    form_args = {
        "is_in_progress": {
            "choices": [(True, "Sí"), (False, "No")],
            "coerce": lambda x: x == 'True' if isinstance(x, str) else bool(x)
        },
        "activa": {
            "choices": [(True, "Sí"), (False, "No")], 
            "coerce": lambda x: x == 'True' if isinstance(x, str) else bool(x)
        }
    }
    column_filters = [Skill.category, Skill.is_in_progress, Skill.activa]
    
    # Custom labels for better UX
    column_labels = {
        "name": "Nombre",
        "category": "Categoría",
        "activa": "Activa",
        "is_in_progress": "En Progreso",
        "display_order": "Orden",
        "created_at": "Fecha Creación"
    }
    
    # Note: Boolean fields now use SelectField with Sí/No options
    # This avoids checkbox compatibility issues with SQLAdmin
    
    name = "Habilidad"
    name_plural = "Habilidades"
    icon = "fa-solid fa-cog"


# Project Admin View
class ProjectAdmin(ModelView, model=Project):
    column_list = [Project.id, Project.title_en, Project.title_es, Project.technologies, Project.display_order, Project.activa]
    column_searchable_list = [Project.title_en, Project.title_es, Project.description_en, Project.description_es, Project.technologies]
    column_sortable_list = [Project.id, Project.title_en, Project.display_order, Project.created_at]
    column_details_exclude_list = [Project.created_at]
    
    # Format datetime columns
    column_formatters = {
        Project.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else "",
    }
    form_columns = [
        # Project info (English & Spanish)
        Project.title_en, Project.title_es,
        Project.description_en, Project.description_es,
        # Media and links (no translation needed)
        Project.image_url, Project.technologies,
        Project.source_url, Project.demo_url,
        # Settings (no translation needed)
        Project.display_order,
        # Boolean field
        Project.activa
    ]
    
    # Custom form overrides for boolean fields using SelectField
    form_overrides = {
        "activa": SelectField
    }
    
    form_args = {
        "activa": {
            "choices": [(True, "Sí"), (False, "No")],
            "coerce": lambda x: x == 'True' if isinstance(x, str) else bool(x)
        }
    }
    column_filters = [Project.activa]
    
    # Custom labels for better UX
    column_labels = {
        "title_en": "Título (Inglés)",
        "title_es": "Título (Español)",
        "description_en": "Descripción (Inglés)",
        "description_es": "Descripción (Español)",
        "image_url": "Imagen URL",
        "technologies": "Tecnologías",
        "source_url": "Código Fuente",
        "demo_url": "Demo URL",
        "display_order": "Orden",
        "activa": "Activa",
        "created_at": "Fecha Creación"
    }
    
    # Note: Boolean field now uses SelectField with Sí/No options
    # This avoids checkbox compatibility issues with SQLAdmin
    
    name = "Proyecto"
    name_plural = "Proyectos" 
    icon = "fa-solid fa-folder"


# Experience Admin View
class ExperienceAdmin(ModelView, model=Experience):
    column_list = [Experience.id, Experience.company, Experience.position_en, Experience.start_date, Experience.end_date, Experience.activo]
    column_searchable_list = [Experience.company, Experience.position_en, Experience.position_es, Experience.location]
    column_sortable_list = [Experience.id, Experience.company, Experience.display_order, Experience.start_date, Experience.created_at]
    column_details_exclude_list = [Experience.created_at]
    
    # Format datetime columns
    column_formatters = {
        Experience.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else "",
        Experience.start_date: lambda m, a: m.start_date.strftime("%Y-%m-%d %H:%M") if m.start_date else "",
        Experience.end_date: lambda m, a: m.end_date.strftime("%Y-%m-%d %H:%M") if m.end_date else "",
    }
    form_columns = [
        # Company and dates (no translation needed)
        Experience.company, Experience.start_date, Experience.end_date, Experience.location,
        # Position and description (English & Spanish)
        Experience.position_en, Experience.position_es,
        Experience.description_en, Experience.description_es,
        # Settings (no translation needed)
        Experience.display_order,
        # Boolean field
        Experience.activo
    ]
    
    # Custom form overrides for boolean fields using SelectField
    form_overrides = {
        "activo": SelectField
    }
    
    form_args = {
        "activo": {
            "choices": [(True, "Sí"), (False, "No")],
            "coerce": lambda x: x == 'True' if isinstance(x, str) else bool(x)
        }
    }
    
    # Custom labels for better UX
    column_labels = {
        "company": "Empresa",
        "position_en": "Puesto (Inglés)",
        "position_es": "Puesto (Español)",
        "description_en": "Descripción (Inglés)",
        "description_es": "Descripción (Español)",
        "start_date": "Fecha Inicio",
        "end_date": "Fecha Fin",
        "location": "Ubicación",
        "display_order": "Orden",
        "activo": "Activo",
        "created_at": "Fecha Creación"
    }
    
    name = "Experiencia"
    name_plural = "Experiencias"
    icon = "fa-solid fa-briefcase"


# Education Admin View  
class EducationAdmin(ModelView, model=Education):
    column_list = [Education.id, Education.institution, Education.degree_en, Education.start_date, Education.end_date, Education.activo]
    column_searchable_list = [Education.institution, Education.degree_en, Education.degree_es, Education.field_of_study_en, Education.field_of_study_es]
    column_sortable_list = [Education.id, Education.institution, Education.display_order, Education.start_date, Education.created_at]
    column_details_exclude_list = [Education.created_at]
    
    # Format datetime columns
    column_formatters = {
        Education.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else "",
        Education.start_date: lambda m, a: m.start_date.strftime("%Y-%m-%d %H:%M") if m.start_date else "",
        Education.end_date: lambda m, a: m.end_date.strftime("%Y-%m-%d %H:%M") if m.end_date else "",
    }
    form_columns = [
        # Institution and dates (no translation needed)
        Education.institution, Education.start_date, Education.end_date, Education.location,
        # Degree and field (English & Spanish)
        Education.degree_en, Education.degree_es,
        Education.field_of_study_en, Education.field_of_study_es,
        Education.description_en, Education.description_es,
        # Settings (no translation needed)
        Education.display_order,
        # Boolean field
        Education.activo
    ]
    
    # Custom form overrides for boolean fields using SelectField
    form_overrides = {
        "activo": SelectField
    }
    
    form_args = {
        "activo": {
            "choices": [(True, "Sí"), (False, "No")],
            "coerce": lambda x: x == 'True' if isinstance(x, str) else bool(x)
        }
    }
    
    # Custom labels for better UX
    column_labels = {
        "institution": "Institución",
        "degree_en": "Título (Inglés)",
        "degree_es": "Título (Español)",
        "field_of_study_en": "Campo de Estudio (Inglés)",
        "field_of_study_es": "Campo de Estudio (Español)",
        "description_en": "Descripción (Inglés)",
        "description_es": "Descripción (Español)",
        "start_date": "Fecha Inicio",
        "end_date": "Fecha Fin",
        "location": "Ubicación",
        "display_order": "Orden",
        "activo": "Activo",
        "created_at": "Fecha Creación"
    }
    
    name = "Educación"
    name_plural = "Educación"
    icon = "fa-solid fa-graduation-cap"


# Contact Admin View
class ContactAdmin(ModelView, model=Contact):
    column_list = [Contact.id, Contact.email, Contact.phone, Contact.linkedin_url, Contact.github_url, Contact.cv_file_url]
    column_searchable_list = [Contact.email, Contact.phone]
    column_sortable_list = [Contact.id, Contact.email, Contact.created_at]
    column_details_exclude_list = [Contact.updated_at, Contact.created_at]
    
    # Format datetime columns
    column_formatters = {
        Contact.created_at: lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else "",
        Contact.updated_at: lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M") if m.updated_at else "",
    }
    form_columns = [
        # Contact info (no translation needed) 
        Contact.email, Contact.phone, Contact.cv_file_url,
        # Social media links (no translation needed)
        Contact.linkedin_url, Contact.github_url, Contact.twitter_url, Contact.instagram_url,
        # Contact messages (English & Spanish)
        Contact.contact_message_en, Contact.contact_message_es,
        # Boolean field
        Contact.contact_form_enabled
    ]
    
    # Custom form overrides for boolean fields using SelectField
    form_overrides = {
        "contact_form_enabled": SelectField
    }
    
    form_args = {
        "contact_form_enabled": {
            "choices": [(True, "Sí"), (False, "No")],
            "coerce": lambda x: x == 'True' if isinstance(x, str) else bool(x)
        }
    }
    column_filters = [Contact.contact_form_enabled]
    
    # Custom labels for better UX
    column_labels = {
        "email": "Email",
        "phone": "Teléfono",
        "linkedin_url": "LinkedIn",
        "github_url": "GitHub",
        "twitter_url": "Twitter",
        "instagram_url": "Instagram",
        "contact_form_enabled": "Formulario Habilitado",
        "contact_message_en": "Mensaje de Contacto (Inglés)",
        "contact_message_es": "Mensaje de Contacto (Español)",
        "cv_file_url": "Archivo CV",
        "created_at": "Fecha Creación",
        "updated_at": "Fecha Actualización"
    }
    
    name = "Contacto"
    name_plural = "Contacto"
    icon = "fa-solid fa-envelope"


def register_admin_views(admin):
    """Register all admin views with the admin instance."""
    admin.add_view(UserAdmin)
    admin.add_view(AboutAdmin)
    admin.add_view(SkillAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(ExperienceAdmin)
    admin.add_view(EducationAdmin)
    admin.add_view(ContactAdmin)