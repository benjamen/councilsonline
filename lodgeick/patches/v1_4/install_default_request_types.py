# Copyright (c) 2025, Hohmesy and contributors
# For license information, please see license.txt

"""
Patch to ensure default request types and condition templates are installed
This runs during deployment/update to ensure all sites have the latest request type configuration
"""

import frappe
from frappe import _


def execute():
	"""
	Install or update default request types and condition templates
	"""
	frappe.log("v1.4: Installing default request types and condition templates...")

	try:
		from lodgeick.setup.install import (
			install_consent_condition_templates,
			install_request_types,
			link_templates_to_request_types
		)

		# Install/update with force=True to ensure latest configurations
		template_count = install_consent_condition_templates(force=False)
		rt_count = install_request_types(force=False)
		link_count = link_templates_to_request_types(force=False)

		frappe.db.commit()

		frappe.log(f"✓ Installed {template_count} consent condition templates")
		frappe.log(f"✓ Installed {rt_count} request types")
		frappe.log(f"✓ Created {link_count} template links")
		frappe.log("✓ Default request types installation completed")

	except Exception as e:
		frappe.log_error(f"Error installing default request types: {str(e)}")
		# Don't raise - allow migration to continue even if this fails
		frappe.log(f"⚠ Warning: Default request types installation failed: {str(e)}")
