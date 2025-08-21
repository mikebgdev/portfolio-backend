# Portfolio Backend API Documentation

## Overview

Portfolio Backend API is a robust, scalable FastAPI-based REST API designed for personal portfolio websites. The API provides multilingual content management with comprehensive caching and security features.

**Base URL:** `http://your-domain/api/v1`  
**Version:** 1.0.0  
**Languages Supported:** English (en), Spanish (es)  
**Default Language:** English (en)

## Features

- ✅ **Multilingual Support**: Content available in English and Spanish
- ✅ **Caching**: High-performance in-memory caching with TTL
- ✅ **Security**: Rate limiting, input sanitization, security headers
- ✅ **CORS**: Cross-Origin Resource Sharing enabled
- ✅ **Compression**: Response compression for better performance

## Authentication

The public API endpoints do not require authentication.

## Language Support

All content endpoints support the `lang` query parameter:
- `lang=en` (English) - Default
- `lang=es` (Spanish)

If an unsupported language is provided, the API defaults to English.

## Date Format and Ordering

- **Date Format**: All dates are returned in `YYYY/MM/DD` format
- **Sorting Logic**: Experience and Education records are sorted as follows:
  1. **Ongoing records first** (end_date = null) - current jobs/studies
  2. **Then by most recent end date** (reverse chronological order)
  3. **Finally by most recent start date** (as secondary sort)

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **Default**: 100 requests per minute per IP
- **Headers**: Rate limit information is included in response headers

## Response Format

All endpoints return JSON responses with appropriate HTTP status codes:
- **200**: Success
- **400**: Bad Request
- **404**: Not Found
- **429**: Too Many Requests
- **500**: Internal Server Error

## Public API Endpoints (/api/v1)

The following endpoints are available for external consumption:

---

### Site Configuration

#### GET /api/v1/site-config/
Get site configuration including social media metadata for frontend sharing.

**Response:**
```json
{
  "id": 1,
  "site_name": "Mike BG Dev",
  "site_description": "Portfolio website",
  "site_url": "https://mikebgdev.com",
  "og_title": "Mike BG Dev - Software Developer",
  "og_description": "Backend developer specialized in PHP and Python",
  "og_image": "https://mikebgdev.com/og-image.jpg",
  "og_url": "https://mikebgdev.com",
  "og_type": "website",
  "twitter_card": "summary_large_image",
  "twitter_site": "@mikebgdev",
  "twitter_creator": "@mikebgdev",
  "twitter_title": "Mike BG Dev - Software Developer",
  "twitter_description": "Backend developer specialized in PHP and Python",
  "twitter_image": "https://mikebgdev.com/twitter-image.jpg",
  "created_at": "2025-08-11T20:31:37.777206Z",
  "updated_at": "2025-08-20T21:46:23.367523Z"
}
```

---

### About Section

#### GET /api/v1/about/
Get personal information and bio.

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:**
```json
{
  "name": "Michael",
  "last_name": "Ballester Granero",
  "birth_date": "1994-04-07",
  "email": "mike@mikebgdev.com",
  "location": "Anna, Valencia",
  "photo_url": "https://example.com/profile.webp",
  "bio_en": "I'm a Software Developer...",
  "bio_es": "Soy Software Developer...",
  "hero_description_en": "Building scalable software...",
  "hero_description_es": "Construyendo software escalable...",
  "job_title_en": "Software Developer (Backend)",
  "job_title_es": "Software Developer (Backend)",
  "nationality_en": "Spanish",
  "nationality_es": "Español",
  "id": 1,
  "created_at": "2025-08-11T20:31:37.777206Z",
  "updated_at": "2025-08-20T21:46:23.367523Z",
  "language": "en",
  "available_languages": ["en", "es"]
}
```

---

### Skills

#### GET /api/v1/skills/
Get skills grouped by categories.

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:**
```json
{
  "categories": [
    {
      "id": "web",
      "label": "Web Development",
      "icon_name": "Globe",
      "skills": [
        {
          "name": "FastAPI",
          "icon_name": "Code",
          "color": null
        },
        {
          "name": "JavaScript",
          "icon_name": "Code",
          "color": null
        }
      ]
    }
  ]
}
```

---

### Projects

#### GET /api/v1/projects/
Get all projects.

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:**
```json
[
  {
    "id": 1,
    "title_en": "Portfolio Backend",
    "title_es": "Backend Portfolio",
    "description_en": "FastAPI backend for portfolio website",
    "description_es": "Backend FastAPI para sitio web portfolio",
    "image_url": "https://example.com/project.jpg",
    "technologies": ["FastAPI", "Python", "PostgreSQL"],
    "source_url": "https://github.com/user/project",
    "demo_url": "https://project-demo.com",
    "display_order": 1,
    "activa": true,
    "created_at": "2025-08-11T20:31:37.777206Z",
    "language": "en"
  }
]
```

#### GET /api/v1/projects/{project_id}
Get specific project by ID.

**Path Parameters:**
- `project_id`: Project ID (integer)

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:** Same as individual project object above.

---

### Experience

#### GET /api/v1/experience/
Get all work experiences.

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:**
```json
[
  {
    "id": 1,
    "company": "Tech Company",
    "location": "Valencia, Spain",
    "position_en": "Backend Developer",
    "position_es": "Desarrollador Backend",
    "description_en": "Developed REST APIs...",
    "description_es": "Desarrollé APIs REST...",
    "start_date": "2022/01/01",
    "end_date": "2023/12/31",
    "display_order": 1,
    "activo": true,
    "created_at": "2025-08-11T20:31:37.777206Z",
    "language": "en"
  }
]
```

#### GET /api/v1/experience/{experience_id}
Get specific experience by ID.

**Path Parameters:**
- `experience_id`: Experience ID (integer)

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:** Same as individual experience object above.

---

### Education

#### GET /api/v1/education/
Get all education records.

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:**
```json
[
  {
    "id": 1,
    "institution": "University Name",
    "location": "Valencia, Spain",
    "degree_en": "Computer Science Degree",
    "degree_es": "Grado en Informática",
    "start_date": "2018/09/01",
    "end_date": "2022/06/30",
    "display_order": 1,
    "activo": true,
    "created_at": "2025-08-11T20:31:37.777206Z",
    "language": "en"
  }
]
```

#### GET /api/v1/education/{education_id}
Get specific education record by ID.

**Path Parameters:**
- `education_id`: Education ID (integer)

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:** Same as individual education object above.

---

### Contact

#### GET /api/v1/contact/
Get contact information.

**Query Parameters:**
- `lang` (optional): Language code (en, es). Default: en

**Response:**
```json
{
  "id": 1,
  "email": "mike@mikebgdev.com",
  "phone": "+34 123 456 789",
  "linkedin_url": "https://linkedin.com/in/username",
  "github_url": "https://github.com/username",
  "twitter_url": "https://twitter.com/username",
  "instagram_url": "https://instagram.com/username",
  "contact_form_enabled": true,
  "contact_message_en": "Feel free to contact me",
  "contact_message_es": "No dudes en contactarme",
  "cv_file_url": "https://example.com/cv.pdf",
  "created_at": "2025-08-11T20:31:37.777206Z",
  "updated_at": "2025-08-20T21:46:23.367523Z",
  "language": "en"
}
```

---

## Error Handling

The API uses standard HTTP status codes and returns error responses in JSON format:

```json
{
  "detail": "Error description"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side error

## Caching

The API implements intelligent caching:
- **Content Cache**: 10 minutes (600 seconds) for dynamic content
- **Static Content**: 30 minutes (1800 seconds) for rarely changing data
- **Cache Headers**: Responses include cache control headers

## Security Features

- **Rate Limiting**: Protection against abuse
- **Input Sanitization**: XSS protection
- **Security Headers**: CORS, CSP, XSS protection
- **Request Size Limits**: Protection against large payloads
- **HTTPS Enforcement**: Secure communication (in production)

## Interactive Documentation

For testing and exploring the API interactively:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

---

**Last Updated**: August 2025  
**API Version**: 1.0.0