# Copyright (c) 2025, Essdee and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime, add_days, getdate
from lodgeick.lodgeick.doctype.request.request import calculate_working_days_between


class AssessmentProject(Document):
	def validate(self):
		"""Validate assessment project data"""
		self.validate_unique_request()
		self.calculate_clock_metrics()
		self.update_current_stage()

	def validate_unique_request(self):
		"""Ensure only one assessment project per request"""
		if self.request:
			existing = frappe.db.exists(
				"Assessment Project",
				{"request": self.request, "name": ["!=", self.name]}
			)
			if existing:
				frappe.throw(f"Assessment Project already exists for Request {self.request}")

	def calculate_clock_metrics(self):
		"""Calculate statutory clock metrics with exclusions"""
		if not self.started_date or not self.statutory_clock_days:
			return

		# Calculate total days excluded from clock suspensions
		total_excluded = 0
		for exclusion in self.clock_exclusions:
			if exclusion.working_days_excluded:
				total_excluded += exclusion.working_days_excluded

		self.total_days_excluded = total_excluded

		# Calculate working days elapsed (excluding suspensions)
		try:
			start_dt = get_datetime(self.started_date)
			now_dt = now_datetime()

			# Calculate gross working days between start and now
			gross_days = calculate_working_days_between(start_dt, now_dt)

			# Net working days = gross days - excluded days
			self.working_days_elapsed = max(0, gross_days - total_excluded)

			# Working days remaining
			self.working_days_remaining = max(
				0,
				self.statutory_clock_days - self.working_days_elapsed
			)

			# Calculate statutory deadline
			# Start with clock days + excluded days to get gross days needed
			gross_days_needed = self.statutory_clock_days + total_excluded

			# Add gross days to start date to get deadline
			self.statutory_deadline = add_days(
				getdate(self.started_date),
				gross_days_needed
			)

		except Exception as e:
			frappe.log_error(f"Error calculating clock metrics: {str(e)}")

	def update_current_stage(self):
		"""Update current stage based on stage statuses"""
		if not self.stages:
			self.current_stage = None
			return

		# Find first stage that is not completed
		for stage in self.stages:
			if stage.stage_status != "Completed":
				self.current_stage = stage.stage_name
				return

		# All stages completed
		self.current_stage = "All Stages Complete"

	def rollup_time_and_cost(self):
		"""Rollup actual hours and cost from linked WB Tasks"""
		# Get all WB Tasks linked to this assessment project
		tasks = frappe.get_all(
			"WB Task",
			filters={"assessment_project": self.name},
			fields=["name", "actual_time", "total_costing_amount"]
		)

		total_hours = 0
		total_cost = 0

		for task in tasks:
			if task.actual_time:
				total_hours += task.actual_time
			if task.total_costing_amount:
				total_cost += task.total_costing_amount

		self.actual_hours = total_hours
		self.actual_cost = total_cost

	def create_stages_from_template(self):
		"""Create stage instances from assessment template"""
		if not self.assessment_template:
			frappe.throw("Assessment Template is required to create stages")

		template = frappe.get_doc("Assessment Template", self.assessment_template)

		# Clear existing stages
		self.stages = []

		# Create stage instances from template
		for template_stage in template.stages:
			stage_instance = self.append("stages", {})
			stage_instance.stage_number = template_stage.stage_number
			stage_instance.stage_name = template_stage.stage_name
			stage_instance.stage_type = template_stage.stage_type
			stage_instance.required = template_stage.required
			stage_instance.estimated_hours = template_stage.estimated_hours or 0
			stage_instance.checklist_template = template_stage.checklist_template
			stage_instance.stage_status = "Not Started"

		# Set budgeted hours from template
		if template.default_budget_hours:
			self.budgeted_hours = template.default_budget_hours

		frappe.msgprint(f"Created {len(self.stages)} stages from template {template.template_name}")

	def add_clock_exclusion(self, exclusion_type, reference_doctype=None, reference_name=None):
		"""Add a clock exclusion period (e.g., RFI, S37)"""
		exclusion = self.append("clock_exclusions", {})
		exclusion.exclusion_type = exclusion_type
		exclusion.started_date = now_datetime()

		if reference_doctype and reference_name:
			exclusion.reference_doctype = reference_doctype
			exclusion.reference_document = reference_name

		self.save()
		frappe.msgprint(f"Clock exclusion {exclusion_type} started")

		return exclusion

	def end_clock_exclusion(self, exclusion_name):
		"""End a clock exclusion period"""
		for exclusion in self.clock_exclusions:
			if exclusion.name == exclusion_name:
				exclusion.ended_date = now_datetime()
				self.save()
				frappe.msgprint(f"Clock exclusion ended. {exclusion.working_days_excluded} working days excluded.")
				return

		frappe.throw(f"Clock exclusion {exclusion_name} not found")


@frappe.whitelist()
def create_from_template(assessment_project_name):
	"""API method to create stages from template"""
	doc = frappe.get_doc("Assessment Project", assessment_project_name)
	doc.create_stages_from_template()
	doc.save()
	return doc


@frappe.whitelist()
def start_clock_exclusion(assessment_project_name, exclusion_type, reference_doctype=None, reference_name=None):
	"""API method to start a clock exclusion"""
	doc = frappe.get_doc("Assessment Project", assessment_project_name)
	return doc.add_clock_exclusion(exclusion_type, reference_doctype, reference_name)


@frappe.whitelist()
def end_clock_exclusion(assessment_project_name, exclusion_name):
	"""API method to end a clock exclusion"""
	doc = frappe.get_doc("Assessment Project", assessment_project_name)
	doc.end_clock_exclusion(exclusion_name)
	return doc
