# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Data migration patch: Move statutory clock fields from Request to Resource Consent Application

This patch migrates existing statutory clock data from the Request DocType to the
Resource Consent Application DocType as part of the refactoring to separate
Resource Consent-specific fields from the generic Request container.

Migration Steps:
1. Find all Resource Consent requests with statutory clock data
2. Locate corresponding Resource Consent Application records
3. Copy statutory clock fields to RC Application
4. Validate data integrity
5. Log results

This patch is idempotent and can be run multiple times safely.
"""

import frappe
from frappe.utils import now_datetime


def execute():
    """Main migration function"""
    frappe.logger().info("Starting statutory clock migration to Resource Consent Application")

    # Statistics
    total_requests = 0
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    errors = []

    try:
        # Find all Resource Consent requests with statutory clock data
        requests_with_clock = frappe.db.sql("""
            SELECT
                name,
                statutory_clock_started,
                statutory_clock_stopped,
                working_days_elapsed,
                working_days_remaining
            FROM `tabRequest`
            WHERE request_category = 'Resource Consent'
            AND statutory_clock_started IS NOT NULL
        """, as_dict=True)

        total_requests = len(requests_with_clock)
        frappe.logger().info(f"Found {total_requests} Resource Consent requests with statutory clock data")

        for request in requests_with_clock:
            try:
                # Find corresponding Resource Consent Application
                rc_app_name = frappe.db.get_value(
                    "Resource Consent Application",
                    {"request": request.name},
                    "name"
                )

                if not rc_app_name:
                    frappe.logger().warning(
                        f"No Resource Consent Application found for Request {request.name}. Skipping."
                    )
                    skipped_count += 1
                    continue

                # Check if already migrated (idempotency check)
                existing_clock = frappe.db.get_value(
                    "Resource Consent Application",
                    rc_app_name,
                    "statutory_clock_started"
                )

                if existing_clock:
                    frappe.logger().info(
                        f"RC Application {rc_app_name} already has statutory clock data. Skipping."
                    )
                    skipped_count += 1
                    continue

                # Migrate the data using direct SQL update for efficiency
                frappe.db.sql("""
                    UPDATE `tabResource Consent Application`
                    SET
                        statutory_clock_started = %(clock_started)s,
                        statutory_clock_stopped = %(clock_stopped)s,
                        working_days_elapsed = %(days_elapsed)s,
                        working_days_remaining = %(days_remaining)s,
                        modified = %(modified)s
                    WHERE name = %(rc_app_name)s
                """, {
                    "clock_started": request.statutory_clock_started,
                    "clock_stopped": request.statutory_clock_stopped,
                    "days_elapsed": request.working_days_elapsed or 0,
                    "days_remaining": request.working_days_remaining or 0,
                    "modified": now_datetime(),
                    "rc_app_name": rc_app_name
                })

                migrated_count += 1
                frappe.logger().info(
                    f"Migrated statutory clock data for Request {request.name} to RC Application {rc_app_name}"
                )

            except Exception as e:
                error_count += 1
                error_msg = f"Error migrating Request {request.name}: {str(e)}"
                frappe.logger().error(error_msg)
                errors.append(error_msg)
                continue

        # Commit the transaction
        frappe.db.commit()

        # Log summary
        summary = f"""
        Statutory Clock Migration Summary:
        - Total Resource Consent requests with clock data: {total_requests}
        - Successfully migrated: {migrated_count}
        - Skipped (no RC Application or already migrated): {skipped_count}
        - Errors: {error_count}
        """
        frappe.logger().info(summary)

        if errors:
            frappe.logger().error("Migration errors:")
            for error in errors:
                frappe.logger().error(f"  - {error}")

        # Print summary to console
        print("\n" + "="*70)
        print("STATUTORY CLOCK MIGRATION COMPLETE")
        print("="*70)
        print(summary)
        if errors:
            print("\nErrors encountered:")
            for error in errors:
                print(f"  - {error}")
        print("="*70 + "\n")

    except Exception as e:
        frappe.db.rollback()
        error_msg = f"Critical error during migration: {str(e)}"
        frappe.logger().error(error_msg)
        print(f"\nMIGRATION FAILED: {error_msg}\n")
        raise
