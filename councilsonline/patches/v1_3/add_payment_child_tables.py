"""
Add payment child tables to Council and User DocTypes
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
    """Add bank accounts child table to User DocType"""

    # Add bank accounts section to User
    if not frappe.db.exists("Custom Field", "User-bank_accounts_section"):
        create_custom_field("User", {
            "fieldname": "bank_accounts_section",
            "label": "Bank Accounts",
            "fieldtype": "Section Break",
            "insert_after": "user_emails",
            "collapsible": 1
        })
        print("✓ Added bank_accounts_section to User")

    # Add child table field to User
    if not frappe.db.exists("Custom Field", "User-bank_accounts"):
        create_custom_field("User", {
            "fieldname": "bank_accounts",
            "label": "Bank Accounts",
            "fieldtype": "Table",
            "options": "User Bank Account",
            "insert_after": "bank_accounts_section",
            "description": "Bank accounts for receiving payments (pensions, grants, reimbursements)"
        })
        print("✓ Added bank_accounts child table to User")

    frappe.db.commit()
    print("\n✓ Payment child tables added successfully")
