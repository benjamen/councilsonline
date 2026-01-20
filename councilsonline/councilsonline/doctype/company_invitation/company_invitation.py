# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_days, random_string


class CompanyInvitation(Document):
	def before_insert(self):
		"""Generate invitation key and set expiry"""
		if not self.invitation_key:
			self.invitation_key = random_string(32)

		if not self.sent_date:
			self.sent_date = now_datetime()

		if not self.expiry_date:
			# Expire in 7 days
			self.expiry_date = add_days(self.sent_date, 7)

	def send_invitation_email(self):
		"""Send invitation email to user"""
		# Email implementation will be added with API endpoints
		pass
