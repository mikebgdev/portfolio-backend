# Security Policy

## 🛡️ Security Overview

This project takes security seriously and implements multiple layers of protection to ensure the safety of user data and system integrity.

## 🔐 Security Features

### Authentication & Authorization
- **Google OAuth 2.0**: Secure authentication with Google Workspace integration
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Role-Based Access Control**: Admin-only endpoints with proper authorization
- **Session Management**: Secure token handling with automatic expiration

### Data Protection
- **Input Validation**: Comprehensive Pydantic schema validation
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM
- **XSS Protection**: Content Security Policy and input sanitization
- **CORS Configuration**: Secure cross-origin resource sharing

### Infrastructure Security
- **Container Security**: Non-root user execution, minimal attack surface
- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **Dependency Scanning**: Automated vulnerability detection
- **Secret Management**: Environment-based configuration with .env files

## 🔍 Security Scanning

### Automated Security Checks
The project includes automated security scanning in the CI/CD pipeline:

- **Bandit**: Python security linter for common security issues
- **Safety**: Checks Python dependencies for known security vulnerabilities
- **Semgrep**: Static analysis for security vulnerabilities
- **TruffleHog**: Scans for exposed secrets and credentials
- **Trivy**: Container vulnerability scanning

### Manual Security Reviews
- Code reviews for security implications
- Regular dependency updates
- Security configuration validation
- Penetration testing recommendations

## 🚨 Reporting Security Vulnerabilities

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### Reporting Process

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Send an email to: **security@mikebg.dev** with:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Any suggested fixes or mitigation strategies

### Response Timeline
- **Acknowledgment**: Within 24 hours
- **Initial Assessment**: Within 48 hours
- **Status Updates**: Every 72 hours until resolution
- **Resolution**: Target within 30 days for critical issues

### Disclosure Policy
- We follow responsible disclosure practices
- Security fixes will be released as soon as possible
- Public disclosure will occur after fixes are available
- Credit will be given to security researchers (unless requested otherwise)

## 🔧 Security Configuration

### Production Security Checklist

- [ ] **Environment Variables**: All sensitive data in environment variables
- [ ] **Google OAuth**: Production OAuth credentials configured
- [ ] **JWT Secret**: Cryptographically secure secret key (32+ characters)
- [ ] **HTTPS**: Force HTTPS in production environments
- [ ] **CORS**: Restrict CORS origins to production domains only
- [ ] **Debug Mode**: Ensure DEBUG=False in production
- [ ] **Database**: Use strong database passwords and restricted access
- [ ] **Container**: Run containers as non-root user
- [ ] **Dependencies**: Keep all dependencies updated
- [ ] **Monitoring**: Enable security event logging and monitoring

### Security Headers Configuration

The application automatically configures security headers:

```python
# Automatic security headers
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

### OAuth Security Configuration

```bash
# Production OAuth configuration
GOOGLE_CLIENT_ID=production-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-production-secret

# Authorized domains for OAuth
# - https://yourdomain.com
# - https://www.yourdomain.com
```

## 🛠️ Security Best Practices

### For Developers

1. **Code Security**:
   - Always validate user input
   - Use parameterized queries
   - Implement proper error handling
   - Follow principle of least privilege

2. **Authentication**:
   - Never store passwords in plain text
   - Use secure session management
   - Implement proper logout functionality
   - Validate authentication tokens

3. **Data Handling**:
   - Sanitize all user inputs
   - Use HTTPS for all communications
   - Implement proper logging without sensitive data
   - Regular security audits

### For Deployment

1. **Environment Security**:
   - Use environment variables for secrets
   - Restrict network access
   - Enable monitoring and alerting
   - Regular security updates

2. **Container Security**:
   - Use official base images
   - Regular image updates
   - Non-root user execution
   - Minimal attack surface

## 🔄 Security Updates

### Staying Updated
- Monitor GitHub security advisories
- Subscribe to security mailing lists for dependencies
- Regular dependency updates via automated tools
- Security patch management process

### Update Process
1. Security advisory received
2. Impact assessment
3. Patch development and testing
4. Coordinated disclosure
5. Patch deployment
6. Post-incident review

## 📚 Security Resources

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Docker Security](https://docs.docker.com/engine/security/)

### Tools
- [Bandit](https://github.com/PyCQA/bandit) - Python security linter
- [Safety](https://github.com/pyupio/safety) - Dependency vulnerability scanner
- [Semgrep](https://semgrep.dev/) - Static analysis security scanner

## 📞 Contact

For security-related questions or concerns:
- **Email**: security@mikebg.dev
- **Response Time**: 24 hours for security issues
- **Encryption**: PGP key available upon request

---

**Last Updated**: August 2025
**Next Review**: February 2026