#!/usr/bin/env python3
"""
Final test of statutory clock with workflow
Run with: bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.test_statutory_clock_final.test
"""

import frappe


def test():
    """Test statutory clock integration with workflow"""

    print("\n" + "="*80)
    print("FINAL TEST: STATUTORY CLOCK + WORKFLOW INTEGRATION")
    print("="*80 + "\n")

    # Get RC-2025-005 (submitted but not yet acknowledged)
    request_name = "RC-2025-005"

    if not frappe.db.exists("Request", request_name):
        print(f"✗ Request {request_name} not found!")
        return

    doc = frappe.get_doc("Request", request_name)

    print(f"Testing with: {doc.name}")
    print(f"  Current State: {doc.workflow_state}")
    print(f"  Statutory Clock: {doc.statutory_clock_started or 'Not started'}")
    print(f"  Clock Stopped: {doc.statutory_clock_stopped or 'Running'}")

    # Acknowledge the request (should start clock)
    print(f"\n1. ACKNOWLEDGE (should start clock)")
    print("-"*80)

    from frappe.model.workflow import apply_workflow

    try:
        apply_workflow(doc, "Acknowledge")
        frappe.db.commit()
        doc.reload()

        print(f"✓ State changed to: {doc.workflow_state}")
        print(f"  Statutory Clock Started: {doc.statutory_clock_started}")
        print(f"  Acknowledged Date: {doc.acknowledged_date}")
        print(f"  Target Completion: {doc.target_completion_date}")
        print(f"  Assessment Project: {doc.assessment_project}")

        if doc.statutory_clock_started:
            print(f"\n✓✓ STATUTORY CLOCK STARTED SUCCESSFULLY!")
        else:
            print(f"\n✗ FAILED: Clock did not start")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()
        return

    # Start Processing
    print(f"\n2. START PROCESSING (clock should keep running)")
    print("-"*80)

    try:
        apply_workflow(doc, "Start Processing")
        frappe.db.commit()
        doc.reload()

        print(f"✓ State changed to: {doc.workflow_state}")
        print(f"  Clock Still Running: {not doc.statutory_clock_stopped}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()

    # Issue RFI (should stop clock)
    print(f"\n3. ISSUE RFI (should STOP clock)")
    print("-"*80)

    try:
        apply_workflow(doc, "Issue RFI")
        frappe.db.commit()
        doc.reload()

        print(f"✓ State changed to: {doc.workflow_state}")
        print(f"  Clock Stopped: {doc.statutory_clock_stopped}")

        if doc.statutory_clock_stopped:
            print(f"\n✓✓ STATUTORY CLOCK STOPPED SUCCESSFULLY!")
        else:
            print(f"\n✗ FAILED: Clock did not stop")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()

    # Mark RFI Received
    print(f"\n4. MARK RFI RECEIVED")
    print("-"*80)

    try:
        apply_workflow(doc, "Mark RFI Received")
        frappe.db.commit()
        doc.reload()

        print(f"✓ State changed to: {doc.workflow_state}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()

    # Resume Processing (should restart clock - clear stop time)
    print(f"\n5. RESUME PROCESSING (should RESTART clock)")
    print("-"*80)

    try:
        apply_workflow(doc, "Resume Processing")
        frappe.db.commit()
        doc.reload()

        print(f"✓ State changed to: {doc.workflow_state}")
        print(f"  Clock Started: {doc.statutory_clock_started}")
        print(f"  Clock Stopped: {doc.statutory_clock_stopped or 'No (running)'}")

        if not doc.statutory_clock_stopped:
            print(f"\n✓✓ STATUTORY CLOCK RESTARTED SUCCESSFULLY!")
        else:
            print(f"\n✗ FAILED: Clock is still stopped")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

    return True


if __name__ == "__main__":
    test()
