# Copyright (c) 2025, Optified and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, date_diff


class ClockExclusionPeriod(Document):
	"""
	Child table for tracking statutory clock suspension periods.

	Automatically calculates working days excluded when ended_date is set.
	Supports linking to reference documents like RFI, custom documents.
	"""

	def validate(self):
		"""Calculate working days when period ends"""
		if self.ended_date and self.started_date:
			self.calculate_working_days_excluded()

	def calculate_working_days_excluded(self):
		"""Calculate working days between start and end dates"""
		from lodgeick.lodgeick.doctype.request.request import calculate_working_days_between

		try:
			start_dt = get_datetime(self.started_date)
			end_dt = get_datetime(self.ended_date)

			if end_dt < start_dt:
				frappe.throw("End date cannot be before start date")

			# Calculate working days (excludes weekends and NZ holidays)
			self.working_days_excluded = calculate_working_days_between(
				start_dt, end_dt
			)
		except Exception as e:
			frappe.log_error(f"Error calculating working days: {str(e)}")
			# Fallback to calendar days / 7 * 5 (rough estimate)
			calendar_days = date_diff(self.ended_date, self.started_date)
			self.working_days_excluded = int(calendar_days / 7 * 5)
