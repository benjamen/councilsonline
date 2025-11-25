# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SpecialistReview(Document):
	def validate(self):
		"""Validate specialist review"""
		# Auto-set reviewer to current user if not set
		if not self.reviewer:
			self.reviewer = frappe.session.user

	def on_submit(self):
		"""Actions when review is submitted"""
		# Update the specialist assignment status
		self.update_assignment_status()
		# Notify the case manager
		self.notify_case_manager()

	def update_assignment_status(self):
		"""Mark the specialist assignment as completed"""
		if self.specialist_assignment:
			assignment = frappe.get_doc("Specialist Assignment", self.specialist_assignment)
			if assignment.review_status != "Completed":
				assignment.review_status = "Completed"
				assignment.completed_date = frappe.utils.today()
				assignment.save(ignore_permissions=True)

				# Close associated ToDo
				todos = frappe.get_all("ToDo", filters={
					"reference_type": "Specialist Assignment",
					"reference_name": self.specialist_assignment,
					"status": ["!=", "Closed"]
				})
				for todo in todos:
					todo_doc = frappe.get_doc("ToDo", todo.name)
					todo_doc.status = "Closed"
					todo_doc.save(ignore_permissions=True)

	def notify_case_manager(self):
		"""Notify case manager that review is complete"""
		if self.resource_consent_application:
			rca = frappe.get_doc("Resource Consent Application", self.resource_consent_application)
			if rca.case_manager:
				try:
					frappe.sendmail(
						recipients=[rca.case_manager],
						subject=f"Specialist Review Completed: {self.resource_consent_application}",
						message=f"""
							<p>A specialist review has been completed:</p>
							<ul>
								<li><strong>Application:</strong> {self.resource_consent_application}</li>
								<li><strong>Recommendation:</strong> {self.recommendation}</li>
								<li><strong>Reviewer:</strong> {self.reviewer}</li>
							</ul>
							<p><a href="{frappe.utils.get_url()}/app/specialist-review/{self.name}">View Review</a></p>
						"""
					)
				except Exception as e:
					frappe.log_error(f"Failed to send review notification email: {str(e)}")
