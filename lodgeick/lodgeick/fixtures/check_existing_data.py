#!/usr/bin/env python3
"""
Check existing data
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.check_existing_data.check_data
"""

import frappe


def check_data():
    """Check existing request types and requests"""

    print("\n" + "="*80)
    print("CHECKING EXISTING DATA")
    print("="*80 + "\n")

    # Get existing request types
    request_types = frappe.get_all('Request Type', fields=['name'])
    print(f'Existing Request Types ({len(request_types)}):')
    for rt in request_types:
        print(f'  - {rt.name}')

    # Get existing requests
    requests = frappe.get_all(
        'Request',
        fields=['name', 'request_type', 'workflow_state', 'docstatus', 'status'],
        filters={'docstatus': ['!=', 2]},
        limit=10
    )

    print(f'\nExisting Requests ({len(requests)}):')
    for req in requests:
        print(f'  - {req.name}')
        print(f'      Type: {req.request_type}')
        print(f'      Workflow State: {req.workflow_state or "None"}')
        print(f'      Status: {req.status}')
        print(f'      Docstatus: {req.docstatus}')

    # Check workflow
    workflows = frappe.get_all(
        'Workflow',
        filters={'document_type': 'Request', 'is_active': 1},
        fields=['name', 'workflow_name']
    )

    print(f'\nActive Workflow:')
    for wf in workflows:
        print(f'  - {wf.workflow_name}')

    print("\n" + "="*80)

    return True


if __name__ == "__main__":
    check_data()
