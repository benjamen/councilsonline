# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TaskTemplate(Document):
	"""
	Task Template defines reusable task definitions for assessment stages.

	When an Assessment Project is created, tasks are auto-generated from templates
	based on the stage types in the assessment template.
	"""

	def validate(self):
		"""Validate task template fields"""

		# Ensure task sequence is positive
		if self.task_sequence < 1:
			frappe.throw("Task sequence must be at least 1")

		# Ensure estimated hours is reasonable
		if self.estimated_hours <= 0:
			frappe.throw("Estimated hours must be greater than 0")

		# Check for circular dependencies
		if self.depends_on_task:
			self.check_circular_dependency()

	def check_circular_dependency(self):
		"""Check for circular task dependencies"""

		visited = set()
		current = self.depends_on_task

		while current:
			if current == self.name:
				frappe.throw(f"Circular dependency detected: {self.name} depends on itself")

			if current in visited:
				frappe.throw(f"Circular dependency detected in task chain")

			visited.add(current)

			# Get next dependency
			next_dep = frappe.db.get_value("Task Template", current, "depends_on_task")
			current = next_dep


@frappe.whitelist()
def get_tasks_for_stage_type(stage_type):
	"""
	Get all active task templates for a given stage type

	Args:
		stage_type (str): Assessment Stage Type name

	Returns:
		list: List of task template dicts with all fields
	"""

	tasks = frappe.get_all(
		"Task Template",
		filters={
			"stage_type": stage_type,
			"is_active": 1
		},
		fields=[
			"name",
			"task_template_name",
			"task_sequence",
			"task_title",
			"task_description",
			"estimated_hours",
			"required_role",
			"required_team",
			"is_mandatory",
			"task_type",
			"priority",
			"depends_on_task",
			"checklist_template",
			"auto_assign"
		],
		order_by="task_sequence asc"
	)

	return tasks


@frappe.whitelist()
def get_task_templates_by_request_type(request_type):
	"""
	Get all task templates for a request type via its assessment template

	Args:
		request_type (str): Request Type name

	Returns:
		dict: Tasks grouped by stage type
	"""

	# Get default assessment template for request type
	template_name = frappe.db.get_value(
		"Request Type",
		request_type,
		"default_assessment_template"
	)

	if not template_name:
		return {}

	# Get assessment template with stages
	template = frappe.get_doc("Assessment Template", template_name)

	tasks_by_stage = {}

	for stage in template.stages:
		stage_tasks = get_tasks_for_stage_type(stage.stage_type)
		tasks_by_stage[stage.stage_name] = stage_tasks

	return tasks_by_stage
