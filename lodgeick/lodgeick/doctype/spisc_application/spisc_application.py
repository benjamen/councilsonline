# Copyright (c) 2025, Myme and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today
from lodgeick.utils.application_sync import sync_to_request


class SPISCApplication(Document):
	def validate(self):
		"""Validate SPISC application before saving"""
		self.calculate_age()
		self.check_eligibility_criteria()

	def calculate_age(self):
		"""Auto-calculate age from birth_date"""
		if self.birth_date:
			today_date = getdate(today())
			born = getdate(self.birth_date)
			self.age = today_date.year - born.year - (
				(today_date.month, today_date.day) < (born.month, born.day)
			)

	def check_eligibility_criteria(self):
		"""Validate SPISC eligibility requirements"""
		# Age requirement
		if self.age and self.age < 60:
			frappe.throw(
				frappe._("Applicant must be 60 years or older to be eligible for SPISC"),
				title="Age Requirement Not Met"
			)

		# Income threshold warning
		if self.monthly_income and self.monthly_income > 10000:
			frappe.msgprint(
				frappe._("Monthly income exceeds the poverty threshold (PHP 10,000). Eligibility may be affected."),
				indicator="orange",
				title="Income Warning"
			)

		# SSS/GSIS pension check
		if self.sss_number and self.income_source == "Pension":
			frappe.msgprint(
				frappe._(
					"Applicant appears to be receiving SSS/GSIS pension. "
					"Please verify they are not already receiving government pension benefits."
				),
				indicator="orange",
				title="Pension Check Required"
			)

	def on_update(self):
		"""Sync display fields to parent Request using standardized utility"""
		sync_to_request(self)

	def assess_eligibility(self, assessed_by=None):
		"""
		Council staff method to assess applicant eligibility

		Args:
			assessed_by: User who performed the assessment
		"""
		# Check age requirement
		if not self.age or self.age < 60:
			self.eligibility_status = "Ineligible"
			self.eligibility_notes = "Does not meet age requirement (must be 60 or older)"
			self.save()
			return False

		# Check income threshold
		if self.monthly_income and self.monthly_income > 10000:
			self.eligibility_status = "Ineligible"
			self.eligibility_notes = "Monthly income exceeds poverty threshold (PHP 10,000)"
			self.save()
			return False

		# Check residency (basic - would need more validation in production)
		if not self.barangay or not self.municipality:
			self.eligibility_status = "Pending"
			self.eligibility_notes = "Incomplete address information - residency verification required"
			self.save()
			return False

		# If all checks pass
		self.eligibility_status = "Eligible"
		self.eligibility_notes = "Meets all SPISC eligibility criteria"
		self.assessed_by = assessed_by or frappe.session.user
		self.assessed_date = today()
		self.save()

		return True

	def get_display_address(self):
		"""Get formatted address for display"""
		parts = [
			self.address_line,
			self.barangay,
			self.municipality,
			self.province
		]
		return ", ".join(filter(None, parts))

	def get_display_description(self):
		"""Get brief description for Request list view"""
		# Get applicant name from parent Request
		applicant_name = "Unknown"
		if self.request:
			applicant_name = frappe.db.get_value("Request", self.request, "requester_name") or "Unknown"

		desc = f"{applicant_name} - SPISC Application"
		if self.age:
			desc += f" (Age: {self.age})"
		if self.eligibility_status and self.eligibility_status != "Pending":
			desc += f" - {self.eligibility_status}"
		return desc
