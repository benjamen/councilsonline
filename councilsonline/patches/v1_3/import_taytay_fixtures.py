"""
Migration Patch: Import Taytay Council and SPISC Fixtures

This patch imports the Taytay Council configuration and the Social Pension
for Indigent Senior Citizens (SPISC) request type with all its configurable
steps, sections, and fields.

This will run automatically when migrating to v1.3 on production.
"""

import frappe
from councilsonline.councilsonline.fixtures.taytay.import_taytay_fixtures import import_fixtures


def execute():
    """Execute the migration patch"""

    print("\n" + "="*80)
    print("MIGRATION PATCH: Importing Taytay Fixtures (v1.3)")
    print("="*80 + "\n")

    try:
        import_fixtures()
        print("\n✅ Taytay fixtures imported successfully\n")
    except Exception as e:
        print(f"\n❌ Error importing Taytay fixtures: {str(e)}\n")
        # Don't fail the entire migration if fixtures fail
        frappe.log_error(title="Taytay Fixtures Import Failed", message=str(e))
