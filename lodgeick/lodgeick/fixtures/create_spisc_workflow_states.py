#!/usr/bin/env python3
"""
Create SPISC-specific workflow states
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.create_spisc_workflow_states.create_states
"""

import frappe


def create_states():
    """Create SPISC workflow states and actions"""

    print("\n" + "="*80)
    print("CREATING SPISC WORKFLOW STATES AND ACTIONS")
    print("="*80 + "\n")

    # Create workflow states
    states = [
        {
            "workflow_state_name": "Payment Pending",
            "style": "Warning"
        },
        {
            "workflow_state_name": "Paid",
            "style": "Success"
        }
    ]

    for state_data in states:
        state_name = state_data["workflow_state_name"]

        if frappe.db.exists("Workflow State", state_name):
            print(f"✓ Workflow State '{state_name}' already exists")
        else:
            state_doc = frappe.get_doc({
                "doctype": "Workflow State",
                **state_data
            })
            state_doc.insert(ignore_permissions=True)
            print(f"✓ Created Workflow State: {state_name}")

    # Create workflow actions
    actions = [
        "Setup Payment",
        "Mark as Paid"
    ]

    for action_name in actions:
        if frappe.db.exists("Workflow Action Master", action_name):
            print(f"✓ Workflow Action '{action_name}' already exists")
        else:
            action_doc = frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action_name
            })
            action_doc.insert(ignore_permissions=True)
            print(f"✓ Created Workflow Action: {action_name}")

    frappe.db.commit()

    print(f"\n✓ SPISC workflow states and actions ready!")
    print("="*80 + "\n")


if __name__ == "__main__":
    create_states()
