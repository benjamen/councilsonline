"""
Migration script: Exclusion Types - Hardcoded Select → Master DocType

Migrates hardcoded exclusion type dropdown values to master Exclusion Type doctype
and enables all standard types for all councils.
"""

import frappe
from frappe.utils import now_datetime


def execute():
	"""Main migration function"""
	print("\n" + "="*70)
	print("MIGRATION: Exclusion Types - Select → Master DocType")
	print("="*70 + "\n")

	# Step 1: Import Exclusion Type fixtures (if not already imported)
	print("Step 1: Importing Exclusion Type fixtures...")
	import_exclusion_types()

	# Step 2: Enable all standard exclusion types for all councils
	print("\nStep 2: Enabling standard exclusion types for all councils...")
	enable_types_for_councils()

	# Step 3: Migrate existing Clock Exclusion Period values
	print("\nStep 3: Migrating existing Clock Exclusion Period values...")
	migrate_clock_exclusion_periods()

	frappe.db.commit()

	print("\n" + "="*70)
	print("MIGRATION COMPLETE")
	print("="*70)
	print_summary()


def import_exclusion_types():
	"""Import standard exclusion types from fixtures"""
	# Standard exclusion types (matching the old hardcoded values)
	standard_types = [
		{
			"exclusion_type_name": "RFI Issued",
			"exclusion_code": "RFI",
			"is_standard": 1,
			"applies_to_countries": "NZ, AU",
			"legislation_reference": "RMA Section 92",
			"description": "<p>Request for Information (RFI) issued to applicant. Clock stops until response received.</p>",
			"auto_calculate_days": 1,
			"default_duration_days": 20
		},
		{
			"exclusion_type_name": "Section 37",
			"exclusion_code": "S37",
			"is_standard": 1,
			"applies_to_countries": "NZ",
			"legislation_reference": "RMA Section 37",
			"description": "<p>Extension of time limits under RMA Section 37.</p>",
			"auto_calculate_days": 0
		},
		{
			"exclusion_type_name": "Section 91",
			"exclusion_code": "S91",
			"is_standard": 1,
			"applies_to_countries": "NZ",
			"legislation_reference": "RMA Section 91",
			"description": "<p>Request for further information under Section 91.</p>",
			"auto_calculate_days": 1
		},
		{
			"exclusion_type_name": "Section 92",
			"exclusion_code": "S92",
			"is_standard": 1,
			"applies_to_countries": "NZ",
			"legislation_reference": "RMA Section 92",
			"description": "<p>Request for further information under Section 92.</p>",
			"auto_calculate_days": 1,
			"default_duration_days": 20
		},
		{
			"exclusion_type_name": "Notification Period",
			"exclusion_code": "NOTIFY",
			"is_standard": 1,
			"applies_to_countries": "NZ",
			"legislation_reference": "RMA",
			"description": "<p>Public notification period for notified consents.</p>",
			"auto_calculate_days": 0,
			"default_duration_days": 20
		},
		{
			"exclusion_type_name": "Hearing Period",
			"exclusion_code": "HEARING",
			"is_standard": 1,
			"applies_to_countries": "NZ",
			"legislation_reference": "RMA",
			"description": "<p>Time required for hearings and deliberation.</p>",
			"auto_calculate_days": 0
		},
		{
			"exclusion_type_name": "Applicant Delay",
			"exclusion_code": "DELAY",
			"is_standard": 1,
			"applies_to_countries": "",
			"legislation_reference": "",
			"description": "<p>Delays caused by applicant.</p>",
			"auto_calculate_days": 1
		},
		{
			"exclusion_type_name": "Custom",
			"exclusion_code": "CUSTOM",
			"is_standard": 1,
			"applies_to_countries": "",
			"legislation_reference": "",
			"description": "<p>Custom exclusion type for council-specific circumstances.</p>",
			"auto_calculate_days": 0
		}
	]

	created = 0
	skipped = 0

	for type_data in standard_types:
		if not frappe.db.exists("Exclusion Type", type_data["exclusion_type_name"]):
			try:
				exc_type = frappe.get_doc({
					"doctype": "Exclusion Type",
					**type_data
				})
				exc_type.insert(ignore_permissions=True)
				created += 1
				print(f"  ✓ Created: {type_data['exclusion_type_name']}")
			except Exception as e:
				print(f"  ✗ Error creating {type_data['exclusion_type_name']}: {str(e)}")
		else:
			skipped += 1
			print(f"  - Skipped (exists): {type_data['exclusion_type_name']}")

	print(f"\n  Summary: {created} created, {skipped} skipped")


def enable_types_for_councils():
	"""Enable all standard exclusion types for all councils"""
	councils = frappe.get_all("Council", fields=["name"])

	if not councils:
		print("  No councils found - skipping")
		return

	# Get all standard exclusion types
	exclusion_types = frappe.get_all(
		"Exclusion Type",
		filters={"is_standard": 1},
		fields=["name", "exclusion_type_name"]
	)

	if not exclusion_types:
		print("  No standard exclusion types found")
		return

	enabled_count = 0

	for council in councils:
		council_doc = frappe.get_doc("Council", council.name)

		# Clear existing exclusion types (if any)
		council_doc.exclusion_types = []

		# Add all standard exclusion types
		for exc_type in exclusion_types:
			council_doc.append("exclusion_types", {
				"exclusion_type": exc_type.name,
				"request_type": "",  # Blank = all request types
				"is_enabled": 1,
				"requires_approval": 0,
				"max_uses_per_request": 0  # 0 = unlimited
			})
			enabled_count += 1

		council_doc.save(ignore_permissions=True)
		print(f"  ✓ Enabled {len(exclusion_types)} types for: {council.name}")

	print(f"\n  Summary: {enabled_count} total exclusion type assignments created")


def migrate_clock_exclusion_periods():
	"""Migrate existing Clock Exclusion Period values from string to link"""

	# Mapping of old string values to new Exclusion Type names
	mapping = {
		"RFI Issued": "RFI Issued",
		"Section 37": "Section 37",
		"Section 91": "Section 91",
		"Section 92": "Section 92",
		"Notification Period": "Notification Period",
		"Hearing Period": "Hearing Period",
		"Applicant Delay": "Applicant Delay",
		"Custom": "Custom"
	}

	# Get all Clock Exclusion Periods
	exclusions = frappe.db.sql("""
		SELECT name, exclusion_type
		FROM `tabClock Exclusion Period`
	""", as_dict=True)

	if not exclusions:
		print("  No Clock Exclusion Periods found - skipping")
		return

	migrated = 0
	failed = 0
	mapping_errors = []

	for exc in exclusions:
		old_value = exc.exclusion_type
		new_value = mapping.get(old_value)

		if new_value:
			# Check if new value exists
			if frappe.db.exists("Exclusion Type", new_value):
				try:
					frappe.db.set_value(
						"Clock Exclusion Period",
						exc.name,
						"exclusion_type",
						new_value,
						update_modified=False
					)
					migrated += 1
				except Exception as e:
					print(f"  ✗ Error migrating {exc.name}: {str(e)}")
					failed += 1
			else:
				mapping_errors.append(f"{old_value} → {new_value} (target doesn't exist)")
				failed += 1
		else:
			# No mapping found - might already be migrated or custom value
			if frappe.db.exists("Exclusion Type", old_value):
				# Already a valid link - skip
				migrated += 1
			else:
				mapping_errors.append(f"{old_value} → NO MAPPING")
				failed += 1

	print(f"\n  Summary: {migrated} migrated, {failed} failed")

	if mapping_errors:
		print("\n  Mapping errors:")
		for error in mapping_errors[:10]:  # Show first 10
			print(f"    - {error}")


def print_summary():
	"""Print migration summary"""
	exc_type_count = frappe.db.count("Exclusion Type")
	council_count = frappe.db.count("Council")
	council_exc_count = frappe.db.sql("""
		SELECT COUNT(*) as count
		FROM `tabCouncil Exclusion Type`
	""")[0][0]
	clock_exc_count = frappe.db.count("Clock Exclusion Period")

	print(f"""
Summary:
--------
- Exclusion Types created: {exc_type_count}
- Councils configured: {council_count}
- Council Exclusion Type assignments: {council_exc_count}
- Clock Exclusion Periods migrated: {clock_exc_count}

Next Steps:
-----------
1. Review Council → Exclusion Types configuration in each Council form
2. Test creating new Clock Exclusion Periods (should show filtered dropdown)
3. Verify existing Clock Exclusion Periods display correctly
	""")


if __name__ == "__main__":
	execute()
