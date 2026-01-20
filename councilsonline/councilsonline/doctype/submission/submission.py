# -*- coding: utf-8 -*-
# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Submission(Document):
	def validate(self):
		"""Validate submission"""
		pass

	def on_submit(self):
		"""Actions when submission is submitted"""
		# Send acknowledgment to submitter
		self.send_acknowledgment()

		# Update RCA submission count
		self.update_rca_submission_count()

	def send_acknowledgment(self):
		"""Send acknowledgment email to submitter"""
		if self.submitter_email:
			try:
				frappe.sendmail(
					recipients=[self.submitter_email],
					subject=f"Submission Received: {self.resource_consent_application}",
					message=f"""
						<p>Dear {self.submitter_name},</p>
						<p>Thank you for your submission regarding resource consent application {self.resource_consent_application}.</p>
						<p><strong>Submission Details:</strong></p>
						<ul>
							<li><strong>Date Received:</strong> {frappe.utils.formatdate(self.submission_date)}</li>
							<li><strong>Submission Reference:</strong> {self.name}</li>
							<li><strong>Your Position:</strong> {self.submission_position}</li>
						</ul>
						<p>Your submission will be considered as part of the consent processing.</p>
						<p>You will be notified of the outcome of the application in due course.</p>
					"""
				)

				# Update status to Acknowledged
				self.status = "Acknowledged"
				self.save(ignore_permissions=True)

			except Exception as e:
				frappe.log_error(f"Failed to send submission acknowledgment: {str(e)}")

	def update_rca_submission_count(self):
		"""Update submission count on RCA"""
		if self.resource_consent_application:
			# Count total submissions for this RCA
			submission_count = frappe.db.count("Submission", {
				"resource_consent_application": self.resource_consent_application,
				"docstatus": 1
			})

			# Update RCA
			frappe.db.set_value("Resource Consent Application", self.resource_consent_application,
				"submission_count", submission_count)
