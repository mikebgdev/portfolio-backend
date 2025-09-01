#!/bin/bash

echo "🚀 Creating Pull Request for Iconify Integration & Multilingual Email System"
echo "============================================================================="

# Push changes to remote
echo "📤 Pushing changes to remote..."
git push -u origin refactor/code-quality-improvements

if [ $? -ne 0 ]; then
    echo "❌ Failed to push changes. Please check your connection and try again."
    exit 1
fi

# Create PR using gh CLI
echo "📝 Creating Pull Request..."
gh pr create \
    --title "🎨 Enhanced Iconify Integration & Multilingual Email System" \
    --body "$(cat <<'EOF'
## 📋 Overview

This PR adds comprehensive **Iconify integration** with smart admin tooltips and a **multilingual contact email system** with Gmail SMTP support. The implementation includes intelligent form validation, automatic color suggestions, and professional email templates.

## ✨ Key Features

### 🎨 **Iconify Integration System**
- **100+ Technology Presets**: Official colors for popular technologies (Python, React, Docker, etc.)
- **Smart Admin Fields**: Custom WTForms fields with real-time validation
- **Visual Previews**: Live icon and color previews in admin panel
- **Autocomplete**: Technology suggestions with automatic color recommendations
- **API Endpoints**: `/api/v1/iconify/` for frontend integration

### 📧 **Multilingual Email System**  
- **Contact Form Endpoint**: `POST /api/v1/contact/send/` with language support
- **Gmail SMTP**: Professional email delivery with proper headers
- **Bilingual Templates**: English/Spanish confirmation emails
- **Dynamic Configuration**: Sender names and emails from database
- **Reply-To Headers**: Proper email routing despite Gmail limitations

### 🛠️ **Enhanced Admin Panel**
- **Smart Tooltips**: Detailed help with examples and links
- **Real-time Validation**: Visual feedback (green=valid, red=invalid)
- **Automatic Suggestions**: Colors auto-fill for known technologies
- **Rich Descriptions**: HTML descriptions with code examples
- **Improved UX**: Professional admin experience with JavaScript enhancements

## 🚀 Technical Implementation

### **New Components**
- `app/admin/iconify_fields.py` - Custom WTForms fields with validation
- `app/routers/iconify.py` - API endpoints for icon/color utilities  
- `app/utils/iconify.py` - Core utilities and validation logic
- `app/services/email.py` - Multilingual email system
- `app/services/contact_message.py` - Contact form handling
- `templates/admin/form.html` - JavaScript integration for admin

### **New API Endpoints**
- `GET /api/v1/iconify/tooltip` - Icon validation & suggestions
- `GET /api/v1/iconify/search` - Search technology icons  
- `GET /api/v1/iconify/categories` - Browse icon collections
- `GET /api/v1/iconify/validate-color` - Color format validation
- `POST /api/v1/contact/send/` - Contact form with email notifications

### **Database Changes**
- **Contact Table**: Added `sender_name` field for email signatures
- **Contact Messages**: New table for storing form submissions

## 📚 Documentation

### **Organized Structure**
- `docs/README.md` - Documentation index
- `docs/api/API_DOCUMENTATION.md` - Complete API reference
- `docs/iconify/README.md` - Frontend integration guide  
- `docs/iconify/admin-guide.md` - SQLAdmin usage guide

## 🧪 Testing & Quality

- ✅ All new API endpoints tested and working
- ✅ Admin panel enhancements functional
- ✅ Email system tested with Gmail SMTP
- ✅ Multilingual templates validated (EN/ES)
- ✅ No breaking changes to existing functionality
- ✅ Database migrations tested

## 🔄 Migration Guide

```bash
# Apply database migrations
alembic upgrade head
```

No new environment variables required - uses existing email configuration.

## 📊 Impact

- **Performance**: Minimal impact with smart caching
- **Security**: All inputs validated and sanitized
- **Maintainability**: Clean separation with comprehensive documentation
- **Backward Compatibility**: No breaking changes

## 🎉 Result

This transforms the portfolio backend into a comprehensive content management system with professional admin experience, robust email system, and developer-friendly APIs while maintaining full backward compatibility.

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)" \
    --head refactor/code-quality-improvements \
    --base main

if [ $? -eq 0 ]; then
    echo "✅ Pull Request created successfully!"
    echo "🔗 Check your GitHub repository for the PR link"
else
    echo "❌ Failed to create Pull Request. Please create it manually on GitHub."
    echo "📝 Branch: refactor/code-quality-improvements"
    echo "🎯 Target: main"
fi