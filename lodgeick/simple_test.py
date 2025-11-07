#!/usr/bin/env python3
# Simple test function for costing

import frappe
from frappe.utils import today


def test_wb_task_costing():
	"""Create a simple WB Task and test costing"""
	print("\n=== Testing WB Task Costing ===\n")

	# 1. Test get_hourly_rate API
	print("1. Testing Role Rate API...")
	from lodgeick.lodgeick.doctype.role_rate.role_rate import get_hourly_rate

	rate = get_hourly_rate("Planner", today())
	print(f"   Planner hourly rate: ${rate.get('hourly_rate', 0)}")

	# 2. Create a test WB Task
	print("\n2. Creating test WB Task...")
	from frappe.utils import add_days
	task = frappe.get_doc({
		"doctype": "WB Task",
		"title": "Test Costing - Document Review",
		"description": "Testing automatic cost calculation",
		"status": "Open",
		"priority": "Medium",
		"due_date": add_days(today(), 7),
		"assign_from": "Administrator",
		"assign_to": "Administrator",
		"assigned_role": "Planner",
		"estimated_hours": 2.0,
		"actual_hours": 2.5
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
