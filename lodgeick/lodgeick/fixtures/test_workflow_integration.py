#!/usr/bin/env python3
"""
Test workflow integration
Run with: bench --site lodgeick.localhost execute lodgeick.lodgeick.fixtures.test_workflow_integration.test_workflows
"""

import frappe


def test_workflows():
    """Test workflow configuration and integration"""

    print("\n" + "="*80)
    print("TESTING WORKFLOW INTEGRATION")
    print("="*80 + "\n")

    # Test 1: Check workflows exist
    print("1. Checking Active Workflows...")
    workflows = frappe.get_all(
        'Workflow',
        filters={'document_type': 'Request', 'is_active': 1},
        fields=['name', 'workflow_name']
    )

    if workflows:
        print(f"   ✓ Found {len(workflows)} active workflows for Request:")
        for w in workflows:
            print(f"     - {w.workflow_name}")
    else:
        print("   ✗ No active workflows found!")
        return

    # Test 2: Check workflow states
    print("\n2. Checking Workflow States...")
    states = frappe.get_all('Workflow State', fields=['name', 'style'])
    print(f"   ✓ Found {len(states)} workflow states")

    # Test 3: Check Request Type workflow linkage
    print("\n3. Checking Request Type Workflow Linkage...")
    request_types = frappe.get_all(
        'Request Type',
        fields=['name', 'workflow_template']
    )

    for rt in request_types:
        if rt.workflow_template:
            print(f"   ✓ {rt.name}: {rt.workflow_template}")
        else:
            print(f"   ⊘ {rt.name}: No workflow linked")

    # Test 4: Check existing requests have workflow_state
    print("\n4. Checking Existing Requests...")
    requests = frappe.get_all(
        'Request',
        fields=['name', 'request_type', 'status', 'workflow_state'],
        filters={'docstatus': ['!=', 2]},
        limit=10
    )

    if requests:
        print(f"   Found {len(requests)} requests:")
        for req in requests:
            status = '✓' if req.workflow_state else '⊘'
            print(f"   {status} {req.name}: status='{req.status}', workflow_state='{req.workflow_state or 'None'}'")
    else:
        print("   No requests found")

    # Test 5: Check workflow transitions
    print("\n5. Checking Workflow Transitions...")
    for workflow in workflows:
        wf_doc = frappe.get_doc('Workflow', workflow.name)
        print(f"   {workflow.workflow_name}:")
        print(f"     States: {len(wf_doc.states)}")
        print(f"     Transitions: {len(wf_doc.transitions)}")

        # Show a few transitions
        print(f"     Sample transitions:")
        for trans in wf_doc.transitions[:5]:
            print(f"       {trans.state} → [{trans.action}] → {trans.next_state} (Allowed: {trans.allowed})")

    print("\n" + "="*80)
    print("WORKFLOW INTEGRATION TEST COMPLETE")
    print("="*80)

    return {
        'workflows_found': len(workflows),
        'states_found': len(states),
        'requests_checked': len(requests) if requests else 0
    }


if __name__ == "__main__":
    test_workflows()
