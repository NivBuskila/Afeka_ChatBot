# Security Policy

## Supported Versions

Currently, only the latest version of the Afeka ChatBot is supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Measures Implemented

The Afeka ChatBot implements several security measures to protect the application and user data:

### Docker Security
- All services run as non-root users
- Container resource limits are enforced
- Multi-stage builds to minimize attack surface
- Specific image versions pinned to avoid unexpected updates
- Health checks implemented for all services

### API Security
- Rate limiting on all API endpoints
- Input validation and sanitization for all user inputs
- Security headers implemented (Content-Security-Policy, X-XSS-Protection, etc.)
- Proper error handling to avoid information disclosure
- API key authentication for sensitive endpoints

### Web Security
- CORS restrictions with specific allowed origins
- Content Security Policy implemented
- Protection against common web vulnerabilities (XSS, CSRF, clickjacking)
- Secure cookie configuration
- TLS/HTTPS support ready for production deployment

### Infrastructure Security
- Network traffic restricted between services
- Limited scope of access for each service
- Environment variable validation
- Internal API keys for service-to-service communication
- Logging and monitoring for security events

## Reporting a Vulnerability

If you discover a security vulnerability in the Afeka ChatBot, please report it by:

1. **DO NOT** disclose the vulnerability publicly
2. Create a security advisory by emailing [security@example.com](mailto:security@example.com)
3. Include detailed steps to reproduce the vulnerability
4. If possible, include a proof of concept
5. Suggest a fix or mitigation if available

### What to expect
- A confirmation of receipt within 48 hours
- A determination of the vulnerability's validity within 7 days
- Regular updates on the progress of the fix if accepted
- Credit for discovering the vulnerability (if desired)

## Security Best Practices for Deployment

When deploying this application, please follow these security best practices:

1. **Environment Variables**
   - Never commit sensitive environment variables to version control
   - Use a secure method for managing secrets in production

2. **Supabase Security**
   - Restrict Supabase RLS policies to the minimum required access
   - Regularly audit database access patterns
   - Keep the Supabase API key secure and never expose it to client-side code

3. **Network Security**
   - Deploy behind a properly configured reverse proxy in production
   - Enable HTTPS with valid certificates
   - Consider using a Web Application Firewall (WAF)

4. **Docker Deployment**
   - Keep Docker and container images updated
   - Scan images for vulnerabilities before deployment
   - Implement network segregation between containers
   - Limit container capabilities

5. **Monitoring and Logs**
   - Set up monitoring for suspicious activities
   - Regularly review logs for security incidents
   - Implement alerting for potential security events

## Security Updates

Security updates will be distributed through the normal release process. For critical security vulnerabilities, emergency patches may be released outside the regular release schedule.

Users will be notified about security updates through:
- Release notes
- Security advisories
- Direct communication for critical issues

## Responsible Disclosure

We appreciate the work of security researchers in improving the security of our project. We are committed to working with researchers who report vulnerabilities and will acknowledge their contributions.

## License

This security policy is provided under the same license as the Afeka ChatBot project. 