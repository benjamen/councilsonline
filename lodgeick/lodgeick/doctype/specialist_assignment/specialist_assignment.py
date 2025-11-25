# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days

class SpecialistAssignment(Document):
	def validate(self):
		"""Validate specialist assignment"""
		# Ensure due date is after assignment date
		if self.due_date and self.assignment_date:
			if getdate(self.due_date) < getdate(self.assignment_date):
				frappe.throw("Due Date cannot be before Assignment Date")

		# Auto-set completed date when status is Completed
		if self.review_status == "Completed" and not self.completed_date:
			self.completed_date = frappe.utils.today()

	def on_submit(self):
		"""Actions when assignment is submitted"""
		# Create notification/todo for assigned specialist
		self.notify_specialist()

	def notify_specialist(self):
		"""Send notification to assigned specialist"""
		if self.assigned_to:
			# Create ToDo for the specialist
			if not frappe.db.exists("ToDo", {
				"reference_type": "Specialist Assignment",
				"reference_name": self.name,
				"allocated_to": self.assigned_to
			}):
				todo = frappe.get_doc({
					"doctype": "ToDo",
					"allocated_to": self.assigned_to,
					"reference_type": "Specialist Assignment",
					"reference_name": self.name,
					"description": f"Specialist review required: {self.specialist_type} for {self.resource_consent_application}",
					"priority": "Medium",
					"status": "Open",
					"date": self.due_date
				})
				todo.insert(ignore_permissions=True)

			# Send email notification
			try:
				frappe.sendmail(
					recipients=[self.assigned_to],
					subject=f"Specialist Assignment: {self.specialist_type} - {self.resource_consent_application}",
					message=f"""
						<p>You have been assigned a specialist review:</p>
						<ul>
							<li><strong>Type:</strong> {self.specialist_type}</li>
							<li><strong>Application:</strong> {self.resource_consent_application}</li>
							<li><strong>Due Date:</strong> {frappe.utils.formatdate(self.due_date)}</li>
						</ul>
						<p><a href="{frappe.utils.get_url()}/app/specialist-assignment/{self.name}">View Assignment</a></p>
					"""
				)
			except Exception as e:
				frappe.log_error(f"Failed to send specialist assignment email: {str(e)}")
