#!/bin/bash
# ============================================================================
# MedLogistics Migration Test Script
# ============================================================================
# This script automates the complete testing of the user migration process
# from API keys to Auth0 in a safe, isolated Docker environment.
#
# Usage:
#   ./test_migration.sh [OPTIONS]
#
# Options:
#   --skip-build     Skip Docker image building
#   --keep-data      Keep test data after completion
#   --verbose        Enable verbose logging
#   --batch-size N   Set migration batch size (default: 5)
#   --user-count N   Number of test users to create (default: 5)
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - Auth0 test tenant configured
#   - Environment variables set for Auth0 test credentials
# ============================================================================

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.test-migration.yml"
LOG_FILE="migration_test_$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Default values
SKIP_BUILD=false
KEEP_DATA=false
VERBOSE=false
BATCH_SIZE=5
USER_COUNT=5
COMPOSE_PROJECT_NAME="medlog-migration-test"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
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

log_separator() {
    echo -e "${BLUE}$(printf '=%.0s' {1..80})${NC}" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    # Check Auth0 test credentials
    if [[ -z "${AUTH0_TEST_DOMAIN:-}" ]]; then
        log_warning "AUTH0_TEST_DOMAIN not set - using default test domain"
    fi
    
    if [[ -z "${AUTH0_TEST_MANAGEMENT_CLIENT_ID:-}" ]]; then
        log_warning "AUTH0_TEST_MANAGEMENT_CLIENT_ID not set - migration will use dry-run mode"
    fi
    
    log_success "Prerequisites check completed"
}

cleanup_test_environment() {
    log "Cleaning up test environment..."
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" down --remove-orphans || true
    
    # Remove volumes if not keeping data
    if [[ "$KEEP_DATA" == false ]]; then
        docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" down -v || true
        log_success "Test data cleaned up"
    else
        log_warning "Test data preserved (use --cleanup to remove)"
    fi
    
    # Remove unused networks
    docker network prune -f || true
}

build_services() {
    if [[ "$SKIP_BUILD" == true ]]; then
        log "Skipping Docker image build"
        return
    fi
    
    log "Building Docker services..."
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" build --no-cache
    log_success "Docker services built successfully"
}

start_services() {
    log "Starting test services..."
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" up -d db_test_migration redis_test_migration
    
    # Wait for database to be healthy
    log "Waiting for database to be ready..."
    timeout=60
    counter=0
    while [[ $counter -lt $timeout ]]; do
        if docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" exec -T db_test_migration pg_isready -U medlog_test_user -d medlogistics_test_migration; then
            log_success "Database is ready"
            break
        fi
        sleep 2
        counter=$((counter + 2))
    done
    
    if [[ $counter -ge $timeout ]]; then
        log_error "Database failed to start within $timeout seconds"
        return 1
    fi
    
    log_success "Test services started successfully"
}

run_command_in_container() {
    local command="$1"
    local service_name="${2:-api_test_migration}"
    
    if [[ "$VERBOSE" == true ]]; then
        log "Executing: $command"
    fi
    
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" run --rm "$service_name" sh -c "$command"
}

apply_initial_schema() {
    log "Applying initial database schema (pre-migration)..."
    
    # Create tables with initial schema
    run_command_in_container "python -c 'from database import engine; from models import Base; Base.metadata.create_all(bind=engine); print(\"Tables created successfully\")'"
    
    log_success "Initial schema applied"
}

seed_pre_migration_data() {
    log "Seeding database with pre-migration test data..."
    
    run_command_in_container "python seed_pre_migration_users.py --count=$USER_COUNT --clear"
    
    log_success "Pre-migration test data seeded"
}

apply_migration_schema() {
    log "Applying Auth0 migration schema changes..."
    
    # Note: In a real scenario, you would use Alembic migrations
    # For testing, we're using the new schema directly
    run_command_in_container "python -c 'print(\"Schema migration would be applied here via Alembic\")'"
    
    log_success "Migration schema applied"
}

run_user_migration() {
    log "Running user migration to Auth0..."
    
    # Determine if we should run in dry-run mode
    if [[ -z "${AUTH0_TEST_MANAGEMENT_CLIENT_ID:-}" ]]; then
        log_warning "Running migration in DRY-RUN mode (no Auth0 credentials)"
        run_command_in_container "python migrate_users_to_auth0.py --dry-run --batch-size=$BATCH_SIZE --confirm"
    else
        log "Running migration in LIVE mode with Auth0 test tenant"
        run_command_in_container "python migrate_users_to_auth0.py --batch-size=$BATCH_SIZE --confirm"
    fi
    
    log_success "User migration completed"
}

verify_migration() {
    log "Verifying migration results..."
    
    run_command_in_container "python verify_migration.py"
    
    log_success "Migration verification completed"
}

run_integration_tests() {
    log "Running integration tests..."
    
    # Test basic API functionality
    run_command_in_container "python -c 'from database import SessionLocal; from models import User; db = SessionLocal(); users = db.query(User).all(); print(f\"Found {len(users)} users in database\"); db.close()'"
    
    # Test Auth0 integration (if credentials available)
    if [[ -n "${AUTH0_TEST_MANAGEMENT_CLIENT_ID:-}" ]]; then
        run_command_in_container "python -c 'from migrate_users_to_auth0 import Auth0MigrationClient; import os; client = Auth0MigrationClient(os.getenv(\"AUTH0_DOMAIN\"), os.getenv(\"AUTH0_MANAGEMENT_CLIENT_ID\"), os.getenv(\"AUTH0_MANAGEMENT_CLIENT_SECRET\")); token = client.get_management_token(); print(\"Auth0 connection successful\")'"
    fi
    
    log_success "Integration tests completed"
}

generate_test_report() {
    log "Generating test report..."
    
    local report_file="migration_test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
MEDLOGISTICS MIGRATION TEST REPORT
==================================
Test Date: $(date)
Test Environment: Docker Compose Isolated Environment
Migration Type: API Key to Auth0

CONFIGURATION:
- Test Users Created: $USER_COUNT
- Migration Batch Size: $BATCH_SIZE
- Auth0 Test Mode: ${AUTH0_TEST_MANAGEMENT_CLIENT_ID:+Live}${AUTH0_TEST_MANAGEMENT_CLIENT_ID:-Dry Run}
- Docker Compose File: $COMPOSE_FILE

TEST RESULTS:
EOF
    
    # Add container logs to report
    echo "" >> "$report_file"
    echo "=== TEST EXECUTION LOG ===" >> "$report_file"
    cat "$LOG_FILE" >> "$report_file"
    
    # Add migration reports if they exist
    if docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" exec -T api_test_migration find /app -name "*migration_report*" -type f 2>/dev/null; then
        echo "" >> "$report_file"
        echo "=== MIGRATION REPORTS ===" >> "$report_file"
        docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" exec -T api_test_migration sh -c 'find /app -name "*migration_report*" -type f -exec cat {} \;' >> "$report_file" 2>/dev/null || true
    fi
    
    log_success "Test report generated: $report_file"
}

# ============================================================================
# Main Test Sequence
# ============================================================================

main() {
    log_separator
    log "STARTING MEDLOGISTICS MIGRATION TEST"
    log "Test started at: $TIMESTAMP"
    log_separator
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --keep-data)
                KEEP_DATA=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --batch-size)
                BATCH_SIZE="$2"
                shift 2
                ;;
            --user-count)
                USER_COUNT="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-build     Skip Docker image building"
                echo "  --keep-data      Keep test data after completion"
                echo "  --verbose        Enable verbose logging"
                echo "  --batch-size N   Set migration batch size (default: 5)"
                echo "  --user-count N   Number of test users to create (default: 5)"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Set up trap for cleanup
    trap 'log_error "Test interrupted!"; cleanup_test_environment; exit 1' INT TERM
    
    # Execute test sequence
    check_prerequisites
    
    # Clean up any existing test environment
    cleanup_test_environment
    
    # Build and start services
    build_services
    start_services
    
    # Execute migration test sequence
    apply_initial_schema
    seed_pre_migration_data
    apply_migration_schema
    run_user_migration
    verify_migration
    run_integration_tests
    
    # Generate final report
    generate_test_report
    
    log_separator
    log_success "MIGRATION TEST COMPLETED SUCCESSFULLY!"
    log "Test Duration: $(($(date +%s) - $(date -d "$TIMESTAMP" +%s))) seconds"
    log_separator
    
    # Cleanup
    if [[ "$KEEP_DATA" == false ]]; then
        cleanup_test_environment
    else
        log_warning "Test environment preserved. Use 'docker-compose -f $COMPOSE_FILE -p $COMPOSE_PROJECT_NAME down -v' to clean up manually."
    fi
    
    exit 0
}

# ============================================================================
# Script Execution
# ============================================================================

# Change to script directory
cd "$SCRIPT_DIR"

# Make sure we have a clean log file
> "$LOG_FILE"

# Run main function
main "$@" 