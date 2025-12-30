# Copyright (c) 2025, Hohmesy and contributors
# For license information, please see license.txt

"""
Installation and configuration data setup for Lodgeick
This module handles default data installation for Request Types, Condition Templates, etc.
"""

import frappe
from frappe import _


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

	# Note: Condition template linking skipped - Request Type schema doesn't support it yet
	# This feature may be added in a future version

	frappe.msgprint(
		_("Default configuration data has been installed successfully!"),
		title=_("Installation Complete"),
		indicator="green"
	)
