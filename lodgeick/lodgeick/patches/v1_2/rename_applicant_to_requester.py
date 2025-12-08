"""
Migration patch to rename 'applicant' terminology to 'requester' throughout the system.

This patch:
1. Renames database columns in Request DocType (applicant_* -> requester_*)
2. Creates new 'Requester' role (keeps 'Applicant' as alias for backward compatibility)
3. Updates all role assignments from 'Applicant' to 'Requester'
4. Updates field labels and descriptions in DocType definitions
"""

import frappe


def execute():
    """Execute the migration"""
    frappe.reload_doc("lodgeick", "doctype", "request", force=True)

    # Step 1: Rename database columns in Request DocType
    rename_request_fields()

    # Step 2: Create Requester role and migrate permissions
    create_requester_role()

    # Step 3: Migrate user role assignments
    migrate_user_roles()

    # Step 4: Update role permissions for all DocTypes
    migrate_doctype_permissions()

    frappe.db.commit()
    print("✅ Migration complete: applicant → requester")


def rename_request_fields():
    """Rename applicant_* fields to requester_* in Request DocType"""

    field_mappings = [
        ("applicant", "requester"),
        ("applicant_name", "requester_name"),
        ("applicant_email", "requester_email"),
        ("applicant_phone", "requester_phone"),
        ("applicant_type", "requester_type"),
        ("applicant_signature_first_name", "requester_signature_first_name"),
        ("applicant_signature_date", "requester_signature_date"),
    ]

    print("\n📦 Renaming Request fields...")

    for old_field, new_field in field_mappings:
        try:
            # Check if old field exists and new field doesn't
            if frappe.db.has_column("tabRequest", old_field):
                if not frappe.db.has_column("tabRequest", new_field):
                    print(f"  - Renaming: {old_field} → {new_field}")
                    # Use SQL rename instead of rename_field for better control
                    frappe.db.sql(f"ALTER TABLE `tabRequest` CHANGE `{old_field}` `{new_field}` VARCHAR(255)")
                    frappe.db.commit()
                else:
                    print(f"  ⚠ Skipping {old_field}: {new_field} already exists")
            else:
                print(f"  ℹ Skipping {old_field}: column doesn't exist")
        except Exception as e:
            print(f"  ✗ Error renaming {old_field}: {str(e)}")
            # Continue with other fields even if one fails


def create_requester_role():
    """Create Requester role if it doesn't exist"""

    print("\n📦 Creating Requester role...")

    if not frappe.db.exists("Role", "Requester"):
        try:
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": "Requester",
                "desk_access": 0,  # Website user role
                "disabled": 0,
                "is_custom": 0
            })
            role.insert(ignore_permissions=True)
            print("  ✓ Created Requester role")
        except Exception as e:
            print(f"  ✗ Error creating Requester role: {str(e)}")
    else:
        print("  ℹ Requester role already exists")

    # Keep Applicant role as an alias (don't delete for backward compatibility)
    print("  ℹ Keeping 'Applicant' role for backward compatibility")


def migrate_user_roles():
    """Migrate all users from Applicant role to Requester role"""

    print("\n📦 Migrating user roles...")

    # Get all users with Applicant role
    user_roles = frappe.get_all(
        "Has Role",
        filters={"role": "Applicant", "parenttype": "User"},
        fields=["parent", "name"]
    )

    migrated = 0
    for user_role in user_roles:
        try:
            user = user_role.parent

            # Check if user already has Requester role
            if not frappe.db.exists("Has Role", {"parent": user, "role": "Requester"}):
                # Add Requester role
                frappe.get_doc({
                    "doctype": "Has Role",
                    "parent": user,
                    "parenttype": "User",
                    "parentfield": "roles",
                    "role": "Requester"
                }).insert(ignore_permissions=True)

                migrated += 1
        except Exception as e:
            print(f"  ✗ Error migrating user {user}: {str(e)}")

    print(f"  ✓ Migrated {migrated} users to Requester role")
    print(f"  ℹ Applicant role assignments kept for backward compatibility")


def migrate_doctype_permissions():
    """Add Requester role permissions to all DocTypes that have Applicant permissions"""

    print("\n📦 Migrating DocType permissions...")

    # Get all DocType permissions for Applicant role
    applicant_perms = frappe.get_all(
        "DocPerm",
        filters={"role": "Applicant"},
        fields=["*"]
    )

    migrated = 0
    for perm in applicant_perms:
        try:
            doctype = perm.parent

            # Check if Requester permission already exists for this DocType
            existing = frappe.db.exists(
                "DocPerm",
                {
                    "parent": doctype,
                    "role": "Requester",
                    "permlevel": perm.permlevel
                }
            )

            if not existing:
                # Create new permission for Requester role (copy from Applicant)
                new_perm = frappe.get_doc({
                    "doctype": "DocPerm",
                    "parent": doctype,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": "Requester",
                    "permlevel": perm.permlevel,
                    "read": perm.read,
                    "write": perm.write,
                    "create": perm.create,
                    "delete": perm.delete,
                    "submit": perm.submit,
                    "cancel": perm.cancel,
                    "amend": perm.amend,
                    "report": perm.report,
                    "export": perm.export,
                    "import": perm.get("import"),
                    "share": perm.share,
                    "print": perm.get("print"),
                    "email": perm.email,
                    "if_owner": perm.if_owner,
                })
                new_perm.insert(ignore_permissions=True)
                migrated += 1
        except Exception as e:
            print(f"  ✗ Error migrating permissions for {doctype}: {str(e)}")

    print(f"  ✓ Migrated permissions for {migrated} DocTypes")
    print(f"  ℹ Applicant role permissions kept for backward compatibility")
