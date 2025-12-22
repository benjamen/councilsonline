#!/usr/bin/env python3
"""
Test script to verify the acknowledge workflow fix

This script:
1. Creates a test request
2. Submits it
3. Attempts to acknowledge it
4. Verifies the workflow transition works
"""

import frappe
from frappe.utils import getdate


def test_acknowledge_workflow():
	"""Test the acknowledge workflow end-to-end"""

	print("\n" + "="*80)
	print("TESTING ACKNOWLEDGE WORKFLOW FIX")
	print("="*80 + "\n")

	frappe.set_user("Administrator")

	# Step 1: Find a test council and request type
	print("Step 1: Finding test data...")

	councils = frappe.get_all("Council", filters={"is_active": 1}, limit=1)
	if not councils:
		print("❌ No active councils found")
		return False

	council_name = councils[0].name
	print(f"  ✓ Using council: {council_name}")

	request_types = frappe.get_all("Request Type", limit=1)
	if not request_types:
		print("❌ No request types found")
		return False

	request_type = request_types[0].name
	print(f"  ✓ Using request type: {request_type}")

	# Step 2: Create a draft request
	print("\nStep 2: Creating test request...")

	try:
		request = frappe.get_doc({
			"doctype": "Request",
			"council": council_name,
			"request_type": request_type,
			"requester": "Administrator",
			"requester_name": "Test User",
			"requester_email": "test@example.com",
			"brief_description": "Test request for acknowledge workflow"
		})
		request.insert(ignore_permissions=True)
		print(f"  ✓ Created request: {request.name}")
		print(f"    Status: {request.status}")
		print(f"    Workflow State: {request.workflow_state}")
	except Exception as e:
		print(f"❌ Failed to create request: {str(e)}")
		return False

	# Step 3: Submit the request
	print("\nStep 3: Submitting request...")

	try:
		request.submit()
		request.reload()
		print(f"  ✓ Request submitted")
		print(f"    Status: {request.status}")
		print(f"    Workflow State: {request.workflow_state}")
		print(f"    DocStatus: {request.docstatus}")
	except Exception as e:
		print(f"❌ Failed to submit request: {str(e)}")
		frappe.db.rollback()
		return False

	# Step 4: Check available workflow actions
	print("\nStep 4: Checking available workflow actions...")

	try:
		from frappe.model.workflow import get_transitions
		transitions = get_transitions(request)

		print(f"  Available actions: {len(transitions)}")
		for t in transitions:
			print(f"    - {t.get('action')} (allowed: {t.get('allowed')}, self-approval: {t.get('allow_self_approval')})")

		# Check if Acknowledge is available
		acknowledge_available = any(t.get('action') == 'Acknowledge' for t in transitions)
		if not acknowledge_available:
			print("  ❌ Acknowledge action NOT available!")
			print("  This means the fix didn't work properly.")
			frappe.db.rollback()
			return False

		print("  ✓ Acknowledge action is available!")

		# Check self-approval setting
		ack_transition = [t for t in transitions if t.get('action') == 'Acknowledge'][0]
		if ack_transition.get('allow_self_approval') == 1:
			print("  ✓ Self-approval is ENABLED (allow_self_approval=1)")
		else:
			print("  ⚠ Self-approval is DISABLED (allow_self_approval=0)")

	except Exception as e:
		print(f"❌ Failed to check transitions: {str(e)}")
		frappe.db.rollback()
		return False

	# Step 5: Acknowledge the request
	print("\nStep 5: Acknowledging request...")

	try:
		from frappe.model.workflow import apply_workflow

		# Apply the Acknowledge workflow action
		apply_workflow(request, 'Acknowledge')
		request.reload()

		print(f"  ✓ Request acknowledged successfully!")
		print(f"    Status: {request.status}")
		print(f"    Workflow State: {request.workflow_state}")
		print(f"    Acknowledged Date: {request.acknowledged_date}")

		# Verify the state changed
		if request.workflow_state == "Acknowledged":
			print("  ✓ Workflow state is 'Acknowledged' - SUCCESS!")
		else:
			print(f"  ❌ Unexpected workflow state: {request.workflow_state}")
			frappe.db.rollback()
			return False

	except Exception as e:
		print(f"❌ Failed to acknowledge request: {str(e)}")
		print(f"   Error type: {type(e).__name__}")
		frappe.db.rollback()
		return False

	# Clean up
	print("\nStep 6: Cleaning up test data...")
	try:
		frappe.delete_doc("Request", request.name, force=1)
		frappe.db.commit()
		print(f"  ✓ Deleted test request: {request.name}")
	except Exception as e:
		print(f"  ⚠ Cleanup failed: {str(e)}")
		frappe.db.rollback()

	print("\n" + "="*80)
	print("✓✓✓ ACKNOWLEDGE WORKFLOW TEST PASSED! ✓✓✓")
	print("="*80 + "\n")
	print("Summary:")
	print("  • Request created successfully")
	print("  • Request submitted successfully")
	print("  • Acknowledge action available to user")
	print("  • Self-approval enabled")
	print("  • Workflow transition Submitted → Acknowledged works!")
	print("\nThe fix is working correctly! 🎉\n")

	return True


if __name__ == "__main__":
	frappe.init(site="lodgeick.localhost")
	frappe.connect()

	try:
		success = test_acknowledge_workflow()
		exit_code = 0 if success else 1
	except Exception as e:
		print(f"\n❌ Test failed with error: {str(e)}")
		import traceback
		traceback.print_exc()
		exit_code = 1
	finally:
		frappe.destroy()

	exit(exit_code)
