# 🚀 Coolify Deployment Guide

## 📋 Overview

This guide provides specific instructions for deploying the Portfolio Backend on **Coolify** with proper SQLAdmin styling and static file serving.

## ⚡ Quick Deploy

### 1. **Create New Project in Coolify**
- Choose **"Deploy from Git Repository"**
- Repository: `https://github.com/yourusername/portfolio-backend`
- Branch: `main` or `refactor/code-quality-improvements`

### 2. **Environment Configuration**
Copy these environment variables to your Coolify service:

```bash
# Core Settings
ENVIRONMENT=production
DEBUG=false

# Database (Update with your Coolify PostgreSQL service)
POSTGRES_HOST=your-postgres-service-name
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=portfolio_db

# Security (REQUIRED)
SECRET_KEY=your-super-secure-secret-key-at-least-32-characters-long

# CORS (Update with your domain)
CORS_ORIGINS=["https://yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true

# Email Configuration
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_USE_TLS=true
```

### 3. **Database Setup**
Create a PostgreSQL service in Coolify and note the connection details.

### 4. **Deploy Configuration**
- **Port**: `8000`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1`

## 🔧 SQLAdmin Styling Fix

### Problem
SQLAdmin panel loads without CSS styling in production environments like Coolify.

### Solution
The updated configuration now includes:

1. **Proper Static File Mounting**: Templates and static files are correctly served
2. **Debug Mode Control**: Proper debug settings for SQLAdmin
3. **Environment-Aware Configuration**: Production-optimized settings

### Files Updated
- `app/admin/base.py` - Added debug configuration
- `app/main.py` - Enhanced static file serving
- `.env.coolify.example` - Coolify-specific environment template

## 🗄️ Database Migration

After deployment, run migrations:

```bash
# In Coolify terminal or using Coolify's command execution
alembic upgrade head
```

## 🎯 Access Points

After successful deployment:

- **🌐 API**: `https://yourdomain.com/api/v1/`
- **📚 API Docs**: `https://yourdomain.com/docs`
- **👨‍💼 Admin Panel**: `https://yourdomain.com/admin`
- **❤️ Health Check**: `https://yourdomain.com/health`

## 🔍 Verification Steps

### 1. **Check API Health**
```bash
curl https://yourdomain.com/health
```

### 2. **Test Admin Panel**
- Navigate to `https://yourdomain.com/admin`
- ✅ **CSS should load properly** (fixed styling issue)
- ✅ **Login should work** with admin credentials

### 3. **Test API Endpoints**
```bash
# Test basic endpoint
curl https://yourdomain.com/api/v1/about/

# Test Iconify endpoints
curl https://yourdomain.com/api/v1/iconify/categories
```

### 4. **Test Contact Form** (if configured)
```bash
curl -X POST https://yourdomain.com/api/v1/contact/send/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Test message"}'
```

## 🐛 Troubleshooting

### SQLAdmin No Styles
- ✅ **Fixed**: Updated static file serving configuration
- ✅ **Verified**: Debug mode properly configured
- ✅ **Tested**: Template directory mounting

### Database Connection Issues
```bash
# Check environment variables in Coolify
echo $POSTGRES_HOST
echo $POSTGRES_DB

# Test connection
python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
```

### Email Issues
```bash
# Test SMTP configuration
python -c "from app.services.email import email_service; print(email_service.email_enabled)"
```

## 🔒 Security Checklist

- [ ] **SECRET_KEY**: Strong 32+ character key set
- [ ] **CORS**: Only your domain(s) allowed
- [ ] **Database**: Secure password used
- [ ] **Email**: App password (not main password) used
- [ ] **Debug**: Set to `false` in production
- [ ] **Environment**: Set to `production`

## 🚀 Performance Optimization

### Recommended Settings
```bash
# Caching (automatically enabled in production)
CACHE_TTL_CONTENT=300
CACHE_TTL_STATIC=3600

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Upload Limits
MAX_UPLOAD_SIZE=10485760
```

## 🎉 Result

After following this guide:
- ✅ **SQLAdmin styling works properly**
- ✅ **All API endpoints functional**
- ✅ **Static files served correctly**
- ✅ **Database connected and migrated**
- ✅ **Email system operational**
- ✅ **Iconify integration working**

## 📞 Support

If you encounter issues:

1. **Check Coolify Logs**: Application and build logs
2. **Verify Environment Variables**: All required variables set
3. **Test Database Connection**: Ensure PostgreSQL service is running
4. **Check Domain Configuration**: CORS and URL settings correct

---

**Your Portfolio Backend is now production-ready on Coolify!** 🎯