# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RequestTypeStepSection(Document):
	def validate(self):
		"""Validate section configuration"""
		self.validate_section_code()

	def validate_section_code(self):
		"""Ensure section code is lowercase with underscores"""
		if self.section_code:
			self.section_code = self.section_code.lower().strip().replace(' ', '_').replace('-', '_')

			# Check if alphanumeric with underscores
			if not all(c.isalnum() or c == '_' for c in self.section_code):
				frappe.throw("Section Code must be alphanumeric (underscores allowed)")
