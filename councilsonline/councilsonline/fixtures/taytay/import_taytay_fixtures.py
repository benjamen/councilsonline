#!/usr/bin/env python3
"""
Import Taytay Council and Request Type Fixtures

This script imports the Taytay council configuration and the SPISC request type
with all its configurable steps, sections, and fields.

Usage:
    bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.taytay.import_taytay_fixtures.import_fixtures
"""

import frappe
import json
import os
from pathlib import Path


def import_fixtures():
    """Import Taytay council and request type fixtures"""

    frappe.flags.in_import = True

    # Get the directory of this script
    fixture_dir = Path(__file__).parent

    print("\n" + "="*80)
    print("IMPORTING TAYTAY FIXTURES")
    print("="*80 + "\n")

    # Import Philippines Holiday List FIRST (needed for statutory clock calculations)
    print("Step 1: Importing Philippines Holiday List...")
    holiday_file = fixture_dir / "ph_holiday_list.json"
    import_holiday_list_fixture(holiday_file)

    # Import SPISC Request Type (Council references it)
    print("\nStep 2: Importing SPISC Request Type with step configuration...")
    spisc_file = fixture_dir / "spisc_request_type.json"
    import_request_type_fixture(spisc_file)

    # Import SPISC Assessment Template (needed for auto-creating assessment projects)
    print("\nStep 3: Importing SPISC Assessment Template...")
    template_file = fixture_dir / "spisc_assessment_template.json"
    import_assessment_template_fixture(template_file)

    # Import Council AFTER Request Types exist
    print("\nStep 4: Importing Taytay Council...")
    council_file = fixture_dir / "taytay_council.json"
    import_council_fixture(council_file)

    frappe.db.commit()

    print("\n" + "="*80)
    print("IMPORT COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Verify council in UI: http://127.0.0.1:8090/app/council/TAYTAY-PH")
    print("2. Verify request type: http://127.0.0.1:8090/app/request-type/Social Pension for Indigent Senior Citizens (SPISC)")
    print("3. Test form: http://127.0.0.1:8090/frontend")
    print()


def import_holiday_list_fixture(file_path):
    """Import Holiday List fixture with holidays child table"""

    if not os.path.exists(file_path):
        print(f"  ❌ File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    doc_name = data.get('name')
    doctype = 'Holiday List'

    # Check if document already exists
    if frappe.db.exists(doctype, doc_name):
        print(f"  ⚠️  {doctype} '{doc_name}' already exists - updating...")
        doc = frappe.get_doc(doctype, doc_name)

        # Update basic fields
        for key, value in data.items():
            if key not in ['doctype', 'name', 'creation', 'modified', 'modified_by', 'owner', 'holidays']:
                doc.set(key, value)

        # Update holidays child table
        doc.holidays = []
        for holiday_data in data.get('holidays', []):
            doc.append('holidays', holiday_data)

        doc.save()
        print(f"  ✅ Updated {doctype}: {doc_name}")
        print(f"     - {len(data.get('holidays', []))} holidays")
    else:
        print(f"  📝 Creating {doctype}: {doc_name}...")
        doc = frappe.get_doc(data)
        doc.insert()
        print(f"  ✅ Created {doctype}: {doc_name}")
        print(f"     - {len(data.get('holidays', []))} holidays")


def import_json_fixture(file_path, doctype):
    """Import a standard JSON fixture file"""

    if not os.path.exists(file_path):
        print(f"  ❌ File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    for doc_data in data:
        doc_name = doc_data.get('name')

        # Check if document already exists
        if frappe.db.exists(doctype, doc_name):
            print(f"  ⚠️  {doctype} '{doc_name}' already exists - updating...")
            doc = frappe.get_doc(doctype, doc_name)

            # Update fields
            for key, value in doc_data.items():
                if key not in ['doctype', 'name', 'creation', 'modified', 'modified_by', 'owner']:
                    if isinstance(value, list):
                        # Clear child table and re-add
                        doc.set(key, [])
                        for child_data in value:
                            doc.append(key, child_data)
                    else:
                        doc.set(key, value)

            doc.save()
            print(f"  ✅ Updated {doctype}: {doc_name}")
        else:
            print(f"  📝 Creating {doctype}: {doc_name}...")
            doc = frappe.get_doc(doc_data)
            doc.insert()
            print(f"  ✅ Created {doctype}: {doc_name}")


def import_assessment_template_fixture(file_path):
    """Import Assessment Template with stages child table"""

    if not os.path.exists(file_path):
        print(f"  ❌ File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    template_name = data.get('template_name')
    doctype = 'Assessment Template'

    # Check if document already exists
    if frappe.db.exists(doctype, template_name):
        print(f"  ⚠️  {doctype} '{template_name}' already exists - updating...")
        doc = frappe.get_doc(doctype, template_name)

        # Update basic fields
        for key, value in data.items():
            if key not in ['doctype', 'name', 'template_name', 'creation', 'modified', 'modified_by', 'owner', 'stages']:
                doc.set(key, value)

        # Update stages child table
        doc.stages = []
        for stage_data in data.get('stages', []):
            doc.append('stages', stage_data)

        doc.save()
        print(f"  ✅ Updated {doctype}: {template_name}")
        print(f"     - {len(data.get('stages', []))} stages")
    else:
        print(f"  📝 Creating {doctype}: {template_name}...")
        doc = frappe.get_doc(data)
        doc.insert()
        print(f"  ✅ Created {doctype}: {template_name}")
        print(f"     - {len(data.get('stages', []))} stages")


def import_request_type_fixture(file_path):
    """Import Request Type with flattened child tables"""

    if not os.path.exists(file_path):
        print(f"  ❌ File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    doc_name = data.get('name')
    doctype = 'Request Type'

    # Check if document already exists
    if frappe.db.exists(doctype, doc_name):
        print(f"  ⚠️  {doctype} '{doc_name}' already exists - updating...")
        doc = frappe.get_doc(doctype, doc_name)

        # Update basic fields
        for key, value in data.items():
            if key not in ['doctype', 'name', 'creation', 'modified', 'modified_by', 'owner',
                          'step_configs', 'step_sections', 'step_fields', 'condition_templates']:
                doc.set(key, value)

        # Update step_configs (child table)
        doc.step_configs = []
        for step_data in data.get('step_configs', []):
            doc.append('step_configs', step_data)

        # Update step_sections (flattened child table with parent_step_code)
        doc.step_sections = []
        for section_data in data.get('step_sections', []):
            doc.append('step_sections', section_data)

        # Update step_fields (flattened child table with parent_section_code)
        doc.step_fields = []
        for field_data in data.get('step_fields', []):
            doc.append('step_fields', field_data)

        doc.save()
        print(f"  ✅ Updated {doctype}: {doc_name}")
        print(f"     - {len(data.get('step_configs', []))} steps")
        print(f"     - {len(data.get('step_sections', []))} sections")
        print(f"     - {len(data.get('step_fields', []))} fields")
    else:
        print(f"  📝 Creating {doctype}: {doc_name}...")
        doc = frappe.get_doc(data)
        doc.insert()
        print(f"  ✅ Created {doctype}: {doc_name}")
        print(f"     - {len(data.get('step_configs', []))} steps")
        print(f"     - {len(data.get('step_sections', []))} sections")
        print(f"     - {len(data.get('step_fields', []))} fields")


def import_council_fixture(file_path):
    """Import Council Single DocType fixture"""

    if not os.path.exists(file_path):
        print(f"  ❌ File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    # Council fixture is a list with one item (even though it's a Single DocType)
    if isinstance(data, list):
        data = data[0] if data else {}

    doctype = 'Council'

    # For Single DocTypes, always get the existing doc (name is always the doctype name)
    print(f"  📝 Configuring {doctype} Single DocType...")
    doc = frappe.get_doc(doctype)

    # Update fields from fixture
    for key, value in data.items():
        if key not in ['doctype', 'name', 'creation', 'modified', 'modified_by', 'owner']:
            if isinstance(value, list):
                # Clear child table and re-add
                doc.set(key, [])
                for child_data in value:
                    # Only add if the linked record exists (for Request Types)
                    if key == 'enabled_request_types':
                        rt_name = child_data.get('request_type')
                        if rt_name and frappe.db.exists('Request Type', rt_name):
                            doc.append(key, child_data)
                        else:
                            print(f"     ⚠️  Skipping Request Type '{rt_name}' - not found")
                    else:
                        doc.append(key, child_data)
            else:
                doc.set(key, value)

    doc.save()
    enabled_count = len(doc.enabled_request_types) if doc.enabled_request_types else 0
    print(f"  ✅ Configured {doctype}: {doc.council_name}")
    print(f"     - {enabled_count} enabled Request Types")


if __name__ == "__main__":
    import_fixtures()
