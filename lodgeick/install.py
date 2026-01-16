# Copyright (c) 2025, Hohmesy and contributors
# For license information, please see license.txt

"""
Installation and configuration data setup for Lodgeick
This module handles default data installation for Request Types, Condition Templates, etc.
"""

import frappe
from frappe import _


def setup_taytay_admin_user():
	"""
	Create or update Taytay admin user with appropriate roles.
	This user has access to council management features but not full admin access.
	"""
	user_email = "taytay-admin@lodgeick.localhost"

	if not frappe.db.exists("User", user_email):
		user = frappe.get_doc({
			"doctype": "User",
			"email": user_email,
			"first_name": "Taytay",
			"last_name": "Admin",
			"enabled": 1,
			"user_type": "System User",
			"send_welcome_email": 0
		})
		user.insert(ignore_permissions=True)
		frappe.log(f"Created user: {user_email}")
	else:
		user = frappe.get_doc("User", user_email)
		user.enabled = 1
		frappe.log(f"User {user_email} already exists, updating roles")

	# Define roles for Taytay admin
	roles = [
		"Council Admin",
		"Council Manager",
		"Council Staff",
		"Lodgeick Admin",
		"Lodgeick Manager",
		"Lodgeick User",
		"Desk User",
		"Report Manager",
		"System Manager",
		"Workspace Manager"
	]

	# Clear existing roles and add new ones
	user.roles = []
	for role in roles:
		if frappe.db.exists("Role", role):
			user.append("roles", {"role": role})

	user.save(ignore_permissions=True)

	# Set default password (user should change on first login)
	from frappe.utils.password import update_password
	update_password(user_email, "Taytay@Council2025!")

	frappe.log(f"Taytay admin user configured with {len(user.roles)} roles")


def setup_taytay_demo_user():
	"""
	Create or update Taytay demo user with limited roles.
	This user has access to dashboard and request management only.
	"""
	user_email = "taytay-demo@lodgeick.localhost"

	if not frappe.db.exists("User", user_email):
		user = frappe.get_doc({
			"doctype": "User",
			"email": user_email,
			"first_name": "Taytay",
			"last_name": "Demo",
			"enabled": 1,
			"user_type": "System User",
			"send_welcome_email": 0
		})
		user.insert(ignore_permissions=True)
		frappe.log(f"Created user: {user_email}")
	else:
		user = frappe.get_doc("User", user_email)
		user.enabled = 1
		frappe.log(f"User {user_email} already exists, updating roles")

	# Limited roles for demo user - dashboard and request management only
	roles = [
		"Council Staff",
		"Lodgeick User",
		"Desk User"
	]

	# Clear existing roles and add new ones
	user.roles = []
	for role in roles:
		if frappe.db.exists("Role", role):
			user.append("roles", {"role": role})

	user.save(ignore_permissions=True)

	# Set default password
	from frappe.utils.password import update_password
	update_password(user_email, "TaytayDemo2025")

	frappe.log(f"Taytay demo user configured with {len(user.roles)} roles")


def after_install():
	"""
	Called automatically after app installation.
	Sets up default configuration data.
	"""
	frappe.log("Starting Lodgeick default data installation...")

	try:
		install_default_data()
		frappe.db.commit()
		frappe.log("✓ Lodgeick default data installation completed successfully")
	except Exception as e:
		frappe.log_error(f"Error during Lodgeick installation: {str(e)}")
		frappe.db.rollback()
		raise


def install_default_data(force=False):
	"""
	Install all default configuration data.

	Args:
		force (bool): If True, reinstall even if data exists
	"""
	from lodgeick.setup.install import (
		install_consent_condition_templates,
		install_request_types,
		install_assessment_templates,
		link_assessment_templates_to_request_types
	)

	frappe.log("Installing Consent Condition Templates...")
	install_consent_condition_templates(force=force)

	frappe.log("Installing Request Types...")
	install_request_types(force=force)

	frappe.log("Installing Assessment Templates...")
	install_assessment_templates(force=force)

	frappe.log("Linking Assessment Templates to Request Types...")
	link_assessment_templates_to_request_types(force=force)

	# Install SPISC and Taytay Council
	frappe.log("Installing SPISC Request Type and Taytay Council...")
	from lodgeick.lodgeick.fixtures.taytay.import_taytay_fixtures import import_fixtures as import_taytay
	import_taytay()

	# Create roles
	frappe.log("Creating Lodgeick roles...")
	from lodgeick.lodgeick.fixtures.create_roles import create_roles
	create_roles()

	# Create workflow
	frappe.log("Creating Request workflow...")
	from lodgeick.lodgeick.fixtures.create_unified_workflow import create_workflow
	create_workflow()

	# Setup Taytay admin user
	frappe.log("Setting up Taytay admin user...")
	setup_taytay_admin_user()

	# Setup Taytay demo user (limited access)
	frappe.log("Setting up Taytay demo user...")
	setup_taytay_demo_user()

	# Note: Condition template linking skipped - Request Type schema doesn't support it yet
	# This feature may be added in a future version

	frappe.msgprint(
		_("Default configuration data has been installed successfully!"),
		title=_("Installation Complete"),
		indicator="green"
	)
