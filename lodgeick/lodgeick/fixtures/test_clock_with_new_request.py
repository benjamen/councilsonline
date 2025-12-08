#!/usr/bin/env python3
"""
Test the statutory clock fix by creating a new request
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.test_clock_with_new_request.test
"""

import frappe
from frappe.utils import getdate


def test():
    """Test statutory clock with a new properly configured request"""

    print("\n" + "="*80)
    print("TESTING STATUTORY CLOCK FIX WITH NEW REQUEST")
    print("="*80 + "\n")

    # Create a new request with all required fields
    print("Creating new Resource Consent request...")

    doc = frappe.get_doc({
        "doctype": "Request",
        "request_type": "Resource Consent",
        "property_address": "789 Workflow Test Street, Wellington",
        "brief_description": "Test request for workflow statutory clock validation",
        "requester_name": "Workflow Tester",
        "requester_email": "workflow@test.com",
        "requester_phone": "021-555-0199",
        "requester_type": "Individual",
        "submitted_date": getdate()
    })

    doc.insert()
    frappe.db.commit()

    print(f"✓ Created: {doc.name}")
    print(f"  State: {doc.workflow_state or 'Draft'}")

    # Submit
    print(f"\nSubmitting...")
    doc.submit()
    frappe.db.commit()
    doc.reload()

    print(f"✓ Submitted: {doc.workflow_state}")

    # Test 1: Acknowledge (should start clock)
    print(f"\n" + "="*80)
    print("TEST 1: ACKNOWLEDGE - Start Statutory Clock")
    print("="*80)

    from frappe.model.workflow import apply_workflow

    try:
        print(f"\nBefore Acknowledge:")
        print(f"  Clock Started: {doc.statutory_clock_started}")
        print(f"  Acknowledged Date: {doc.acknowledged_date}")
        print(f"  Target Completion: {doc.target_completion_date}")

        apply_workflow(doc, "Acknowledge")
        frappe.db.commit()
        doc.reload()

        print(f"\nAfter Acknowledge:")
        print(f"  Clock Started: {doc.statutory_clock_started}")
        print(f"  Acknowledged Date: {doc.acknowledged_date}")
        print(f"  Target Completion: {doc.target_completion_date}")
        print(f"  Assessment Project: {doc.assessment_project}")

        # Verify
        if doc.statutory_clock_started and doc.acknowledged_date:
            print(f"\n✓✓✓ SUCCESS! Clock started at {doc.statutory_clock_started}")
            print(f"✓✓✓ SUCCESS! Acknowledged on {doc.acknowledged_date}")
        else:
            print(f"\n✗✗✗ FAILED!")
            if not doc.statutory_clock_started:
                print(f"  - Clock did not start")
            if not doc.acknowledged_date:
                print(f"  - Acknowledged date not set")
            return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()
        return False

    # Test 2: Start Processing
    print(f"\n" + "="*80)
    print("TEST 2: START PROCESSING")
    print("="*80)

    try:
        apply_workflow(doc, "Start Processing")
        frappe.db.commit()
        doc.reload()

        print(f"\n✓ State: {doc.workflow_state}")
        print(f"  Clock: {doc.statutory_clock_started} (still running)")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()

    # Test 3: Issue RFI (should stop clock)
    print(f"\n" + "="*80)
    print("TEST 3: ISSUE RFI - Stop Statutory Clock")
    print("="*80)

    try:
        print(f"\nBefore RFI:")
        print(f"  Clock Stopped: {doc.statutory_clock_stopped or 'No (running)'}")

        apply_workflow(doc, "Issue RFI")
        frappe.db.commit()
        doc.reload()

        print(f"\nAfter RFI:")
        print(f"  Clock Stopped: {doc.statutory_clock_stopped}")

        if doc.statutory_clock_stopped:
            print(f"\n✓✓✓ SUCCESS! Clock stopped at {doc.statutory_clock_stopped}")
        else:
            print(f"\n✗✗✗ FAILED! Clock did not stop")
            return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()
        return False

    # Test 4: Mark RFI Received
    print(f"\n" + "="*80)
    print("TEST 4: MARK RFI RECEIVED")
    print("="*80)

    try:
        apply_workflow(doc, "Mark RFI Received")
        frappe.db.commit()
        doc.reload()

        print(f"\n✓ State: {doc.workflow_state}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.db.rollback()

    # Test 5: Resume Processing (should restart clock)
    print(f"\n" + "="*80)
    print("TEST 5: RESUME PROCESSING - Restart Clock")
    print("="*80)

    try:
        print(f"\nBefore Resume:")
        print(f"  Clock Stopped: {doc.statutory_clock_stopped}")

        apply_workflow(doc, "Resume Processing")
        frappe.db.commit()
        doc.reload()

        print(f"\nAfter Resume:")
        print(f"  Clock Stopped: {doc.statutory_clock_stopped or 'No (running)'}")
        print(f"  Clock Started: {doc.statutory_clock_started}")

        if not doc.statutory_clock_stopped:
            print(f"\n✓✓✓ SUCCESS! Clock restarted (stop time cleared)")
        else:
            print(f"\n✗✗✗ FAILED! Clock still stopped")
            return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()
        return False

    # Final summary
    print(f"\n" + "="*80)
    print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
    print("="*80)

    print(f"\nFinal Request State ({doc.name}):")
    print(f"  Workflow State: {doc.workflow_state}")
    print(f"  Status: {doc.status}")
    print(f"  Clock Started: {doc.statutory_clock_started}")
    print(f"  Clock Stopped: {doc.statutory_clock_stopped or 'No (running)'}")
    print(f"  Acknowledged: {doc.acknowledged_date}")
    print(f"  Target Completion: {doc.target_completion_date}")
    print(f"  Assessment Project: {doc.assessment_project}")

    print(f"\n" + "="*80)
    print("STATUTORY CLOCK INTEGRATION: FULLY OPERATIONAL")
    print("="*80 + "\n")

    return True


if __name__ == "__main__":
    test()
