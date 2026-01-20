"""
Drop council link fields from Request and Council Meeting tables.
These fields are no longer needed since Council is now a Single DocType.
"""

import frappe


def execute():
	"""Drop council columns from database tables"""

	frappe.log("Dropping council fields from tables...")

	# List of tables and their council columns to drop
	tables_to_update = [
		("tabRequest", "council"),
		("tabCouncil Meeting", "council"),
		("tabLogin Event", "council"),
		("tabPayout Batch", "council"),
	]

	for table_name, column_name in tables_to_update:
		# Check if column exists
		column_exists = frappe.db.sql("""
			SELECT COLUMN_NAME
			FROM INFORMATION_SCHEMA.COLUMNS
			WHERE TABLE_SCHEMA = DATABASE()
			AND TABLE_NAME = %s
			AND COLUMN_NAME = %s
		""", (table_name, column_name))

		if column_exists:
			frappe.log(f"Dropping column '{column_name}' from {table_name}")
			frappe.db.sql(f"ALTER TABLE `{table_name}` DROP COLUMN `{column_name}`")
			frappe.log(f"✓ Dropped {column_name} from {table_name}")
		else:
			frappe.log(f"Column '{column_name}' not found in {table_name} (already dropped)")

	frappe.db.commit()

	print("=" * 80)
	print("MIGRATION COMPLETE: Council fields dropped from all tables")
	print("=" * 80)
