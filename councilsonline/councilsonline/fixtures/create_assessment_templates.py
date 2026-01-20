#!/usr/bin/env python3
"""
Script to create default assessment templates
Run with: bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.create_assessment_templates.create_templates
"""

import frappe


def create_templates():
    """Create all assessment templates"""
    frappe.flags.in_import = True

    templates = [
        {
            "template_name": "Resource Consent - Non-Notified",
            "request_type": "Resource Consent",
            "is_active": 1,
            "default_budget_hours": 40,
            "description": "<p>Standard assessment workflow for non-notified resource consent applications processed under RMA. Includes vetting, technical assessment, decision, and implementation stages with 20 working day statutory timeframe.</p>",
            "stages": [
                {
                    "stage_number": 1,
                    "stage_name": "Vetting & S88 Compliance",
                    "stage_type": "Vetting",
                    "required": 1,
                    "estimated_hours": 4
                },
                {
                    "stage_number": 2,
                    "stage_name": "Technical Assessment",
                    "stage_type": "Technical Assessment",
                    "required": 1,
                    "estimated_hours": 20
                },
                {
                    "stage_number": 3,
                    "stage_name": "Decision Preparation",
                    "stage_type": "Decision",
                    "required": 1,
                    "estimated_hours": 10
                },
                {
                    "stage_number": 4,
                    "stage_name": "Implementation & Issuance",
                    "stage_type": "Implementation",
                    "required": 1,
                    "estimated_hours": 6
                }
            ]
        },
        {
            "template_name": "Resource Consent - Notified",
            "request_type": "Resource Consent",
            "is_active": 1,
            "default_budget_hours": 80,
            "description": "<p>Assessment workflow for publicly notified resource consent applications. Includes notification period, submission processing, hearing (if required), and extended decision timeframes.</p>",
            "stages": [
                {
                    "stage_number": 1,
                    "stage_name": "Vetting & S88 Compliance",
                    "stage_type": "Vetting",
                    "required": 1,
                    "estimated_hours": 4
                },
                {
                    "stage_number": 2,
                    "stage_name": "Public Notification",
                    "stage_type": "Notification",
                    "required": 1,
                    "estimated_hours": 8
                },
                {
                    "stage_number": 3,
                    "stage_name": "Submission Processing",
                    "stage_type": "Technical Assessment",
                    "required": 1,
                    "estimated_hours": 12
                },
                {
                    "stage_number": 4,
                    "stage_name": "Hearing (if required)",
                    "stage_type": "Hearing",
                    "required": 0,
                    "estimated_hours": 20
                },
                {
                    "stage_number": 5,
                    "stage_name": "Technical Assessment",
                    "stage_type": "Technical Assessment",
                    "required": 1,
                    "estimated_hours": 20
                },
                {
                    "stage_number": 6,
                    "stage_name": "Decision Preparation",
                    "stage_type": "Decision",
                    "required": 1,
                    "estimated_hours": 12
                },
                {
                    "stage_number": 7,
                    "stage_name": "Implementation & Issuance",
                    "stage_type": "Implementation",
                    "required": 1,
                    "estimated_hours": 4
                }
            ]
        },
        {
            "template_name": "Building Consent - Standard",
            "request_type": "Building Consent",
            "is_active": 1,
            "default_budget_hours": 30,
            "description": "<p>Standard building consent assessment workflow for residential and commercial buildings. Includes plan vetting, technical assessment, and decision within 20 working days.</p>",
            "stages": [
                {
                    "stage_number": 1,
                    "stage_name": "Plan Vetting",
                    "stage_type": "Vetting",
                    "required": 1,
                    "estimated_hours": 6
                },
                {
                    "stage_number": 2,
                    "stage_name": "Technical Assessment",
                    "stage_type": "Technical Assessment",
                    "required": 1,
                    "estimated_hours": 16
                },
                {
                    "stage_number": 3,
                    "stage_name": "Decision & Issuance",
                    "stage_type": "Decision",
                    "required": 1,
                    "estimated_hours": 8
                }
            ]
        },
        {
            "template_name": "Building Consent - Fast Track",
            "request_type": "Building Consent",
            "is_active": 1,
            "default_budget_hours": 15,
            "description": "<p>Fast track building consent assessment for simple structures like sheds, carports, and minor alterations. Streamlined process with 10 working day target.</p>",
            "stages": [
                {
                    "stage_number": 1,
                    "stage_name": "Fast Track Vetting",
                    "stage_type": "Vetting",
                    "required": 1,
                    "estimated_hours": 3
                },
                {
                    "stage_number": 2,
                    "stage_name": "Simplified Assessment",
                    "stage_type": "Technical Assessment",
                    "required": 1,
                    "estimated_hours": 8
                },
                {
                    "stage_number": 3,
                    "stage_name": "Quick Decision",
                    "stage_type": "Decision",
                    "required": 1,
                    "estimated_hours": 4
                }
            ]
        },
        {
            "template_name": "LIM Assessment",
            "request_type": "LIM",
            "is_active": 1,
            "default_budget_hours": 12,
            "description": "<p>Land Information Memorandum assessment workflow. Comprehensive property information gathering and report preparation within 10 working days.</p>",
            "stages": [
                {
                    "stage_number": 1,
                    "stage_name": "Information Gathering",
                    "stage_type": "Vetting",
                    "required": 1,
                    "estimated_hours": 6
                },
                {
                    "stage_number": 2,
                    "stage_name": "Report Compilation",
                    "stage_type": "Technical Assessment",
                    "required": 1,
                    "estimated_hours": 4
                },
                {
                    "stage_number": 3,
                    "stage_name": "Quality Check & Issuance",
                    "stage_type": "Decision",
                    "required": 1,
                    "estimated_hours": 2
                }
            ]
        }
    ]

    created = []
    for template_data in templates:
        # Check if template already exists
        if frappe.db.exists("Assessment Template", template_data["template_name"]):
            print(f"Template '{template_data['template_name']}' already exists, skipping...")
            continue

        # Create template
        try:
            doc = frappe.get_doc({
                "doctype": "Assessment Template",
                **template_data
            })
            doc.insert(ignore_permissions=True)
            created.append(template_data["template_name"])
            print(f"✓ Created template: {template_data['template_name']}")
        except Exception as e:
            print(f"✗ Failed to create template '{template_data['template_name']}': {str(e)}")
            frappe.log_error(f"Failed to create template: {str(e)}")

    frappe.db.commit()
    frappe.flags.in_import = False

    print(f"\n=== Summary ===")
    print(f"Created {len(created)} templates")
    if created:
        print("Templates created:")
        for name in created:
            print(f"  - {name}")

    return {"created": created}


if __name__ == "__main__":
    create_templates()
