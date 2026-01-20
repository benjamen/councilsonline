# Copyright (c) 2025, Essdee and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssessmentCondition(Document):
	def validate(self):
		"""Validate condition data"""
		self.validate_s108aa_compliance()
		self.validate_condition_number()

	def validate_s108aa_compliance(self):
		"""Ensure S108AA justification is provided for RMA compliance"""
		# For active conditions, ensure basic S108AA fields are filled
		if self.condition_status == "Active":
			if not self.s108aa_purpose:
				frappe.msgprint(
					"Warning: S108AA Purpose should be specified for active conditions",
					alert=True
				)

			# Strong validation for resource consent conditions
			if self.assessment_project:
				project = frappe.get_doc("Assessment Project", self.assessment_project)
				if project.request_type and "Resource Consent" in project.request_type:
					if not self.s108aa_relationship:
						frappe.msgprint(
							"Warning: S108AA Relationship should be documented for Resource Consent conditions",
							alert=True
						)

	def validate_condition_number(self):
		"""Ensure condition number is unique within assessment project"""
		if self.assessment_project and self.condition_number:
			existing = frappe.db.exists(
				"Assessment Condition",
				{
					"assessment_project": self.assessment_project,
					"condition_number": self.condition_number,
					"name": ["!=", self.name]
				}
			)
			if existing:
				frappe.throw(
					f"Condition number {self.condition_number} already exists for this assessment project"
				)

	def get_next_condition_number(self):
		"""Get the next available condition number for the assessment project"""
		if not self.assessment_project:
			return 1

		# Get max condition number for this project
		max_number = frappe.db.get_value(
			"Assessment Condition",
			{"assessment_project": self.assessment_project},
			"MAX(condition_number)"
		)

		return (max_number or 0) + 1

	def before_insert(self):
		"""Auto-assign condition number if not provided"""
		if not self.condition_number:
			self.condition_number = self.get_next_condition_number()


@frappe.whitelist()
def create_standard_conditions(assessment_project, condition_type):
	"""Create standard condition templates based on type"""
	templates = {
		"Lapsing": {
			"condition_text": "This consent shall lapse five years from the date of commencement unless:\n(a) The consent is given effect to; or\n(b) The Council grants an extension under Section 125 of the Resource Management Act 1991.",
			"s108aa_purpose": "Lapse conditions",
			"s108aa_relationship": "Standard lapsing condition ensuring consent is exercised within reasonable timeframe",
			"s108aa_reasonableness": "Required under RMA to prevent indefinite consents",
			"condition_type": "Lapsing",
			"timing": "Ongoing"
		},
		"Pre-Commencement": {
			"condition_text": "At least 10 working days prior to commencement of works, the consent holder shall:\n(a) Provide the Council with the proposed start date; and\n(b) Provide contact details for the site supervisor.",
			"s108aa_purpose": "Administrative matters",
			"s108aa_relationship": "Enables Council to plan monitoring and compliance activities",
			"s108aa_reasonableness": "Necessary for effective consent administration and monitoring",
			"condition_type": "Pre-Commencement",
			"timing": "Before Commencement"
		}
	}

	template = templates.get(condition_type)
	if not template:
		frappe.throw(f"No standard template found for condition type: {condition_type}")

	# Create condition
	condition = frappe.get_doc({
		"doctype": "Assessment Condition",
		"assessment_project": assessment_project,
		**template
	})
	condition.insert()

	return condition
