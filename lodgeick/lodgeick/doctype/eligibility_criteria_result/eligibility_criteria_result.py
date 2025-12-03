# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class EligibilityCriteriaResult(Document):
	def validate(self):
		"""Calculate score percentage"""
		if self.overall_score and self.max_possible_score:
			self.score_percentage = (flt(self.overall_score) / flt(self.max_possible_score)) * 100

	def before_save(self):
		"""Auto-determine eligibility status based on score"""
		if not self.manual_override:
			self.auto_determine_eligibility()

	def auto_determine_eligibility(self):
		"""
		Auto-determine eligibility status based on score percentage
		Rules:
		- >= 80%: Eligible
		- 60-79%: Partially Eligible (Needs Review)
		- < 60%: Not Eligible
		"""
		if not self.score_percentage:
			self.eligibility_status = "Needs Review"
			return

		percentage = flt(self.score_percentage)

		if percentage >= 80:
			self.eligibility_status = "Eligible"
			self.final_decision = "Approved"
		elif percentage >= 60:
			self.eligibility_status = "Partially Eligible"
			self.final_decision = "Pending Review"
		else:
			self.eligibility_status = "Not Eligible"
			self.final_decision = "Rejected"

		# Override if critical criteria not met
		if not self.kyc_verified:
			self.eligibility_status = "Not Eligible"
			self.final_decision = "Rejected"
			self.eligibility_notes = (self.eligibility_notes or "") + "\n[System] KYC verification is required."

	def on_update(self):
		"""Update linked Request status"""
		if self.request and self.final_decision == "Approved":
			try:
				request = frappe.get_doc("Request", self.request)
				# Add comment to request
				request.add_comment("Comment", f"Eligibility check passed with {self.score_percentage:.1f}% score")
			except Exception as e:
				frappe.log_error(f"Failed to update request: {str(e)}")
