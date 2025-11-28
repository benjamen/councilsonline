# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CompanyAccount(Document):
	def validate(self):
		"""Validate company account before saving"""
		# Validate NZBN format if provided
		if self.nzbn and not self.is_valid_nzbn(self.nzbn):
			frappe.throw("Invalid NZBN format. NZBN must be 13 digits.")

		# Ensure at least one admin user
		if not self.admin_users:
			frappe.throw("Company account must have at least one admin user")

		# Set billing contact to first admin if not set
		if not self.billing_contact and self.admin_users:
			self.billing_contact = self.admin_users[0].user

	def is_valid_nzbn(self, nzbn):
		"""Validate NZBN format (13 digits)"""
		import re
		return bool(re.match(r'^\d{13}$', nzbn.replace(' ', '')))

	def get_user_role(self, user):
		"""Get user's role in this company"""
		# Check admin table
		for admin in self.admin_users:
			if admin.user == user:
				return "Admin"

		# Check linked users table
		for linked_user in self.linked_users:
			if linked_user.user == user and linked_user.is_active:
				return linked_user.role

		return None

	def can_user_perform_action(self, user, action):
		"""Check if user can perform specific action"""
		role = self.get_user_role(user)
		if not role:
			return False

		PERMISSION_MATRIX = {
			"view_profile": ["Admin", "Submitter", "Viewer"],
			"edit_profile": ["Admin"],
			"create_application": ["Admin", "Submitter"],
			"edit_application": ["Admin", "Submitter"],
			"submit_application": ["Admin", "Submitter"],
			"cancel_application": ["Admin"],
			"invite_users": ["Admin"],
			"remove_users": ["Admin"],
			"manage_billing": ["Admin"],
		}

		return role in PERMISSION_MATRIX.get(action, [])

	def update_totals(self):
		"""Update total applications and payments"""
		# Count applications
		self.total_applications = frappe.db.count(
			"Request",
			filters={"company_account": self.name}
		)

		# Sum payments
		total = frappe.db.sql("""
			SELECT SUM(total_fees_incl_gst)
			FROM `tabRequest`
			WHERE company_account = %s
			AND payment_status = 'Paid'
		""", (self.name,))

		self.total_payments = total[0][0] if total and total[0][0] else 0


def has_permission(doc, ptype=None, user=None):
	"""Custom permission logic for Company Account"""
	if not user:
		user = frappe.session.user

	# System Manager has all permissions
	if frappe.db.get_value("User", user, "name") == "Administrator" or \
	   "System Manager" in frappe.get_roles(user):
		return True

	# Check if user is admin
	for admin in doc.admin_users:
		if admin.user == user:
			return True

	# Check if user is linked user
	for linked_user in doc.linked_users:
		if linked_user.user == user and linked_user.is_active:
			if ptype in ["read", "write"]:
				return True
			elif ptype == "delete" and linked_user.role == "Admin":
				return True

	return False
