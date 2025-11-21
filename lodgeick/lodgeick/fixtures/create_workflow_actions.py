#!/usr/bin/env python3
"""
Script to create Workflow Action Master records
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.create_workflow_actions.create_actions
"""

import frappe


def create_actions():
    """Create workflow action master records"""
    frappe.flags.in_import = True

    actions = [
        "Submit",
        "Acknowledge",
        "Return for Amendments",
        "Start Processing",
        "Issue RFI",
        "Send to Manager",
        "Mark RFI Received",
        "Resume Processing",
        "Issue Another RFI",
        "Approve",
        "Approve with Conditions",
        "Decline",
        "Return to Planner",
        "Mark Under Appeal",
        "Withdraw",
        "Complete",
        "Assign",
        "Resolve",
        "Close",
        "Escalate",
        "Ready for Inspection",
        "Complete Inspections",
        "Issue CCC",
        "Close Request"
    ]

    print("\n" + "="*80)
    print("CREATING WORKFLOW ACTION MASTERS")
    print("="*80 + "\n")

    created = []
    skipped = []

    for action_name in actions:
        if frappe.db.exists("Workflow Action Master", action_name):
            print(f"⊘ Skipped '{action_name}' (already exists)")
            skipped.append(action_name)
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action_name
            })
            doc.insert(ignore_permissions=True)
            created.append(action_name)
            print(f"✓ Created action: {action_name}")
        except Exception as e:
            print(f"✗ Failed to create action '{action_name}': {str(e)}")
            frappe.log_error(f"Failed to create workflow action: {str(e)}")

    frappe.db.commit()
    frappe.flags.in_import = False

    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Created: {len(created)} actions")
    print(f"Skipped: {len(skipped)} actions")

    if created:
        print("\n✓ Actions created:")
        for name in created:
            print(f"  - {name}")

    return {"created": created, "skipped": skipped}


if __name__ == "__main__":
    create_actions()
