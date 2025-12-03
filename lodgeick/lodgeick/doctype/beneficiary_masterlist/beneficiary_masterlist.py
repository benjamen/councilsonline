# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, nowdate, flt


class BeneficiaryMasterlist(Document):
	def before_save(self):
		"""Update statistics"""
		self.update_statistics()

	def update_statistics(self):
		"""Calculate payout statistics"""
		# Get all completed payouts for this beneficiary
		payouts = frappe.get_all("Benefit Payout",
								filters={
									"beneficiary": self.beneficiary,
									"payout_status": "Completed"
								},
								fields=["payout_amount", "payout_date"])

		# Total stats
		self.total_payouts_received = len(payouts)
		self.total_amount_received = sum([flt(p.payout_amount) for p in payouts])

		# Last 12 months stats
		twelve_months_ago = add_months(nowdate(), -12)
		recent_payouts = [p for p in payouts if p.payout_date >= twelve_months_ago]
		self.last_twelve_months_payouts = len(recent_payouts)
		self.last_twelve_months_amount = sum([flt(p.payout_amount) for p in recent_payouts])

		# Last payout date
		if payouts:
			self.last_payout_date = max([p.payout_date for p in payouts])

	def on_update(self):
		"""Handle status changes"""
		if self.has_value_changed("beneficiary_status"):
			if self.beneficiary_status == "Suspended":
				self.handle_suspension()

	def handle_suspension(self):
		"""Cancel pending payouts when beneficiary is suspended"""
		pending_payouts = frappe.get_all("Benefit Payout",
										filters={
											"beneficiary": self.beneficiary,
											"payout_status": ["in", ["Pending", "Approved"]]
										})

		for payout in pending_payouts:
			payout_doc = frappe.get_doc("Benefit Payout", payout.name)
			payout_doc.payout_status = "Cancelled"
			payout_doc.rejection_reason = f"Beneficiary suspended: {self.suspension_reason}"
			payout_doc.save(ignore_permissions=True)

		frappe.db.commit()
