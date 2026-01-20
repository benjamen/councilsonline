# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, flt
from datetime import datetime


class HouseholdRecord(Document):
	def autoname(self):
		"""Generate unique household ID"""
		if not self.household_id:
			# Generate ID based on barangay and timestamp
			timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
			barangay_code = self.barangay[:3].upper() if self.barangay else "HH"
			self.household_id = f"{barangay_code}-{timestamp}"

	def validate(self):
		"""Validate household data"""
		# Check if head of household already has a household
		if not self.is_new():
			return

		existing = frappe.db.get_value(
			"Household Record",
			{"head_of_household": self.head_of_household, "name": ["!=", self.name]},
			"name"
		)
		if existing:
			frappe.throw(f"User {self.head_of_household} is already registered as head of household: {existing}")

		# Auto-calculate vulnerability indicators from members
		self.calculate_vulnerability_indicators()

		# Auto-calculate poverty threshold status
		self.calculate_poverty_threshold()

	def before_save(self):
		"""Update last_updated timestamp"""
		self.last_updated = frappe.utils.now()

		# Recalculate indicators
		self.calculate_vulnerability_indicators()
		self.calculate_poverty_threshold()

	def calculate_vulnerability_indicators(self):
		"""Auto-calculate vulnerability flags based on household members"""
		if not self.household_members:
			return

		# Reset flags
		self.has_senior_citizen = 0
		self.has_pwd_member = 0

		for member in self.household_members:
			# Check for senior citizens (60+)
			if member.age and member.age >= 60:
				self.has_senior_citizen = 1

			# Check for PWD
			if member.is_pwd:
				self.has_pwd_member = 1

	def calculate_poverty_threshold(self):
		"""
		Calculate poverty threshold status based on income
		Philippines poverty threshold (2025): ~PHP 12,000/month per household
		"""
		if not self.total_monthly_income:
			self.poverty_threshold_status = "Below"
			return

		# Calculate household size
		household_size = len(self.household_members) if self.household_members else 1

		# Basic poverty threshold: PHP 3,000 per person per month
		# This is simplified - actual PSA thresholds vary by region
		poverty_threshold = 3000 * household_size

		income = flt(self.total_monthly_income)

		if income < poverty_threshold * 0.8:
			self.poverty_threshold_status = "Below"
		elif income < poverty_threshold * 1.2:
			self.poverty_threshold_status = "At"
		else:
			self.poverty_threshold_status = "Above"

	def on_update(self):
		"""Update head of household user record with household info"""
		if self.head_of_household:
			try:
				user = frappe.get_doc("User", self.head_of_household)
				# Update user's Philippines location fields
				user.philippines_barangay = self.barangay
				user.philippines_municipality = self.municipality
				user.philippines_province = self.province
				user.save(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(f"Failed to update user household info: {str(e)}")
