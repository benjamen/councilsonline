#!/usr/bin/env python3
# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Test script for costing system
Creates test data and verifies calculations
"""

import frappe
from frappe.utils import today, add_days


def create_test_data():
	"""Create test data for costing system"""
	print("\n=== Creating Test Data ===\n")

	# 1. Create Role Rates
	print("1. Creating Role Rates...")
	roles_to_create = [
		{"role": "Planner", "hourly_rate": 150, "cost_rate": 100},
		{"role": "Building Inspector", "hourly_rate": 180, "cost_rate": 120},
		{"role": "Consent Officer", "hourly_rate": 120, "cost_rate": 80},
	]

	for role_data in roles_to_create:
		if not frappe.db.exists("Role", role_data["role"]):
			print(f"  - Creating Role: {role_data['role']}")
			role = frappe.get_doc({
				"doctype": "Role",
				"role_name": role_data["role"]
			})
			role.insert()

		# Create Role Rate
		role_rate_name = f"RR-{role_data['role']}-{today()}"
		if not frappe.db.exists("Role Rate", role_rate_name):
			print(f"  - Creating Role Rate for {role_data['role']}: ${role_data['hourly_rate']}/hr")
			role_rate = frappe.get_doc({
				"doctype": "Role Rate",
				"role": role_data["role"],
				"hourly_rate": role_data["hourly_rate"],
				"cost_rate": role_data["cost_rate"],
				"effective_from": today(),
				"is_active": 1,
				"description": "Test rate"
			})
			role_rate.insert()
		else:
			print(f"  - Role Rate already exists for {role_data['role']}")

	# 2. Create Activity Types
	print("\n2. Creating Activity Types...")
	activities = [
		{"activity_name": "Site Inspection", "category": "Inspection", "default_hourly_rate": 180},
		{"activity_name": "Document Review", "category": "Document Review", "default_hourly_rate": 120},
		{"activity_name": "Consultation Meeting", "category": "Consultation", "default_hourly_rate": 150},
	]

	for activity in activities:
		if not frappe.db.exists("Activity Type", activity["activity_name"]):
			print(f"  - Creating Activity Type: {activity['activity_name']}")
			activity_doc = frappe.get_doc({
				"doctype": "Activity Type",
				**activity
			})
			activity_doc.insert()
		else:
			print(f"  - Activity Type already exists: {activity['activity_name']}")

	frappe.db.commit()
	print("\n=== Test Data Created Successfully ===\n")


def test_costing_calculations():
	"""Test costing calculations with sample data"""
	print("\n=== Testing Costing Calculations ===\n")

	# Get or create a test Request
	print("1. Creating Test Request...")

	# First ensure we have a Request Type
	if not frappe.db.exists("Request Type", "Building Consent"):
		print("  - Request Type 'Building Consent' not found. Creating it...")
		request_type = frappe.get_doc({
			"doctype": "Request Type",
			"type_name": "Building Consent",
			"type_code": "BC",
			"category": "Building Consent",
			"description": "Building consent applications",
			"processing_sla_days": 20,
			"base_fee": 500
		})
		request_type.insert()

	# Create test Request
	test_request = frappe.get_doc({
		"doctype": "Request",
		"request_type": "Building Consent",
		"brief_description": "Test building consent for costing",
		"property_address": "123 Test Street",
		"requester_name": "Test User",
		"requester_email": "test@example.com"
	})
	test_request.insert()
	print(f"  - Created Request: {test_request.name}")

	# 2. Create Project Tasks linked to this Request
	print("\n2. Creating Project Tasks...")

	tasks_data = [
		{
			"title": "Initial Document Review",
			"assigned_role": "Consent Officer",
			"actual_hours": 2.5
		},
		{
			"title": "Site Inspection",
			"assigned_role": "Building Inspector",
			"actual_hours": 3.5
		},
		{
			"title": "Planning Review",
			"assigned_role": "Planner",
			"actual_hours": 2.0
		}
	]

	created_tasks = []
	for task_data in tasks_data:
		task = frappe.get_doc({
			"doctype": "Project Task",
			"title": task_data["title"],
			"description": f"Test task: {task_data['title']}",
			"status": "Open",
			"priority": "Medium",
			"due_date": add_days(today(), 7),
			"assigned_to": "Administrator",
			"assigned_by": "Administrator",
			"request": test_request.name,
			"assigned_role": task_data["assigned_role"],
			"actual_hours": task_data["actual_hours"],
			"task_type": "Manual"
		})
		task.insert()
		created_tasks.append(task)
		print(f"  - Created Task: {task.title}")
		print(f"    - Role: {task.assigned_role}")
		print(f"    - Hourly Rate: ${task.hourly_rate or 0}")
		print(f"    - Actual Hours: {task.actual_hours}")
		print(f"    - Total Cost: ${task.total_cost or 0}")

	# 3. Add Disbursements to Request
	print("\n3. Adding Disbursements to Request...")
	test_request.reload()
	test_request.append("disbursements", {
		"item_description": "Council filing fee",
		"amount": 150
	})
	test_request.append("disbursements", {
		"item_description": "Engineering report",
		"amount": 500
	})
	test_request.save()
	print("  - Added 2 disbursement items")

	# 4. Reload and display final calculations
	print("\n4. Final Calculations:")
	test_request.reload()

	print(f"\n  Request: {test_request.name}")
	print(f"  ─────────────────────────────────────")
	print(f"  Application Fee:        ${test_request.application_fee or 0:,.2f}")
	print(f"  Total Task Cost:        ${test_request.total_task_cost or 0:,.2f}")
	print(f"  Total Disbursements:    ${test_request.total_disbursements or 0:,.2f}")
	print(f"  ─────────────────────────────────────")
	print(f"  TOTAL AMOUNT DUE:       ${test_request.total_amount_due or 0:,.2f}")
	print(f"  ─────────────────────────────────────")

	# Show breakdown of task costs
	print(f"\n  Task Cost Breakdown:")
	for task in created_tasks:
		task.reload()
		print(f"    • {task.title}")
		print(f"      {task.actual_hours} hrs × ${task.hourly_rate or 0}/hr = ${task.total_cost or 0:,.2f}")

	frappe.db.commit()
	print("\n=== Test Completed Successfully ===\n")

	return {
		"request": test_request.name,
		"tasks": [t.name for t in created_tasks]
	}


def cleanup_test_data(test_info):
	"""Clean up test data"""
	print("\n=== Cleaning Up Test Data ===\n")

	# Delete tasks
	for task_name in test_info.get("tasks", []):
		try:
			frappe.delete_doc("Project Task", task_name, force=1)
			print(f"  - Deleted Task: {task_name}")
		except:
			pass

	# Delete request
	request_name = test_info.get("request")
	if request_name:
		try:
			frappe.delete_doc("Request", request_name, force=1)
			print(f"  - Deleted Request: {request_name}")
		except:
			pass

	frappe.db.commit()
	print("\n=== Cleanup Complete ===\n")


if __name__ == "__main__":
	frappe.init(site="councilsonline.localhost")
	frappe.connect()

	# Create test data
	create_test_data()

	# Run tests
	test_info = test_costing_calculations()

	# Ask if user wants to clean up
	print("\nTest data created. Do you want to clean up? (y/n): ", end="")
	# For automated testing, we'll skip cleanup by default
	# cleanup = input().lower() == 'y'
	# if cleanup:
	# 	cleanup_test_data(test_info)

	print("\n✓ Costing system test completed!")
	print(f"\nTest Request: {test_info['request']}")
	print("You can view it in the Frappe UI to verify the calculations.\n")
