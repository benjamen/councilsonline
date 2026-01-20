# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class RoleRate(Document):
	def validate(self):
		"""Validation before saving"""
		# Ensure effective_from is before effective_to
		if self.effective_to and self.effective_from:
			if getdate(self.effective_to) < getdate(self.effective_from):
				frappe.throw("Effective To date cannot be before Effective From date")


@frappe.whitelist()
def get_hourly_rate(role, date=None):
	"""Get hourly rate for a role on a specific date"""
	if not date:
		date = frappe.utils.today()

	# Find active role rate for the given date
	role_rate = frappe.db.get_value(
		"Role Rate",
		filters={
			"role": role,
			"is_active": 1,
			"effective_from": ["<=", date],
		},
		fieldname=["hourly_rate", "cost_rate"],
		order_by="effective_from desc"
	)

	if role_rate:
		return {
			"hourly_rate": role_rate[0],
			"cost_rate": role_rate[1]
		}

	return {"hourly_rate": 0, "cost_rate": 0}
