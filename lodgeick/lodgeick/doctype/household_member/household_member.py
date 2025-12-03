# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from datetime import datetime


class HouseholdMember(Document):
	def validate(self):
		"""Calculate age and auto-set senior citizen flag"""
		if self.birth_date:
			# Calculate age
			today = getdate(nowdate())
			birth = getdate(self.birth_date)
			age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
			self.age = age

			# Auto-set senior citizen flag
			self.is_senior_citizen = 1 if age >= 60 else 0
