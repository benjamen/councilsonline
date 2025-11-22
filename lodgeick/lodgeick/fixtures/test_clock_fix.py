#!/usr/bin/env python3
"""
Test the statutory clock fix with db_set
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.test_clock_fix.test
"""

import frappe


def test():
    """Test statutory clock with db_set fix"""

    print("\n" + "="*80)
    print("TESTING STATUTORY CLOCK FIX (db_set)")
    print("="*80 + "\n")

    # Get RC-2025-001 (draft state)
    request_name = "RC-2025-001"

    if not frappe.db.exists("Request", request_name):
        print(f"✗ Request {request_name} not found!")
        return

    doc = frappe.get_doc("Request", request_name)

    print(f"Testing with: {doc.name}")
    print(f"  Current State: {doc.workflow_state or 'Draft'}")
    print(f"  Docstatus: {doc.docstatus}")

    # Submit if needed
    if doc.docstatus == 0:
        print(f"\nSubmitting request...")
        doc.submit()
        frappe.db.commit()
        doc.reload()
        print(f"✓ Submitted. State: {doc.workflow_state}")

    # Acknowledge (should start clock)
    print(f"\n1. ACKNOWLEDGE - Testing Clock Start")
    print("-"*80)

    from frappe.model.workflow import apply_workflow

    try:
        # Get initial state
        initial_clock = doc.statutory_clock_started
        initial_ack = doc.acknowledged_date

        print(f"Before: Clock={initial_clock}, AckDate={initial_ack}")

        # Apply workflow
        apply_workflow(doc, "Acknowledge")
        frappe.db.commit()

        # Reload to get fresh data from database
        doc.reload()

        print(f"After:  Clock={doc.statutory_clock_started}, AckDate={doc.acknowledged_date}")
        print(f"        Target={doc.target_completion_date}")
        print(f"        Assessment={doc.assessment_project}")

        # Verify
        if doc.statutory_clock_started:
            print(f"\n✓✓ SUCCESS! Statutory clock started: {doc.statutory_clock_started}")
        else:
            print(f"\n✗ FAILED! Clock did not start")
            return False

        if doc.acknowledged_date:
            print(f"✓✓ SUCCESS! Acknowledged date set: {doc.acknowledged_date}")
        else:
            print(f"\n✗ FAILED! Acknowledged date not set")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()
        return False

    # Start Processing
    print(f"\n2. START PROCESSING")
    print("-"*80)

    try:
        apply_workflow(doc, "Start Processing")
        frappe.db.commit()
        doc.reload()

        print(f"✓ State: {doc.workflow_state}")
        print(f"  Clock still running: {doc.statutory_clock_started}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()

    # Issue RFI (should stop clock)
    print(f"\n3. ISSUE RFI - Testing Clock Stop")
    print("-"*80)

    try:
        clock_before = doc.statutory_clock_stopped
        print(f"Before: ClockStopped={clock_before}")

        apply_workflow(doc, "Issue RFI")
        frappe.db.commit()
        doc.reload()

        print(f"After:  ClockStopped={doc.statutory_clock_stopped}")

        if doc.statutory_clock_stopped:
            print(f"\n✓✓ SUCCESS! Clock stopped: {doc.statutory_clock_stopped}")
        else:
            print(f"\n✗ FAILED! Clock did not stop")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()
        return False

    # Mark RFI Received
    print(f"\n4. MARK RFI RECEIVED")
    print("-"*80)

    try:
        apply_workflow(doc, "Mark RFI Received")
        frappe.db.commit()
        doc.reload()
        print(f"✓ State: {doc.workflow_state}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()

    # Resume Processing (should restart clock - clear stop time)
    print(f"\n5. RESUME PROCESSING - Testing Clock Restart")
    print("-"*80)

    try:
        clock_stop_before = doc.statutory_clock_stopped
        print(f"Before: ClockStopped={clock_stop_before}")

        apply_workflow(doc, "Resume Processing")
        frappe.db.commit()
        doc.reload()

        print(f"After:  ClockStopped={doc.statutory_clock_stopped}")
        print(f"        ClockStarted={doc.statutory_clock_started}")

        if not doc.statutory_clock_stopped:
            print(f"\n✓✓ SUCCESS! Clock restarted (stop time cleared)")
        else:
            print(f"\n✗ FAILED! Clock still stopped")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()
        return False

    print("\n" + "="*80)
    print("ALL TESTS PASSED!")
    print("="*80)
    print(f"\nFinal State:")
    print(f"  Workflow State: {doc.workflow_state}")
    print(f"  Clock Started: {doc.statutory_clock_started}")
    print(f"  Clock Stopped: {doc.statutory_clock_stopped or 'No (running)'}")
    print(f"  Acknowledged: {doc.acknowledged_date}")
    print(f"  Target Completion: {doc.target_completion_date}")
    print(f"  Assessment Project: {doc.assessment_project}")

    print("\n✓✓✓ STATUTORY CLOCK INTEGRATION FULLY WORKING!")

    return True


if __name__ == "__main__":
    test()
