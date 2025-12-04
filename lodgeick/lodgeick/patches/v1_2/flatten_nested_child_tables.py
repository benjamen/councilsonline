"""
Migration patch to flatten nested child tables in Request Type Step configuration.

PROBLEM:
Frappe doesn't support nested child tables (3+ levels):
Request Type → Step Config → Section → Field (❌ 3 LEVELS - ILLEGAL)

SOLUTION:
Flatten to 2 levels maximum:
Request Type → Step Config (child)
Request Type → Section (child with parent_step_code link)
Request Type → Field (child with parent_section_code link)

This patch:
1. Adds parent_step_code to sections
2. Adds parent_section_code to fields
3. Moves sections from step_config.sections to request_type.step_sections
4. Moves fields from section.fields to request_type.step_fields
5. Removes the nested relationships
"""

import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
    """Execute the migration"""
    frappe.reload_doc("lodgeick", "doctype", "request_type")
    frappe.reload_doc("lodgeick", "doctype", "request_type_step_config")
    frappe.reload_doc("lodgeick", "doctype", "request_type_step_section")
    frappe.reload_doc("lodgeick", "doctype", "request_type_step_field")

    # Get all Request Types
    request_types = frappe.get_all("Request Type", fields=["name"])

    for rt in request_types:
        flatten_request_type(rt.name)

    frappe.db.commit()
    print(f"✅ Flattened {len(request_types)} Request Types")


def flatten_request_type(request_type_name):
    """Flatten a single Request Type"""
    try:
        doc = frappe.get_doc("Request Type", request_type_name)

        # Initialize new flat child tables if they don't exist
        if not hasattr(doc, 'step_sections'):
            doc.step_sections = []
        if not hasattr(doc, 'step_fields'):
            doc.step_fields = []

        # Process each step
        for step in doc.step_configs:
            # Get sections that were nested under this step
            nested_sections = frappe.get_all(
                "Request Type Step Section",
                filters={
                    "parent": step.name,
                    "parenttype": "Request Type Step Config",
                    "parentfield": "sections"
                },
                fields=["*"]
            )

            for section_data in nested_sections:
                # Create new section at Request Type level with parent_step_code link
                new_section = doc.append("step_sections", {})
                new_section.parent_step_code = step.step_code
                new_section.section_code = section_data.section_code
                new_section.section_title = section_data.section_title
                new_section.section_type = section_data.get("section_type", "Section")
                new_section.sequence = section_data.get("sequence", 1)
                new_section.is_enabled = section_data.get("is_enabled", 1)
                new_section.is_required = section_data.get("is_required", 1)
                new_section.show_on_review = section_data.get("show_on_review", 1)
                new_section.depends_on = section_data.get("depends_on")

                # Get fields that were nested under this section
                nested_fields = frappe.get_all(
                    "Request Type Step Field",
                    filters={
                        "parent": section_data.name,
                        "parenttype": "Request Type Step Section",
                        "parentfield": "fields"
                    },
                    fields=["*"]
                )

                for field_data in nested_fields:
                    # Create new field at Request Type level with parent_section_code link
                    new_field = doc.append("step_fields", {})
                    new_field.parent_section_code = section_data.section_code
                    new_field.field_name = field_data.field_name
                    new_field.field_label = field_data.field_label
                    new_field.field_type = field_data.field_type
                    new_field.is_required = field_data.get("is_required", 0)
                    new_field.show_on_review = field_data.get("show_on_review", 1)
                    new_field.options = field_data.get("options")
                    new_field.default_value = field_data.get("default_value")
                    new_field.depends_on = field_data.get("depends_on")
                    new_field.validation = field_data.get("validation")
                    new_field.review_label = field_data.get("review_label")

        # Save the flattened Request Type
        doc.flags.ignore_validate = True  # Skip validation during migration
        doc.flags.ignore_mandatory = True
        doc.save()

        # Clean up old nested records
        cleanup_nested_records(request_type_name)

        print(f"✅ Flattened: {request_type_name}")

    except Exception as e:
        print(f"❌ Error flattening {request_type_name}: {str(e)}")
        frappe.log_error(
            message=frappe.get_traceback(),
            title=f"Flatten Request Type Error: {request_type_name}"
        )


def cleanup_nested_records(request_type_name):
    """Delete old nested child records that are now duplicated"""
    try:
        # Get all step configs for this request type
        step_configs = frappe.get_all(
            "Request Type Step Config",
            filters={
                "parent": request_type_name,
                "parenttype": "Request Type",
                "parentfield": "step_configs"
            },
            fields=["name"]
        )

        for step in step_configs:
            # Delete nested sections
            frappe.db.delete("Request Type Step Section", {
                "parent": step.name,
                "parenttype": "Request Type Step Config",
                "parentfield": "sections"
            })

        # Delete orphaned fields (sections that were nested)
        orphaned_sections = frappe.get_all(
            "Request Type Step Section",
            filters={
                "parenttype": "Request Type Step Config"
            },
            fields=["name"]
        )

        for section in orphaned_sections:
            frappe.db.delete("Request Type Step Field", {
                "parent": section.name,
                "parenttype": "Request Type Step Section",
                "parentfield": "fields"
            })

        frappe.db.commit()

    except Exception as e:
        print(f"⚠️  Cleanup warning for {request_type_name}: {str(e)}")
