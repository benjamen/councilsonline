"""
Migration patch to convert Council from multi-instance to Single DocType.
This patch preserves TAYTAY-PH council data and removes all other councils.
"""

import frappe
from frappe.model.utils import sync_field_order_in_db


def execute():
	"""Convert Council from multi-instance to Single DocType"""

	frappe.log("Starting Council to Single DocType conversion...")

	# 1. Get TayTay Council data before deletion
	taytay_name = frappe.db.get_value("Council", {"council_code": "TAYTAY-PH"}, "name")

	if not taytay_name:
		frappe.log_error("TAYTAY-PH council not found! Cannot proceed with migration.")
		return

	# Get full council data including child tables
	taytay_council = frappe.get_doc("Council", taytay_name)
	council_data = taytay_council.as_dict()

	# Store child table data separately
	enabled_request_types = council_data.get("enabled_request_types", [])
	business_hours = council_data.get("business_hours", [])
	exclusion_types = council_data.get("exclusion_types", [])
	payment_accounts = council_data.get("payment_accounts", [])

	frappe.log(f"Backing up TAYTAY-PH council: {council_data.get('council_name')}")
	frappe.log(f"- {len(enabled_request_types)} request types")
	frappe.log(f"- {len(business_hours)} business hour records")
	frappe.log(f"- {len(exclusion_types)} exclusion types")
	frappe.log(f"- {len(payment_accounts)} payment accounts")

	# 2. Delete ALL councils (including TayTay)
	# This must happen before the DocType sync converts Council to Single
	frappe.log("Deleting all council records...")

	# Delete child table records first
	for child_table in ["Council Request Type", "Council Business Hours",
	                    "Council Exclusion Type", "Council Payment Account"]:
		frappe.db.sql(f"DELETE FROM `tab{child_table}`")

	# Delete parent council records
	frappe.db.sql("DELETE FROM `tabCouncil`")
	frappe.db.commit()

	frappe.log("All council records deleted")

	# 3. The DocType sync (model_sync) happens automatically by Frappe
	# after this patch runs. It will convert Council to Single DocType
	# based on the updated council.json (issingle: 1)

	# 4. After sync, recreate TayTay as Single
	# We need to manually create the Single instance
	frappe.log("Creating Council Single DocType with TAYTAY-PH data...")

	# For Single DocTypes, the 'name' field is always 'Council'
	single_doc = frappe.new_doc("Council")

	# Set all scalar fields
	excluded_fields = ['name', 'doctype', 'creation', 'modified', 'modified_by',
	                   'owner', 'docstatus', 'idx', 'enabled_request_types',
	                   'business_hours', 'exclusion_types', 'payment_accounts']

	for key, value in council_data.items():
		if key not in excluded_fields and value is not None:
			single_doc.set(key, value)

	# Set child tables
	for rt in enabled_request_types:
		single_doc.append("enabled_request_types", {
			"request_type": rt.get("request_type"),
			"is_enabled": rt.get("is_enabled", 1),
			"custom_label": rt.get("custom_label"),
			"description": rt.get("description"),
			"override_fee_amount": rt.get("override_fee_amount"),
			"override_sla_days": rt.get("override_sla_days"),
		})

	for bh in business_hours:
		single_doc.append("business_hours", {
			"day_of_week": bh.get("day_of_week"),
			"is_working_day": bh.get("is_working_day", 1),
			"start_time": bh.get("start_time"),
			"end_time": bh.get("end_time"),
		})

	for et in exclusion_types:
		single_doc.append("exclusion_types", {
			"exclusion_type": et.get("exclusion_type"),
			"applies_to_request_type": et.get("applies_to_request_type"),
			"is_enabled": et.get("is_enabled", 1),
		})

	for pa in payment_accounts:
		single_doc.append("payment_accounts", {
			"account_name": pa.get("account_name"),
			"account_number": pa.get("account_number"),
			"bank_name": pa.get("bank_name"),
			"account_type": pa.get("account_type"),
			"is_active": pa.get("is_active", 1),
		})

	# Insert/Save the Single instance
	single_doc.insert(ignore_permissions=True)
	frappe.db.commit()

	frappe.log("✓ Council Single DocType created successfully")
	frappe.log(f"✓ Council Code: {single_doc.council_code}")
	frappe.log(f"✓ Council Name: {single_doc.council_name}")

	print("=" * 80)
	print("MIGRATION COMPLETE: Council converted to Single DocType")
	print(f"Preserved council: {single_doc.council_name} ({single_doc.council_code})")
	print("All other councils have been removed")
	print("=" * 80)
