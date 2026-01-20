#!/usr/bin/env python3
"""
Check workflow status
Run with: bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.check_workflow_status.check_workflows
"""

import frappe


def check_workflows():
    """Check workflow status and configuration"""

    print("\n" + "="*80)
    print("CHECKING WORKFLOW STATUS")
    print("="*80 + "\n")

    # Check all workflows including inactive ones
    all_workflows = frappe.get_all(
        'Workflow',
        filters={'document_type': 'Request'},
        fields=['name', 'workflow_name', 'is_active']
    )

    print(f'Found {len(all_workflows)} workflows for Request:')
    for w in all_workflows:
        status = 'Active' if w.is_active else 'Inactive'
        print(f'  [{status}] {w.workflow_name}')

    # Check Resource Consent workflow specifically
    if frappe.db.exists('Workflow', 'Resource Consent Workflow'):
        print('\n' + '-'*80)
        print('Resource Consent Workflow Details:')
        print('-'*80)

        wf = frappe.get_doc('Workflow', 'Resource Consent Workflow')
        print(f'  Is Active: {wf.is_active}')
        print(f'  Document Type: {wf.document_type}')
        print(f'  States: {len(wf.states)}')
        print(f'  Transitions: {len(wf.transitions)}')

        # Check if there are any errors in states or transitions
        print('\n  States:')
        for state in wf.states[:5]:
            print(f'    - {state.state} (docstatus: {state.doc_status})')

        print('\n  First 5 Transitions:')
        for trans in wf.transitions[:5]:
            print(f'    - {trans.state} → [{trans.action}] → {trans.next_state}')
    else:
        print('\n✗ Resource Consent Workflow NOT FOUND!')

    # Check LIM workflow
    if frappe.db.exists('Workflow', 'LIM Request Workflow'):
        print('\n' + '-'*80)
        print('LIM Request Workflow Details:')
        print('-'*80)

        wf = frappe.get_doc('Workflow', 'LIM Request Workflow')
        print(f'  Is Active: {wf.is_active}')
        print(f'  Document Type: {wf.document_type}')
        print(f'  States: {len(wf.states)}')
        print(f'  Transitions: {len(wf.transitions)}')

    print("\n" + "="*80)

    return {'workflows': len(all_workflows)}


if __name__ == "__main__":
    check_workflows()
