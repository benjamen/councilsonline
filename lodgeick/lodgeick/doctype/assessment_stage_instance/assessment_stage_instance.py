# Copyright (c) 2025, Essdee and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class AssessmentStageInstance(Document):
	def validate(self):
		"""Validate stage instance"""
		self.update_dates_based_on_status()

	def update_dates_based_on_status(self):
		"""Auto-update started/completed dates based on status changes"""
		# If status changed to In Progress and no started date, set it
		if self.stage_status == "In Progress" and not self.started_date:
			self.started_date = now_datetime()

		# If status changed to Completed and no completed date, set it
		if self.stage_status == "Completed" and not self.completed_date:
			self.completed_date = now_datetime()

		# If status changed away from Completed, clear completed date
		if self.stage_status != "Completed" and self.completed_date:
			self.completed_date = None

	def create_primary_task(self, project_name, board=None):
		"""Create a Project Task for this stage"""
		if self.primary_task:
			frappe.throw("Primary task already exists for this stage")

		# Get parent assessment project
		assessment_project = frappe.get_doc("Assessment Project", project_name)
		from frappe.utils import today, add_days

		# Create Project Task
		task = frappe.get_doc({
			"doctype": "Project Task",
			"title": f"{self.stage_name} - {assessment_project.request}",
			"description": self.notes or f"Assessment stage: {self.stage_name}",
			"status": "Open",
			"priority": "Medium",
			"due_date": add_days(today(), 14),
			"assigned_to": self.assigned_to or "Administrator",
			"assigned_by": "Administrator",
			"assessment_project": project_name,
			"assessment_stage": self.stage_name,
			"task_type": "Auto"
		})

		task.insert()

		# Link task back to stage
		self.primary_task = task.name

		frappe.msgprint(f"Created task {task.name} for stage {self.stage_name}")

		return task
