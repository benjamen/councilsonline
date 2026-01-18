# Copyright (c) 2026, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate


class ScheduledAppointment(Document):
	def validate(self):
		self.validate_times()
		self.calculate_duration()
		self.set_date()

	def before_insert(self):
		if not self.booked_by:
			self.booked_by = frappe.session.user
		if not self.booked_at:
			self.booked_at = now_datetime()

	def validate_times(self):
		"""Ensure end time is after start time"""
		if self.scheduled_start and self.scheduled_end:
			if self.scheduled_end <= self.scheduled_start:
				frappe.throw(_("End time must be after start time"))

	def calculate_duration(self):
		"""Calculate duration in minutes from start and end times"""
		if self.scheduled_start and self.scheduled_end:
			from frappe.utils import get_datetime
			start = get_datetime(self.scheduled_start)
			end = get_datetime(self.scheduled_end)
			self.duration_minutes = int((end - start).total_seconds() / 60)

	def set_date(self):
		"""Set scheduled_date from scheduled_start"""
		if self.scheduled_start:
			from frappe.utils import get_datetime
			self.scheduled_date = get_datetime(self.scheduled_start).date()

	def confirm(self):
		"""Mark appointment as confirmed"""
		self.status = "Confirmed"
		self.confirmed_at = now_datetime()
		self.save()

	def complete(self, notes=None):
		"""Mark appointment as completed"""
		self.status = "Completed"
		self.completed_at = now_datetime()
		if notes:
			self.notes = (self.notes or "") + f"\n\nCompletion Notes: {notes}"
		self.save()

	def cancel(self, reason=None):
		"""Cancel the appointment"""
		self.status = "Cancelled"
		self.cancelled_at = now_datetime()
		if reason:
			self.cancellation_reason = reason
		self.save()

	def mark_no_show(self):
		"""Mark appointment as no show"""
		self.status = "No Show"
		self.save()
