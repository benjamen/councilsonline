#!/usr/bin/env python3
"""
Create a unified comprehensive workflow for all Request Types
Since Frappe only allows ONE active workflow per DocType, this creates
a single workflow with conditional transitions based on request_type

Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.create_unified_workflow.create_workflow
"""

import frappe


def create_workflow():
    """Create unified Request workflow with conditional transitions"""

    workflow_name = "Request Processing Workflow"

    # Check if workflow already exists
    if frappe.db.exists("Workflow", workflow_name):
        print(f"⊘ Workflow '{workflow_name}' already exists")
        print("  Deleting and recreating...")
        frappe.delete_doc("Workflow", workflow_name, force=1)
        frappe.db.commit()

    print("\n" + "="*80)
    print("CREATING UNIFIED REQUEST WORKFLOW")
    print("="*80 + "\n")

    workflow = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": workflow_name,
        "document_type": "Request",
        "is_active": 1,
        "workflow_state_field": "workflow_state",
        "override_status": 0,
        "send_email_alert": 1,

        # All possible states
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
                "is_optional_state": 1  # Optional - only for Resource/Building Consents
            },
            {
                "state": "RFI Received",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 1  # Optional
            },
            {
                "state": "Awaiting Inspection",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 1  # Optional - only for Building Consents
            },
            {
                "state": "Inspections Complete",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 1  # Optional
            },
            {
                "state": "Pending Decision",
                "doc_status": "1",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 1  # Optional - for Resource Consents
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
                "is_optional_state": 1  # Optional
            },
            {
                "state": "Declined",
                "doc_status": "1",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 1  # Optional
            },
            {
                "state": "Completed",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 0
            },
            {
                "state": "CCC Issued",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 1  # Optional - Building Consent only
            },
            {
                "state": "Withdrawn",
                "doc_status": "2",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 1
            },
            {
                "state": "Under Appeal",
                "doc_status": "1",
                "allow_edit": "Lodgeick Admin",
                "is_optional_state": 1  # Optional
            },
            {
                "state": "Payment Pending",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 1  # Optional - SPISC only
            },
            {
                "state": "Paid",
                "doc_status": "1",
                "allow_edit": "Lodgeick User",
                "is_optional_state": 1  # Optional - SPISC only
            }
        ],

        # Transitions covering all request types
        "transitions": [
            # === COMMON TRANSITIONS (All Request Types) ===

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
                "allow_self_approval": 1  # Enable for testing/small councils
            },

            # Acknowledged → Processing
            {
                "state": "Acknowledged",
                "action": "Start Processing",
                "next_state": "Processing",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },

            # === LIM REQUEST FLOW ===

            # Processing → Completed (LIM, simple requests)
            {
                "state": "Processing",
                "action": "Complete",
                "next_state": "Completed",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1,
                "condition": "doc.request_type in ['LIM']"
            },

            # === RESOURCE CONSENT FLOW ===

            # Processing → Issue RFI
            {
                "state": "Processing",
                "action": "Issue RFI",
                "next_state": "RFI Issued",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1,
                "condition": "doc.request_type in ['Resource Consent', 'Social Pension for Indigent Senior Citizens (SPISC)']"
            },

            # Processing → Send to Manager (Resource Consent, SPISC)
            {
                "state": "Processing",
                "action": "Send to Manager",
                "next_state": "Pending Decision",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1,
                "condition": "doc.request_type in ['Resource Consent', 'Social Pension for Indigent Senior Citizens (SPISC)']"
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

            # === BUILDING CONSENT FLOW ===

            # Processing → Awaiting Inspection (Building Consent)
            {
                "state": "Processing",
                "action": "Ready for Inspection",
                "next_state": "Awaiting Inspection",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1,
                "condition": "doc.request_type == 'Building Consent'"
            },

            # Awaiting Inspection → Inspections Complete
            {
                "state": "Awaiting Inspection",
                "action": "Complete Inspections",
                "next_state": "Inspections Complete",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },

            # Inspections Complete → CCC Issued
            {
                "state": "Inspections Complete",
                "action": "Issue CCC",
                "next_state": "CCC Issued",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },

            # CCC Issued → Completed
            {
                "state": "CCC Issued",
                "action": "Close Request",
                "next_state": "Completed",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },

            # === APPEAL TRANSITIONS ===

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

            # === SPISC PAYMENT FLOW ===

            # Approved → Payment Pending (SPISC)
            {
                "state": "Approved",
                "action": "Setup Payment",
                "next_state": "Payment Pending",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1,
                "condition": "doc.request_type == 'Social Pension for Indigent Senior Citizens (SPISC)'"
            },

            # Payment Pending → Paid
            {
                "state": "Payment Pending",
                "action": "Mark as Paid",
                "next_state": "Paid",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },

            # Paid → Completed
            {
                "state": "Paid",
                "action": "Complete",
                "next_state": "Completed",
                "allowed": "Lodgeick User",
                "allow_self_approval": 1
            },

            # === WITHDRAWAL TRANSITIONS (Multiple states) ===

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
    print(f"  States: {len(workflow.states)} (including optional states)")
    print(f"  Transitions: {len(workflow.transitions)}")
    print(f"\nWorkflow Flow Summary:")
    print(f"  • All Requests: Draft → Submitted → Acknowledged → Processing")
    print(f"  • LIM Requests: Processing → Completed")
    print(f"  • Resource Consents: Processing → [RFI cycle] → Pending Decision → Approved/Declined")
    print(f"  • Building Consents: Processing → Awaiting Inspection → CCC Issued → Completed")

    # Deactivate other workflows
    print(f"\nDeactivating other workflows...")
    other_workflows = frappe.get_all(
        'Workflow',
        filters={
            'document_type': 'Request',
            'name': ['!=', workflow_name]
        }
    )

    for wf in other_workflows:
        wf_doc = frappe.get_doc('Workflow', wf.name)
        wf_doc.is_active = 0
        wf_doc.save()
        print(f"  ⊘ Deactivated: {wf_doc.workflow_name}")

    frappe.db.commit()

    print(f"\n✓ Unified workflow activated!")
    print("="*80 + "\n")

    return workflow


if __name__ == "__main__":
    create_workflow()
