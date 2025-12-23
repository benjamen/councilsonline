"""
Migration patch to clean up old multi-instance Council records.
This runs after Council DocType is converted to Single (issingle: 1).
TayTay Council data will be loaded from fixtures.
"""

import frappe


def execute():
	"""Delete old multi-instance council records"""

	frappe.log("Cleaning up old multi-instance Council records...")

	# Delete old child table records from multi-instance councils
	for child_table in ["Council Request Type", "Council Business Hours",
	                    "Council Exclusion Type", "Council Payment Account"]:
		# Get count before deletion
		count = frappe.db.count(child_table)
		if count > 0:
			frappe.log(f"Deleting {count} records from {child_table}")
			frappe.db.sql(f"DELETE FROM `tab{child_table}` WHERE parent != 'Council'")

	# Delete all multi-instance council records (keep only the Single instance)
	# The Single instance will have name='Council', all others are old multi-instance
	deleted = frappe.db.sql("""
		DELETE FROM `tabCouncil`
		WHERE name != 'Council'
	""")

	frappe.db.commit()

	frappe.log(f"✓ Deleted {deleted[0][0] if deleted else 0} old council records")
	frappe.log("✓ Council is now Single DocType")
	frappe.log("✓ TayTay Council data will be loaded from fixtures")

	print("=" * 80)
	print("MIGRATION COMPLETE: Old council records cleaned up")
	print("Council is now a Single DocType")
	print("TayTay Council data loading from fixtures...")
	print("=" * 80)
