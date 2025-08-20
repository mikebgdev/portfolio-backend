# SQLAdmin Access Guide

## 🔐 Admin Panel Access

### URLs disponibles (solo SQLAdmin):
- **Login Page**: `http://localhost:8000/admin/login` (diseño original de SQLAdmin)
- **Admin Dashboard**: `http://localhost:8000/admin` (🔒 protegido - redirige al login si no autenticado)
- **Logout**: `http://localhost:8000/admin/logout` (logout de SQLAdmin)

### ✅ Funcionalidad de protección:
- **Sin autenticación**: Acceder a `/admin` → redirige automáticamente a `/admin/login`
- **Con autenticación**: Acceder a `/admin` → redirige a `/admin/` (panel completo)

### 👤 Credenciales de acceso:
- **Usuario**: `admin@portfolio.com`
- **Contraseña**: La contraseña del usuario admin creado en la base de datos

### 🚀 Cómo acceder:

1. **Inicia el servidor**:
   ```bash
   ./restart_server.sh
   # O manualmente:
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Ve a la página de login**:
   ```
   http://localhost:8000/admin/login
   ```

3. **Usa las credenciales admin** para iniciar sesión

4. **Accede al panel completo**:
   ```
   http://localhost:8000/admin
   ```

### 📋 Funcionalidades disponibles:
- ✅ **Usuarios** - Gestión completa
- ✅ **Configuración del Sitio** - Título, marca, SEO
- ✅ **Acerca de** - Información personal bilingüe
- ✅ **Categorías de Habilidades** - Gestión de categorías
- ✅ **Habilidades** - Con relación a categorías
- ✅ **Proyectos** - Portfolio de proyectos
- ✅ **Experiencias** - Historial laboral
- ✅ **Educación** - Formación académica
- ✅ **Contacto** - Información de contacto

### 🔧 Troubleshooting:

**Si no puedes acceder:**
1. Verifica que el servidor esté corriendo
2. Confirma que estás usando la URL correcta
3. Verifica las credenciales del usuario admin
4. Revisa los logs del servidor: `tail -f server.log`

**Para crear un nuevo usuario admin:**
```python
from app.auth.oauth import auth_service
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
hashed_password = auth_service.hash_password("tu_nueva_contraseña")
new_admin = User(
    email="nuevo@admin.com",
    name="Admin User",
    password_hash=hashed_password,
    role="admin",
    is_active=True
)
db.add(new_admin)
db.commit()
db.close()
```