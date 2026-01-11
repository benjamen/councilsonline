# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Company Account Management API

Handles multi-user company accounts, invitations, and team management.
This module provides endpoints for:
- Company account registration and profile management
- User invitation system with email notifications
- Role-based access control (Admin/Submitter/Viewer)
- Team member management and permissions
"""

import frappe
from frappe import _
from frappe.utils import cint
import secrets
from datetime import datetime


@frappe.whitelist()
def register_company_account(company_data):
	"""
	Register a new company account
	Validates NZBN, creates Company Account doc
	Links creating user as first admin

	Args:
		company_data: dict with company details

	Returns:
		dict: Success message and company account name
	"""
	import json
	if isinstance(company_data, str):
		company_data = json.loads(company_data)

	# Validate required fields
	if not company_data.get("company_name"):
		frappe.throw(_("Company name is required"))
	if not company_data.get("legal_name"):
		frappe.throw(_("Legal name is required"))
	if not company_data.get("primary_email"):
		frappe.throw(_("Primary email is required"))
	if not company_data.get("primary_phone"):
		frappe.throw(_("Primary phone is required"))
	if not company_data.get("registered_office_address"):
		frappe.throw(_("Registered office address is required"))

	# Check if company already exists
	if frappe.db.exists("Company Account", company_data.get("company_name")):
		frappe.throw(_("Company account with this name already exists"))

	# Check NZBN uniqueness if provided
	if company_data.get("nzbn"):
		if frappe.db.exists("Company Account", {"nzbn": company_data.get("nzbn")}):
			frappe.throw(_("Company account with this NZBN already exists"))

	try:
		# Create Company Account
		company = frappe.get_doc({
			"doctype": "Company Account",
			"company_name": company_data.get("company_name"),
			"legal_name": company_data.get("legal_name"),
			"trading_name": company_data.get("trading_name"),
			"company_number": company_data.get("company_number"),
			"nzbn": company_data.get("nzbn"),
			"company_type": company_data.get("company_type", "Limited Liability Company"),
			"registered_office_address": company_data.get("registered_office_address"),
			"postal_address": company_data.get("postal_address"),
			"primary_phone": company_data.get("primary_phone"),
			"primary_email": company_data.get("primary_email"),
			"website": company_data.get("website"),
			"default_council": company_data.get("default_council"),
			"account_status": "Active",
			"admin_users": [{
				"user": frappe.session.user,
				"designation": company_data.get("user_designation", "Director"),
				"can_manage_users": 1,
				"can_manage_billing": 1
			}]
		})
		company.insert()

		# Update current user's company fields
		user = frappe.get_doc("User", frappe.session.user)
		user.company_account = company.name
		user.company_role = "Admin"
		user.save(ignore_permissions=True)

		return {
			"success": True,
			"company_name": company.name,
			"message": _("Company account created successfully")
		}

	except Exception as e:
		frappe.log_error(title="Error creating company account", message=str(e))
		frappe.throw(_("Error creating company account: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def get_user_company_account():
	"""
	Get company account details for current user
	Returns company info + user's role in company

	Returns:
		dict: Company account details or None
	"""
	user = frappe.get_doc("User", frappe.session.user)

	if not hasattr(user, 'company_account') or not user.company_account:
		return None

	try:
		company = frappe.get_doc("Company Account", user.company_account)

		# Get user's role
		user_role = company.get_user_role(frappe.session.user)

		return {
			"name": company.name,
			"company_name": company.company_name,
			"legal_name": company.legal_name,
			"trading_name": company.trading_name,
			"nzbn": company.nzbn,
			"company_number": company.company_number,
			"company_type": company.company_type,
			"primary_email": company.primary_email,
			"primary_phone": company.primary_phone,
			"registered_office_address": company.registered_office_address,
			"postal_address": company.postal_address,
			"website": company.website,
			"default_council": company.default_council,
			"account_status": company.account_status,
			"user_role": user_role,
			"total_applications": company.total_applications,
			"total_payments": company.total_payments
		}

	except frappe.DoesNotExistError:
		# Company was deleted
		if hasattr(user, 'company_account'):
			user.company_account = None
		if hasattr(user, 'company_role'):
			user.company_role = None
		user.save(ignore_permissions=True)
		return None


@frappe.whitelist()
def update_company_account(company_name, updates):
	"""
	Update company account details
	Requires: Admin role in company

	Args:
		company_name: Name of company account
		updates: dict of fields to update

	Returns:
		dict: Success message
	"""
	import json
	if isinstance(updates, str):
		updates = json.loads(updates)

	company = frappe.get_doc("Company Account", company_name)

	# Check permission
	if not company.can_user_perform_action(frappe.session.user, "edit_profile"):
		frappe.throw(_("You do not have permission to edit this company"))

	# Update allowed fields
	allowed_fields = [
		"trading_name", "company_number", "nzbn", "company_type",
		"registered_office_address", "postal_address",
		"primary_phone", "primary_email", "website",
		"bank_name", "bank_account_number", "billing_email",
		"billing_contact", "default_council"
	]

	for field, value in updates.items():
		if field in allowed_fields:
			setattr(company, field, value)

	company.save()

	return {
		"success": True,
		"message": _("Company account updated successfully")
	}


@frappe.whitelist()
def send_company_invitation(company_name, email, role, designation=None):
	"""
	Invite/link a user to company account
	Requires: Admin role with can_manage_users permission

	Args:
		company_name: Name of company account
		email: Email of user to invite
		role: Role to assign (Admin/Submitter/Viewer)
		designation: Optional designation

	Returns:
		dict: Success message and invitation details
	"""
	company = frappe.get_doc("Company Account", company_name)

	# Check permission
	if not company.can_user_perform_action(frappe.session.user, "invite_users"):
		frappe.throw(_("You do not have permission to invite users"))

	# Check if user already exists
	user_exists = frappe.db.exists("User", email)

	# Check if user is already linked
	for admin in company.admin_users:
		if admin.user == email:
			frappe.throw(_("User is already an admin of this company"))

	for linked_user in company.linked_users:
		if linked_user.user == email:
			frappe.throw(_("User is already linked to this company"))

	# Create invitation
	from frappe.utils import random_string, now_datetime, add_days

	invitation = frappe.get_doc({
		"doctype": "Company Invitation",
		"company_account": company_name,
		"invited_user": email,
		"invited_by": frappe.session.user,
		"role": role,
		"status": "Pending",
		"invitation_key": random_string(32),
		"sent_date": now_datetime(),
		"expiry_date": add_days(now_datetime(), 7)
	})
	invitation.insert()

	# Send invitation email
	send_invitation_email(invitation, company, user_exists)

	return {
		"success": True,
		"invitation_key": invitation.invitation_key,
		"message": _("Invitation sent to {0}").format(email)
	}


def send_invitation_email(invitation, company, user_exists):
	"""Send invitation email to user"""
	from frappe.utils import get_url

	subject = _("Invitation to join {0} on Lodgeick").format(company.company_name)

	invitation_url = get_url(f"/accept-invitation/{invitation.invitation_key}")

	if user_exists:
		message = f"""
		<h2>You've been invited to join {company.company_name}</h2>

		<p>You have been invited to join {company.company_name} as a <strong>{invitation.role}</strong>.</p>

		<p><a href="{invitation_url}" style="display: inline-block; padding: 12px 24px; background-color: #2563EB; color: white; text-decoration: none; border-radius: 6px;">Accept Invitation</a></p>

		<p>This invitation will expire in 7 days.</p>

		<p>Invited by: {invitation.invited_by}</p>
		"""
	else:
		message = f"""
		<h2>You've been invited to join {company.company_name} on Lodgeick</h2>

		<p>You have been invited to join {company.company_name} as a <strong>{invitation.role}</strong>.</p>

		<p>Since you don't have a Lodgeick account yet, you'll need to register first, then accept this invitation.</p>

		<p><a href="{invitation_url}" style="display: inline-block; padding: 12px 24px; background-color: #2563EB; color: white; text-decoration: none; border-radius: 6px;">Register & Accept Invitation</a></p>

		<p>This invitation will expire in 7 days.</p>

		<p>Invited by: {invitation.invited_by}</p>
		"""

	frappe.sendmail(
		recipients=[invitation.invited_user],
		subject=subject,
		message=message,
		reference_doctype="Company Invitation",
		reference_name=invitation.name
	)


@frappe.whitelist(allow_guest=True)
def accept_company_invitation(invitation_key):
	"""
	Accept company invitation
	Links user to company with specified role

	Args:
		invitation_key: Unique invitation key

	Returns:
		dict: Success message and company details
	"""
	invitation = frappe.get_doc("Company Invitation", {"invitation_key": invitation_key})

	if invitation.status != "Pending":
		frappe.throw(_("This invitation has already been {0}").format(invitation.status.lower()))

	# Check expiry
	from frappe.utils import now_datetime
	if now_datetime() > invitation.expiry_date:
		invitation.status = "Expired"
		invitation.save(ignore_permissions=True)
		frappe.throw(_("This invitation has expired"))

	# User must be logged in and match invited email
	if frappe.session.user == "Guest":
		frappe.throw(_("Please log in to accept this invitation"))

	if frappe.session.user != invitation.invited_user:
		frappe.throw(_("This invitation was sent to {0}. Please log in with that account.").format(invitation.invited_user))

	# Add user to company
	company = frappe.get_doc("Company Account", invitation.company_account)

	if invitation.role == "Admin":
		company.append("admin_users", {
			"user": invitation.invited_user,
			"can_manage_users": 1,
			"can_manage_billing": 1
		})
	else:
		company.append("linked_users", {
			"user": invitation.invited_user,
			"role": invitation.role,
			"added_by": invitation.invited_by,
			"is_active": 1
		})

	company.save(ignore_permissions=True)

	# Update user's company fields
	user = frappe.get_doc("User", invitation.invited_user)
	user.company_account = company.name
	user.company_role = invitation.role
	user.save(ignore_permissions=True)

	# Update invitation status
	invitation.status = "Accepted"
	invitation.accepted_date = now_datetime()
	invitation.save(ignore_permissions=True)

	return {
		"success": True,
		"company_name": company.company_name,
		"role": invitation.role,
		"message": _("You have joined {0} as a {1}").format(company.company_name, invitation.role)
	}


@frappe.whitelist()
def remove_user_from_company(company_name, user_email):
	"""
	Remove user from company account
	Requires: Admin role with can_manage_users permission

	Args:
		company_name: Name of company account
		user_email: Email of user to remove

	Returns:
		dict: Success message
	"""
	company = frappe.get_doc("Company Account", company_name)

	# Check permission
	if not company.can_user_perform_action(frappe.session.user, "remove_users"):
		frappe.throw(_("You do not have permission to remove users"))

	# Cannot remove self if last admin
	if user_email == frappe.session.user:
		admin_count = len(company.admin_users)
		if admin_count <= 1:
			frappe.throw(_("Cannot remove yourself as you are the only admin"))

	# Remove from admin_users
	for i, admin in enumerate(company.admin_users):
		if admin.user == user_email:
			company.remove(company.admin_users[i])
			break

	# Remove from linked_users
	for i, linked_user in enumerate(company.linked_users):
		if linked_user.user == user_email:
			company.remove(company.linked_users[i])
			break

	company.save()

	# Update user's company fields
	if frappe.db.exists("User", user_email):
		user = frappe.get_doc("User", user_email)
		user.company_account = None
		user.company_role = None
		user.save(ignore_permissions=True)

	return {
		"success": True,
		"message": _("User removed from company")
	}


@frappe.whitelist()
def update_user_company_role(company_name, user_email, new_role):
	"""
	Update user's role and permissions in company
	Requires: Admin role with can_manage_users permission

	Args:
		company_name: Name of company account
		user_email: Email of user
		new_role: New role (Admin/Submitter/Viewer)

	Returns:
		dict: Success message
	"""
	company = frappe.get_doc("Company Account", company_name)

	# Check permission
	if not company.can_user_perform_action(frappe.session.user, "invite_users"):
		frappe.throw(_("You do not have permission to update user roles"))

	# Find and update user
	updated = False

	# Check if in linked_users
	for linked_user in company.linked_users:
		if linked_user.user == user_email:
			linked_user.role = new_role
			updated = True
			break

	if updated:
		company.save()

		# Update user's company_role field
		user = frappe.get_doc("User", user_email)
		user.company_role = new_role
		user.save(ignore_permissions=True)

		return {
			"success": True,
			"message": _("User role updated to {0}").format(new_role)
		}
	else:
		frappe.throw(_("User not found in company"))


@frappe.whitelist()
def get_company_users(company_name):
	"""
	Get all users linked to company with their roles
	Requires: Any company member (read-only for non-admins)

	Args:
		company_name: Name of company account

	Returns:
		list: List of users with roles
	"""
	company = frappe.get_doc("Company Account", company_name)

	# Check if user is member
	user_role = company.get_user_role(frappe.session.user)
	if not user_role:
		frappe.throw(_("You do not have access to this company"))

	users = []

	# Add admin users
	for admin in company.admin_users:
		user_doc = frappe.get_doc("User", admin.user)
		users.append({
			"email": admin.user,
			"full_name": user_doc.full_name,
			"role": "Admin",
			"designation": admin.designation,
			"added_date": admin.added_date,
			"can_manage_users": admin.can_manage_users,
			"can_manage_billing": admin.can_manage_billing,
			"is_active": 1
		})

	# Add linked users
	for linked_user in company.linked_users:
		user_doc = frappe.get_doc("User", linked_user.user)
		users.append({
			"email": linked_user.user,
			"full_name": user_doc.full_name,
			"role": linked_user.role,
			"designation": None,
			"added_date": linked_user.added_date,
			"added_by": linked_user.added_by,
			"is_active": linked_user.is_active
		})

	return users
