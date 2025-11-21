#!/usr/bin/env python3
"""
Script to create Workflow State records
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.create_workflow_states.create_states
"""

import frappe
import json
import os


def create_states():
    """Create all workflow state records"""
    frappe.flags.in_import = True

    # Get the fixtures file path
    fixtures_dir = os.path.dirname(os.path.abspath(__file__))
    states_file = os.path.join(fixtures_dir, 'workflow_states.json')

    # Load states from JSON
    with open(states_file, 'r') as f:
        states = json.load(f)

    print("\n" + "="*80)
    print("CREATING WORKFLOW STATES")
    print("="*80 + "\n")

    created = []
    skipped = []

    for state_data in states:
        state_name = state_data["workflow_state_name"]

        # Check if state already exists
        if frappe.db.exists("Workflow State", state_name):
            print(f"⊘ Skipped '{state_name}' (already exists)")
            skipped.append(state_name)
            continue

        # Create state
        try:
            doc = frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": state_name,
                "style": state_data.get("style", "Default")
            })
            doc.insert(ignore_permissions=True)
            created.append(state_name)
            print(f"✓ Created state: {state_name} ({state_data.get('style', 'Default')})")
        except Exception as e:
            print(f"✗ Failed to create state '{state_name}': {str(e)}")
            frappe.log_error(f"Failed to create workflow state: {str(e)}")

    frappe.db.commit()
    frappe.flags.in_import = False

    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Created: {len(created)} states")
    print(f"Skipped: {len(skipped)} states (already existed)")

    if created:
        print("\n✓ States created:")
        for name in created:
            print(f"  - {name}")

    return {"created": created, "skipped": skipped}


if __name__ == "__main__":
    create_states()
