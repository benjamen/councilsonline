"""
Configuration Pack Installer for CouncilsOnline

This module handles installation of configuration packs (request types,
assessment templates, etc.) based on region/use case.
"""
import frappe
import json
import os
from pathlib import Path


def get_packs_dir():
	"""Get the path to the packs directory"""
	app_path = frappe.get_app_path("councilsonline")
	return Path(app_path) / "councilsonline" / "fixtures" / "packs"


def get_pack_info(pack_name):
	"""Get pack_info.json for a specific pack"""
	pack_dir = get_packs_dir() / pack_name
	pack_info_file = pack_dir / "pack_info.json"

	if not pack_info_file.exists():
		return None

	with open(pack_info_file) as f:
		return json.load(f)


def install_config_pack(pack_name, force=False):
	"""
	Install a configuration pack by name

	Args:
		pack_name: Name of the pack (e.g., 'nz_resource_consent', 'ph_social_services')
		force: If True, reinstall even if already installed

	Returns:
		bool: True if successful, False otherwise
	"""
	pack_info = get_pack_info(pack_name)

	if not pack_info:
		frappe.log_error(f"Pack '{pack_name}' not found")
		return False

	frappe.log(f"Installing pack: {pack_info.get('display_name', pack_name)}")

	try:
		if pack_name == "base":
			return install_base_pack(force)
		elif pack_name == "nz_resource_consent":
			return install_nz_resource_consent_pack(force)
		elif pack_name == "ph_social_services":
			return install_ph_social_services_pack(force)
		else:
			frappe.log_error(f"Unknown pack: {pack_name}")
			return False

	except Exception as e:
		frappe.log_error(f"Error installing pack '{pack_name}': {str(e)}")
		return False


def install_base_pack(force=False):
	"""Install base infrastructure (roles, workflows, stage types)"""
	from councilsonline.setup.install import (
		install_assessment_stage_types,
	)
	from councilsonline.councilsonline.fixtures.create_roles import create_roles
	from councilsonline.councilsonline.fixtures.create_unified_workflow import create_workflow

	frappe.log("Installing base pack...")

	# Create roles
	frappe.log("  - Creating roles...")
	create_roles()

	# Create workflow
	frappe.log("  - Creating workflow...")
	create_workflow()

	# Install assessment stage types
	frappe.log("  - Installing assessment stage types...")
	install_assessment_stage_types(force=force)

	frappe.log("Base pack installed successfully")
	return True


def install_nz_resource_consent_pack(force=False):
	"""Install New Zealand Resource Consent pack"""
	from councilsonline.setup.install import (
		install_consent_condition_templates,
		install_request_types,
		install_assessment_templates,
		link_assessment_templates_to_request_types,
	)

	frappe.log("Installing NZ Resource Consent pack...")

	# Install consent condition templates
	frappe.log("  - Installing consent condition templates...")
	install_consent_condition_templates(force=force)

	# Install NZ request types
	frappe.log("  - Installing NZ request types...")
	install_request_types(force=force)

	# Install NZ assessment templates
	frappe.log("  - Installing assessment templates...")
	install_assessment_templates(force=force, pack="nz")

	# Link templates to request types
	frappe.log("  - Linking assessment templates...")
	link_assessment_templates_to_request_types(force=force, pack="nz")

	frappe.log("NZ Resource Consent pack installed successfully")
	return True


def install_ph_social_services_pack(force=False):
	"""Install Philippines Social Services pack"""
	from councilsonline.setup.install import (
		install_assessment_templates,
		link_assessment_templates_to_request_types,
	)
	from councilsonline.councilsonline.fixtures.taytay.import_taytay_fixtures import import_fixtures

	frappe.log("Installing PH Social Services pack...")

	# Import SPISC request type and Taytay council
	frappe.log("  - Importing SPISC request type and Taytay council...")
	import_fixtures()

	# Install PH assessment templates
	frappe.log("  - Installing PH assessment templates...")
	install_assessment_templates(force=force, pack="ph")

	# Link templates
	frappe.log("  - Linking assessment templates...")
	link_assessment_templates_to_request_types(force=force, pack="ph")

	# Setup demo users
	frappe.log("  - Setting up demo users...")
	setup_taytay_users()

	frappe.log("PH Social Services pack installed successfully")
	return True


def setup_taytay_users():
	"""Create Taytay admin and demo users"""
	from councilsonline.install import setup_taytay_admin_user, setup_taytay_demo_user

	setup_taytay_admin_user()
	setup_taytay_demo_user()


def install_all_packs(force=False):
	"""Install all available configuration packs"""
	packs_dir = get_packs_dir()
	installed = []

	for pack_dir in packs_dir.iterdir():
		if pack_dir.is_dir() and pack_dir.name not in ["__pycache__", "base"]:
			pack_info_file = pack_dir / "pack_info.json"
			if pack_info_file.exists():
				if install_config_pack(pack_dir.name, force=force):
					installed.append(pack_dir.name)

	return installed


def get_installed_packs():
	"""Get list of installed packs based on what data exists"""
	installed = []

	# Check for NZ pack indicators
	if frappe.db.exists("Request Type", "Land Use Consent - Residential"):
		installed.append("nz_resource_consent")

	# Check for PH pack indicators
	if frappe.db.exists("Request Type", "Social Pension for Indigent Senior Citizens (SPISC)"):
		installed.append("ph_social_services")

	return installed
