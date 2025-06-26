# Keycloak Troubleshooting Guide

## Common Issues and Solutions

### 1. Keycloak Constantly Loading

**Symptoms:**
- Keycloak interface shows loading spinner indefinitely
- Cannot access Keycloak admin console
- Login requests timeout

**Solutions:**

#### A. Check Host File Configuration
Ensure your hosts file includes the required entries:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac:** `/etc/hosts`

```
127.0.0.1 medlog.local api.medlog.local keycloak.medlog.local
```

#### B. Verify Docker Services
Check if all services are running:
```bash
docker-compose ps
```

Check Keycloak logs:
```bash
docker-compose logs keycloak
```

#### C. Clear Browser Cache
1. Clear browser cache and cookies
2. Try accessing in incognito/private mode
3. Disable browser extensions temporarily

### 2. Frontend Login Failures

**Symptoms:**
- Login form shows errors
- "Network error" or "Connection refused"
- CORS errors in browser console

**Solutions:**

#### A. Check Network Configuration
1. Verify Keycloak is accessible:
   ```bash
   curl -v http://keycloak.medlog.local/health/ready
   ```

2. Test from frontend container:
   ```bash
   docker exec -it medlog_frontend curl http://keycloak.medlog.local/health/ready
   ```

#### B. CORS Configuration
Ensure CORS is properly configured in docker-compose.yml:
```yaml
environment:
  - KC_HTTP_CORS_ORIGINS=http://medlog.local,http://localhost,http://localhost:3000,http://localhost:5173,http://localhost:80
```

#### C. Check Keycloak Realm Configuration
1. Access Keycloak admin console: http://keycloak.medlog.local
2. Go to realm settings
3. Verify client configuration:
   - Client ID: `medlog-clients`
   - Access Type: `public` or `confidential`
   - Valid Redirect URIs: `http://localhost:3000/*`, `http://medlog.local/*`
   - Web Origins: `http://localhost:3000`, `http://medlog.local`

### 3. Token Issues

**Symptoms:**
- Invalid token errors
- Authentication fails after successful login
- Token parsing errors

**Solutions:**

#### A. Check Token Format
Enable debug logging in frontend to see token details:
```javascript
console.log('Token received:', tokenData);
```

#### B. Verify Realm Access
Ensure users have proper roles assigned in Keycloak:
1. Go to Users → Select User → Role Mappings
2. Assign realm roles: `doctor`, `nurse`, `pharmacist`, `admin`

### 4. Environment-Specific Issues

#### Development Environment
- Use `localhost:8081` for direct Keycloak access
- Use `keycloak.medlog.local` for Traefik routing

#### Production Environment
- Ensure proper SSL certificates
- Update CORS origins for production domains
- Configure proper hostname settings

### 5. Debugging Steps

#### Step 1: Check Service Health
```bash
# Check all services
docker-compose ps

# Check Keycloak specifically
docker-compose logs keycloak --tail=50

# Check Traefik routing
docker-compose logs traefik --tail=50
```

#### Step 2: Test Network Connectivity
```bash
# From host machine
ping keycloak.medlog.local
curl -v http://keycloak.medlog.local/health/ready

# From frontend container
docker exec -it medlog_frontend ping keycloak
docker exec -it medlog_frontend curl http://keycloak:8080/health/ready
```

#### Step 3: Browser Developer Tools
1. Open browser dev tools (F12)
2. Check Network tab for failed requests
3. Look for CORS errors in Console tab
4. Verify cookies are being set

#### Step 4: Keycloak Admin Console
1. Access: http://keycloak.medlog.local
2. Login with admin credentials
3. Check realm settings
4. Verify client configuration
5. Check user roles and permissions

### 6. Common Error Messages

#### "Failed to fetch"
- **Cause:** Network connectivity issue
- **Solution:** Check Docker networking, host file configuration

#### "CORS policy blocked"
- **Cause:** Missing or incorrect CORS configuration
- **Solution:** Update Keycloak CORS settings and Traefik middleware

#### "Invalid token"
- **Cause:** Token format or parsing issue
- **Solution:** Check token structure and user roles

#### "Connection refused"
- **Cause:** Service not running or wrong port
- **Solution:** Verify service status and port configuration

### 7. Quick Fixes

#### Reset Everything
```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

#### Restart Keycloak Only
```bash
docker-compose restart keycloak
```

#### Clear Frontend Cache
```bash
# Clear npm cache
npm cache clean --force

# Rebuild frontend
docker-compose build frontend
```

### 8. Monitoring Commands

#### Real-time Logs
```bash
# All services
docker-compose logs -f

# Keycloak only
docker-compose logs -f keycloak

# Frontend only
docker-compose logs -f frontend
```

#### Health Checks
```bash
# Check Keycloak health
curl http://keycloak.medlog.local/health/ready

# Check frontend accessibility
curl http://medlog.local

# Check backend API
curl http://localhost/api/health
```

### 9. Environment Variables

Create a `.env` file in the root directory:
```env
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
VITE_KEYCLOAK_URL=http://keycloak.medlog.local
VITE_KEYCLOAK_REALM=medlog-realm
VITE_KEYCLOAK_CLIENT_ID=medlog-clients
```

### 10. Final Checklist

Before seeking additional help, verify:
- [ ] Host file is correctly configured
- [ ] All Docker services are running
- [ ] Keycloak health endpoint responds
- [ ] Browser cache is cleared
- [ ] CORS configuration is correct
- [ ] Realm and client settings are proper
- [ ] Network connectivity works
- [ ] Environment variables are set
- [ ] Logs don't show critical errors

If issues persist, provide:
1. Docker service status (`docker-compose ps`)
2. Keycloak logs (`docker-compose logs keycloak`)
3. Browser console errors
4. Network request details from browser dev tools 