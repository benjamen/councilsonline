# Copyright (c) 2025, Hohmesy and contributors
# For license information, please see license.txt

"""
Installation and configuration data setup for CouncilsOnline
This module handles default data installation for Request Types, Condition Templates, etc.
"""

import frappe
from frappe import _


def setup_taytay_admin_user():
	"""
	Create or update Taytay admin user with appropriate roles.
	This user has access to council management features but not full admin access.
	"""
	user_email = "taytay-admin@councilsonline.localhost"

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
		"CouncilsOnline Admin",
		"CouncilsOnline Manager",
		"CouncilsOnline User",
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
	user_email = "taytay-demo@councilsonline.localhost"

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
		"CouncilsOnline User",
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


def setup_payments_team():
	"""
	Create PAYMENTS team for cash pickup scheduling.
	"""
	if not frappe.db.exists('Council Team', 'PAYMENTS'):
		team = frappe.get_doc({
			'doctype': 'Council Team',
			'team_code': 'PAYMENTS',
			'team_name': 'Payments Team',
			'description': 'Handles cash pickup appointments',
			'is_active': 1,
			'enable_scheduling': 1,
			'default_appointment_duration': 15,
			'available_appointment_durations': '15,30',
			'appointment_buffer_time': 10,
			'max_daily_appointments': 50,
			'advance_booking_days': 30,
			'min_notice_hours': 24,
			'default_location': 'Municipal Treasury Office',
			'available_locations': 'Municipal Treasury Office',
			'business_hours': []
		})

		# Add business hours (Monday-Friday 8am-5pm)
		for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
			team.append('business_hours', {
				'day_of_week': day,
				'is_open': 1,
				'start_time': '08:00:00',
				'end_time': '17:00:00'
			})
		team.insert(ignore_permissions=True)
		frappe.log(f"Created PAYMENTS team for cash pickup scheduling")
	else:
		frappe.log("PAYMENTS team already exists")


def after_install():
	"""
	Called automatically after app installation.
	Installs BASE infrastructure only - region-specific data via config packs.
	"""
	frappe.log("Starting CouncilsOnline base installation...")

	# Always setup PAYMENTS team first (no dependencies)
	try:
		frappe.log("Setting up PAYMENTS team...")
		setup_payments_team()
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Error creating PAYMENTS team: {str(e)}")

	try:
		install_base_infrastructure()
		frappe.db.commit()
		frappe.log("✓ CouncilsOnline base installation completed")

		# Print instructions for adding region-specific data
		frappe.msgprint(
			_("""<b>Base installation complete!</b><br><br>
			To add region-specific configuration, run one of:<br>
			<code>bench --site {site} install-config-packs --pack nz_resource_consent</code><br>
			<code>bench --site {site} install-config-packs --pack ph_social_services</code><br><br>
			Or use interactive mode:<br>
			<code>bench --site {site} install-config-packs</code><br><br>
			You can also select packs during the Setup Wizard.""").format(site=frappe.local.site),
			title=_("Installation Complete"),
			indicator="green"
		)
	except Exception as e:
		frappe.log_error(f"Error during CouncilsOnline installation: {str(e)}")
		frappe.db.rollback()
		raise


def install_base_infrastructure(force=False):
	"""
	Install base infrastructure (roles, workflows, stage types).
	Region-specific data is installed via configuration packs.

	Args:
		force (bool): If True, reinstall even if data exists
	"""
	from councilsonline.setup.install import install_assessment_stage_types
	from councilsonline.councilsonline.fixtures.create_roles import create_roles
	from councilsonline.councilsonline.fixtures.create_unified_workflow import create_workflow

	# Create roles
	frappe.log("Creating CouncilsOnline roles...")
	create_roles()

	# Create workflow
	frappe.log("Creating Request workflow...")
	create_workflow()

	# Install assessment stage types (base infrastructure)
	frappe.log("Installing Assessment Stage Types...")
	install_assessment_stage_types(force=force)

	frappe.log("Base infrastructure installed. Use 'bench install-config-packs' for region-specific data.")


def install_default_data(force=False):
	"""
	DEPRECATED: Use configuration packs instead.

	Install all default configuration data (legacy function for backward compatibility).
	For new installations, use:
		bench --site <site> install-config-packs --all

	Args:
		force (bool): If True, reinstall even if data exists
	"""
	frappe.log("WARNING: install_default_data is deprecated. Use config packs instead.")

	# Install base first
	install_base_infrastructure(force=force)

	# Install all packs for backward compatibility
	from councilsonline.setup.pack_installer import install_config_pack
	install_config_pack("nz_resource_consent", force=force)
	install_config_pack("ph_social_services", force=force)

	frappe.msgprint(
		_("Default configuration data has been installed successfully!"),
		title=_("Installation Complete"),
		indicator="green"
	)
