# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, get_datetime

class NotificationDecision(Document):
	def validate(self):
		"""Validate notification decision"""
		# Calculate submission period for public notification (20 working days)
		if self.notification_decision == "Public Notification (s95)":
			if self.submission_period_start and not self.submission_period_end:
				self.submission_period_end = self.calculate_submission_end_date(self.submission_period_start)

		# Auto-set decided_by to current user if not set
		if not self.decided_by:
			self.decided_by = frappe.session.user

	def calculate_submission_end_date(self, start_date):
		"""Calculate end date 20 working days from start date"""
		from frappe.utils import add_days, getdate

		current_date = getdate(start_date)
		working_days_added = 0

		# Add 20 working days (excluding weekends)
		while working_days_added < 20:
			current_date = add_days(current_date, 1)
			# Check if it's a weekday (Monday=0, Sunday=6)
			if current_date.weekday() < 5:  # Monday to Friday
				working_days_added += 1

		return current_date

	def on_submit(self):
		"""Actions when notification decision is submitted"""
		# Update RCA with notification decision
		self.update_rca_notification_status()

		# Create notification tasks based on decision
		if self.notification_decision == "Limited Notification (s95B)":
			self.create_limited_notification_tasks()
		elif self.notification_decision == "Public Notification (s95)":
			self.create_public_notification_tasks()

	def update_rca_notification_status(self):
		"""Update the Resource Consent Application with notification decision"""
		if self.resource_consent_application:
			rca = frappe.get_doc("Resource Consent Application", self.resource_consent_application)

			# Map notification decision to status
			if self.notification_decision == "Non-Notified (s95A applies)":
				rca.notification_status = "Non-Notified"
			elif self.notification_decision == "Limited Notification (s95B)":
				rca.notification_status = "Limited Notification"
			elif self.notification_decision == "Public Notification (s95)":
				rca.notification_status = "Public Notification"

			rca.notification_decision_date = self.decision_date
			rca.save(ignore_permissions=True)

	def create_limited_notification_tasks(self):
		"""Create tasks for limited notification process"""
		# Create ToDo for serving limited notification
		if not frappe.db.exists("ToDo", {
			"reference_type": "Notification Decision",
			"reference_name": self.name,
			"description": ["like", "%Serve limited notification%"]
		}):
			todo = frappe.get_doc({
				"doctype": "ToDo",
				"allocated_to": self.decided_by,
				"reference_type": "Notification Decision",
				"reference_name": self.name,
				"description": f"Serve limited notification to {len(self.limited_notification_parties)} parties for {self.resource_consent_application}",
				"priority": "High",
				"status": "Open"
			})
			todo.insert(ignore_permissions=True)

	def create_public_notification_tasks(self):
		"""Create tasks for public notification process"""
		# Create ToDo for publishing public notification
		if not frappe.db.exists("ToDo", {
			"reference_type": "Notification Decision",
			"reference_name": self.name,
			"description": ["like", "%Publish public notification%"]
		}):
			todo = frappe.get_doc({
				"doctype": "ToDo",
				"allocated_to": self.decided_by,
				"reference_type": "Notification Decision",
				"reference_name": self.name,
				"description": f"Publish public notification for {self.resource_consent_application} ({self.public_notification_method})",
				"priority": "High",
				"status": "Open",
				"date": self.submission_period_start
			})
			todo.insert(ignore_permissions=True)
