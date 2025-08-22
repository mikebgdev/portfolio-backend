"""Admin views for all models and custom views."""
from sqladmin import ModelView, BaseView, expose
from starlette.requests import Request
import httpx
from app.config import settings
from app.admin.file_fields import ImageUploadField, DocumentUploadField

# Import all models
from app.models.user import User
from app.models.site_config import SiteConfig
from app.models.about import About
from app.models.contact import Contact
from app.models.skills import Skill, SkillCategory
from app.models.projects import Project
from app.models.experience import Experience
from app.models.education import Education



def is_admin_user(request: Request) -> bool:
    """Check if the current user is an admin."""
    return (request.session.get("authenticated", False) and 
            request.session.get("user_role") == "admin")


# ==================== USER ADMIN ====================
class UserAdmin(ModelView, model=User):
    """Admin view for User management."""
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

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


# ==================== SITE CONFIG ADMIN ====================
class SiteConfigAdmin(ModelView, model=SiteConfig):
    """Admin view for Site Configuration."""
    name = "Configuración del Sitio"
    name_plural = "Configuración del Sitio" 
    icon = "fa-solid fa-cogs"
    
    form_excluded_columns = [SiteConfig.id, SiteConfig.created_at, SiteConfig.updated_at]
    column_list = [SiteConfig.id, SiteConfig.site_title, SiteConfig.brand_name, SiteConfig.favicon_file]
    column_searchable_list = [SiteConfig.site_title, SiteConfig.brand_name]
    
    # Custom form fields for file uploads
    form_overrides = {
        'favicon_file': ImageUploadField,
        'og_image_file': ImageUploadField,
        'twitter_image_file': ImageUploadField
    }
    
    column_labels = {
        "id": "ID",
        "site_title": "Título del sitio",
        "brand_name": "Nombre de la marca",
        "meta_description": "Meta descripción",
        "meta_keywords": "Meta palabras clave",
        # File uploads
        "favicon_file": "Archivo Favicon",
        # Open Graph fields
        "og_title": "Título OG",
        "og_description": "Descripción OG",
        "og_image_file": "Archivo Imagen OG",
        "og_url": "URL Canónica",
        "og_type": "Tipo OG",
        # Twitter Card fields
        "twitter_card": "Tipo de Twitter Card",
        "twitter_title": "Título Twitter",
        "twitter_description": "Descripción Twitter",
        "twitter_image_file": "Archivo Imagen Twitter",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


# ==================== ABOUT ADMIN ====================
class AboutAdmin(ModelView, model=About):
    """Admin view for About/Personal Information."""
    name = "Acerca de"
    name_plural = "Acerca de"
    icon = "fa-solid fa-user-circle"
    
    form_excluded_columns = [About.id, About.created_at, About.updated_at]
    column_list = [About.id, About.name, About.last_name, About.email, About.location, About.photo_file]
    column_searchable_list = [About.name, About.last_name, About.email]
    
    # Custom form fields
    form_overrides = {
        'photo_file': ImageUploadField
    }
    
    column_labels = {
        "id": "ID",
        "name": "Nombre",
        "last_name": "Apellidos", 
        "birth_date": "Fecha de nacimiento",
        "email": "Correo electrónico",
        "location": "Ubicación",
        "photo_file": "Archivo de foto",
        "bio_en": "Biografía (Inglés)",
        "bio_es": "Biografía (Español)",
        "hero_description_en": "Descripción hero (Inglés)",
        "hero_description_es": "Descripción hero (Español)",
        "job_title_en": "Título del trabajo (Inglés)",
        "job_title_es": "Título del trabajo (Español)",
        "nationality_en": "Nacionalidad (Inglés)",
        "nationality_es": "Nacionalidad (Español)",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


# ==================== CONTACT ADMIN ====================
class ContactAdmin(ModelView, model=Contact):
    """Admin view for Contact Information."""
    name = "Contacto"
    name_plural = "Contacto"
    icon = "fa-solid fa-envelope"
    
    form_excluded_columns = [Contact.id, Contact.created_at, Contact.updated_at]
    column_list = [Contact.id, Contact.email, Contact.contact_form_enabled, Contact.cv_file]
    column_searchable_list = [Contact.email]
    
    # Custom form fields
    form_overrides = {
        'cv_file': DocumentUploadField
    }
    
    column_labels = {
        "id": "ID",
        "email": "Correo electrónico",
        "linkedin_url": "URL LinkedIn",
        "github_url": "URL GitHub",
        "contact_form_enabled": "¿Formulario contacto activo?",
        "contact_message_en": "Mensaje de contacto (Inglés)",
        "contact_message_es": "Mensaje de contacto (Español)",
        "cv_file": "Archivo CV",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


# ==================== SKILLS ADMIN ====================
class SkillCategoryAdmin(ModelView, model=SkillCategory):
    """Admin view for Skill Categories."""
    name = "Categoría de habilidad"
    name_plural = "Categorías de habilidades"
    icon = "fa-solid fa-tags"
    
    form_excluded_columns = [SkillCategory.id, SkillCategory.created_at, SkillCategory.updated_at]
    column_list = [SkillCategory.id, SkillCategory.slug, SkillCategory.label_en, SkillCategory.active, SkillCategory.display_order]
    column_searchable_list = [SkillCategory.slug, SkillCategory.label_en, SkillCategory.label_es]
    column_sortable_list = [SkillCategory.id, SkillCategory.slug, SkillCategory.display_order]
    
    column_labels = {
        "id": "ID",
        "slug": "Slug (identificador único)",
        "label_en": "Etiqueta (Inglés)",
        "label_es": "Etiqueta (Español)",
        "icon_name": "Nombre del icono",
        "display_order": "Orden de visualización",
        "active": "¿Activo?",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


class SkillAdmin(ModelView, model=Skill):
    """Admin view for Skills."""
    name = "Habilidad"
    name_plural = "Habilidades"
    icon = "fa-solid fa-code"
    
    form_excluded_columns = [Skill.id, Skill.created_at, Skill.updated_at]
    column_list = [Skill.id, "skill_category", Skill.name_en, Skill.active, Skill.display_order]
    column_searchable_list = [Skill.name_en, Skill.name_es]
    column_sortable_list = [Skill.id, Skill.name_en, Skill.display_order]
    
    column_labels = {
        "id": "ID", 
        "name_en": "Nombre (Inglés)",
        "name_es": "Nombre (Español)",
        "category_id": "ID Categoría",
        "skill_category": "Categoría de habilidad",
        "icon_name": "Nombre del icono",
        "color": "Color CSS",
        "display_order": "Orden de visualización",
        "active": "¿Activo?",
        "created_at": "Fecha de creación",
        "updated_at": "Última modificación"
    }

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


# ==================== PROJECTS ADMIN ====================
class ProjectAdmin(ModelView, model=Project):
    """Admin view for Projects."""
    name = "Proyecto"
    name_plural = "Proyectos"
    icon = "fa-solid fa-folder-open"
    
    form_excluded_columns = [Project.id, Project.created_at]
    column_list = [Project.id, Project.title_en, Project.technologies, Project.activa, Project.display_order, Project.image_file]
    column_searchable_list = [Project.title_en, Project.title_es, Project.technologies]
    column_sortable_list = [Project.id, Project.title_en, Project.display_order, Project.created_at]
    
    # Custom form fields
    form_overrides = {
        'image_file': ImageUploadField
    }
    
    column_labels = {
        "id": "ID",
        "title_en": "Título (Inglés)",
        "title_es": "Título (Español)",
        "description_en": "Descripción (Inglés)",
        "description_es": "Descripción (Español)",
        "image_file": "Archivo de imagen",
        "technologies": "Tecnologías utilizadas",
        "source_url": "URL código fuente",
        "demo_url": "URL demo en vivo",
        "display_order": "Orden de visualización",
        "activa": "¿Activo?",
        "created_at": "Fecha de creación"
    }

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


# ==================== EXPERIENCE ADMIN ====================
class ExperienceAdmin(ModelView, model=Experience):
    """Admin view for Work Experience."""
    name = "Experiencia"
    name_plural = "Experiencias"
    icon = "fa-solid fa-briefcase"
    
    form_excluded_columns = [Experience.id, Experience.created_at]
    column_list = [Experience.id, Experience.company, Experience.position_en, Experience.start_date, Experience.end_date, Experience.activo]
    column_searchable_list = [Experience.company, Experience.position_en, Experience.position_es]
    column_sortable_list = [Experience.id, Experience.company, Experience.start_date, Experience.display_order]
    
    column_labels = {
        "id": "ID",
        "company": "Empresa",
        "position_en": "Posición (Inglés)",
        "position_es": "Posición (Español)",
        "description_en": "Descripción (Inglés)",
        "description_es": "Descripción (Español)",
        "start_date": "Fecha de inicio",
        "end_date": "Fecha de fin",
        "location": "Ubicación",
        "display_order": "Orden de visualización",
        "activo": "¿Activo?",
        "created_at": "Fecha de creación"
    }

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


# ==================== EDUCATION ADMIN ====================
class EducationAdmin(ModelView, model=Education):
    """Admin view for Education."""
    name = "Educación"
    name_plural = "Educación"
    icon = "fa-solid fa-graduation-cap"
    
    form_excluded_columns = [Education.id, Education.created_at]
    column_list = [Education.id, Education.institution, Education.degree_en, Education.start_date, Education.end_date, Education.activo]
    column_searchable_list = [Education.institution, Education.degree_en, Education.degree_es]
    column_sortable_list = [Education.id, Education.institution, Education.start_date, Education.display_order]
    
    column_labels = {
        "id": "ID",
        "institution": "Institución",
        "degree_en": "Título (Inglés)",
        "degree_es": "Título (Español)",
        "start_date": "Fecha de inicio",
        "end_date": "Fecha de fin",
        "location": "Ubicación",
        "display_order": "Orden de visualización",
        "activo": "¿Activo?",
        "created_at": "Fecha de creación"
    }

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


# ==================== METRICS CUSTOM VIEW ====================
class MetricsView(BaseView):
    """Custom admin view for displaying analytics dashboard."""
    name = "Métricas y Análisis"
    icon = "fa-solid fa-chart-line"

    @expose("/metrics", methods=["GET"])
    async def metrics_dashboard(self, request):
        """Display comprehensive metrics dashboard."""
        if not is_admin_user(request):
            return self.templates.TemplateResponse("admin/unauthorized.html", {"request": request})
        
        try:
            # Import metrics directly instead of HTTP calls to avoid circular dependency
            from app.utils.enhanced_monitoring import metrics_collector, enhanced_health_checker
            from app.utils.cache import cache_manager
            
            # Ensure we have some system metrics
            metrics_collector.record_system_metrics()
            
            # Get metrics directly from services
            dashboard_data = {
                "overview": {
                    "health": enhanced_health_checker.get_comprehensive_health(),
                    "uptime_seconds": (enhanced_health_checker.startup_time - enhanced_health_checker.startup_time).total_seconds()
                },
                "requests": metrics_collector.get_request_metrics(),
                "system": metrics_collector.get_system_metrics(hours=24),
                "database": metrics_collector.get_database_metrics(),
                "security": metrics_collector.get_security_metrics(),
                "time_range_hours": 24
            }
            
            # Get alerts
            health = enhanced_health_checker.get_comprehensive_health()
            alerts_data = {"alerts": [], "total_alerts": 0, "severity_counts": {"critical": 0, "warning": 0, "info": 0}}
            
            # Check for failed health checks
            if health["status"] != "healthy":
                failed_checks = health.get("failed_checks", [])
                warning_checks = health.get("warning_checks", [])
                
                for check in failed_checks:
                    check_data = health["checks"][check]
                    alerts_data["alerts"].append({
                        "type": "health_check_failed",
                        "severity": "critical",
                        "component": check,
                        "message": check_data.get("message", f"{check} health check failed"),
                        "timestamp": health["timestamp"]
                    })
                
                for check in warning_checks:
                    check_data = health["checks"][check]
                    alerts_data["alerts"].append({
                        "type": "health_check_warning",
                        "severity": "warning", 
                        "component": check,
                        "message": check_data.get("message", f"{check} health check warning"),
                        "timestamp": health["timestamp"]
                    })
            
            # Check for high error rates
            request_metrics = metrics_collector.get_request_metrics()
            if request_metrics.get("error_rate", 0) > 10:
                alerts_data["alerts"].append({
                    "type": "high_error_rate",
                    "severity": "critical" if request_metrics["error_rate"] > 25 else "warning",
                    "component": "api",
                    "message": f"High error rate: {request_metrics['error_rate']:.1f}%",
                    "details": {"error_rate": request_metrics["error_rate"]}
                })
            
            alerts_data["total_alerts"] = len(alerts_data["alerts"])
            for alert in alerts_data["alerts"]:
                alerts_data["severity_counts"][alert["severity"]] += 1
                
            # Get cache data
            cache_data = cache_manager.get_stats()
                
            # Prepare context for template
            context = {
                "dashboard": dashboard_data,
                "alerts": alerts_data,
                "cache": cache_data,
                "error": None
            }
                
        except Exception as e:
            context = {
                "dashboard": {},
                "alerts": {},
                "cache": {},
                "error": f"Error al cargar métricas: {str(e)}"
            }
            
        return self.templates.TemplateResponse("admin/metrics.html", {"request": request, **context})

    def is_accessible(self, request: Request) -> bool:
        return is_admin_user(request)


def register_admin_views(admin):
    """Register all admin views with the admin instance."""
    # Custom views
    admin.add_view(MetricsView)
    
    # Content management views
    admin.add_view(UserAdmin)
    admin.add_view(SiteConfigAdmin)
    admin.add_view(AboutAdmin)
    admin.add_view(ContactAdmin)
    admin.add_view(SkillCategoryAdmin)
    admin.add_view(SkillAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(ExperienceAdmin)
    admin.add_view(EducationAdmin)
    
