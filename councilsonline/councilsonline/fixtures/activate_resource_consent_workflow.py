#!/usr/bin/env python3
"""
Activate Resource Consent Workflow
Run with: bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.activate_resource_consent_workflow.activate
"""

import frappe


def activate():
    """Activate Resource Consent Workflow"""

    print("\n" + "="*80)
    print("ACTIVATING RESOURCE CONSENT WORKFLOW")
    print("="*80 + "\n")

    # Note: In Frappe, only ONE workflow can be active per DocType
    # This means activating Resource Consent Workflow will deactivate LIM Workflow

    print("⚠ Important: Only ONE workflow can be active per DocType in Frappe")
    print("  This means we need a different approach for multiple workflows per Request Type\n")

    # Get all workflows
    workflows = frappe.get_all(
        'Workflow',
        filters={'document_type': 'Request'},
        fields=['name', 'workflow_name', 'is_active']
    )

    print("Current Workflows:")
    for w in workflows:
        status = 'Active' if w.is_active else 'Inactive'
        print(f'  [{status}] {w.workflow_name}')

    # Activate Resource Consent Workflow
    print("\nActivating Resource Consent Workflow...")

    if frappe.db.exists('Workflow', 'Resource Consent Workflow'):
        wf = frappe.get_doc('Workflow', 'Resource Consent Workflow')
        wf.is_active = 1
        wf.save()
        frappe.db.commit()
        print("✓ Resource Consent Workflow activated")
    else:
        print("✗ Resource Consent Workflow not found!")
        return

    # Check status after activation
    workflows_after = frappe.get_all(
        'Workflow',
        filters={'document_type': 'Request'},
        fields=['name', 'workflow_name', 'is_active']
    )

    print("\nWorkflows After Activation:")
    for w in workflows_after:
        status = 'Active' if w.is_active else 'Inactive'
        print(f'  [{status}] {w.workflow_name}')

    print("\n" + "="*80)
    print("IMPORTANT NOTE")
    print("="*80)
    print("""
Frappe's Workflow system has a limitation: Only ONE workflow can be active
per DocType at a time.

This means we CANNOT have different workflows for different Request Types
using the standard Workflow system.

SOLUTION OPTIONS:
1. Use a single comprehensive workflow with conditional transitions
2. Use DocType variants (e.g., ResourceConsentRequest, BuildingConsentRequest)
3. Implement custom workflow system

For now, Resource Consent Workflow is active since it's the most complex.
LIM and other request types can use the same workflow with appropriate
conditional transitions.

Alternatively, we can keep workflows inactive and manage state transitions
manually in the Request.py code as we were doing before.
""")

    print("="*80)

    return True


if __name__ == "__main__":
    activate()
