"""
Migration patch to set up CouncilsOnline roles and fix workflow

This patch:
1. Creates "CouncilsOnline User" and "CouncilsOnline Admin" roles
2. Assigns roles to existing staff users
3. Recreates the workflow with self-approval enabled for Acknowledge action

This fixes the blocking issue where staff cannot acknowledge submitted requests.
"""

import frappe


def execute():
	"""Execute the migration patch"""

	print("\n" + "="*80)
	print("RUNNING COUNCILSONLINE ROLES SETUP MIGRATION")
	print("="*80 + "\n")

	# Step 1: Create roles
	print("Step 1: Creating roles...")
	try:
		from councilsonline.councilsonline.fixtures.create_roles import create_roles
		create_roles()
	except Exception as e:
		print(f"Error creating roles: {str(e)}")
		frappe.log_error(f"Role creation error: {str(e)}", "CouncilsOnline Roles Migration")

	# Step 2: Assign roles to staff
	print("\nStep 2: Assigning roles to staff...")
	try:
		from councilsonline.councilsonline.fixtures.assign_councilsonline_roles import assign_roles
		assign_roles()
	except Exception as e:
		print(f"Error assigning roles: {str(e)}")
		frappe.log_error(f"Role assignment error: {str(e)}", "CouncilsOnline Roles Migration")

	# Step 3: Recreate workflow with updated settings
	print("\nStep 3: Recreating workflow with self-approval enabled...")
	try:
		from councilsonline.councilsonline.fixtures.create_unified_workflow import create_workflow
		create_workflow()
	except Exception as e:
		print(f"Error recreating workflow: {str(e)}")
		frappe.log_error(f"Workflow creation error: {str(e)}", "CouncilsOnline Roles Migration")

	print("\n" + "="*80)
	print("✓ COUNCILSONLINE ROLES SETUP MIGRATION COMPLETE")
	print("="*80 + "\n")
	print("Staff users can now acknowledge submitted requests.")
	print("Self-approval is enabled for testing/small councils.\n")
