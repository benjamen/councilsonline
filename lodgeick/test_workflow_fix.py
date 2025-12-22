#!/usr/bin/env python3
"""
Test script to verify the acknowledge workflow fix
"""
import frappe
from frappe.model.workflow import apply_workflow, get_transitions

def test_acknowledge_workflow():
    """Test that staff can acknowledge submitted requests"""

    # Find any council with request types configured
    # Council Request Type is a child table - parent field is the council name
    # Join with Council to ensure the council actually exists
    councils_with_types = frappe.db.sql("""
        SELECT DISTINCT crt.parent as council, crt.request_type
        FROM `tabCouncil Request Type` crt
        INNER JOIN `tabCouncil` c ON c.name = crt.parent
        WHERE crt.is_enabled = 1
        LIMIT 1
    """, as_dict=1)

    if not councils_with_types:
        print("ERROR: No councils have request types configured in test data")
        return False

    council_name = councils_with_types[0].council
    request_type = councils_with_types[0].request_type

    print(f"Testing with council: {council_name}")
    print(f"Testing with request_type: {request_type}")

    # Get current user info
    current_user = frappe.session.user
    user_roles = frappe.get_roles(current_user)
    print(f"\nCurrent user: {current_user}")
    print(f"Has Lodgeick User role: {'Lodgeick User' in user_roles}")
    print(f"Has Lodgeick Admin role: {'Lodgeick Admin' in user_roles}")

    # Create a minimal test request with all required fields
    request = frappe.get_doc({
        "doctype": "Request",
        "council": council_name,
        "request_type": request_type,
        "title": "Test Acknowledge Workflow Fix",
        "description": "Verifying workflow state transition from Submitted to Acknowledged",
        "requester": frappe.session.user,  # Required field
        "brief_description": "Testing workflow acknowledge transition",  # Required field
        "applicant_name": "Test Applicant",
        "applicant_email": "test@example.com",
        "applicant_phone": "021234567",
        "property_address": "123 Test Street",
        "legal_description": "LOT 1 DP 12345",
    })

    print("\n=== Creating request ===")
    request.insert(ignore_permissions=True)
    print(f"✓ Request created: {request.name}")

    print("\n=== Submitting request ===")
    request.submit()
    print(f"✓ Request submitted")
    print(f"  Current workflow_state: {request.workflow_state}")

    # Check available transitions
    transitions = get_transitions(request)
    print(f"\n=== Available workflow actions ===")
    for t in transitions:
        print(f"  • {t.action} → {t.next_state} (self-approval: {t.allow_self_approval})")

    # Verify Acknowledge action is available
    acknowledge_transition = [t for t in transitions if t.action == 'Acknowledge']
    if not acknowledge_transition:
        print("\n✗ FAILED: Acknowledge action not available!")
        return False

    print(f"\n✓ Acknowledge action is available")
    print(f"  Self-approval enabled: {acknowledge_transition[0].allow_self_approval}")

    # Apply the Acknowledge action
    print(f"\n=== Applying Acknowledge action ===")
    try:
        apply_workflow(request, 'Acknowledge')
        request.reload()

        print(f"\n{'='*60}")
        print(f"✓✓✓ SUCCESS! ✓✓✓")
        print(f"{'='*60}")
        print(f"Request {request.name} workflow state: {request.workflow_state}")
        print(f"\nThe acknowledge workflow fix is WORKING!")
        print(f"Staff can now acknowledge submitted requests.")
        print(f"{'='*60}")

        return True

    except Exception as e:
        print(f"\n✗ FAILED to apply workflow action")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    frappe.init(site='lodgeick.localhost')
    frappe.connect()

    try:
        success = test_acknowledge_workflow()
        exit(0 if success else 1)
    finally:
        frappe.destroy()
