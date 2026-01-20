# Copyright (c) 2026, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CouncilTeam(Document):
	def validate(self):
		self.validate_business_hours()
		self.validate_durations()

	def validate_business_hours(self):
		"""Ensure no duplicate days in business hours"""
		if self.business_hours:
			days = [bh.day_of_week for bh in self.business_hours]
			if len(days) != len(set(days)):
				frappe.throw(_("Duplicate days found in business hours"))

	def validate_durations(self):
		"""Validate duration settings"""
		if self.enable_scheduling:
			if self.default_appointment_duration <= 0:
				frappe.throw(_("Default appointment duration must be greater than 0"))
			if self.appointment_buffer_time < 0:
				frappe.throw(_("Buffer time cannot be negative"))

	def get_business_hours_dict(self):
		"""Return business hours as a dictionary keyed by day name"""
		from datetime import timedelta, time as datetime_time

		hours = {}
		if self.business_hours:
			for bh in self.business_hours:
				if bh.is_open:
					start_time = bh.start_time
					end_time = bh.end_time

					if isinstance(start_time, timedelta):
						total_seconds = int(start_time.total_seconds())
						hours_val = total_seconds // 3600
						minutes = (total_seconds % 3600) // 60
						start_time = datetime_time(hours_val, minutes)

					if isinstance(end_time, timedelta):
						total_seconds = int(end_time.total_seconds())
						hours_val = total_seconds // 3600
						minutes = (total_seconds % 3600) // 60
						end_time = datetime_time(hours_val, minutes)

					hours[bh.day_of_week] = {
						"start_time": start_time,
						"end_time": end_time
					}
		return hours

	def get_locations_list(self):
		"""Return available locations as a list"""
		locations = []
		if self.available_locations:
			locations = [loc.strip() for loc in self.available_locations.split("\n") if loc.strip()]
		if self.default_location and self.default_location not in locations:
			locations.insert(0, self.default_location)
		return locations
