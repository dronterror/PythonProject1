# MedLogistics Production Deployment Guide

## Overview

This guide provides complete instructions for deploying the MedLogistics application's Auth0 migration to production. This is a **critical migration** that transforms the authentication system from API keys to Auth0 JWT tokens.

> ⚠️ **CRITICAL WARNING**: This deployment involves irreversible changes to production data. Follow this guide exactly and ensure all testing has been completed before proceeding.

## Prerequisites

### 1. Auth0 Production Tenant
- [ ] Production Auth0 tenant configured (see `AUTH0_PRODUCTION_SETUP.md`)
- [ ] SPA application created and configured
- [ ] API resource server created and configured
- [ ] Machine-to-Machine application created for user management
- [ ] Custom Action deployed for role claims
- [ ] All roles created (super_admin, pharmacist, doctor, nurse)

### 2. Environment Configuration
- [ ] Production server with Docker and Docker Compose
- [ ] All environment variables configured (see `production-env-template.txt`)
- [ ] Database backup capability verified
- [ ] SSL certificates in place
- [ ] Monitoring and alerting configured

### 3. Testing Completed
- [ ] Migration tested in staging environment
- [ ] Docker-based migration test completed (`./test_migration.sh`)
- [ ] All verification scripts tested
- [ ] Rollback procedures tested

### 4. Team Readiness
- [ ] Deployment team assembled and briefed
- [ ] Communication plan established
- [ ] Rollback decision criteria defined
- [ ] User communication prepared

## Pre-Deployment Checklist

### 1. Code and Environment
```bash
# Verify you're on the correct branch
git branch
git status

# Verify environment variables
echo $APP_ENV  # Should be 'production'
echo $AUTH0_DOMAIN
echo $DATABASE_URL

# Test database connection
docker-compose exec api python -c "from database import engine; engine.connect().close(); print('DB OK')"

# Test Auth0 connection
docker-compose exec api python -c "from migrate_users_to_auth0 import Auth0MigrationClient; import os; Auth0MigrationClient(os.getenv('AUTH0_DOMAIN'), os.getenv('AUTH0_MANAGEMENT_CLIENT_ID'), os.getenv('AUTH0_MANAGEMENT_CLIENT_SECRET')).get_management_token(); print('Auth0 OK')"
```

### 2. User Communication
- [ ] Notify users of scheduled maintenance window
- [ ] Prepare communication for post-migration password reset
- [ ] Set up status page updates

### 3. Infrastructure
- [ ] Verify disk space (minimum 5GB free)
- [ ] Ensure monitoring is active
- [ ] Verify backup systems are operational
- [ ] Confirm rollback procedures are ready

## Deployment Phases

### Phase 1: Pre-Deployment Checks

**Duration**: 10-15 minutes  
**Downtime**: None

```bash
# Run comprehensive pre-checks
./deployment/production-deployment.sh pre-check
```

**Verify**:
- ✅ All environment variables present
- ✅ Database connection working
- ✅ Auth0 connection working
- ✅ Sufficient disk space
- ✅ All services healthy

**On Failure**: Fix issues and re-run pre-checks before proceeding.

### Phase 2: Database Backup

**Duration**: 5-10 minutes  
**Downtime**: None

```bash
# Create production database backup
./deployment/production-deployment.sh backup
```

**Verify**:
- ✅ Backup file created in `./backups/`
- ✅ Backup file is not empty
- ✅ Backup file is compressed
- ✅ Metadata file created

**Critical**: Do not proceed without a successful backup.

### Phase 3: Database Schema Migration

**Duration**: 2-5 minutes  
**Downtime**: 2-5 minutes

⚠️ **MAINTENANCE WINDOW STARTS**

```bash
# Apply database schema changes
./deployment/production-deployment.sh schema
```

This phase will:
1. Stop the API service (downtime begins)
2. Apply Alembic migrations
3. Restart the API service (downtime ends)

**Verify**:
- ✅ Alembic migrations applied successfully
- ✅ `auth0_user_id` column added to users table
- ✅ New tables created (hospitals, wards, user_ward_permissions)
- ✅ API service restarted successfully

**On Failure**: Automatic rollback will be attempted.

### Phase 4: User Migration to Auth0

**Duration**: 5-20 minutes (depends on user count)  
**Downtime**: None (users can still authenticate during migration)

```bash
# Migrate users to Auth0
./deployment/production-deployment.sh migrate
```

This phase will:
1. Fetch all users without `auth0_user_id`
2. Create users in Auth0 with temporary passwords
3. Update local database with Auth0 user IDs
4. Process users in batches to avoid rate limits

**Verify**:
- ✅ Migration script completed without errors
- ✅ Migration report shows 100% success rate
- ✅ All users have `auth0_user_id` values
- ✅ No duplicate Auth0 user IDs

**On Failure**: 
- Review migration report
- Fix issues with failed users
- Re-run migration for failed users only

### Phase 5: Deployment Verification

**Duration**: 5-10 minutes  
**Downtime**: None

```bash
# Verify deployment success
./deployment/production-deployment.sh verify
```

**Verify**:
- ✅ All users have Auth0 user IDs
- ✅ No duplicate Auth0 user IDs
- ✅ Database constraints satisfied
- ✅ API health checks passing
- ✅ Sample Auth0 login works

**On Failure**: Investigate issues immediately and consider rollback.

## Full Deployment Command

For experienced operators, the entire deployment can be run with a single command:

```bash
# Full deployment (includes all phases)
./deployment/production-deployment.sh full
```

This will execute all phases in sequence with appropriate confirmations.

## Post-Deployment Tasks

### 1. Verification
```bash
# Run additional verification
docker-compose exec api python verify_migration.py

# Test API endpoints
curl -f https://api.medlog.app/health
curl -f https://api.medlog.app/docs

# Check Auth0 users created
# Login to Auth0 dashboard and verify user count
```

### 2. User Communication
- [ ] Send communication about password reset requirement
- [ ] Update status page to "operational"
- [ ] Monitor user login success rates

### 3. Monitoring
- [ ] Monitor application logs for Auth0-related errors
- [ ] Track authentication success/failure rates
- [ ] Monitor database performance
- [ ] Watch for any user-reported issues

### 4. Documentation Updates
- [ ] Update API documentation
- [ ] Update user guides
- [ ] Update development setup instructions

## Rollback Procedures

### When to Rollback
Consider rollback if:
- Migration verification fails
- Critical Auth0 issues discovered
- Significant user impact observed
- Data integrity issues detected

### How to Rollback

⚠️ **CRITICAL**: Rollback must be executed quickly to minimize data loss.

```bash
# Immediate rollback to pre-migration state
./deployment/production-deployment.sh rollback
```

This will:
1. Stop the application
2. Restore database from backup
3. Restart application with old authentication

**Post-Rollback**:
- Users will return to API key authentication
- All Auth0 users created during migration will remain in Auth0
- Investigate issues before attempting migration again

## Troubleshooting

### Common Issues

#### 1. Auth0 Connection Failures
```bash
# Check Auth0 credentials
echo $AUTH0_MANAGEMENT_CLIENT_ID
echo $AUTH0_MANAGEMENT_CLIENT_SECRET

# Test Management API access
docker-compose exec api python -c "
from migrate_users_to_auth0 import Auth0MigrationClient
import os
client = Auth0MigrationClient(os.getenv('AUTH0_DOMAIN'), os.getenv('AUTH0_MANAGEMENT_CLIENT_ID'), os.getenv('AUTH0_MANAGEMENT_CLIENT_SECRET'))
print(client.get_management_token())
"
```

#### 2. Database Migration Failures
```bash
# Check Alembic status
docker-compose exec api alembic current
docker-compose exec api alembic history

# Manually run specific migration
docker-compose exec api alembic upgrade +1
```

#### 3. User Migration Failures
```bash
# Check migration logs
docker-compose exec api cat user_migration.log

# Restart failed migration
docker-compose exec api python migrate_users_to_auth0.py --batch-size=5
```

#### 4. Performance Issues
```bash
# Check database connections
docker-compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT count(*) FROM pg_stat_activity;"

# Check container resources
docker stats

# Monitor Auth0 rate limits
# Check Auth0 dashboard for rate limit notifications
```

## Recovery Scenarios

### Scenario 1: Partial Migration Failure
Some users migrated successfully, others failed.

**Solution**:
1. Identify failed users from migration report
2. Fix underlying issues (email validation, etc.)
3. Re-run migration script (it will skip already migrated users)

### Scenario 2: Auth0 Service Outage During Migration
Auth0 becomes unavailable during user migration.

**Solution**:
1. Wait for Auth0 service restoration
2. Re-run migration script
3. Verify all users were migrated
4. Continue with verification phase

### Scenario 3: Database Corruption
Database becomes corrupted during schema migration.

**Solution**:
1. Stop all services immediately
2. Restore from backup using rollback procedure
3. Investigate root cause
4. Fix issues and retry migration

## Security Considerations

### 1. Temporary Passwords
- All migrated users receive temporary passwords
- Users must reset passwords on first login
- Monitor for password reset completion rates

### 2. Auth0 User IDs
- Auth0 user IDs are permanent and cannot be changed
- Ensure proper backup of user ID mappings
- Monitor for any duplicate or invalid user IDs

### 3. API Key Deprecation
- Old API keys remain in database initially
- Plan for API key removal after migration success
- Monitor for any continued API key authentication attempts

## Performance Monitoring

### Key Metrics to Monitor

1. **Authentication Performance**
   - JWT token validation time
   - Auth0 login success rate
   - Token refresh frequency

2. **Database Performance**
   - Query response times
   - Connection pool utilization
   - Index usage on new columns

3. **Application Performance**
   - API response times
   - Error rates
   - User session duration

### Alerting Rules

Set up alerts for:
- Authentication failure rate > 5%
- API response time > 2 seconds
- Database connection failures
- Auth0 rate limit warnings

## Success Criteria

The deployment is considered successful when:

- [ ] All users have been migrated to Auth0
- [ ] Migration verification passes 100%
- [ ] API health checks are passing
- [ ] Sample user login via Auth0 works
- [ ] No critical errors in application logs
- [ ] Database performance is stable
- [ ] User authentication success rate > 95%

## Emergency Contacts

During deployment, ensure these contacts are available:

- **Database Administrator**: [Contact Info]
- **Auth0 Support**: [Support Plan Details]
- **Infrastructure Team**: [Contact Info]
- **Product Manager**: [Contact Info]

## Deployment Checklist Summary

**Pre-Deployment**:
- [ ] Auth0 production tenant configured
- [ ] Environment variables set
- [ ] Testing completed
- [ ] Team assembled
- [ ] Users notified

**Deployment**:
- [ ] Pre-checks passed
- [ ] Backup created
- [ ] Schema migration applied
- [ ] User migration completed
- [ ] Verification passed

**Post-Deployment**:
- [ ] Monitoring active
- [ ] Users notified
- [ ] Documentation updated
- [ ] Success metrics met

---

## Final Notes

This migration represents a significant architectural upgrade for the MedLogistics platform. The careful execution of this deployment plan will ensure:

1. **Zero Data Loss**: Comprehensive backup and verification procedures
2. **Minimal Downtime**: Only during schema migration phase
3. **Secure Migration**: All users properly migrated with secure temporary passwords
4. **Rollback Ready**: Complete rollback procedures available if needed

**Remember**: Take your time, follow the procedures exactly, and don't hesitate to rollback if anything looks incorrect. The success of this migration is critical for the platform's future growth and security. 