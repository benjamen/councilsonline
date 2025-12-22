#!/usr/bin/env python3
"""
Check workflow setup for SPISC requests
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.check_workflow_setup.check_workflow
"""

import frappe


def check_workflow():
    """Verify workflow is properly configured for SPISC"""

    print("\n" + "="*80)
    print("CHECKING WORKFLOW SETUP FOR SPISC")
    print("="*80 + "\n")

    # 1. Check if workflow exists and is active
    workflow = frappe.get_doc("Workflow", "Request Processing Workflow")
    print(f"Workflow: {workflow.name}")
    print(f"  Document Type: {workflow.document_type}")
    print(f"  Is Active: {workflow.is_active}")
    print(f"  Workflow State Field: {workflow.workflow_state_field}")

    if not workflow.is_active:
        print("\n⚠ WARNING: Workflow is NOT active!")
        print("  Activating workflow...")
        workflow.is_active = 1
        workflow.save(ignore_permissions=True)
        frappe.db.commit()
        print("  ✓ Workflow activated")

    # 2. Check states
    print(f"\nWorkflow States ({len(workflow.states)}):")
    state_names = []
    for state in workflow.states:
        state_names.append(state.state)
        print(f"  - {state.state} (doc_status: {state.doc_status})")

    # Verify Payment Pending and Paid exist
    if "Payment Pending" in state_names and "Paid" in state_names:
        print("\n✓ SPISC payment states found (Payment Pending, Paid)")
    else:
        print("\n⚠ WARNING: SPISC payment states missing!")
        if "Payment Pending" not in state_names:
            print("  Missing: Payment Pending")
        if "Paid" not in state_names:
            print("  Missing: Paid")

    # 3. Check transitions
    print(f"\nWorkflow Transitions ({len(workflow.transitions)}):")
    spisc_transitions = []
    payment_transitions = []

    for t in workflow.transitions:
        condition = t.get("condition", "") or ""

        # Check for SPISC-specific transitions
        if "SPISC" in condition or "Social Pension" in condition:
            spisc_transitions.append(t)
            print(f"  ✓ SPISC: {t.state} --[{t.action}]--> {t.next_state}")

        # Check for payment flow transitions
        if t.state in ["Approved", "Payment Pending", "Paid"] or \
           t.next_state in ["Payment Pending", "Paid"]:
            payment_transitions.append(t)
            print(f"  💰 Payment: {t.state} --[{t.action}]--> {t.next_state}")

    print(f"\n✓ Found {len(spisc_transitions)} SPISC-specific transitions")
    print(f"✓ Found {len(payment_transitions)} payment-related transitions")

    # 4. Check workflow actions exist
    print("\nChecking Workflow Actions:")

    payment_actions = ["Setup Payment", "Mark as Paid"]
    for action_name in payment_actions:
        exists = frappe.db.exists("Workflow Action Master", action_name)
        if exists:
            print(f"  ✓ {action_name} exists")
        else:
            print(f"  ✗ {action_name} MISSING")

    # 5. Check workflow states exist
    print("\nChecking Workflow States:")

    payment_states = ["Payment Pending", "Paid"]
    for state_name in payment_states:
        exists = frappe.db.exists("Workflow State", state_name)
        if exists:
            print(f"  ✓ {state_name} exists")
        else:
            print(f"  ✗ {state_name} MISSING")

    # 6. Get SPISC request type exact name
    print("\nChecking Request Type:")
    spisc_types = frappe.get_all(
        "Request Type",
        filters=[["name", "like", "%SPISC%"]],
        fields=["name"]
    )

    if spisc_types:
        for rt in spisc_types:
            print(f"  ✓ Found: {rt.name}")
    else:
        print("  ✗ No SPISC request type found")

    # 7. Test a sample SPISC request to see available actions
    print("\nChecking Available Actions for SPISC in Approved state:")

    # Get a SPISC request in Approved state (or create test scenario)
    spisc_requests = frappe.get_all(
        "Request",
        filters={
            "request_type": "Social Pension for Indigent Senior Citizens (SPISC)",
            "workflow_state": "Approved"
        },
        fields=["name", "workflow_state", "request_type"],
        limit=1
    )

    if spisc_requests:
        req = spisc_requests[0]
        print(f"  Found test request: {req.name}")
        print(f"    State: {req.workflow_state}")
        print(f"    Type: {req.request_type}")

        # Get available actions
        doc = frappe.get_doc("Request", req.name)

        # Get workflow actions for current state
        available_actions = []
        for transition in workflow.transitions:
            if transition.state == doc.workflow_state:
                # Check condition
                condition = transition.get("condition", "")
                if condition:
                    try:
                        # Evaluate condition
                        if eval(condition, {"doc": doc}):
                            available_actions.append({
                                "action": transition.action,
                                "next_state": transition.next_state,
                                "condition": condition
                            })
                    except Exception as e:
                        print(f"    ⚠ Error evaluating condition for {transition.action}: {e}")
                else:
                    # No condition, action is available
                    available_actions.append({
                        "action": transition.action,
                        "next_state": transition.next_state,
                        "condition": "None"
                    })

        print(f"\n  Available actions for {req.name}:")
        if available_actions:
            for action in available_actions:
                print(f"    ✓ {action['action']} → {action['next_state']}")
                if action['condition'] != "None":
                    print(f"      Condition: {action['condition']}")
        else:
            print("    ⚠ No actions available!")
            print("    This may indicate workflow condition issues")
    else:
        print("  ⚠ No SPISC requests in Approved state found for testing")
        print("  Create test data to verify workflow actions")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    check_workflow()
