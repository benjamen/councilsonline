# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExclusionType(Document):
	def validate(self):
		"""Validation before saving"""
		# Prevent deletion of standard types
		if self.is_standard and self.has_value_changed("is_standard"):
			if not self.is_standard:
				frappe.throw("Cannot remove 'Is Standard' flag from standard exclusion types")

	def before_delete(self):
		"""Prevent deletion of standard types"""
		if self.is_standard:
			frappe.throw(f"Cannot delete standard exclusion type: {self.exclusion_type_name}")
