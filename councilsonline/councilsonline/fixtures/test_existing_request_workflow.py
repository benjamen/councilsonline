#!/usr/bin/env python3
"""
Test workflow with existing requests
Run with: bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.test_existing_request_workflow.test
"""

import frappe


def test():
    """Test workflow with an existing submitted request"""

    print("\n" + "="*80)
    print("TESTING WORKFLOW WITH EXISTING REQUEST")
    print("="*80 + "\n")

    # Get a submitted request
    request_name = "RC-2025-006"

    if not frappe.db.exists("Request", request_name):
        print(f"✗ Request {request_name} not found!")
        return

    doc = frappe.get_doc("Request", request_name)

    print(f"Testing with: {doc.name}")
    print(f"  Request Type: {doc.request_type}")
    print(f"  Current Workflow State: {doc.workflow_state}")
    print(f"  Docstatus: {doc.docstatus}")
    print(f"  Statutory Clock: {doc.statutory_clock_started or 'Not started'}")

    # Get available transitions
    print(f"\nGetting available workflow transitions...")

    from frappe.model.workflow import get_transitions

    try:
        transitions = get_transitions(doc)

        if transitions:
            print(f"✓ Found {len(transitions)} available transitions:")
            for trans in transitions:
                print(f"    - {trans.get('action')}: {trans.get('state')} → {trans.get('next_state')}")
                if trans.get('condition'):
                    print(f"      Condition: {trans.get('condition')}")

            # Try to acknowledge the request
            print(f"\nAttempting to 'Acknowledge' the request...")

            if any(t.get('action') == 'Acknowledge' for t in transitions):
                from frappe.model.workflow import apply_workflow

                try:
                    # Record state before
                    state_before = doc.workflow_state
                    clock_before = doc.statutory_clock_started

                    # Apply workflow
                    apply_workflow(doc, "Acknowledge")
                    frappe.db.commit()
                    doc.reload()

                    # Check state after
                    print(f"✓ Successfully acknowledged!")
                    print(f"    State: {state_before} → {doc.workflow_state}")
                    print(f"    Statutory Clock: {clock_before or 'None'} → {doc.statutory_clock_started}")
                    print(f"    Acknowledged Date: {doc.acknowledged_date}")
                    print(f"    Assessment Project: {doc.assessment_project or 'None (may be created async)'}")

                    # Get new available transitions
                    new_transitions = get_transitions(doc)
                    print(f"\n✓ New available transitions ({len(new_transitions)}):")
                    for trans in new_transitions:
                        print(f"    - {trans.get('action')}")

                    # Try to start processing
                    if any(t.get('action') == 'Start Processing' for t in new_transitions):
                        print(f"\nAttempting to 'Start Processing'...")
                        apply_workflow(doc, "Start Processing")
                        frappe.db.commit()
                        doc.reload()

                        print(f"✓ Successfully started processing!")
                        print(f"    Current State: {doc.workflow_state}")

                        # Check for Resource Consent specific actions
                        processing_transitions = get_transitions(doc)
                        print(f"\n✓ Available actions in Processing ({len(processing_transitions)}):")
                        for trans in processing_transitions:
                            action = trans.get('action')
                            condition = trans.get('condition')
                            print(f"    - {action}")
                            if condition:
                                print(f"      Condition: {condition}")

                        # Try Issue RFI
                        if any(t.get('action') == 'Issue RFI' for t in processing_transitions):
                            print(f"\nAttempting to 'Issue RFI' (should stop statutory clock)...")
                            clock_running = not doc.statutory_clock_stopped

                            apply_workflow(doc, "Issue RFI")
                            frappe.db.commit()
                            doc.reload()

                            print(f"✓ Successfully issued RFI!")
                            print(f"    Current State: {doc.workflow_state}")
                            print(f"    Clock was running: {clock_running}")
                            print(f"    Clock now stopped: {doc.statutory_clock_stopped}")

                            # Get RFI state transitions
                            rfi_transitions = get_transitions(doc)
                            print(f"\n✓ Available actions in RFI Issued ({len(rfi_transitions)}):")
                            for trans in rfi_transitions:
                                print(f"    - {trans.get('action')}")

                except Exception as e:
                    print(f"✗ Error applying workflow: {str(e)}")
                    frappe.db.rollback()
                    import traceback
                    traceback.print_exc()

            else:
                print(f"  'Acknowledge' action not available")

        else:
            print(f"  No transitions available (request may be in terminal state)")

    except Exception as e:
        print(f"✗ Error getting transitions: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

    return True


if __name__ == "__main__":
    test()
