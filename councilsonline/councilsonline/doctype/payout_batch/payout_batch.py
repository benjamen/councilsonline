# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PayoutBatch(Document):
	def before_save(self):
		"""Calculate batch statistics"""
		self.calculate_statistics()

	def calculate_statistics(self):
		"""Calculate total payouts and amount"""
		payouts = frappe.get_all("Benefit Payout",
								filters={"payout_batch": self.name},
								fields=["payout_amount", "payout_status"])

		self.total_payouts = len(payouts)
		self.total_amount = sum([flt(p.payout_amount) for p in payouts])
		self.completed_count = len([p for p in payouts if p.payout_status == "Completed"])
		self.failed_count = len([p for p in payouts if p.payout_status == "Failed"])

	def approve_batch(self):
		"""Approve batch for processing"""
		self.batch_status = "Approved"
		self.approved_by = frappe.session.user
		self.approval_date = frappe.utils.now()
		self.save()

		# Update all payouts in batch to Approved
		frappe.db.sql("""
			UPDATE `tabBenefit Payout`
			SET payout_status = 'Approved',
				approved_by = %s,
				approval_date = %s
			WHERE payout_batch = %s
				AND payout_status = 'Pending'
		""", (frappe.session.user, frappe.utils.now(), self.name))

		frappe.db.commit()
