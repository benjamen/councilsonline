# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_years, nowdate


class UserIdentityVerification(Document):
	def before_save(self):
		"""Set expiry date when verification status changes to Verified"""
		if self.verification_status == "Verified" and not self.expiry_date:
			# Set expiry to 1 year from verification date
			self.expiry_date = add_years(nowdate(), 1)

	def validate(self):
		"""Validate KYC data"""
		# Check for duplicate PhilSys ID
		if self.philsys_id:
			existing = frappe.db.get_value(
				"User Identity Verification",
				{"philsys_id": self.philsys_id, "name": ["!=", self.name]},
				"user"
			)
			if existing:
				frappe.throw(f"PhilSys ID {self.philsys_id} is already used by another user: {existing}")

		# Check for duplicate SSS number
		if self.sss_number:
			existing = frappe.db.get_value(
				"User Identity Verification",
				{"sss_number": self.sss_number, "name": ["!=", self.name]},
				"user"
			)
			if existing:
				frappe.throw(f"SSS Number {self.sss_number} is already used by another user: {existing}")

	def on_update(self):
		"""Update verification status and send notifications"""
		if self.has_value_changed("verification_status"):
			if self.verification_status == "Verified":
				self.send_verification_approved_email()
			elif self.verification_status == "Rejected":
				self.send_verification_rejected_email()

	def send_verification_approved_email(self):
		"""Send email notification when KYC is approved"""
		try:
			user = frappe.get_doc("User", self.user)
			frappe.sendmail(
				recipients=[user.email],
				subject="KYC Verification Approved",
				message=f"""
				<p>Dear {user.full_name},</p>
				<p>Your identity verification (KYC) has been approved. You can now apply for social assistance programs.</p>
				<p>Your verification is valid until {frappe.utils.format_date(self.expiry_date)}.</p>
				<p>Thank you,<br>TayTay Council</p>
				"""
			)
		except Exception as e:
			frappe.log_error(f"Failed to send KYC approval email: {str(e)}")

	def send_verification_rejected_email(self):
		"""Send email notification when KYC is rejected"""
		try:
			user = frappe.get_doc("User", self.user)
			frappe.sendmail(
				recipients=[user.email],
				subject="KYC Verification Requires Attention",
				message=f"""
				<p>Dear {user.full_name},</p>
				<p>Your identity verification (KYC) requires additional attention.</p>
				<p><strong>Reason:</strong> {self.rejection_reason or 'Not specified'}</p>
				<p>Please contact us or resubmit your documents.</p>
				<p>Thank you,<br>TayTay Council</p>
				"""
			)
		except Exception as e:
			frappe.log_error(f"Failed to send KYC rejection email: {str(e)}")
