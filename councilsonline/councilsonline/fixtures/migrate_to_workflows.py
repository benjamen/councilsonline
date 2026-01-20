#!/usr/bin/env python3
"""
Script to migrate existing Request status to workflow_state
Run with: bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.migrate_to_workflows.migrate_requests
"""

import frappe


def migrate_requests():
    """Migrate existing Request records from status to workflow_state"""

    print("\n" + "="*80)
    print("MIGRATING REQUESTS TO WORKFLOW STATES")
    print("="*80 + "\n")

    # Status to workflow_state mapping
    status_mapping = {
        "Draft": "Draft",
        "Submitted": "Submitted",
        "Acknowledged": "Acknowledged",
        "Processing": "Processing",
        "RFI Issued": "RFI Issued",
        "RFI Received": "RFI Received",
        "Pending Decision": "Pending Decision",
        "Approved": "Approved",
        "Approved with Conditions": "Approved with Conditions",
        "Declined": "Declined",
        "Withdrawn": "Withdrawn",
        "Under Appeal": "Under Appeal"
    }

    # Get all requests
    requests = frappe.get_all(
        "Request",
        fields=["name", "status", "workflow_state", "request_type"],
        filters={"docstatus": ["!=", 2]}  # Exclude cancelled
    )

    print(f"Found {len(requests)} requests to migrate\n")

    migrated = 0
    skipped = 0
    errors = []

    for req in requests:
        # Skip if workflow_state is already set
        if req.workflow_state:
            print(f"⊘ Skipped {req.name} - workflow_state already set ({req.workflow_state})")
            skipped += 1
            continue

        # Map status to workflow_state
        workflow_state = status_mapping.get(req.status)

        if not workflow_state:
            print(f"⚠ Warning: No mapping for status '{req.status}' in {req.name}")
            errors.append(f"{req.name}: Unknown status '{req.status}'")
            skipped += 1
            continue

        # Check if workflow state exists
        if not frappe.db.exists("Workflow State", workflow_state):
            print(f"✗ Error: Workflow State '{workflow_state}' does not exist for {req.name}")
            errors.append(f"{req.name}: Workflow State '{workflow_state}' not found")
            skipped += 1
            continue

        # Update workflow_state
        try:
            frappe.db.set_value(
                "Request",
                req.name,
                "workflow_state",
                workflow_state,
                update_modified=False
            )
            print(f"✓ Migrated {req.name}: {req.status} → {workflow_state}")
            migrated += 1

        except Exception as e:
            print(f"✗ Failed to migrate {req.name}: {str(e)}")
            errors.append(f"{req.name}: {str(e)}")
            skipped += 1

    # Commit changes
    frappe.db.commit()

    # Summary
    print(f"\n" + "="*80)
    print("MIGRATION SUMMARY")
    print("="*80)
    print(f"Total requests: {len(requests)}")
    print(f"Migrated: {migrated}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {len(errors)}")

    if errors:
        print(f"\n⚠ Errors encountered:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    print(f"\n✓ Migration complete!")

    return {
        "total": len(requests),
        "migrated": migrated,
        "skipped": skipped,
        "errors": len(errors)
    }


def link_workflows_to_request_types():
    """Link workflows to Request Types"""

    print("\n" + "="*80)
    print("LINKING WORKFLOWS TO REQUEST TYPES")
    print("="*80 + "\n")

    # Define mappings
    workflow_mappings = {
        "Resource Consent": "Resource Consent Workflow",
        "LIM": "LIM Request Workflow"
    }

    linked = 0
    skipped = 0

    for request_type_name, workflow_name in workflow_mappings.items():
        # Check if Request Type exists
        if not frappe.db.exists("Request Type", request_type_name):
            print(f"⊘ Skipped: Request Type '{request_type_name}' not found")
            skipped += 1
            continue

        # Check if Workflow exists
        if not frappe.db.exists("Workflow", workflow_name):
            print(f"⊘ Skipped: Workflow '{workflow_name}' not found")
            skipped += 1
            continue

        # Link workflow to request type
        try:
            frappe.db.set_value(
                "Request Type",
                request_type_name,
                "workflow_template",
                workflow_name,
                update_modified=False
            )
            print(f"✓ Linked: {request_type_name} → {workflow_name}")
            linked += 1

        except Exception as e:
            print(f"✗ Failed to link {request_type_name}: {str(e)}")
            skipped += 1

    frappe.db.commit()

    print(f"\n" + "="*80)
    print("LINKING SUMMARY")
    print("="*80)
    print(f"Linked: {linked}")
    print(f"Skipped: {skipped}")

    return {"linked": linked, "skipped": skipped}


def run_full_migration():
    """Run complete migration process"""

    print("\n" + "="*80)
    print("COMPLETE WORKFLOW MIGRATION")
    print("="*80)

    # Step 1: Link workflows to request types
    print("\nStep 1: Linking workflows to Request Types...")
    link_result = link_workflows_to_request_types()

    # Step 2: Migrate existing requests
    print("\nStep 2: Migrating existing requests...")
    migrate_result = migrate_requests()

    # Final summary
    print("\n" + "="*80)
    print("COMPLETE MIGRATION SUMMARY")
    print("="*80)
    print(f"\nWorkflows linked: {link_result['linked']}")
    print(f"Requests migrated: {migrate_result['migrated']}/{migrate_result['total']}")
    print(f"Total skipped: {migrate_result['skipped']}")
    print(f"Total errors: {migrate_result['errors']}")

    print("\n✓ Full migration complete!")
    print("\nNext steps:")
    print("1. Test workflow transitions in UI")
    print("2. Verify statutory clock tracking works")
    print("3. Test assessment project creation on 'Acknowledged' state")
    print("4. Train staff on Workflow Actions inbox")

    return {
        "workflows_linked": link_result,
        "requests_migrated": migrate_result
    }


if __name__ == "__main__":
    run_full_migration()
