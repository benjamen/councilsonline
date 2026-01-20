# -*- coding: utf-8 -*-
# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_months

class Council(Document):
	def validate(self):
		"""Validate council data"""
		self.validate_council_code()
		self.validate_license_dates()
		self.set_defaults()

	def validate_council_code(self):
		"""Ensure council code is uppercase alphanumeric"""
		if self.council_code:
			self.council_code = self.council_code.upper().strip()

			# Check if alphanumeric (allow hyphens)
			if not all(c.isalnum() or c == '-' for c in self.council_code):
				frappe.throw("Council Code must be alphanumeric (hyphens allowed)")

	def validate_license_dates(self):
		"""Validate license start and expiry dates"""
		if self.license_start_date and self.license_expiry_date:
			if getdate(self.license_expiry_date) <= getdate(self.license_start_date):
				frappe.throw("License Expiry Date must be after License Start Date")

	def set_defaults(self):
		"""Set default values"""
		# Set default colors if not provided
		if not self.primary_color:
			self.primary_color = "#2563EB"  # Blue

		if not self.secondary_color:
			self.secondary_color = "#1E40AF"  # Darker blue

		if not self.accent_color:
			self.accent_color = "#059669"  # Emerald green for highlights

	def is_license_valid(self):
		"""Check if council license is currently valid"""
		if not self.is_active:
			return False

		# If no license dates set, assume valid
		if not self.license_start_date or not self.license_expiry_date:
			return True

		today = getdate(nowdate())
		start_date = getdate(self.license_start_date)
		expiry_date = getdate(self.license_expiry_date)

		return start_date <= today <= expiry_date

	def can_accept_requests(self):
		"""Check if council can accept new requests"""
		# First check license validity
		if not self.is_license_valid():
			return False

		# If no monthly limit, can always accept
		if not self.max_requests_per_month or self.max_requests_per_month == 0:
			return True

		# Check monthly quota
		from frappe.utils import get_first_day, get_last_day

		first_day = get_first_day(nowdate())
		last_day = get_last_day(nowdate())

		request_count = frappe.db.count("Request", {
			"council": self.name,
			"creation": ["between", [first_day, last_day]]
		})

		return request_count < self.max_requests_per_month

	def get_monthly_request_count(self):
		"""Get count of requests created this month"""
		from frappe.utils import get_first_day, get_last_day

		first_day = get_first_day(nowdate())
		last_day = get_last_day(nowdate())

		return frappe.db.count("Request", {
			"council": self.name,
			"creation": ["between", [first_day, last_day]]
		})

	def get_enabled_request_types(self):
		"""Get list of enabled request types for this council"""
		enabled_types = []

		for row in self.enabled_request_types:
			if row.is_enabled:
				enabled_types.append({
					"request_type": row.request_type,
					"custom_fee": row.base_fee_override,
					"custom_sla": row.sla_days_override
				})

		return enabled_types
