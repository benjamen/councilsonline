"""
Sync SPISC Payment Step Configuration

This patch syncs the Payment Details step configuration from the JSON file
to the SPISC Request Type in the database.
"""

import frappe
import json
import os


def execute():
    """Sync payment step configuration to SPISC Request Type"""

    # Path to SPISC request type JSON file
    json_path = frappe.get_app_path(
        "lodgeick",
        "lodgeick",
        "request_type",
        "social_pension_for_indigent_senior_citizens_(spisc)",
        "social_pension_for_indigent_senior_citizens_(spisc).json"
    )

    if not os.path.exists(json_path):
        frappe.log_error(f"JSON file not found: {json_path}")
        return

    # Load JSON configuration
    with open(json_path, 'r') as f:
        config = json.load(f)

    # Get SPISC Request Type
    rt_name = "Social Pension for Indigent Senior Citizens (SPISC)"

    if not frappe.db.exists("Request Type", rt_name):
        frappe.log_error(f"Request Type not found: {rt_name}")
        return

    rt = frappe.get_doc("Request Type", rt_name)

    # Extract payment step configuration from JSON
    payment_step = None
    payment_section = None
    payment_fields = []

    for step in config.get("step_configs", []):
        if step.get("step_code") == "payment_details":
            payment_step = step
            break

    for section in config.get("step_sections", []):
        if section.get("parent_step_code") == "payment_details":
            payment_section = section
            break

    for field in config.get("step_fields", []):
        if field.get("parent_section_code") == "payment_information":
            payment_fields.append(field)

    if not payment_step:
        print("Payment step not found in JSON configuration")
        return

    # Check if step already exists in database
    existing_step = None
    for step in rt.step_configs:
        if step.step_code == "payment_details":
            existing_step = step
            break

    if existing_step:
        print("Payment step already exists in database")
        # Update existing
        existing_step.update(payment_step)
    else:
        print("Adding payment step to database...")
        # Add new step
        rt.append("step_configs", payment_step)

    # Check if section already exists
    existing_section = None
    for section in rt.step_sections:
        if section.get("section_code") == "payment_information":
            existing_section = section
            break

    if existing_section:
        print("Payment section already exists in database")
        existing_section.update(payment_section)
    else:
        if payment_section:
            print("Adding payment section to database...")
            rt.append("step_sections", payment_section)

    # Add payment fields
    for field_config in payment_fields:
        existing_field = None
        for field in rt.step_fields:
            if field.get("field_name") == field_config.get("field_name"):
                existing_field = field
                break

        if existing_field:
            print(f"Field {field_config.get('field_name')} already exists, updating...")
            existing_field.update(field_config)
        else:
            print(f"Adding field {field_config.get('field_name')} to database...")
            rt.append("step_fields", field_config)

    # Renumber steps: Supporting Documents 4→5, Declaration 5→6
    for step in rt.step_configs:
        if step.step_code == "supporting_documents" and step.step_number == 4:
            step.step_number = 5
            print("Renumbered Supporting Documents: 4 → 5")
        elif step.step_code == "declaration" and step.step_number == 5:
            step.step_number = 6
            print("Renumbered Declaration: 5 → 6")

    # Save the updated Request Type
    rt.save(ignore_permissions=True)
    frappe.db.commit()

    print("✅ SPISC Payment step configuration synced successfully!")
    print(f"   - Step: {payment_step.get('step_title')}")
    print(f"   - Section: {payment_section.get('section_title') if payment_section else 'None'}")
    print(f"   - Fields: {len(payment_fields)}")
