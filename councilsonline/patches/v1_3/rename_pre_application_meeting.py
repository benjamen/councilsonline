"""
Patch to rename Pre-Application Meeting to Council Meeting
"""

import frappe
from frappe.model.rename_doc import rename_doc


def execute():
	"""Rename Pre-Application Meeting DocType to Council Meeting"""

	# Check if old DocType exists
	if frappe.db.exists("DocType", "Pre-Application Meeting"):
		print("Renaming Pre-Application Meeting to Council Meeting...")

		try:
			# Rename the DocType
			rename_doc(
				"DocType",
				"Pre-Application Meeting",
				"Council Meeting",
				force=True,
				merge=False
			)

			print("✓ Successfully renamed to Council Meeting")

		except Exception as e:
			print(f"Error renaming DocType: {str(e)}")
			# If rename fails, it might already be renamed
			if frappe.db.exists("DocType", "Council Meeting"):
				print("Council Meeting already exists - skipping rename")
			else:
				raise

	elif frappe.db.exists("DocType", "Council Meeting"):
		print("Council Meeting already exists - no rename needed")

	else:
		print("Neither Pre-Application Meeting nor Council Meeting exists - will be created on migrate")

	frappe.db.commit()
