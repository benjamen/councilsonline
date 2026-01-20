"""
Add missing Property fields to RC Request Type configuration
Run this via: bench execute councilsonline.fixtures.add_property_fields.add_fields
"""

import frappe

def add_fields():
    """Add postcode, certificate_of_title, and site_area fields to Step 2"""

    frappe.flags.in_install = True  # Bypass permission checks

    print("\n" + "=" * 70)
    print("Adding Missing Property Fields to RC Request Type")
    print("=" * 70)

    # Get RC Request Type
    rt = frappe.get_doc("Request Type", "Resource Consent")
    print(f"\n✅ Loaded: {rt.name}")
    print(f"   Current fields: {len(rt.step_fields)}")

    # Find property section
    property_section_code = None
    for section in rt.step_sections:
        if section.parent_step == "rc_property_info":
            property_section_code = section.section_code
            print(f"\n✅ Found section: {section.section_title}")
            print(f"   Code: {property_section_code}")
            break

    if not property_section_code:
        print("\n❌ Property section not found!")
        return

    # Check existing fields
    existing_codes = [f.field_code for f in rt.step_fields]

    # Define new fields
    new_fields = [
        {
            "field_code": "postcode",
            "field_label": "Postcode",
            "field_type": "Data",
            "help_text": "Property postcode",
            "field_order": 25
        },
        {
            "field_code": "certificate_of_title",
            "field_label": "Certificate of Title",
            "field_type": "Data",
            "help_text": "Certificate of Title number (e.g., CT 123456)",
            "field_order": 26
        },
        {
            "field_code": "site_area",
            "field_label": "Site Area (sqm)",
            "field_type": "Float",
            "help_text": "Total site area in square metres",
            "field_order": 27
        }
    ]

    added = 0

    print("\n" + "-" * 70)

    for field_def in new_fields:
        if field_def["field_code"] in existing_codes:
            print(f"⏭️  '{field_def['field_label']}' exists - skipping")
        else:
            rt.append("step_fields", {
                "doctype": "Request Type Step Field",
                "parent": "Resource Consent",
                "parenttype": "Request Type",
                "parentfield": "step_fields",
                "parent_step": "rc_property_info",
                "parent_section": property_section_code,
                "field_code": field_def["field_code"],
                "field_label": field_def["field_label"],
                "field_type": field_def["field_type"],
                "is_required": 1,
                "show_on_review": 1,
                "field_order": field_def["field_order"],
                "help_text": field_def["help_text"]
            })
            print(f"✅ Added: {field_def['field_label']} ({field_def['field_code']})")
            added += 1

    if added > 0:
        print(f"\n" + "-" * 70)
        print(f"Saving Request Type with {added} new fields...")
        rt.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"✅ Saved! Total fields: {len(rt.step_fields)}")
    else:
        print(f"\n✅ All fields already exist!")

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70 + "\n")
