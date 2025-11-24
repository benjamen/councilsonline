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
		link_templates_to_request_types
	)

	frappe.log("Installing Consent Condition Templates...")
	install_consent_condition_templates(force=force)

	frappe.log("Installing Request Types...")
	install_request_types(force=force)

	frappe.log("Linking Templates to Request Types...")
	link_templates_to_request_types(force=force)

	frappe.msgprint(
		_("Default configuration data has been installed successfully!"),
		title=_("Installation Complete"),
		indicator="green"
	)
