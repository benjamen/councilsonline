# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now


class ProjectTask(Document):
	def validate(self):
		"""Validation before saving"""
		# Calculate costing
		self.calculate_costing()

		# Update timeliness
		self.update_timeliness()

		# Set completion date when status changes to Completed
		if self.status == "Completed" and not self.date_of_completion:
			self.date_of_completion = getdate()

	def calculate_costing(self):
		"""Calculate cost from hours × hourly rate"""
		# Auto-fetch hourly rate when assigned_role is set
		if self.assigned_role and not self.hourly_rate:
			from councilsonline.councilsonline.doctype.role_rate.role_rate import get_hourly_rate
			rates = get_hourly_rate(self.assigned_role, frappe.utils.today())
			if rates:
				self.hourly_rate = rates.get("hourly_rate", 0)

		# Calculate total cost = actual_hours × hourly_rate
		if self.actual_hours and self.hourly_rate:
			self.total_cost = self.actual_hours * self.hourly_rate
		else:
			self.total_cost = 0

	def update_timeliness(self):
		"""Update timeliness based on completion date vs due date"""
		if self.status == "Completed" and self.date_of_completion and self.due_date:
			if getdate(self.date_of_completion) <= getdate(self.due_date):
				self.timeliness = "On Time"
			else:
				self.timeliness = "Late"

	def on_update(self):
		"""Actions after document is updated"""
		# Rollup costing to Request when task is updated
		if self.request:
			try:
				request_doc = frappe.get_doc("Request", self.request)
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
		task = frappe.get_doc("Project Task", task_name)

		# Get hourly rate from Role Rate
		from councilsonline.councilsonline.doctype.role_rate.role_rate import get_hourly_rate
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
