# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class BenefitPayout(Document):
	def validate(self):
		"""Validate payout data"""
		# Validate payment method details
		if self.payment_method == "Bank Transfer":
			if not self.bank_name or not self.bank_account_number:
				frappe.throw("Bank name and account number are required for bank transfers")
		elif self.payment_method == "GCash":
			if not self.gcash_number:
				frappe.throw("GCash number is required for GCash payments")
		elif self.payment_method == "Cash Pickup":
			if not self.pickup_location:
				frappe.throw("Pickup location is required for cash pickup")

	def before_submit(self):
		"""Mark as approved when submitted"""
		if self.payout_status == "Pending":
			self.payout_status = "Approved"
			self.approved_by = frappe.session.user
			self.approval_date = frappe.utils.now()

	def on_update(self):
		"""Handle status changes"""
		if self.has_value_changed("payout_status"):
			if self.payout_status == "Completed":
				self.send_completion_notification()
			elif self.payout_status == "Failed":
				self.send_failure_notification()

	def send_completion_notification(self):
		"""Send notification when payout is completed"""
		try:
			beneficiary = frappe.get_doc("User", self.beneficiary)
			frappe.sendmail(
				recipients=[beneficiary.email],
				subject=f"Payout Completed - {self.name}",
				message=f"""
				<p>Dear {beneficiary.full_name},</p>
				<p>Your benefit payout has been completed.</p>
				<p><strong>Amount:</strong> {self.currency} {self.payout_amount:,.2f}</p>
				<p><strong>Payment Method:</strong> {self.payment_method}</p>
				<p><strong>Reference:</strong> {self.transaction_reference or 'N/A'}</p>
				<p>Thank you,<br>TayTay Council</p>
				"""
			)
		except Exception as e:
			frappe.log_error(f"Failed to send payout completion email: {str(e)}")

	def send_failure_notification(self):
		"""Send notification when payout fails"""
		try:
			beneficiary = frappe.get_doc("User", self.beneficiary)
			frappe.sendmail(
				recipients=[beneficiary.email],
				subject=f"Payout Issue - {self.name}",
				message=f"""
				<p>Dear {beneficiary.full_name},</p>
				<p>There was an issue processing your benefit payout.</p>
				<p><strong>Amount:</strong> {self.currency} {self.payout_amount:,.2f}</p>
				<p><strong>Reason:</strong> {self.rejection_reason or 'Not specified'}</p>
				<p>Please contact us to resolve this issue.</p>
				<p>Thank you,<br>TayTay Council</p>
				"""
			)
		except Exception as e:
			frappe.log_error(f"Failed to send payout failure email: {str(e)}")
