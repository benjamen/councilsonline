# -*- coding: utf-8 -*-
# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RequestTypeStepField(Document):
	def validate(self):
		"""Validate field configuration"""
		self.validate_field_name()

	def validate_field_name(self):
		"""Ensure field name is lowercase with underscores"""
		if self.field_name:
			self.field_name = self.field_name.lower().strip().replace(' ', '_').replace('-', '_')

			# Check if alphanumeric with underscores
			if not all(c.isalnum() or c == '_' for c in self.field_name):
				frappe.throw("Field Name must be alphanumeric (underscores allowed)")
