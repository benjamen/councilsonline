"""
Step Template Utility for Request Type Configuration

Provides helper functions to load and apply step templates to Request Types,
reducing configuration duplication and ensuring consistency.

Usage:
    from councilsonline.templates.step_templates import load_template, apply_template

    # Load a template
    declaration_template = load_template("declaration")

    # Apply template to a request type
    apply_template(request_type_doc, "declaration", customization={
        "add_privacy_consent": True
    })
"""

import json
import os
import frappe
from frappe import _


def get_template_path(template_name):
    """Get the file path for a step template"""
    templates_dir = os.path.join(
        frappe.get_app_path("councilsonline"),
        "templates",
        "step_templates"
    )
    template_file = f"{template_name}.json"
    return os.path.join(templates_dir, template_file)


def load_template(template_name):
    """
    Load a step template from JSON file

    Args:
        template_name (str): Name of the template (e.g., "declaration", "applicant_details")

    Returns:
        dict: Template configuration including step_config, sections, and fields

    Raises:
        FileNotFoundError: If template does not exist
    """
    template_path = get_template_path(template_name)

    if not os.path.exists(template_path):
        frappe.throw(_("Step template '{0}' not found at {1}").format(template_name, template_path))

    with open(template_path, 'r') as f:
        template_data = json.load(f)

    return template_data


def list_available_templates():
    """
    List all available step templates

    Returns:
        list: List of template names
    """
    templates_dir = os.path.join(
        frappe.get_app_path("councilsonline"),
        "templates",
        "step_templates"
    )

    if not os.path.exists(templates_dir):
        return []

    templates = []
    for filename in os.listdir(templates_dir):
        if filename.endswith('.json'):
            templates.append(filename.replace('.json', ''))

    return templates


def apply_template(request_type_doc, template_name, customization=None, step_number=None):
    """
    Apply a step template to a Request Type document

    Args:
        request_type_doc: Request Type document object
        template_name (str): Name of the template to apply
        customization (dict): Optional customization options to override template defaults
        step_number (int): Optional step number (auto-assigned if not provided)

    Returns:
        dict: Applied template configuration

    Example:
        apply_template(rt_doc, "declaration", customization={
            "add_privacy_consent": True
        }, step_number=5)
    """
    template = load_template(template_name)

    # Apply customizations if provided
    if customization:
        for key, value in customization.items():
            if key in template.get("customization_options", {}):
                template["customization_options"][key] = value

    # Determine step number
    if step_number is None:
        existing_steps = len(request_type_doc.step_configs) if request_type_doc.step_configs else 0
        step_number = existing_steps + 1

    # Create step config
    step_config = template["step_config"].copy()
    step_config["step_number"] = step_number

    # Add step config to request type
    request_type_doc.append("step_configs", step_config)

    # Add sections and fields
    for section in template["sections"]:
        section_data = section.copy()
        section_data["parent_step_code"] = step_config["step_code"]

        # Remove fields from section (they're added separately)
        fields = section_data.pop("fields", [])

        # Add section to request type
        request_type_doc.append("step_sections", section_data)

        # Add fields
        for field in fields:
            field_data = field.copy()
            field_data["parent_section_code"] = section_data["section_code"]

            request_type_doc.append("step_fields", field_data)

    return {
        "step_code": step_config["step_code"],
        "step_number": step_number,
        "sections_added": len(template["sections"]),
        "fields_added": sum(len(s.get("fields", [])) for s in template["sections"])
    }


def get_template_info(template_name):
    """
    Get information about a template without loading full configuration

    Args:
        template_name (str): Name of the template

    Returns:
        dict: Template metadata (name, title, description, version)
    """
    template = load_template(template_name)
    return {
        "template_name": template.get("template_name"),
        "template_title": template.get("template_title"),
        "description": template.get("description"),
        "version": template.get("version"),
        "usage_notes": template.get("usage_notes")
    }


def validate_template(template_data):
    """
    Validate template structure

    Args:
        template_data (dict): Template configuration

    Returns:
        tuple: (is_valid, errors)
    """
    errors = []

    # Required fields
    required_keys = ["template_name", "step_config", "sections"]
    for key in required_keys:
        if key not in template_data:
            errors.append(f"Missing required key: {key}")

    # Validate step_config
    if "step_config" in template_data:
        required_step_keys = ["step_code", "step_title", "step_component"]
        for key in required_step_keys:
            if key not in template_data["step_config"]:
                errors.append(f"Missing required step_config key: {key}")

    # Validate sections
    if "sections" in template_data:
        for i, section in enumerate(template_data["sections"]):
            required_section_keys = ["section_code", "section_title", "fields"]
            for key in required_section_keys:
                if key not in section:
                    errors.append(f"Section {i}: Missing required key: {key}")

            # Validate fields
            if "fields" in section:
                for j, field in enumerate(section["fields"]):
                    required_field_keys = ["field_name", "field_label", "field_type"]
                    for key in required_field_keys:
                        if key not in field:
                            errors.append(f"Section {i}, Field {j}: Missing required key: {key}")

    is_valid = len(errors) == 0
    return (is_valid, errors)
