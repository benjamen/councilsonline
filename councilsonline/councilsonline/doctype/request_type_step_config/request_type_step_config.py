# -*- coding: utf-8 -*-
# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RequestTypeStepConfig(Document):
	def validate(self):
		"""Validate step configuration"""
		self.validate_step_code()
		self.validate_step_number()

	def validate_step_code(self):
		"""Ensure step code is lowercase with underscores"""
		if self.step_code:
			self.step_code = self.step_code.lower().strip().replace(' ', '_').replace('-', '_')

			# Check if alphanumeric with underscores
			if not all(c.isalnum() or c == '_' for c in self.step_code):
				frappe.throw("Step Code must be alphanumeric (underscores allowed)")

	def validate_step_number(self):
		"""Ensure step number is positive"""
		if self.step_number and self.step_number < 1:
			frappe.throw("Step Number must be 1 or greater")
