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

	def create_tasks_from_template(self):
		"""
		Auto-create WB Tasks from Task Templates for all stages
		This creates a complete project plan with all tasks assigned
		"""
		if not self.stages:
			frappe.throw("No stages found. Create stages from template first.")

		total_tasks_created = 0

		for stage_instance in self.stages:
			# Get all task templates for this stage type
			from lodgeick.lodgeick.doctype.task_template.task_template import get_tasks_for_stage_type

			task_templates = get_tasks_for_stage_type(stage_instance.stage_type)

			if not task_templates:
				frappe.msgprint(
					f"No task templates found for stage type: {stage_instance.stage_type}",
					indicator="orange"
				)
				continue

			created_tasks_in_stage = []

			for template_data in task_templates:
				# Get full template document
				template = frappe.get_doc("Task Template", template_data.name)

				# Calculate due date based on stage timeline and task sequence
				task_due_date = self.calculate_task_due_date(
					stage_instance,
					template.estimated_hours,
					created_tasks_in_stage
				)

				# Determine assignee based on team/role
				assignee = self.get_assignee_for_task(
					template.required_role,
					template.required_team
				)

				# Render task description with context
				task_description = self.render_task_description(template, stage_instance)

				# Create WB Task
				task = frappe.get_doc({
					"doctype": "WB Task",
					"title": template.task_title,
					"description": task_description,
					"assessment_project": self.name,
					"assessment_stage": stage_instance.stage_name,
					"request": self.request,
					"assign_from": self.project_owner or frappe.session.user,
					"assign_to": assignee,
					"assigned_role": template.required_role,
					"estimated_hours": template.estimated_hours,
					"priority": template.priority,
					"due_date": task_due_date,
					"checklist_template": template.checklist_template,
					"task_type": "Auto",  # Mark as auto-generated
					"status": "Open"
				})

				task.insert(ignore_permissions=True)

				created_tasks_in_stage.append({
					"task": task.name,
					"template": template.name,
					"estimated_hours": template.estimated_hours,
					"task_type": template.task_type
				})

				total_tasks_created += 1

				# Link first task as primary task for stage
				if template.task_sequence == 1:
					stage_instance.db_set("primary_task", task.name, update_modified=False)

			# Update stage estimated hours from sum of task hours
			if created_tasks_in_stage:
				total_stage_hours = sum(t["estimated_hours"] for t in created_tasks_in_stage)
				stage_instance.db_set("estimated_hours", total_stage_hours, update_modified=False)

		frappe.db.commit()

		frappe.msgprint(
			f"✅ Created {total_tasks_created} tasks across {len(self.stages)} stages",
			indicator="green",
			title="Tasks Created"
		)

		return total_tasks_created

	def calculate_task_due_date(self, stage_instance, task_hours, previous_tasks):
		"""
		Calculate task due date based on assessment timeline and task dependencies

		Args:
			stage_instance: Assessment Stage Instance
			task_hours: Estimated hours for this task
			previous_tasks: List of tasks already created in this stage

		Returns:
			date: Calculated due date
		"""
		# Start from assessment project start date
		from frappe.utils import add_to_date

		start_date = get_datetime(self.started_date) if self.started_date else now_datetime()

		# Add hours from all previous sequential tasks
		# (Parallel tasks don't affect timeline)
		total_previous_hours = 0
		for task_data in previous_tasks:
			if task_data.get("task_type") == "Sequential":
				total_previous_hours += task_data["estimated_hours"]

		# Convert hours to working days (assume 8-hour workday)
		working_days_offset = int((total_previous_hours + task_hours) / 8)

		# Add working days to start date
		from lodgeick.lodgeick.doctype.request.request import add_working_days
		due_date = add_working_days(start_date, working_days_offset)

		return due_date

	def get_assignee_for_task(self, required_role, required_team):
		"""
		Get user to assign task to based on role and team

		Priority:
		1) Team member with required role
		2) Any user with required role
		3) Project owner (fallback)

		Args:
			required_role: Role required for the task
			required_team: Preferred team (optional)

		Returns:
			str: User email to assign to
		"""
		# Option 1: Find user with required role in required team
		if required_team:
			team_members = self.get_team_members(required_team)
			for member in team_members:
				user_roles = frappe.get_roles(member)
				if required_role in user_roles:
					return member

		# Option 2: Find any user with required role (prefer active users)
		users_with_role = frappe.get_all(
			"Has Role",
			filters={
				"role": required_role,
				"parenttype": "User"
			},
			fields=["parent"],
			limit=1
		)

		if users_with_role:
			user = users_with_role[0].parent
			# Check if user is enabled
			if frappe.db.get_value("User", user, "enabled"):
				return user

		# Option 3: Fallback to project owner
		return self.project_owner or frappe.session.user

	def get_team_members(self, team_name):
		"""
		Get list of users in a team

		TODO: Integrate with Team DocType or User Groups once implemented

		Args:
			team_name: Team name

		Returns:
			list: List of user emails in the team
		"""
		# For now, return empty list
		# In future, integrate with User Groups or custom Team DocType
		# Example:
		# if frappe.db.exists("User Group", team_name):
		#     return frappe.get_doc("User Group", team_name).get_members()

		return []

	def render_task_description(self, template, stage_instance):
		"""
		Render task description with context variables using Jinja2

		Args:
			template: Task Template document
			stage_instance: Assessment Stage Instance

		Returns:
			str: Rendered description with context
		"""
		if not template.task_description:
			return ""

		# Get request document for context
		request = frappe.get_doc("Request", self.request) if self.request else None

		context = {
			"request": request,
			"stage": stage_instance,
			"project": self,
			"doc": request  # Alias for Jinja compatibility
		}

		# Use Jinja2 to render dynamic descriptions
		try:
			from frappe.utils.jinja import render_template
			return render_template(template.task_description, context)
		except Exception as e:
			frappe.log_error(f"Error rendering task description: {str(e)}")
			# Return plain description if rendering fails
			return template.task_description

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


@frappe.whitelist()
def create_tasks_from_template(assessment_project_name):
	"""
	API method to create tasks from templates

	This generates the complete project plan with all tasks for all stages
	"""
	doc = frappe.get_doc("Assessment Project", assessment_project_name)
	tasks_created = doc.create_tasks_from_template()
	doc.save()
	return {
		"assessment_project": doc.name,
		"tasks_created": tasks_created,
		"stages": len(doc.stages)
	}
