# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Assessment & Project Management API - Handles assessment templates, request type configuration, and project management
"""

import frappe
from frappe import _
from frappe.utils import cint
import json


def get_request_type_steps(request_type, council_code=None):
	"""
	Get step configuration for a request type, with optional council overrides

	Args:
		request_type: Name of Request Type
		council_code: Optional council code to apply council-specific overrides

	Returns:
		dict: Steps configuration with sections and fields
	"""
	try:
		# Get request type document
		rt_doc = frappe.get_doc("Request Type", request_type)

		# If no step_configs, return empty (fallback to hardcoded flow)
		if not rt_doc.step_configs:
			return {
				"steps": [],
				"uses_config": False,
				"message": "No step configuration found. Using default hardcoded flow."
			}

		steps = []

		# Load base step configuration
		for step_config in rt_doc.step_configs:
			if not step_config.is_enabled:
				continue

			step_data = {
				"step_number": step_config.step_number,
				"step_code": step_config.step_code,
				"step_title": step_config.step_title,
				"step_component": step_config.step_component or "DynamicStepRenderer",
				"is_enabled": step_config.is_enabled,
				"is_required": step_config.is_required,
				"show_on_review": step_config.show_on_review,
				"depends_on": step_config.depends_on,
				"sections": []
			}

			# FLATTENED STRUCTURE: Query sections by parent_step_code instead of nested parent
			# Sections are now stored directly under Request Type with a parent_step_code link
			sections = frappe.get_all(
				"Request Type Step Section",
				filters={
					"parent": rt_doc.name,  # Parent is now Request Type, not Step Config
					"parenttype": "Request Type",
					"parent_step_code": step_config.step_code  # Link via step_code
				},
				fields=["name", "section_code", "section_title", "section_type", "sequence",
				        "is_enabled", "is_required", "show_on_review", "depends_on"],
				order_by="sequence asc"
			)

			for section in sections:
				if not section.is_enabled:
					continue

				section_data = {
					"section_code": section.section_code,
					"section_title": section.section_title,
					"section_type": section.section_type,
					"sequence": section.sequence,
					"is_enabled": section.is_enabled,
					"is_required": section.is_required,
					"show_on_review": section.show_on_review,
					"depends_on": section.depends_on,
					"fields": []
				}

				# FLATTENED STRUCTURE: Query fields by parent_section_code instead of nested parent
				# Fields are now stored directly under Request Type with a parent_section_code link
				fields = frappe.get_all(
					"Request Type Step Field",
					filters={
						"parent": rt_doc.name,  # Parent is now Request Type, not Section
						"parenttype": "Request Type",
						"parent_section_code": section.section_code  # Link via section_code
					},
					fields=["field_name", "field_label", "field_type", "is_required", "options",
					        "default_value", "depends_on", "validation", "show_on_review", "review_label"]
				)

				for field in fields:
					field_data = {
						"field_name": field.field_name,
						"field_label": field.field_label,
						"field_type": field.field_type,
						"is_required": field.is_required,
						"options": field.options,
						"default_value": field.default_value,
						"depends_on": field.depends_on,
						"validation": field.validation,
						"show_on_review": field.show_on_review,
						"review_label": field.review_label or field.field_label
					}
					section_data["fields"].append(field_data)

				step_data["sections"].append(section_data)

			steps.append(step_data)

		# NOTE: Payment and bank details steps are now defined in Request Type configuration
		# (not injected here). To add payment collection or bank details steps:
		# 1. Add step_config, step_sections, and step_fields to Request Type JSON
		# 2. Use depends_on conditions if steps should be conditional
		# 3. Set collects_payment or make_payment flags for accounting/reporting purposes
		#
		# This approach allows:
		# - Customizable payment workflows per council
		# - Configuration-driven forms (no code changes)
		# - Flexible field requirements and validation
		#
		# Example: SPISC could add a bank_details step to its configuration
		# Example: RC could add a payment_collection step for lodgement fees

		# REMOVED: Hardcoded payment step injection (Phase 2.4)
		# Previous code injected payment_collection and bank_details steps based on flags
		# Now these should be added to Request Type configuration instead

		# Apply council-specific overrides if provided
		if council_code:
			steps = apply_council_step_overrides(steps, request_type, council_code)

		# Sort by step_number
		steps = sorted(steps, key=lambda x: x.get("step_number", 999))

		return {
			"steps": steps,
			"uses_config": True,
			"request_type": request_type,
			"council_code": council_code
		}

	except Exception as e:
		frappe.log_error(f"Get Request Type Steps Error: {str(e)}")
		return {
			"steps": [],
			"uses_config": False,
			"error": str(e)
		}


def apply_council_step_overrides(steps, request_type, council_code):
	"""
	Apply council-specific step overrides

	Args:
		steps: List of step configurations
		request_type: Request Type name
		council_code: Council code

	Returns:
		list: Steps with council overrides applied
	"""
	try:
		# Get council request type configuration
		council_rt = frappe.db.get_value("Council Request Type",
										filters={
											"parent": council_code,
											"request_type": request_type
										},
										fieldname="name")

		if not council_rt:
			return steps

		# Get step overrides for this council
		overrides = frappe.get_all("Council Request Type Step Override",
								  filters={"parent": council_rt},
								  fields=["*"])

		if not overrides:
			return steps

		# Apply overrides
		for step in steps:
			for override in overrides:
				if override.step_code == step["step_code"]:
					# Override step-level settings
					if override.custom_title:
						step["step_title"] = override.custom_title
					if override.sequence_override:
						step["step_number"] = override.sequence_override
					step["is_enabled"] = override.is_enabled
					step["is_required"] = override.is_required

					# Apply section overrides
					section_overrides = frappe.get_all("Council Step Section Override",
													  filters={"parent": override.name},
													  fields=["*"])

					for section in step.get("sections", []):
						for sec_override in section_overrides:
							if sec_override.section_code == section["section_code"]:
								if sec_override.custom_title:
									section["section_title"] = sec_override.custom_title
								section["is_enabled"] = sec_override.is_enabled
								section["is_required"] = sec_override.is_required

		# Filter out disabled steps
		steps = [s for s in steps if s.get("is_enabled", True)]

		return steps

	except Exception as e:
		frappe.log_error(f"Apply Council Step Overrides Error: {str(e)}")
		return steps


@frappe.whitelist()
def validate_step_data(request_type, council_code, step_code, data):
	"""
	Validate data for a specific step based on configuration

	Args:
		request_type: Name of Request Type
		council_code: Council code
		step_code: Step code to validate
		data: Form data (JSON string or dict)

	Returns:
		dict: Validation result with errors
	"""
	try:
		if isinstance(data, str):
			data = json.loads(data)

		# Get step configuration
		result = get_request_type_steps(request_type, council_code)

		if not result.get("uses_config"):
			return {
				"valid": True,
				"message": "No step configuration found. Skipping validation."
			}

		# Find the step
		step = next((s for s in result["steps"] if s["step_code"] == step_code), None)

		if not step:
			return {
				"valid": False,
				"errors": {"step": f"Step {step_code} not found in configuration"}
			}

		errors = {}

		# Validate each section
		for section in step.get("sections", []):
			if not section.get("is_enabled"):
				continue

			# Validate each field
			for field in section.get("fields", []):
				field_name = field["field_name"]
				field_value = data.get(field_name)

				# Check required fields
				if field["is_required"]:
					if field_value is None or field_value == "":
						errors[field_name] = f"{field['field_label']} is required"

				# Run custom validation if provided
				if field.get("validation") and field_value:
					try:
						# Execute custom validation (would need sandbox evaluation)
						# For now, skip custom validation for security
						pass
					except Exception as e:
						errors[field_name] = f"Validation error: {str(e)}"

		return {
			"valid": len(errors) == 0,
			"errors": errors,
			"message": "Validation successful" if len(errors) == 0 else f"Found {len(errors)} validation error(s)"
		}

	except Exception as e:
		frappe.log_error(f"Validate Step Data Error: {str(e)}")
		return {
			"valid": False,
			"errors": {"system": str(e)}
		}


# ============================================================================
# REQUEST TYPE BUILDER API ENDPOINTS
# ============================================================================

@frappe.whitelist()
def get_step_templates():
	"""
	Get list of available step templates for Request Type Builder

	Returns:
		list: List of template metadata
	"""
	try:
		from lodgeick.templates.step_templates import list_available_templates, get_template_info

		templates = list_available_templates()
		template_list = []

		for template_name in templates:
			try:
				info = get_template_info(template_name)
				template_list.append({
					"name": template_name,
					"title": info.get("template_title", template_name),
					"description": info.get("description", ""),
					"version": info.get("version", "1.0")
				})
			except Exception as e:
				frappe.log_error(f"Error loading template {template_name}: {str(e)}")
				continue

		return template_list

	except Exception as e:
		frappe.log_error(f"Get Step Templates Error: {str(e)}")
		frappe.throw(_("Failed to load step templates: {0}").format(str(e)))


@frappe.whitelist()
def load_step_template(template_name):
	"""
	Load a specific step template for Request Type Builder

	Args:
		template_name: Name of the template to load

	Returns:
		dict: Template configuration
	"""
	try:
		from lodgeick.templates.step_templates import load_template

		template = load_template(template_name)

		return {
			"success": True,
			"template": template
		}

	except Exception as e:
		frappe.log_error(f"Load Step Template Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def save_request_type_config(config):
	"""
	Save Request Type configuration from Request Type Builder

	Args:
		config: JSON string or dict containing Request Type configuration

	Returns:
		dict: Success status and created/updated Request Type name
	"""
	try:
		if isinstance(config, str):
			config = json.loads(config)

		# Validate required fields
		if not config.get("name"):
			frappe.throw(_("Request Type name is required"))

		rt_name = config["name"]

		# Check if Request Type exists
		exists = frappe.db.exists("Request Type", rt_name)

		# Create or get Request Type document
		if exists:
			rt_doc = frappe.get_doc("Request Type", rt_name)
			# Clear existing configuration
			rt_doc.step_configs = []
			rt_doc.step_sections = []
			rt_doc.step_fields = []
		else:
			rt_doc = frappe.new_doc("Request Type")
			rt_doc.name = rt_name

		# Set basic fields
		rt_doc.category = config.get("category", "Planning")
		rt_doc.description = config.get("description", "")
		rt_doc.collects_payment = cint(config.get("collects_payment", 0))
		rt_doc.make_payment = cint(config.get("make_payment", 0))
		rt_doc.is_active = 1

		# Add steps, sections, and fields
		for step in config.get("steps", []):
			step_config = {
				"step_number": step.get("step_number"),
				"step_code": step.get("step_code"),
				"step_title": step.get("step_title"),
				"step_component": step.get("step_component", "DynamicStepRenderer"),
				"is_enabled": cint(step.get("is_enabled", 1)),
				"is_required": cint(step.get("is_required", 1)),
				"show_on_review": cint(step.get("show_on_review", 1)),
				"description": step.get("description", "")
			}

			rt_doc.append("step_configs", step_config)

			# Add sections
			for section in step.get("sections", []):
				section_data = {
					"parent_step_code": step.get("step_code"),
					"section_code": section.get("section_code"),
					"section_title": section.get("section_title"),
					"section_type": section.get("section_type", "Standard"),
					"sequence": section.get("sequence", 1),
					"is_enabled": cint(section.get("is_enabled", 1)),
					"is_required": cint(section.get("is_required", 1)),
					"show_on_review": cint(section.get("show_on_review", 1)),
					"description": section.get("description", "")
				}

				rt_doc.append("step_sections", section_data)

				# Add fields
				for field in section.get("fields", []):
					field_data = {
						"parent_section_code": section.get("section_code"),
						"field_name": field.get("field_name"),
						"field_label": field.get("field_label"),
						"field_type": field.get("field_type"),
						"is_required": cint(field.get("is_required", 0)),
						"show_on_review": cint(field.get("show_on_review", 1)),
						"review_label": field.get("review_label", field.get("field_label")),
						"options": field.get("options", ""),
						"default_value": field.get("default_value", ""),
						"validation": field.get("validation", ""),
						"depends_on": field.get("depends_on", ""),
						"description": field.get("description", "")
					}

					rt_doc.append("step_fields", field_data)

		# Save the document
		if exists:
			rt_doc.save()
			action = "updated"
		else:
			rt_doc.insert()
			action = "created"

		frappe.db.commit()

		return {
			"success": True,
			"message": f"Request Type '{rt_name}' {action} successfully",
			"name": rt_name
		}

	except Exception as e:
		frappe.log_error(f"Save Request Type Config Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def load_request_type_config(request_type_name):
	"""
	Load existing Request Type configuration for editing in Request Type Builder

	Args:
		request_type_name: Name of the Request Type to load

	Returns:
		dict: Request Type configuration in builder format
	"""
	try:
		if not frappe.db.exists("Request Type", request_type_name):
			frappe.throw(_("Request Type '{0}' not found").format(request_type_name))

		rt_doc = frappe.get_doc("Request Type", request_type_name)

		# Build configuration object
		config = {
			"name": rt_doc.name,
			"category": rt_doc.category,
			"description": rt_doc.description or "",
			"collects_payment": cint(rt_doc.collects_payment),
			"make_payment": cint(rt_doc.make_payment),
			"steps": []
		}

		# Group sections and fields by step
		for step_config in rt_doc.step_configs:
			step = {
				"step_number": step_config.step_number,
				"step_code": step_config.step_code,
				"step_title": step_config.step_title,
				"step_component": step_config.step_component,
				"is_enabled": cint(step_config.is_enabled),
				"is_required": cint(step_config.is_required),
				"show_on_review": cint(step_config.show_on_review),
				"description": step_config.description or "",
				"expanded": False,
				"sections": []
			}

			# Get sections for this step
			sections = [s for s in rt_doc.step_sections if s.parent_step_code == step_config.step_code]

			for section in sections:
				section_data = {
					"section_code": section.section_code,
					"section_title": section.section_title,
					"section_type": section.section_type,
					"sequence": section.sequence,
					"is_enabled": cint(section.is_enabled),
					"is_required": cint(section.is_required),
					"show_on_review": cint(section.show_on_review),
					"description": section.description or "",
					"fields": []
				}

				# Get fields for this section
				fields = [f for f in rt_doc.step_fields if f.parent_section_code == section.section_code]

				for field in fields:
					field_data = {
						"field_name": field.field_name,
						"field_label": field.field_label,
						"field_type": field.field_type,
						"is_required": cint(field.is_required),
						"show_on_review": cint(field.show_on_review),
						"review_label": field.review_label or field.field_label,
						"options": field.options or "",
						"default_value": field.default_value or "",
						"validation": field.validation or "",
						"depends_on": field.depends_on or "",
						"description": field.description or ""
					}

					section_data["fields"].append(field_data)

				step["sections"].append(section_data)

			config["steps"].append(step)

		return {
			"success": True,
			"config": config
		}

	except Exception as e:
		frappe.log_error(f"Load Request Type Config Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def get_assessment_templates():
	"""
	List all assessment templates with metadata for builder

	Returns:
		list: Assessment templates with name, request_type, is_active, stage_count
	"""
	try:
		templates = frappe.get_all(
			"Assessment Template",
			fields=[
				"name",
				"template_name",
				"request_type",
				"is_active",
				"default_budget_hours",
				"description",
				"modified"
			],
			order_by="modified desc"
		)

		# Enrich with stage count and request type name
		for template in templates:
			# Get stage count
			stage_count = frappe.db.count(
				"Assessment Template Stage",
				{"parent": template.name}
			)
			template["stage_count"] = stage_count

			# Get request type name
			if template.get("request_type"):
				request_type_name = frappe.db.get_value(
					"Request Type",
					template.request_type,
					"type_name"
				)
				template["request_type_name"] = request_type_name

		return {
			"success": True,
			"templates": templates
		}

	except Exception as e:
		frappe.log_error(f"Get Assessment Templates Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def load_assessment_template(template_name):
	"""
	Load assessment template with all stages for editing

	Args:
		template_name: Name of the Assessment Template

	Returns:
		dict: Template configuration with stages
	"""
	try:
		# Get template document
		template = frappe.get_doc("Assessment Template", template_name)

		# Build configuration object
		config = {
			"name": template.name,
			"template_name": template.template_name,
			"request_type": template.request_type,
			"is_active": template.is_active,
			"default_budget_hours": template.default_budget_hours,
			"description": template.description,
			"stages": []
		}

		# Get request type name if linked
		if template.request_type:
			request_type_name = frappe.db.get_value(
				"Request Type",
				template.request_type,
				"type_name"
			)
			config["request_type_name"] = request_type_name

		# Add stages
		for stage in template.stages:
			stage_data = {
				"stage_number": stage.stage_number,
				"stage_type": stage.stage_type,
				"estimated_hours": stage.estimated_hours,
				"required": stage.required,
				"description": stage.description
			}

			# Get stage type details
			if stage.stage_type:
				stage_type_doc = frappe.get_doc("Assessment Stage Type", stage.stage_type)
				stage_data["stage_type_name"] = stage_type_doc.stage_type_name
				stage_data["stage_type_description"] = stage_type_doc.description
				stage_data["stage_type_color"] = stage_type_doc.color

			config["stages"].append(stage_data)

		return {
			"success": True,
			"template": config
		}

	except Exception as e:
		frappe.log_error(f"Load Assessment Template Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def save_assessment_template(config):
	"""
	Validate and save assessment template configuration

	Args:
		config: JSON configuration with template and stages

	Returns:
		dict: Success status and saved template name
	"""
	try:
		# Parse config if string
		if isinstance(config, str):
			config = json.loads(config)

		# Determine if creating new or updating existing
		template_name = config.get("name")

		if template_name and frappe.db.exists("Assessment Template", template_name):
			# Update existing template
			template = frappe.get_doc("Assessment Template", template_name)
		else:
			# Create new template
			template = frappe.new_doc("Assessment Template")

		# Set basic fields
		template.template_name = config.get("template_name")
		template.request_type = config.get("request_type")
		template.is_active = config.get("is_active", 1)
		template.default_budget_hours = config.get("default_budget_hours")
		template.description = config.get("description")

		# Clear existing stages
		template.stages = []

		# Add stages from config
		for stage_config in config.get("stages", []):
			template.append("stages", {
				"stage_number": stage_config.get("stage_number"),
				"stage_type": stage_config.get("stage_type"),
				"estimated_hours": stage_config.get("estimated_hours"),
				"required": stage_config.get("required", 0),
				"description": stage_config.get("description")
			})

		# Save (validation will run automatically)
		if template.is_new():
			template.insert()
		else:
			template.save()

		return {
			"success": True,
			"message": "Assessment template saved successfully",
			"template_name": template.name
		}

	except Exception as e:
		frappe.log_error(f"Save Assessment Template Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def get_assessment_stage_types():
	"""
	Get master list of available assessment stage types

	Returns:
		list: Assessment stage types with name, description, color
	"""
	try:
		stage_types = frappe.get_all(
			"Assessment Stage Type",
			fields=[
				"name",
				"stage_type_name",
				"description",
				"color",
				"is_active"
			],
			filters={"is_active": 1},
			order_by="stage_type_name"
		)

		return {
			"success": True,
			"stage_types": stage_types
		}

	except Exception as e:
		frappe.log_error(f"Get Assessment Stage Types Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


# ==================== SPISC APPLICATION ACTION BAR APIS ====================

@frappe.whitelist()
def get_spisc_summary_data(request_id):
	"""
	Get summary data for SPISC Application dashboard

	Args:
		request_id: Request ID

	Returns:
		dict: Summary metrics
	"""
	try:
		# Get tasks count
		tasks_count = frappe.db.count("Project Task", {
			"request": request_id,
			"status": ["in", ["Open", "In Progress"]]
		})

		# Get meetings count
		meetings_count = frappe.db.count("Council Meeting", {
			"request": request_id
		})

		# Get communications count
		communications_count = frappe.db.count("Communication Log", {
			"request": request_id
		})

		# Get assessment project status
		assessment = frappe.db.get_value("Assessment Project",
			{"request": request_id},
			["overall_status"],
			as_dict=True
		)
		assessment_status = assessment.overall_status if assessment else "Not Started"

		# Get eligibility status from SPISC Application
		spisc_app = frappe.get_all("SPISC Application",
			filters={"request": request_id},
			fields=["eligibility_status"],
			limit=1
		)
		eligibility_status = spisc_app[0].eligibility_status if spisc_app else "Pending"

		return {
			"tasks_count": tasks_count,
			"meetings_count": meetings_count,
			"communications_count": communications_count,
			"assessment_status": assessment_status,
			"eligibility_status": eligibility_status
		}

	except Exception as e:
		frappe.log_error(f"Get SPISC Summary Error: {str(e)}", "SPISC API Error")
		frappe.throw(_("Failed to get SPISC summary data: {0}").format(str(e)))


@frappe.whitelist()
def create_assessment_project_for_request(request, request_type):
	"""
	Create Assessment Project for a SPISC request

	Args:
		request: Request ID
		request_type: Request Type name

	Returns:
		dict: Created Assessment Project
	"""
	try:
		# Check if Assessment Project already exists
		existing = frappe.db.exists("Assessment Project", {"request": request})
		if existing:
			return frappe.get_doc("Assessment Project", existing)

		# Get Assessment Template for SPISC
		template = frappe.db.get_value("Assessment Template",
			{"request_type": request_type},
			"name"
		)

		if not template:
			frappe.throw(_("No Assessment Template found for {0}").format(request_type))

		# Create Assessment Project
		assessment_project = frappe.get_doc({
			"doctype": "Assessment Project",
			"request": request,
			"assessment_template": template,
			"status": "Not Started"
		})
		assessment_project.insert(ignore_permissions=True)
		frappe.db.commit()

		return assessment_project

	except Exception as e:
		frappe.log_error(f"Create Assessment Project Error: {str(e)}", "Assessment API Error")
		frappe.throw(_("Failed to create Assessment Project: {0}").format(str(e)))
