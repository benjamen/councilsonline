# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Application → Request Bidirectional Sync Utility

Provides standardized event-driven sync mechanism for updating Request
display fields when Application data changes.

Usage:
    from lodgeick.utils.application_sync import sync_to_request

    class MyApplication(Document):
        def on_update(self):
            sync_to_request(self)
"""

import frappe
from frappe import _


def sync_to_request(application_doc, sync_config=None):
	"""
	Sync Application data to parent Request display fields

	Args:
		application_doc: Application Document instance (SPISC, RC, BC, etc.)
		sync_config: Optional dict with sync rules. If not provided, uses default mapping.
			Example:
			{
				"property_address": lambda doc: doc.get_display_address(),
				"brief_description": lambda doc: doc.get_display_description(),
				"requester_name": "applicant_full_name"  # Direct field mapping
			}

	Returns:
		bool: True if sync successful, False otherwise
	"""
	try:
		# Validate that application has a parent request
		if not hasattr(application_doc, 'request') or not application_doc.request:
			frappe.log_error("Application doc has no parent Request", "Application Sync")
			return False

		# Check if Request exists
		if not frappe.db.exists("Request", application_doc.request):
			frappe.log_error(f"Request {application_doc.request} not found", "Application Sync")
			return False

		# Get Request document
		request = frappe.get_doc("Request", application_doc.request)

		# Use provided sync_config or default
		if not sync_config:
			sync_config = get_default_sync_config(application_doc)

		# Track if any updates were made
		updates_made = False

		# Apply sync rules
		for request_field, mapping in sync_config.items():
			try:
				# Get new value based on mapping type
				if callable(mapping):
					# Lambda/function mapping
					new_value = mapping(application_doc)
				elif isinstance(mapping, str):
					# Direct field name mapping
					new_value = getattr(application_doc, mapping, None)
				else:
					frappe.log_error(f"Invalid sync mapping for {request_field}: {mapping}", "Application Sync")
					continue

				# Get current value
				current_value = getattr(request, request_field, None)

				# Only update if value changed
				if new_value and new_value != current_value:
					request.db_set(request_field, new_value, update_modified=False)
					updates_made = True
					frappe.logger().info(f"Synced {request_field} to Request {request.name}: {new_value}")

			except Exception as e:
				frappe.log_error(f"Error syncing {request_field}: {str(e)}", "Application Sync")
				continue

		if updates_made:
			frappe.db.commit()

		return True

	except Exception as e:
		frappe.log_error(f"Application Sync Error: {str(e)}", "Application Sync")
		return False


def get_default_sync_config(application_doc):
	"""
	Get default sync configuration based on Application DocType

	Args:
		application_doc: Application Document instance

	Returns:
		dict: Sync configuration mapping
	"""
	doctype = application_doc.doctype

	# SPISC Application
	if doctype == "SPISC Application":
		return {
			"property_address": lambda doc: get_spisc_address(doc),
			"brief_description": lambda doc: get_spisc_description(doc)
		}

	# Resource Consent Application
	elif doctype == "Resource Consent Application":
		return {
			"brief_description": lambda doc: get_resource_consent_description(doc)
		}

	# Building Consent Application
	elif doctype == "Building Consent Application":
		return {
			"brief_description": lambda doc: get_building_consent_description(doc)
		}

	# Default: no sync
	else:
		return {}


# ============================================================================
# Application-Specific Display Logic
# ============================================================================

def get_spisc_address(doc):
	"""Build display address for SPISC Application"""
	address_parts = [
		doc.barangay,
		doc.municipality,
		doc.province
	]
	return ", ".join(filter(None, address_parts))


def get_spisc_description(doc):
	"""Build brief description for SPISC Application"""
	# Get applicant name from parent Request
	applicant_name = "Unknown"
	if doc.request:
		applicant_name = frappe.db.get_value("Request", doc.request, "requester_name") or "Unknown"

	desc = f"{applicant_name} - SPISC Application"
	if doc.age:
		desc += f" (Age: {doc.age})"
	return desc


def get_resource_consent_description(doc):
	"""Build brief description for Resource Consent Application"""
	# Get applicant name from parent Request
	applicant_name = "Unknown"
	if doc.request:
		applicant_name = frappe.db.get_value("Request", doc.request, "requester_name") or "Unknown"

	desc = f"{applicant_name} - Resource Consent"

	# Add activity status if available
	if hasattr(doc, 'activity_status') and doc.activity_status:
		desc += f" ({doc.activity_status})"

	# Add consent type if available
	if hasattr(doc, 'consent_types') and doc.consent_types:
		consent_type_list = [ct.consent_type for ct in doc.consent_types if ct.consent_type]
		if consent_type_list:
			desc += f" - {', '.join(consent_type_list[:2])}"  # Show first 2 types

	return desc


def get_building_consent_description(doc):
	"""Build brief description for Building Consent Application"""
	# Get applicant name from parent Request
	applicant_name = "Unknown"
	if doc.request:
		applicant_name = frappe.db.get_value("Request", doc.request, "requester_name") or "Unknown"

	desc = f"{applicant_name} - Building Consent"

	# Add building work type if available
	if hasattr(doc, 'building_work_type') and doc.building_work_type:
		desc += f" ({doc.building_work_type})"

	return desc


# ============================================================================
# Event Hooks - Called from DocType hooks
# ============================================================================

def on_application_insert(doc, method=None):
	"""
	Hook called on Application after_insert
	Syncs initial data to Request
	"""
	sync_to_request(doc)


def on_application_update(doc, method=None):
	"""
	Hook called on Application on_update
	Syncs changed data to Request
	"""
	sync_to_request(doc)
