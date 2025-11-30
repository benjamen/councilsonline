# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RequestConsentTypeDuration(Document):
	"""Child table for storing duration details per consent type."""

	def validate(self):
		"""Validate duration based on consent type and RMA requirements."""
		# s.123 RMA: WP, DP, CP have max 35 years
		# LUC and SC can be unlimited
		max_duration_types = ["Discharge Permit", "Water Permit", "Coastal Permit"]

		if self.consent_type in max_duration_types:
			if self.duration_unlimited:
				frappe.throw(
					f"{self.consent_type} cannot have unlimited duration. "
					f"Maximum is 35 years per s.123 RMA."
				)
			if self.duration_years and self.duration_years > 35:
				frappe.throw(
					f"{self.consent_type} duration cannot exceed 35 years per s.123 RMA."
				)

		# Ensure either duration_years or duration_unlimited is set
		if not self.duration_unlimited and not self.duration_years:
			frappe.throw(
				f"Please specify either a duration in years or select unlimited duration "
				f"for {self.consent_type}."
			)
