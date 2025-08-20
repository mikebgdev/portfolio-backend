from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy.orm import Session

from app.database import engine
from app.models.user import User
from app.models.content import About, Skill, SkillCategory, Project, Experience, Education, Contact
from app.models.site_config import SiteConfig


class AdminAuth(AuthenticationBackend):
    """Authentication backend for SQLAdmin"""
    
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
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("authenticated", False)


# Create authentication backend
authentication_backend = AdminAuth(secret_key="your-admin-secret-key")


def create_admin(app):
    """Create and configure SQLAdmin instance"""
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="Portfolio Admin Panel",
        logo_url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    )
    return admin


# ==================== USER ADMIN ====================
class UserAdmin(ModelView, model=User):
    name = "Usuario"
    name_plural = "Usuarios"
    icon = "fa-solid fa-user"
    
    form_excluded_columns = [User.id, User.created_at, User.updated_at]
    
    column_list = [User.id, User.email, User.name, User.role, User.is_active]
    column_searchable_list = [User.email, User.name]
    column_sortable_list = [User.id, User.email, User.name]
    
    column_labels = {
        "id": "ID",
        "email": "Correo electrónico", 
        "name": "Nombre completo",
        "password_hash": "Contraseña (hash)",
        "role": "Rol del usuario",
        "is_active": "¿Usuario activo?",
        "created_at": "Fecha de registro",
        "updated_at": "Última modificación"
    }


# ==================== SITE CONFIG ADMIN ====================
class SiteConfigAdmin(ModelView, model=SiteConfig):
    name = "Configuración del Sitio"
    name_plural = "Configuración del Sitio" 
    icon = "fa-solid fa-cogs"
    
    form_excluded_columns = [SiteConfig.id, SiteConfig.created_at, SiteConfig.updated_at]
    
    column_list = [SiteConfig.id, SiteConfig.site_title, SiteConfig.brand_name]
    column_searchable_list = [SiteConfig.site_title, SiteConfig.brand_name]
    
    column_labels = {
        "id": "ID",
        "site_title": "Título del sitio web",
        "brand_name": "Nombre de la marca/empresa",
        "meta_description": "Descripción para SEO (meta description)",
        "meta_keywords": "Palabras clave para SEO",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }


# ==================== ABOUT ADMIN ====================
class AboutAdmin(ModelView, model=About):
    name = "Acerca de"
    name_plural = "Acerca de"
    icon = "fa-solid fa-info-circle"
    
    form_excluded_columns = [About.id, About.created_at, About.updated_at]
    
    column_list = [About.id, About.name, About.last_name, About.email]
    column_searchable_list = [About.name, About.email]
    
    column_labels = {
        "id": "ID",
        "name": "Nombre",
        "last_name": "Apellidos", 
        "birth_date": "Fecha de nacimiento",
        "email": "Correo electrónico",
        "location": "Ubicación/Ciudad",
        "photo_url": "URL de la foto de perfil",
        "bio_en": "Biografía en inglés",
        "bio_es": "Biografía en español",
        "hero_description_en": "Descripción hero (inglés)",
        "hero_description_es": "Descripción hero (español)",
        "job_title_en": "Título profesional (inglés)",
        "job_title_es": "Título profesional (español)",
        "nationality_en": "Nacionalidad (inglés)",
        "nationality_es": "Nacionalidad (español)",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }


# ==================== SKILL CATEGORY ADMIN ====================
class SkillCategoryAdmin(ModelView, model=SkillCategory):
    name = "Categoría de Habilidades"
    name_plural = "Categorías de Habilidades"
    icon = "fa-solid fa-tags"
    
    # Exclude relationship fields - skills are managed from Skill admin
    form_excluded_columns = [SkillCategory.id, SkillCategory.created_at, SkillCategory.updated_at, SkillCategory.skills]
    
    column_list = [SkillCategory.id, SkillCategory.slug, SkillCategory.label_en, SkillCategory.active]
    column_searchable_list = [SkillCategory.slug, SkillCategory.label_en]
    
    column_labels = {
        "id": "ID",
        "slug": "Identificador único (ej: 'web', 'tools')",
        "label_en": "Nombre en inglés",
        "label_es": "Nombre en español",
        "icon_name": "Nombre del icono (ej: 'Globe', 'Wrench')",
        "display_order": "Orden de visualización",
        "active": "¿Categoría activa?",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }


# ==================== SKILL ADMIN ====================  
class SkillAdmin(ModelView, model=Skill):
    name = "Habilidad"
    name_plural = "Habilidades"
    icon = "fa-solid fa-star"
    
    form_excluded_columns = [Skill.id, Skill.created_at, Skill.updated_at]
    
    column_list = [Skill.id, Skill.name_en, Skill.skill_category, Skill.active]
    column_searchable_list = [Skill.name_en]
    
    column_labels = {
        "id": "ID",
        "name_en": "Nombre en inglés",
        "name_es": "Nombre en español",
        "skill_category": "Categoría",
        "category_id": "Categoría",
        "icon_name": "Nombre del icono (ej: 'Code', 'Server')",
        "color": "Color CSS (ej: 'text-cyan-500')",
        "display_order": "Orden dentro de la categoría",
        "active": "¿Habilidad activa?",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }


# ==================== PROJECT ADMIN ====================
class ProjectAdmin(ModelView, model=Project):
    name = "Proyecto" 
    name_plural = "Proyectos"
    icon = "fa-solid fa-folder"
    
    form_excluded_columns = [Project.id, Project.created_at]
    
    column_list = [Project.id, Project.title_en, Project.activa]
    column_searchable_list = [Project.title_en]
    
    column_labels = {
        "id": "ID",
        "title_en": "Título del proyecto (inglés)", 
        "title_es": "Título del proyecto (español)",
        "description_en": "Descripción del proyecto (inglés)",
        "description_es": "Descripción del proyecto (español)",
        "image_url": "URL de la imagen del proyecto",
        "technologies": "Tecnologías utilizadas (separadas por coma)",
        "source_url": "URL del código fuente (GitHub, etc.)",
        "demo_url": "URL de la demo en vivo",
        "display_order": "Orden de visualización",
        "activa": "¿Proyecto activo/visible?",
        "created_at": "Fecha de creación"
    }


# ==================== EXPERIENCE ADMIN ====================
class ExperienceAdmin(ModelView, model=Experience):
    name = "Experiencia"
    name_plural = "Experiencias" 
    icon = "fa-solid fa-briefcase"
    
    form_excluded_columns = [Experience.id, Experience.created_at]
    
    column_list = [Experience.id, Experience.company, Experience.position_en, Experience.activo]
    column_searchable_list = [Experience.company, Experience.position_en]
    
    column_labels = {
        "id": "ID",
        "company": "Nombre de la empresa",
        "position_en": "Cargo/Puesto (inglés)",
        "position_es": "Cargo/Puesto (español)",
        "description_en": "Descripción del trabajo (inglés)",
        "description_es": "Descripción del trabajo (español)",
        "start_date": "Fecha de inicio",
        "end_date": "Fecha de fin (vacío si es trabajo actual)",
        "location": "Ubicación del trabajo",
        "display_order": "Orden de visualización",
        "activo": "¿Experiencia activa/visible?",
        "created_at": "Fecha de creación"
    }


# ==================== EDUCATION ADMIN ====================
class EducationAdmin(ModelView, model=Education):
    name = "Educación"
    name_plural = "Educación"
    icon = "fa-solid fa-graduation-cap"
    
    form_excluded_columns = [Education.id, Education.created_at]
    
    column_list = [Education.id, Education.institution, Education.degree_en, Education.activo]
    column_searchable_list = [Education.institution, Education.degree_en]
    
    column_labels = {
        "id": "ID", 
        "institution": "Institución educativa",
        "degree_en": "Título/Grado obtenido (inglés)",
        "degree_es": "Título/Grado obtenido (español)",
        "field_of_study_en": "Campo de estudio (inglés)",
        "field_of_study_es": "Campo de estudio (español)",
        "description_en": "Descripción adicional (inglés)",
        "description_es": "Descripción adicional (español)",
        "start_date": "Fecha de inicio",
        "end_date": "Fecha de graduación (vacío si en curso)",
        "location": "Ubicación de la institución",
        "display_order": "Orden de visualización",
        "activo": "¿Educación activa/visible?",
        "created_at": "Fecha de creación"
    }


# ==================== CONTACT ADMIN ====================
class ContactAdmin(ModelView, model=Contact):
    name = "Contacto"
    name_plural = "Contacto"
    icon = "fa-solid fa-envelope"
    
    form_excluded_columns = [Contact.id, Contact.created_at, Contact.updated_at]
    
    column_list = [Contact.id, Contact.email, Contact.phone]
    column_searchable_list = [Contact.email]
    
    column_labels = {
        "id": "ID",
        "email": "Correo electrónico principal",
        "phone": "Número de teléfono", 
        "linkedin_url": "URL del perfil de LinkedIn",
        "github_url": "URL del perfil de GitHub",
        "twitter_url": "URL del perfil de Twitter",
        "instagram_url": "URL del perfil de Instagram",
        "contact_form_enabled": "¿Formulario de contacto activo?",
        "contact_message_en": "Mensaje de contacto (inglés)",
        "contact_message_es": "Mensaje de contacto (español)",
        "cv_file_url": "URL del archivo CV/Resume",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }


def register_admin_views(admin):
    """Register all admin views with the admin instance"""
    admin.add_view(UserAdmin)
    admin.add_view(SiteConfigAdmin)
    admin.add_view(AboutAdmin)
    admin.add_view(SkillCategoryAdmin)
    admin.add_view(SkillAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(ExperienceAdmin)
    admin.add_view(EducationAdmin)
    admin.add_view(ContactAdmin)