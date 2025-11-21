# Copyright (c) 2025, Optified and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssessmentTemplate(Document):
	"""
	Reusable workflow template for assessments.

	Defines the stages, checklists, and automation for different
	types of consent processing (Resource Consent, Building Consent, etc.)

	Can be linked to a Request Type or left generic for manual selection.
	"""

	def validate(self):
		"""Validate stage configuration"""
		self.validate_stage_numbers()
		self.validate_required_stages()

	def validate_stage_numbers(self):
		"""Ensure stage numbers are sequential"""
		stage_numbers = [s.stage_number for s in self.stages]
		if len(stage_numbers) != len(set(stage_numbers)):
			frappe.throw("Stage numbers must be unique")

		# Check sequential
		sorted_numbers = sorted(stage_numbers)
		if sorted_numbers != list(range(1, len(sorted_numbers) + 1)):
			frappe.throw("Stage numbers must be sequential starting from 1")

	def validate_required_stages(self):
		"""At least one stage must be marked required"""
		if not any(s.required for s in self.stages):
			frappe.throw("At least one stage must be marked as required")
