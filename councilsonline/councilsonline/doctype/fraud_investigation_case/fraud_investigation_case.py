# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FraudInvestigationCase(Document):
	def on_update(self):
		"""Handle case status changes"""
		if self.has_value_changed("case_status"):
			if "Closed" in self.case_status or self.case_status == "Resolved":
				self.handle_case_closure()

	def handle_case_closure(self):
		"""Execute actions when case is closed"""
		if self.resolution == "Confirmed Fraud":
			# Suspend beneficiary if fraud confirmed
			if self.subject_user:
				self.suspend_beneficiary()

			# Cancel related payouts
			if self.related_payout:
				self.cancel_payout()

			# Flag household for review
			if self.related_household:
				self.flag_household()

	def suspend_beneficiary(self):
		"""Suspend beneficiary in masterlist"""
		try:
			masterlist = frappe.get_all("Beneficiary Masterlist",
									   filters={"beneficiary": self.subject_user},
									   limit=1)
			if masterlist:
				doc = frappe.get_doc("Beneficiary Masterlist", masterlist[0].name)
				doc.beneficiary_status = "Suspended"
				doc.suspended = 1
				doc.suspension_reason = f"Fraud Investigation Case: {self.name} - {self.resolution}"
				doc.save(ignore_permissions=True)
				frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Failed to suspend beneficiary: {str(e)}")

	def cancel_payout(self):
		"""Cancel related payout"""
		try:
			payout = frappe.get_doc("Benefit Payout", self.related_payout)
			if payout.payout_status not in ["Completed", "Cancelled"]:
				payout.payout_status = "Cancelled"
				payout.rejection_reason = f"Fraud Investigation: {self.name}"
				payout.save(ignore_permissions=True)
				frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Failed to cancel payout: {str(e)}")

	def flag_household(self):
		"""Flag household for review"""
		try:
			household = frappe.get_doc("Household Record", self.related_household)
			household.add_comment("Comment", f"Flagged due to fraud investigation: {self.name}")
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Failed to flag household: {str(e)}")
