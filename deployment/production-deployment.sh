#!/bin/bash
# ============================================================================
# MedLogistics Production Deployment Script
# ============================================================================
# This script orchestrates the complete deployment and migration process
# for the MedLogistics application from API keys to Auth0 in production.
#
# CRITICAL: This script performs irreversible changes to production data.
# Only run after thorough testing in staging environment.
#
# Usage:
#   ./production-deployment.sh [PHASE]
#
# Phases:
#   pre-check    - Run pre-deployment checks only
#   backup       - Create database backup only  
#   schema       - Apply database schema changes only
#   migrate      - Run user migration only
#   verify       - Verify deployment only
#   full         - Run complete deployment (default)
#   rollback     - Rollback to previous state (use with caution)
#
# Prerequisites:
#   - Production environment configured
#   - Auth0 production tenant ready
#   - Database backup capability
#   - All environment variables set
# ============================================================================

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="production_deployment_$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
BACKUP_DIR="./backups"
DEPLOYMENT_PHASE="${1:-full}"

# Configuration
COMPOSE_FILE="docker-compose.yml"
BACKUP_RETENTION_DAYS=30
MAX_DOWNTIME_MINUTES=15
HEALTH_CHECK_TIMEOUT=300

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ============================================================================
# Logging Functions
# ============================================================================

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✓ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ✗ $1${NC}" | tee -a "$LOG_FILE"
}

log_critical() {
    echo -e "${PURPLE}[$(date '+%H:%M:%S')] 🚨 CRITICAL: $1${NC}" | tee -a "$LOG_FILE"
}

log_separator() {
    echo -e "${BLUE}$(printf '=%.0s' {1..80})${NC}" | tee -a "$LOG_FILE"
}

# ============================================================================
# Safety and Validation Functions
# ============================================================================

require_confirmation() {
    local message="$1"
    local required_input="${2:-DEPLOY}"
    
    echo -e "${RED}${message}${NC}"
    echo -e "${YELLOW}This action requires confirmation.${NC}"
    echo -e "${YELLOW}Type '${required_input}' to proceed:${NC}"
    
    read -r confirmation
    if [[ "$confirmation" != "$required_input" ]]; then
        log_error "Confirmation failed. Deployment cancelled."
        exit 1
    fi
    
    log_success "Confirmation received"
}

check_environment() {
    log "Checking production environment..."
    
    local required_vars=(
        "DATABASE_URL"
        "AUTH0_DOMAIN"
        "AUTH0_API_AUDIENCE" 
        "AUTH0_MANAGEMENT_CLIENT_ID"
        "AUTH0_MANAGEMENT_CLIENT_SECRET"
        "APP_ENV"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables:"
        printf '  - %s\n' "${missing_vars[@]}"
        return 1
    fi
    
    # Verify we're in production environment
    if [[ "${APP_ENV}" != "production" ]]; then
        log_error "APP_ENV is not set to 'production' (current: ${APP_ENV})"
        return 1
    fi
    
    log_success "Environment check passed"
}

check_database_connection() {
    log "Checking database connection..."
    
    if ! docker-compose exec -T api python -c "from database import engine; engine.connect().close(); print('Database connection OK')" > /dev/null 2>&1; then
        log_error "Database connection failed"
        return 1
    fi
    
    log_success "Database connection verified"
}

check_auth0_connection() {
    log "Checking Auth0 connection..."
    
    if ! docker-compose exec -T api python -c "
from migrate_users_to_auth0 import Auth0MigrationClient
import os
client = Auth0MigrationClient(
    os.getenv('AUTH0_DOMAIN'),
    os.getenv('AUTH0_MANAGEMENT_CLIENT_ID'),
    os.getenv('AUTH0_MANAGEMENT_CLIENT_SECRET')
)
token = client.get_management_token()
print('Auth0 connection OK')
" > /dev/null 2>&1; then
        log_error "Auth0 connection failed"
        return 1
    fi
    
    log_success "Auth0 connection verified"
}

check_disk_space() {
    log "Checking disk space..."
    
    local available_gb=$(df . | awk 'NR==2 {print int($4/1024/1024)}')
    local required_gb=5
    
    if [[ $available_gb -lt $required_gb ]]; then
        log_error "Insufficient disk space. Available: ${available_gb}GB, Required: ${required_gb}GB"
        return 1
    fi
    
    log_success "Disk space check passed (${available_gb}GB available)"
}

# ============================================================================
# Backup and Recovery Functions
# ============================================================================

create_database_backup() {
    log "Creating database backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    local backup_file="$BACKUP_DIR/medlogistics_backup_$(date +%Y%m%d_%H%M%S).sql"
    local backup_metadata="$BACKUP_DIR/backup_metadata_$(date +%Y%m%d_%H%M%S).json"
    
    # Create database dump
    if ! docker-compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$backup_file"; then
        log_error "Database backup failed"
        return 1
    fi
    
    # Create metadata file
    cat > "$backup_metadata" << EOF
{
    "backup_date": "$(date -Iseconds)",
    "database": "$POSTGRES_DB",
    "backup_file": "$backup_file",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "deployment_phase": "$DEPLOYMENT_PHASE",
    "app_version": "${APP_VERSION:-unknown}"
}
EOF
    
    # Compress backup
    gzip "$backup_file"
    backup_file="${backup_file}.gz"
    
    log_success "Database backup created: $backup_file"
    echo "$backup_file" > /tmp/last_backup_file
}

cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    find "$BACKUP_DIR" -name "medlogistics_backup_*.sql.gz" -mtime +$BACKUP_RETENTION_DAYS -delete || true
    find "$BACKUP_DIR" -name "backup_metadata_*.json" -mtime +$BACKUP_RETENTION_DAYS -delete || true
    
    log_success "Old backups cleaned up"
}

restore_from_backup() {
    local backup_file="$1"
    
    log_critical "RESTORING FROM BACKUP: $backup_file"
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Stop application
    docker-compose stop api
    
    # Restore database
    zcat "$backup_file" | docker-compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
    
    # Restart application
    docker-compose up -d
    
    log_success "Backup restored successfully"
}

# ============================================================================
# Deployment Functions
# ============================================================================

stop_application() {
    log "Stopping application services..."
    
    # Graceful shutdown
    docker-compose stop api
    
    # Wait for connections to drain
    sleep 10
    
    log_success "Application stopped"
}

start_application() {
    log "Starting application services..."
    
    docker-compose up -d
    
    # Wait for services to be healthy
    local timeout=$HEALTH_CHECK_TIMEOUT
    local counter=0
    
    while [[ $counter -lt $timeout ]]; do
        if docker-compose exec -T api python -c "from database import engine; engine.connect().close()" > /dev/null 2>&1; then
            log_success "Application started successfully"
            return 0
        fi
        sleep 5
        counter=$((counter + 5))
    done
    
    log_error "Application failed to start within $timeout seconds"
    return 1
}

apply_database_schema() {
    log "Applying database schema changes..."
    
    # Apply Alembic migrations
    if ! docker-compose exec -T api alembic upgrade head; then
        log_error "Database schema migration failed"
        return 1
    fi
    
    log_success "Database schema updated"
}

run_user_migration() {
    log "Running user migration to Auth0..."
    
    # Run the migration script
    if ! docker-compose exec -T api python migrate_users_to_auth0.py --confirm --batch-size=20; then
        log_error "User migration failed"
        return 1
    fi
    
    log_success "User migration completed"
}

verify_deployment() {
    log "Verifying deployment..."
    
    # Run verification script
    if ! docker-compose exec -T api python verify_migration.py; then
        log_error "Deployment verification failed"
        return 1
    fi
    
    # Test API endpoints
    local api_url="http://localhost:8000"
    if ! curl -f -s "$api_url/health" > /dev/null; then
        log_error "API health check failed"
        return 1
    fi
    
    log_success "Deployment verification passed"
}

# ============================================================================
# Main Deployment Phases
# ============================================================================

phase_pre_check() {
    log_separator
    log "PHASE: PRE-DEPLOYMENT CHECKS"
    log_separator
    
    check_environment
    check_database_connection
    check_auth0_connection
    check_disk_space
    
    log_success "Pre-deployment checks completed"
}

phase_backup() {
    log_separator
    log "PHASE: DATABASE BACKUP"
    log_separator
    
    create_database_backup
    cleanup_old_backups
    
    log_success "Backup phase completed"
}

phase_schema() {
    log_separator
    log "PHASE: SCHEMA MIGRATION"
    log_separator
    
    require_confirmation "About to apply database schema changes in PRODUCTION"
    
    apply_database_schema
    
    log_success "Schema migration phase completed"
}

phase_migrate() {
    log_separator
    log "PHASE: USER MIGRATION"
    log_separator
    
    require_confirmation "About to migrate users to Auth0 in PRODUCTION"
    
    run_user_migration
    
    log_success "User migration phase completed"
}

phase_verify() {
    log_separator
    log "PHASE: DEPLOYMENT VERIFICATION"
    log_separator
    
    verify_deployment
    
    log_success "Verification phase completed"
}

phase_rollback() {
    log_separator
    log "PHASE: ROLLBACK"
    log_separator
    
    require_confirmation "About to ROLLBACK production deployment" "ROLLBACK"
    
    local last_backup
    if [[ -f /tmp/last_backup_file ]]; then
        last_backup=$(cat /tmp/last_backup_file)
    else
        log_error "No backup file found for rollback"
        return 1
    fi
    
    restore_from_backup "$last_backup"
    
    log_success "Rollback completed"
}

phase_full() {
    log_separator
    log "PHASE: FULL DEPLOYMENT"
    log_separator
    
    require_confirmation "About to run FULL PRODUCTION DEPLOYMENT with user migration"
    
    phase_pre_check
    phase_backup
    
    # Record start time for downtime calculation
    local start_time=$(date +%s)
    
    stop_application
    phase_schema
    start_application
    phase_migrate
    phase_verify
    
    # Calculate downtime
    local end_time=$(date +%s)
    local downtime_minutes=$(( (end_time - start_time) / 60 ))
    
    if [[ $downtime_minutes -gt $MAX_DOWNTIME_MINUTES ]]; then
        log_warning "Deployment exceeded maximum downtime: ${downtime_minutes}min (max: ${MAX_DOWNTIME_MINUTES}min)"
    else
        log_success "Deployment completed within acceptable downtime: ${downtime_minutes}min"
    fi
    
    log_success "Full deployment completed successfully"
}

# ============================================================================
# Script Execution
# ============================================================================

main() {
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Initialize log file
    > "$LOG_FILE"
    
    log_separator
    log "MEDLOGISTICS PRODUCTION DEPLOYMENT"
    log "Phase: $DEPLOYMENT_PHASE"
    log "Started at: $TIMESTAMP"
    log_separator
    
    # Set up trap for cleanup on exit
    trap 'log_error "Deployment interrupted!"; exit 1' INT TERM
    
    case "$DEPLOYMENT_PHASE" in
        "pre-check")
            phase_pre_check
            ;;
        "backup")
            phase_backup
            ;;
        "schema")
            phase_pre_check
            phase_backup
            phase_schema
            ;;
        "migrate")
            phase_migrate
            ;;
        "verify")
            phase_verify
            ;;
        "rollback")
            phase_rollback
            ;;
        "full")
            phase_full
            ;;
        *)
            log_error "Unknown deployment phase: $DEPLOYMENT_PHASE"
            echo "Valid phases: pre-check, backup, schema, migrate, verify, rollback, full"
            exit 1
            ;;
    esac
    
    log_separator
    log_success "DEPLOYMENT PHASE '$DEPLOYMENT_PHASE' COMPLETED SUCCESSFULLY"
    log "Completed at: $(date '+%Y-%m-%d %H:%M:%S')"
    log "Log file: $LOG_FILE"
    log_separator
}

# Show usage if help requested
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [PHASE]"
    echo ""
    echo "Phases:"
    echo "  pre-check    - Run pre-deployment checks only"
    echo "  backup       - Create database backup only"
    echo "  schema       - Apply database schema changes only"
    echo "  migrate      - Run user migration only"
    echo "  verify       - Verify deployment only"  
    echo "  full         - Run complete deployment (default)"
    echo "  rollback     - Rollback to previous state"
    echo ""
    echo "Examples:"
    echo "  $0                    # Full deployment"
    echo "  $0 pre-check          # Check prerequisites only"
    echo "  $0 backup             # Create backup only"
    echo "  $0 rollback           # Rollback deployment"
    exit 0
fi

# Run main function
main 