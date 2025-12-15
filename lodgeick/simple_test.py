#!/usr/bin/env python3
# Simple test function for costing

import frappe
from frappe.utils import today


def test_project_task_costing():
	"""Create a simple Project Task and test costing"""
	print("\n=== Testing Project Task Costing ===\n")

	# 1. Test get_hourly_rate API
	print("1. Testing Role Rate API...")
	from lodgeick.lodgeick.doctype.role_rate.role_rate import get_hourly_rate

	rate = get_hourly_rate("Planner", today())
	print(f"   Planner hourly rate: ${rate.get('hourly_rate', 0)}")

	# 2. Create a test Project Task
	print("\n2. Creating test Project Task...")
	from frappe.utils import add_days
	task = frappe.get_doc({
		"doctype": "Project Task",
		"title": "Test Costing - Document Review",
		"description": "Testing automatic cost calculation",
		"status": "Open",
		"priority": "Medium",
		"due_date": add_days(today(), 7),
		"assigned_by": "Administrator",
		"assigned_to": "Administrator",
		"assigned_role": "Planner",
		"actual_hours": 2.5,
		"task_type": "Manual"
	})
	task.insert()

	print(f"   Created task: {task.name}")
	print(f"   - Assigned Role: {task.assigned_role}")
	print(f"   - Hourly Rate: ${task.hourly_rate or 0}")
	print(f"   - Actual Hours: {task.actual_hours}")
	print(f"   - Total Cost: ${task.total_cost or 0}")

	# 3. Verify calculation
	expected_cost = 2.5 * 150.0  # 2.5 hours × $150/hr
	print(f"\n3. Verification:")
	print(f"   Expected: ${expected_cost}")
	print(f"   Actual: ${task.total_cost or 0}")

	if task.total_cost == expected_cost:
		print("   ✓ Cost calculation is CORRECT!")
	else:
		print(f"   ✗ Cost calculation is INCORRECT!")
		print(f"   Difference: ${abs((task.total_cost or 0) - expected_cost)}")

	frappe.db.commit()

	print(f"\n✓ Test completed. Task name: {task.name}\n")
	return task.name
