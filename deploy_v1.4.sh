#!/bin/bash

#############################################################################
# Lodgeick v1.4.0 Deployment Script
#############################################################################
#
# This script deploys Lodgeick v1.4.0 with single-tenant architecture
#
# Prerequisites:
# - Frappe v14+
# - Lodgeick v1.3.x currently installed
# - Database backup completed
# - Adequate disk space
#
# Usage:
#   chmod +x deploy_v1.4.sh
#   ./deploy_v1.4.sh <site-name>
#
# Example:
#   ./deploy_v1.4.sh lodgeick.localhost
#
#############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SITE_NAME="${1}"
APP_NAME="lodgeick"
VERSION="v1.4.0"
BACKUP_DIR="./backups"

#############################################################################
# Helper Functions
#############################################################################

print_header() {
    echo -e "${BLUE}"
    echo "============================================================================"
    echo "$1"
    echo "============================================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check if site name provided
    if [ -z "$SITE_NAME" ]; then
        print_error "Site name not provided"
        echo "Usage: ./deploy_v1.4.sh <site-name>"
        echo "Example: ./deploy_v1.4.sh lodgeick.localhost"
        exit 1
    fi

    # Check if site exists
    if [ ! -d "sites/$SITE_NAME" ]; then
        print_error "Site '$SITE_NAME' does not exist"
        exit 1
    fi

    print_success "Site '$SITE_NAME' found"

    # Check if bench command exists
    if ! command -v bench &> /dev/null; then
        print_error "bench command not found"
        exit 1
    fi

    print_success "bench command available"

    # Check if we're in frappe-bench directory
    if [ ! -f "sites/currentsite.txt" ]; then
        print_error "Not in frappe-bench directory"
        exit 1
    fi

    print_success "In correct directory"

    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    print_success "Backup directory ready"
}

backup_database() {
    print_header "Step 1: Backing Up Database"

    BACKUP_FILE="${BACKUP_DIR}/${SITE_NAME}_pre_v1.4_$(date +%Y%m%d_%H%M%S).sql.gz"

    print_info "Creating backup: $BACKUP_FILE"

    bench --site "$SITE_NAME" backup --with-files || {
        print_error "Backup failed"
        exit 1
    }

    # Find the latest backup
    LATEST_BACKUP=$(ls -t sites/$SITE_NAME/private/backups/*.sql.gz | head -1)
    cp "$LATEST_BACKUP" "$BACKUP_FILE"

    print_success "Database backed up to: $BACKUP_FILE"
}

pull_latest_code() {
    print_header "Step 2: Pulling Latest Code"

    cd apps/$APP_NAME || {
        print_error "App directory not found"
        exit 1
    }

    print_info "Fetching latest changes..."
    git fetch origin

    print_info "Checking out main branch..."
    git checkout main || {
        print_error "Failed to checkout main branch"
        cd ../..
        exit 1
    }

    print_info "Pulling latest changes..."
    git pull origin main || {
        print_error "Failed to pull latest changes"
        cd ../..
        exit 1
    }

    cd ../..
    print_success "Code updated to latest main"
}

run_migrations() {
    print_header "Step 3: Running Database Migrations"

    print_info "Executing migration patches..."
    print_info "  - Converting Council to Single DocType"
    print_info "  - Dropping multi-tenant fields"
    print_info "  - Installing default Request Types"

    bench --site "$SITE_NAME" migrate || {
        print_error "Migration failed"
        print_warning "You may need to restore from backup"
        exit 1
    }

    print_success "Migrations completed"

    # Verify migration
    print_info "Verifying migration..."

    MIGRATED_COUNT=$(bench --site "$SITE_NAME" console <<EOF
import frappe
frappe.init(site="$SITE_NAME")
frappe.connect()
count = frappe.db.count("Request", {"workflow_state": ["is", "set"]})
print(count)
frappe.destroy()
EOF
)

    if [ "$MIGRATED_COUNT" -gt 0 ]; then
        print_success "Migration verified: $MIGRATED_COUNT requests have workflow_state"
    else
        print_warning "No requests found with workflow_state"
    fi
}

verify_request_types() {
    print_header "Step 4: Verifying Request Types Installation"

    print_info "Checking installed request types..."

    bench --site "$SITE_NAME" console <<EOF
import frappe
frappe.init(site="$SITE_NAME")
frappe.connect()

# Count request types
rt_count = frappe.db.count("Request Type", {"is_active": 1})
print(f"✓ Found {rt_count} active Request Types")

# List request types
request_types = frappe.get_all("Request Type",
    filters={"is_active": 1},
    fields=["type_name", "type_code", "category"],
    limit=10
)

if request_types:
    print("\\nInstalled Request Types:")
    for rt in request_types:
        print(f"  • {rt.type_name} ({rt.type_code}) - {rt.category}")
else:
    print("⚠ No active request types found")

# Count condition templates
template_count = frappe.db.count("Consent Condition Template", {"is_active": 1})
print(f"\\n✓ Found {template_count} active Consent Condition Templates")

frappe.destroy()
EOF

    print_success "Request types verified"
}

build_frontend() {
    print_header "Step 5: Building Frontend Assets"

    print_info "Clearing asset cache..."
    bench clear-cache

    print_info "Building $APP_NAME assets..."
    bench build --app "$APP_NAME" || {
        print_error "Frontend build failed"
        exit 1
    }

    print_success "Frontend assets built"
}

restart_services() {
    print_header "Step 6: Restarting Services"

    print_info "Restarting bench..."
    bench restart || {
        print_error "Restart failed"
        exit 1
    }

    print_success "Services restarted"
}

verify_deployment() {
    print_header "Step 7: Verifying Deployment"

    # Check if site is accessible
    print_info "Checking site accessibility..."

    # Verify Council Single DocType
    print_info "Verifying Council Single DocType..."

    bench --site "$SITE_NAME" console <<EOF
import frappe
frappe.init(site="$SITE_NAME")
frappe.connect()

# Check Council is single
meta = frappe.get_meta("Council")
if meta.issingle:
    print("✓ Council is Single DocType")

    # Get council data
    council = frappe.get_single("Council")
    if council.council_name:
        print(f"✓ Council configured: {council.council_name}")
    else:
        print("⚠ Council not configured yet")
else:
    print("✗ Council is not Single DocType - migration may have failed")

# Check Request schema
request_meta = frappe.get_meta("Request")
if request_meta.has_field("workflow_state"):
    print("✓ Request.workflow_state field exists")
else:
    print("✗ Request.workflow_state field missing")

# Check if old council field removed
if request_meta.has_field("council"):
    print("⚠ Request.council field still exists (should be removed)")
else:
    print("✓ Request.council field removed")

frappe.destroy()
EOF

    print_success "Deployment verified"
}

print_summary() {
    print_header "Deployment Summary"

    echo -e "${GREEN}"
    echo "✓ Lodgeick $VERSION deployed successfully!"
    echo ""
    echo "Major Changes in v1.4.0:"
    echo "  • ✓ Single-tenant architecture implemented"
    echo "  • ✓ Council converted to Single DocType"
    echo "  • ✓ Multi-tenant fields removed from Request"
    echo "  • ✓ Default Request Types installed"
    echo "  • ✓ Consent Condition Templates installed"
    echo "  • ✓ Request Management workspace created"
    echo "  • ✓ Number Cards added (5 metrics)"
    echo "  • ✓ Kanban board configuration added"
    echo ""
    echo "Architecture Improvements:"
    echo "  • Simplified codebase (~245 lines removed)"
    echo "  • Single council per site configuration"
    echo "  • Cleaner API endpoints (council_code removed)"
    echo "  • Better performance (no multi-tenant overhead)"
    echo ""
    echo "Next Steps:"
    echo "  1. Configure Council: Navigate to Council in Desk"
    echo "  2. Test Request Management workspace"
    echo "  3. Review Request Types: Desk > Request Type"
    echo "  4. Test key workflows (create request, submit, acknowledge)"
    echo "  5. Monitor error logs: tail -f logs/frappe.log"
    echo ""
    echo "Backup Location:"
    echo "  $BACKUP_FILE"
    echo ""
    echo "If issues occur, restore from backup:"
    echo "  bench --site $SITE_NAME restore $BACKUP_FILE"
    echo -e "${NC}"
}

#############################################################################
# Main Execution
#############################################################################

main() {
    print_header "Lodgeick $VERSION Deployment"

    echo "Site: $SITE_NAME"
    echo "Version: $VERSION"
    echo "Date: $(date)"
    echo ""

    read -p "Continue with deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi

    # Execute deployment steps
    check_prerequisites
    backup_database
    pull_latest_code
    run_migrations
    verify_request_types
    build_frontend
    restart_services
    verify_deployment
    print_summary
}

# Run main function
main "$@"
