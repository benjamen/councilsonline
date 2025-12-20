#!/usr/bin/env python3
"""
Create required Lodgeick roles

This script creates the "Lodgeick User" and "Lodgeick Admin" roles that are
required by the Request workflow but may not exist in the system.

Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.create_roles.create_roles
"""

import frappe


def create_roles():
	"""Create Lodgeick User and Lodgeick Admin roles if they don't exist"""

	roles = [
		{
			"role_name": "Lodgeick User",
			"description": "Standard council staff user - can process requests, issue RFIs, manage assessments"
		},
		{
			"role_name": "Lodgeick Admin",
			"description": "Council manager - can approve/decline requests, manage team assignments"
		}
	]

	print("\n" + "="*80)
	print("CREATING LODGEICK ROLES")
	print("="*80 + "\n")

	for role_data in roles:
		role_name = role_data["role_name"]

		if frappe.db.exists("Role", role_name):
			print(f"⊘ Role already exists: {role_name}")
		else:
			role = frappe.get_doc({
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": 1,
				"description": role_data.get("description", "")
			})
			role.insert(ignore_permissions=True)
			print(f"✓ Created role: {role_name}")
			print(f"  Description: {role_data.get('description', '')}")

	frappe.db.commit()
	print("\n✓ Roles setup complete\n")


if __name__ == "__main__":
	create_roles()
