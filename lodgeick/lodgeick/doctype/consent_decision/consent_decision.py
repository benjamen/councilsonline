# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days

class ConsentDecision(Document):
	def validate(self):
		"""Validate consent decision"""
		# Auto-set drafted_by and drafted_date
		if not self.drafted_by:
			self.drafted_by = frappe.session.user
		if not self.drafted_date:
			self.drafted_date = frappe.utils.today()

		# Calculate objection period end (15 working days from served date)
		if self.served_to_applicant and self.served_date and not self.objection_period_end:
			self.objection_period_end = self.calculate_objection_period_end(self.served_date)

		# Calculate legal effect date (after objection period)
		if self.objection_period_end and not self.legal_effect_date:
			# Legal effect is typically the day after objection period ends
			self.legal_effect_date = add_days(self.objection_period_end, 1)

	def calculate_objection_period_end(self, start_date):
		"""Calculate end date 15 working days from start date"""
		from frappe.utils import add_days, getdate

		current_date = getdate(start_date)
		working_days_added = 0

		# Add 15 working days (excluding weekends)
		while working_days_added < 15:
			current_date = add_days(current_date, 1)
			# Check if it's a weekday (Monday=0, Sunday=6)
			if current_date.weekday() < 5:  # Monday to Friday
				working_days_added += 1

		return current_date

	def on_submit(self):
		"""Actions when decision is submitted"""
		# Update RCA with decision
		self.update_rca_decision()

		# Send notifications based on status
		if self.decision_status == "Approved":
			self.notify_applicant_decision_ready()

	def update_rca_decision(self):
		"""Update the Resource Consent Application with decision"""
		if self.resource_consent_application:
			rca = frappe.get_doc("Resource Consent Application", self.resource_consent_application)

			# Map decision type to status
			if self.decision_type == "Granted" or self.decision_type == "Granted with Conditions":
				rca.status = "Granted"
			elif self.decision_type == "Declined":
				rca.status = "Declined"
			elif self.decision_type == "Withdrawn":
				rca.status = "Withdrawn"
			elif self.decision_type == "Granted in Part":
				rca.status = "Granted"

			rca.decision_date = self.decision_date
			rca.save(ignore_permissions=True)

	def notify_applicant_decision_ready(self):
		"""Notify applicant that decision is ready"""
		if self.resource_consent_application:
			rca = frappe.get_doc("Resource Consent Application", self.resource_consent_application)

			# Get applicant email from request
			if rca.request:
				request = frappe.get_doc("Request", rca.request)
				if request.applicant_email:
					try:
						frappe.sendmail(
							recipients=[request.applicant_email],
							subject=f"Decision Ready: {self.resource_consent_application}",
							message=f"""
								<p>Dear {request.applicant_name},</p>
								<p>A decision has been made on your resource consent application:</p>
								<ul>
									<li><strong>Application:</strong> {self.resource_consent_application}</li>
									<li><strong>Decision:</strong> {self.decision_type}</li>
									<li><strong>Decision Date:</strong> {frappe.utils.formatdate(self.decision_date)}</li>
								</ul>
								<p>You will receive the formal decision letter shortly.</p>
							"""
						)
					except Exception as e:
						frappe.log_error(f"Failed to send decision notification: {str(e)}")

	def approve_decision(self):
		"""Approve the decision"""
		self.decision_status = "Approved"
		self.approved_by = frappe.session.user
		self.approved_date = frappe.utils.today()
		self.save()
		frappe.msgprint("Decision approved successfully")

	def serve_decision(self):
		"""Mark decision as served"""
		self.served_to_applicant = True
		self.served_date = frappe.utils.today()
		self.decision_status = "Served"

		# Calculate objection period
		self.objection_period_end = self.calculate_objection_period_end(self.served_date)
		self.legal_effect_date = add_days(self.objection_period_end, 1)

		self.save()
		frappe.msgprint(f"Decision served. Objection period ends: {frappe.utils.formatdate(self.objection_period_end)}")
