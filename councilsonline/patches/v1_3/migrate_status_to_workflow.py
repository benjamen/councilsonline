# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate


def execute():
    """
    Migration patch to ensure all requests have workflow_state set.
    This patch migrates from the old 'status' field to 'workflow_state'.

    Status field has been removed from Request DocType.
    All status tracking now uses workflow_state only.
    """

    frappe.logger().info("Starting migration: status → workflow_state")

    # Get all requests that don't have workflow_state set
    requests_without_state = frappe.db.sql("""
        SELECT name, status
        FROM `tabRequest`
        WHERE workflow_state IS NULL OR workflow_state = ''
    """, as_dict=True)

    if not requests_without_state:
        frappe.logger().info("No requests need workflow_state migration")
        return

    frappe.logger().info(f"Found {len(requests_without_state)} requests without workflow_state")

    # Mapping of old status values to workflow states
    # Based on the unified workflow in create_unified_workflow.py
    status_to_workflow_state = {
        "Draft": "Draft",
        "Submitted": "Submitted",
        "Acknowledged": "Acknowledged",
        "Assessment": "Assessment",
        "Technical Assessment": "Technical Assessment",
        "Pending Additional Information": "Pending Additional Information",
        "Under Review": "Under Review",
        "Approved": "Approved",
        "Approved with Conditions": "Approved with Conditions",
        "Declined": "Declined",
        "Withdrawn": "Withdrawn",
        "Cancelled": "Cancelled",
        "Completed": "Completed"
    }

    updated_count = 0
    for req in requests_without_state:
        try:
            # Get the status value (may be None or empty)
            old_status = req.get("status") or "Draft"

            # Map to workflow state
            workflow_state = status_to_workflow_state.get(old_status, "Draft")

            # Update the request directly in DB (bypass validation)
            frappe.db.set_value(
                "Request",
                req["name"],
                "workflow_state",
                workflow_state,
                update_modified=False
            )

            updated_count += 1

            if updated_count % 100 == 0:
                frappe.db.commit()
                frappe.logger().info(f"Migrated {updated_count} requests...")

        except Exception as e:
            frappe.logger().error(f"Error migrating request {req['name']}: {str(e)}")
            continue

    # Final commit
    frappe.db.commit()

    frappe.logger().info(f"✓ Migration complete: {updated_count} requests updated with workflow_state")

    # Verify migration
    remaining = frappe.db.count("Request", {
        "workflow_state": ["in", [None, ""]]
    })

    if remaining > 0:
        frappe.logger().warning(f"⚠ {remaining} requests still without workflow_state")
    else:
        frappe.logger().info("✓ All requests now have workflow_state set")
