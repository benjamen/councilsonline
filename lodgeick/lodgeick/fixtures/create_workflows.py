#!/usr/bin/env python3
"""
Script to create Workflows for different Request Types
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.create_workflows.create_all_workflows
"""

import frappe


def create_resource_consent_workflow():
    """Create Resource Consent Workflow"""

    workflow_name = "Resource Consent Workflow"

    # Check if workflow already exists
    if frappe.db.exists("Workflow", workflow_name):
        print(f"⊘ Workflow '{workflow_name}' already exists, skipping...")
        return None

    # Create workflow
    workflow = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": workflow_name,
        "document_type": "Request",
        "is_active": 1,
        "workflow_state_field": "workflow_state",
        "override_status": 0,
        "send_email_alert": 1,

        # Define states
        "states": [
            {
                "state": "Draft",
                "doc_status": "0",
                "allow_edit": "All",
                "is_optional_state": 0
            },
            {
                "state": "Submitted",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 0
            },
            {
                "state": "Acknowledged",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 0
            },
            {
                "state": "Processing",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 0
            },
            {
                "state": "RFI Issued",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 0
            },
            {
                "state": "RFI Received",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 0
            },
            {
                "state": "Pending Decision",
                "doc_status": "1",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 0
            },
            {
                "state": "Approved",
                "doc_status": "1",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 0
            },
            {
                "state": "Approved with Conditions",
                "doc_status": "1",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 0
            },
            {
                "state": "Declined",
                "doc_status": "1",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 0
            },
            {
                "state": "Withdrawn",
                "doc_status": "2",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 0
            },
            {
                "state": "Under Appeal",
                "doc_status": "1",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 0
            }
        ],

        # Define transitions
        "transitions": [
            # Draft → Submitted
            {
                "state": "Draft",
                "action": "Submit",
                "next_state": "Submitted",
                "allowed": "All",
                "allow_self_approval": 1
            },
            # Submitted → Acknowledged
            {
                "state": "Submitted",
                "action": "Acknowledge",
                "next_state": "Acknowledged",
                "allowed": "Lodgeick User",
                "allow_self_approval": 0
            },
            # Acknowledged → Start Processing
            {
                "state": "Acknowledged",
                "action": "Start Processing",
                "next_state": "Processing",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },
            # Processing → Issue RFI
            {
                "state": "Processing",
                "action": "Issue RFI",
                "next_state": "RFI Issued",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },
            # Processing → Send to Manager
            {
                "state": "Processing",
                "action": "Send to Manager",
                "next_state": "Pending Decision",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1,
                "condition": "doc.assessment_status == 'Completed'"
            },
            # RFI Issued → RFI Received
            {
                "state": "RFI Issued",
                "action": "Mark RFI Received",
                "next_state": "RFI Received",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },
            # RFI Received → Resume Processing
            {
                "state": "RFI Received",
                "action": "Resume Processing",
                "next_state": "Processing",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },
            # RFI Received → Issue Another RFI
            {
                "state": "RFI Received",
                "action": "Issue Another RFI",
                "next_state": "RFI Issued",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },
            # Pending Decision → Approve
            {
                "state": "Pending Decision",
                "action": "Approve",
                "next_state": "Approved",
                "allowed": "Lodgeick Admin",
                "allow_self_approval": 0
            },
            # Pending Decision → Approve with Conditions
            {
                "state": "Pending Decision",
                "action": "Approve with Conditions",
                "next_state": "Approved with Conditions",
                "allowed": "Lodgeick Admin",
                "allow_self_approval": 0
            },
            # Pending Decision → Decline
            {
                "state": "Pending Decision",
                "action": "Decline",
                "next_state": "Declined",
                "allowed": "Lodgeick Admin",
                "allow_self_approval": 0
            },
            # Pending Decision → Return to Planner
            {
                "state": "Pending Decision",
                "action": "Return to Planner",
                "next_state": "Processing",
                "allowed": "Lodgeick Admin",
                "allow_self_approval": 1
            },
            # Approved/Declined → Under Appeal
            {
                "state": "Approved",
                "action": "Mark Under Appeal",
                "next_state": "Under Appeal",
                "allowed": "Lodgeick Admin",
                "allow_self_approval": 1
            },
            {
                "state": "Approved with Conditions",
                "action": "Mark Under Appeal",
                "next_state": "Under Appeal",
                "allowed": "Lodgeick Admin",
                "allow_self_approval": 1
            },
            {
                "state": "Declined",
                "action": "Mark Under Appeal",
                "next_state": "Under Appeal",
                "allowed": "Lodgeick Admin",
                "allow_self_approval": 1
            },
            # Any state → Withdrawn
            {
                "state": "Submitted",
                "action": "Withdraw",
                "next_state": "Withdrawn",
                "allowed": "All",
                "allow_self_approval": 1
            },
            {
                "state": "Acknowledged",
                "action": "Withdraw",
                "next_state": "Withdrawn",
                "allowed": "All",
                "allow_self_approval": 1
            },
            {
                "state": "Processing",
                "action": "Withdraw",
                "next_state": "Withdrawn",
                "allowed": "All",
                "allow_self_approval": 1
            },
            {
                "state": "RFI Issued",
                "action": "Withdraw",
                "next_state": "Withdrawn",
                "allowed": "All",
                "allow_self_approval": 1
            },
            {
                "state": "Pending Decision",
                "action": "Withdraw",
                "next_state": "Withdrawn",
                "allowed": "All",
                "allow_self_approval": 1
            }
        ]
    })

    workflow.insert(ignore_permissions=True)
    frappe.db.commit()

    print(f"✓ Created workflow: {workflow_name}")
    print(f"  States: {len(workflow.states)}")
    print(f"  Transitions: {len(workflow.transitions)}")

    return workflow


def create_lim_workflow():
    """Create simple LIM Workflow"""

    workflow_name = "LIM Request Workflow"

    if frappe.db.exists("Workflow", workflow_name):
        print(f"⊘ Workflow '{workflow_name}' already exists, skipping...")
        return None

    workflow = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": workflow_name,
        "document_type": "Request",
        "is_active": 1,
        "workflow_state_field": "workflow_state",
        "override_status": 0,
        "send_email_alert": 1,

        "states": [
            {
                "state": "Draft",
                "doc_status": "0",
                "allow_edit": "All"
            },
            {
                "state": "Submitted",
                "doc_status": "1",
                "allow_edit": "Lodgeick User"
            },
            {
                "state": "Processing",
                "doc_status": "1",
                "allow_edit": "Lodgeick User"
            },
            {
                "state": "Completed",
                "doc_status": "1",
                "allow_edit": "Lodgeick User"
            }
        ],

        "transitions": [
            {
                "state": "Draft",
                "action": "Submit",
                "next_state": "Submitted",
                "allowed": "All",
                "allow_self_approval": 1
            },
            {
                "state": "Submitted",
                "action": "Start Processing",
                "next_state": "Processing",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },
            {
                "state": "Processing",
                "action": "Complete",
                "next_state": "Completed",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            }
        ]
    })

    workflow.insert(ignore_permissions=True)
    frappe.db.commit()

    print(f"✓ Created workflow: {workflow_name}")
    print(f"  States: {len(workflow.states)}")
    print(f"  Transitions: {len(workflow.transitions)}")

    return workflow


def create_all_workflows():
    """Create all workflows"""
    frappe.flags.in_import = True

    print("\n" + "="*80)
    print("CREATING WORKFLOWS")
    print("="*80 + "\n")

    workflows = []

    # Create Resource Consent Workflow
    rc_workflow = create_resource_consent_workflow()
    if rc_workflow:
        workflows.append(rc_workflow.name)

    # Create LIM Workflow
    lim_workflow = create_lim_workflow()
    if lim_workflow:
        workflows.append(lim_workflow.name)

    frappe.flags.in_import = False

    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Created {len(workflows)} workflows")

    if workflows:
        print("\n✓ Workflows created:")
        for name in workflows:
            print(f"  - {name}")

    return {"workflows": workflows}


if __name__ == "__main__":
    create_all_workflows()
