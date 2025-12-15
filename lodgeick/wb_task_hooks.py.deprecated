# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
WB Task hooks for Lodgeick costing system
These functions are called via Server Scripts or hooks
"""

import frappe
from frappe import _


def wb_task_validate(doc, method):
	"""Hook for WB Task validation - calculate costing"""
	# Auto-fetch hourly rate when assigned_role is set
	if doc.get("assigned_role") and not doc.get("hourly_rate"):
		# Get hourly rate from Role Rate
		from lodgeick.lodgeick.doctype.role_rate.role_rate import get_hourly_rate
		rates = get_hourly_rate(doc.assigned_role, frappe.utils.today())
		if rates:
			doc.hourly_rate = rates.get("hourly_rate", 0)

	# Calculate total cost = actual_hours × hourly_rate
	if doc.get("actual_hours") and doc.get("hourly_rate"):
		doc.total_cost = doc.actual_hours * doc.hourly_rate
	else:
		doc.total_cost = 0


def wb_task_on_update(doc, method):
	"""Hook for WB Task on_update - update linked Request totals"""
	# If this task is linked to a Request, trigger recalculation
	if doc.get("request"):
		try:
			request_doc = frappe.get_doc("Request", doc.request)
			request_doc.calculate_costing()
			request_doc.save(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error updating Request costing: {str(e)}")


@frappe.whitelist()
def update_hourly_rate(task_name, assigned_role):
	"""API to manually update hourly rate for a task"""
	if not task_name or not assigned_role:
		return {"success": False, "message": "Task name and role required"}

	try:
		task = frappe.get_doc("WB Task", task_name)

		# Get hourly rate from Role Rate
		from lodgeick.lodgeick.doctype.role_rate.role_rate import get_hourly_rate
		rates = get_hourly_rate(assigned_role, frappe.utils.today())

		if rates:
			task.hourly_rate = rates.get("hourly_rate", 0)
			task.save(ignore_permissions=True)
			return {
				"success": True,
				"hourly_rate": task.hourly_rate,
				"message": "Hourly rate updated successfully"
			}
		else:
			return {
				"success": False,
				"message": f"No active rate found for role: {assigned_role}"
			}
	except Exception as e:
		frappe.log_error(f"Error updating hourly rate: {str(e)}")
		return {"success": False, "message": str(e)}
