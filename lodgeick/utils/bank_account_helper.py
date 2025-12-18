"""
Bank Account Helper Utilities

Handles creation and management of User Bank Account records
for storing reusable bank account information.
"""

import frappe


def create_or_update_user_bank_account(user, bank_name, account_number, account_holder_name, is_default=0):
    """
    Create or update User Bank Account for a user

    Args:
        user: User ID (email)
        bank_name: Name of the bank (e.g., "BDO", "BPI", "Landbank")
        account_number: Bank account number
        account_holder_name: Name of the account holder
        is_default: Whether this should be set as the default account (1 or 0)

    Returns:
        str: Name of the User Bank Account document

    Example:
        >>> create_or_update_user_bank_account(
        ...     user="john@example.com",
        ...     bank_name="BDO",
        ...     account_number="1234567890",
        ...     account_holder_name="John Dela Cruz",
        ...     is_default=1
        ... )
        'ACC-0001'
    """
    # Check if account already exists for this user and account number
    existing = frappe.db.exists("User Bank Account", {
        "user": user,
        "account_number": account_number
    })

    if existing:
        # Update existing record
        doc = frappe.get_doc("User Bank Account", existing)
        doc.bank_name = bank_name
        doc.account_holder_name = account_holder_name

        if is_default:
            doc.is_default = 1

        doc.save(ignore_permissions=True)
        frappe.logger().info(f"Updated User Bank Account: {doc.name} for user {user}")
        return doc.name

    # Create new User Bank Account
    # Use last 4 digits of account number for the account name
    last_4_digits = account_number[-4:] if len(account_number) >= 4 else account_number

    doc = frappe.get_doc({
        "doctype": "User Bank Account",
        "user": user,
        "account_name": f"{bank_name} - {last_4_digits}",
        "account_type": "Savings",  # Default to Savings account
        "bank_name": bank_name,
        "account_number": account_number,
        "account_holder_name": account_holder_name,
        "is_default": is_default
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.logger().info(f"Created User Bank Account: {doc.name} for user {user}")

    return doc.name


def get_user_default_bank_account(user):
    """
    Get the default bank account for a user

    Args:
        user: User ID (email)

    Returns:
        dict: Bank account details or None if no default account exists

    Example:
        >>> get_user_default_bank_account("john@example.com")
        {
            "name": "ACC-0001",
            "bank_name": "BDO",
            "account_number": "1234567890",
            "account_holder_name": "John Dela Cruz"
        }
    """
    account = frappe.db.get_value(
        "User Bank Account",
        {
            "user": user,
            "is_default": 1
        },
        ["name", "bank_name", "account_number", "account_holder_name"],
        as_dict=True
    )

    return account


def get_all_user_bank_accounts(user):
    """
    Get all bank accounts for a user

    Args:
        user: User ID (email)

    Returns:
        list: List of bank account dictionaries

    Example:
        >>> get_all_user_bank_accounts("john@example.com")
        [
            {
                "name": "ACC-0001",
                "bank_name": "BDO",
                "account_number": "1234567890",
                "account_holder_name": "John Dela Cruz",
                "is_default": 1
            },
            {
                "name": "ACC-0002",
                "bank_name": "BPI",
                "account_number": "9876543210",
                "account_holder_name": "John Dela Cruz",
                "is_default": 0
            }
        ]
    """
    accounts = frappe.get_all(
        "User Bank Account",
        filters={"user": user},
        fields=["name", "bank_name", "account_number", "account_holder_name", "is_default"],
        order_by="is_default desc, creation desc"
    )

    return accounts
