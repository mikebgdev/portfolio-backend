# 🚀 Deployment Fix Guide

## 🔧 Issues Fixed

### 1. CORS Configuration
The API was rejecting frontend requests due to CORS misconfiguration.

**Solution**: Updated CORS logic to be more flexible in production.

### 2. Admin Panel Styles Missing  
SQLAdmin static files weren't being served correctly.

**Solution**: Explicitly mount SQLAdmin static files at `/admin/statics`.

## ⚙️ Required Environment Variables

**Copy `.env.production.example` to `.env` and update these values:**

```bash
# CRITICAL: Set your frontend domain(s)
CORS_ORIGINS=["https://your-frontend-domain.com"]

# Or temporarily use wildcard for testing
CORS_ORIGINS=["*"]

# Ensure these are set
ENVIRONMENT=production
SECRET_KEY=your-32-char-secret-key
POSTGRES_HOST=your-db-host
POSTGRES_PASSWORD=your-db-password
```

## 🔍 Debug Endpoints

After deployment, test these endpoints:

1. **Health Check**: `GET /api/v1/health`
2. **CORS Debug**: `GET /api/v1/debug/cors` 
3. **Admin Panel**: `/admin/`

## 📋 Deployment Checklist

- [ ] Environment variables configured (especially CORS_ORIGINS)
- [ ] Database connected
- [ ] Static files serving correctly (`/admin/statics/`)
- [ ] CORS headers include your frontend domain
- [ ] Admin panel loads with styles

## 🔧 Quick Fix Commands

```bash
# Test health endpoint
curl https://your-api-domain.com/api/v1/health

# Check CORS configuration
curl https://your-api-domain.com/api/v1/debug/cors

# Test admin panel
curl -I https://your-api-domain.com/admin/
```

## 🚨 If Still Having Issues

1. **CORS Errors**: Set `CORS_ORIGINS=["*"]` temporarily to test
2. **Admin Styles**: Check `/admin/statics/` endpoint directly
3. **Check Logs**: Look for SQLAdmin static files mount message