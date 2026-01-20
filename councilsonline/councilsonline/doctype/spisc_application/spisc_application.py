# Copyright (c) 2025, Myme and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today
from councilsonline.utils.application_sync import sync_to_request


class SPISCApplication(Document):
	def onload(self):
		"""Auto-populate fields from Request when loading for display"""
		if self.request:
			try:
				request_doc = frappe.get_doc("Request", self.request)

				# Populate fields that were removed from fetch_from (virtual properties)
				if not self.applicant_name:
					self.applicant_name = request_doc.requester_name
				if not self.applicant_email:
					self.applicant_email = request_doc.requester_email
				if not self.applicant_phone:
					self.applicant_phone = request_doc.requester_phone
			except Exception as e:
				frappe.log_error(
					message=f"Failed to populate applicant fields from Request: {str(e)}",
					title=f"SPISC Application {self.name} - Auto-populate Error"
				)

	def validate(self):
		"""Validate SPISC application before saving"""
		# Ensure applicant fields are populated from Request before saving
		if self.request:
			try:
				request_doc = frappe.get_doc("Request", self.request)
				self.applicant_name = request_doc.requester_name
				self.applicant_email = request_doc.requester_email
				self.applicant_phone = request_doc.requester_phone
			except Exception:
				pass  # Don't block validation if Request doesn't exist

		self.calculate_age()
		self.set_full_address_display()
		self.check_eligibility_criteria()

	def calculate_age(self):
		"""Auto-calculate age from birth_date"""
		if self.birth_date:
			today_date = getdate(today())
			born = getdate(self.birth_date)
			self.age = today_date.year - born.year - (
				(today_date.month, today_date.day) < (born.month, born.day)
			)

	def set_full_address_display(self):
		"""Build full address display string for easy viewing"""
		address_parts = []

		if self.address_line:
			address_parts.append(self.address_line)
		if self.barangay:
			address_parts.append(f"Brgy. {self.barangay}")
		if self.municipality:
			address_parts.append(self.municipality)
		if self.province:
			address_parts.append(self.province)

		self.full_address_display = ", ".join(filter(None, address_parts))

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

	def on_submit(self):
		"""Auto-create Assessment Project when application is submitted"""
		if self.request and not self.get_assessment_project():
			self.create_assessment_project()

	def get_assessment_project(self):
		"""Check if Assessment Project already exists for this application"""
		return frappe.db.get_value(
			"Assessment Project",
			{"request": self.request},
			"name"
		)

	def create_assessment_project(self):
		"""Create Assessment Project with tasks for this SPISC application"""
		try:
			# Call the existing API method to create assessment project
			from councilsonline.api import create_assessment_project_for_request

			project = create_assessment_project_for_request(
				request=self.request,
				request_type="Social Pension for Indigent Senior Citizens (SPISC)"
			)

			if project:
				frappe.msgprint(
					frappe._("Assessment Project {0} created successfully with automated tasks").format(
						frappe.bold(project.name)
					),
					title="Assessment Project Created",
					indicator="green"
				)

		except Exception as e:
			frappe.log_error(
				message=str(e),
				title=f"Failed to create Assessment Project for {self.name}"
			)
			# Don't block submission if assessment project creation fails
			frappe.msgprint(
				frappe._("Application submitted successfully, but Assessment Project creation failed. Please create it manually."),
				title="Warning",
				indicator="orange"
			)

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
		# Get applicant name from parent Request (uses virtual property)
		applicant_name = "Unknown"
		if self.request:
			request = frappe.get_doc("Request", self.request)
			applicant_name = request.requester_name or "Unknown"

		desc = f"{applicant_name} - SPISC Application"
		if self.age:
			desc += f" (Age: {self.age})"
		if self.eligibility_status and self.eligibility_status != "Pending":
			desc += f" - {self.eligibility_status}"
		return desc


# ==================== WHITELISTED API METHODS ====================

@frappe.whitelist()
def assess_eligibility(name):
	"""
	Whitelist wrapper for assess_eligibility method
	Allows JavaScript to call this via frappe.call()

	Args:
		name: SPISC Application name

	Returns:
		dict: Updated SPISC Application
	"""
	doc = frappe.get_doc("SPISC Application", name)
	doc.assess_eligibility(assessed_by=frappe.session.user)
	doc.save()
	return doc
