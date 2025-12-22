#!/usr/bin/env python3
"""
Check SPISC assessment template configuration
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.check_spisc_template.check_template
"""

import frappe


def check_template():
    """Check if SPISC assessment template exists and is properly configured"""

    print("\n" + "="*80)
    print("CHECKING SPISC ASSESSMENT TEMPLATE")
    print("="*80 + "\n")

    # Check for SPISC assessment template
    template = frappe.db.get_value(
        'Assessment Template',
        {'request_type': 'Social Pension for Indigent Senior Citizens (SPISC)'},
        ['name', 'is_active', 'request_type'],
        as_dict=True
    )

    if template:
        print(f"✓ SPISC Assessment Template found: {template.name}")
        print(f"  Request Type: {template.request_type}")
        print(f"  Is Active: {template.is_active}")

        if not template.is_active:
            print("\n⚠ WARNING: Template is NOT active")
            print("  Activating template...")
            frappe.db.set_value('Assessment Template', template.name, 'is_active', 1)
            frappe.db.commit()
            print("  ✓ Template activated")

        # Check stages
        stages = frappe.get_all(
            'Assessment Template Stage',
            filters={'parent': template.name},
            fields=['stage_name', 'idx'],
            order_by='idx'
        )

        print(f"\n  Stages ({len(stages)}):")
        for stage in stages:
            print(f"    {stage.idx}. {stage.stage_name}")

        # Check tasks
        tasks = frappe.get_all(
            'Assessment Template Task',
            filters={'parent': template.name},
            fields=['task_id', 'task_name', 'stage'],
            order_by='task_id'
        )

        print(f"\n  Tasks ({len(tasks)}):")
        for task in tasks:
            print(f"    {task.task_id}: {task.task_name} ({task.stage})")

    else:
        print("⚠ No SPISC assessment template found")
        print("\nSearching for similar templates...")

        all_templates = frappe.get_all(
            'Assessment Template',
            fields=['name', 'request_type', 'is_active']
        )

        print(f"\nFound {len(all_templates)} templates:")
        for tmpl in all_templates:
            print(f"  - {tmpl.name} (Type: {tmpl.request_type}, Active: {tmpl.is_active})")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    check_template()
