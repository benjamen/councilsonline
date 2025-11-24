# Copyright (c) 2025, Hohmesy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConsentConditionTemplate(Document):
	"""
	Master template for consent conditions.
	Can be linked to Request Types and instantiated into Resource Consent Applications.
	"""

	def validate(self):
		"""Validate the condition template"""
		# Ensure condition_code is uppercase if provided
		if self.condition_code:
			self.condition_code = self.condition_code.upper()

	def instantiate_for_request(self, request_doc, condition_number=None):
		"""
		Create an instance of this template for a specific request.
		Returns a dict with the condition data ready to append to a child table.
		"""
		# Replace placeholders in condition text
		condition_text = self.condition_text

		# Common placeholder replacements
		if request_doc:
			replacements = {
				'{property_address}': request_doc.get('property_address', '[PROPERTY ADDRESS]'),
				'{applicant_name}': request_doc.get('applicant_name', '[APPLICANT NAME]'),
				'{consent_holder}': request_doc.get('applicant_name', '[CONSENT HOLDER]'),
				'{request_number}': request_doc.get('request_number', '[REQUEST NUMBER]'),
			}

			for placeholder, value in replacements.items():
				condition_text = condition_text.replace(placeholder, value)

		# Return condition data
		return {
			'condition_number': condition_number or '',
			'condition_category': self.condition_category,
			'condition_text': condition_text,
			'compliance_status': 'Not Started',
			'compliance_due_date': None,
			'compliance_notes': f'From template: {self.template_name}'
		}
