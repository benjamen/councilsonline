#!/usr/bin/env python3
"""
Assign CouncilsOnline roles to staff users

This script assigns "CouncilsOnline User" role to users who have "Planner" or "Manager" roles,
and assigns "CouncilsOnline Admin" role to users with "Manager" role.

Run with: bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.assign_councilsonline_roles.assign_roles
"""

import frappe


def assign_roles():
	"""Assign CouncilsOnline User role to users with Planner/Manager roles"""

	print("\n" + "="*80)
	print("ASSIGNING COUNCILSONLINE ROLES TO STAFF USERS")
	print("="*80 + "\n")

	# Find users with Planner or Manager role
	users_with_planner = frappe.get_all(
		"Has Role",
		filters={"role": "Planner"},
		fields=["parent"],
		distinct=True
	)

	users_with_manager = frappe.get_all(
		"Has Role",
		filters={"role": "Manager"},
		fields=["parent"],
		distinct=True
	)

	# Combine and deduplicate
	all_users = set([u.parent for u in users_with_planner + users_with_manager])

	# Filter out system users and disabled users
	valid_users = []
	for username in all_users:
		if not frappe.db.exists("User", username):
			continue

		user_type = frappe.db.get_value("User", username, "user_type")
		enabled = frappe.db.get_value("User", username, "enabled")

		if user_type == "System User" and enabled:
			valid_users.append(username)

	print(f"Found {len(valid_users)} staff users to update")
	print(f"Users: {', '.join(valid_users)}\n")

	if not valid_users:
		print("No staff users found to update.")
		print("Make sure you have users with 'Planner' or 'Manager' role.")
		return

	for username in valid_users:
		user = frappe.get_doc("User", username)
		updated = False

		# Add CouncilsOnline User role if not present
		if not any(r.role == "CouncilsOnline User" for r in user.roles):
			user.append("roles", {"role": "CouncilsOnline User"})
			print(f"  + Added 'CouncilsOnline User' to {username}")
			updated = True

		# Add CouncilsOnline Admin role to Managers
		if any(r.role == "Manager" for r in user.roles):
			if not any(r.role == "CouncilsOnline Admin" for r in user.roles):
				user.append("roles", {"role": "CouncilsOnline Admin"})
				print(f"  + Added 'CouncilsOnline Admin' to {username}")
				updated = True

		if updated:
			user.save(ignore_permissions=True)
		else:
			print(f"  ⊘ {username} already has required roles")

	frappe.db.commit()
	print("\n✓ Role assignment complete\n")


if __name__ == "__main__":
	assign_roles()
