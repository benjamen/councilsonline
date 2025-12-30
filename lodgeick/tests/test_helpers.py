"""
Shared test utilities and fixtures for Lodgeick tests.

This module provides reusable test fixtures and helper functions
to reduce code duplication across test files.
"""

import frappe
import threading
from datetime import datetime, timedelta
from unittest.mock import patch


def create_test_council(council_code="TEST", council_name=None):
    """
    Create a test council fixture.

    Args:
        council_code: Unique council code (default: "TEST")
        council_name: Council display name (default: "Test Council")

    Returns:
        Council document
    """
    if not council_name:
        council_name = f"{council_code} Council"

    # Check if council already exists
    try:
        existing = frappe.db.exists("Council", council_code)
        if existing:
            return frappe.get_doc("Council", council_code)
    except:
        pass

    council = frappe.get_doc({
        "doctype": "Council",
        "council_code": council_code,
        "council_name": council_name,
        "contact_email": f"{council_code.lower()}@example.com",
        "phone": "021-000-0000",
        "address": "123 Test Street",
        "city": "Test City",
        "region": "Test Region",
        "country": "New Zealand"
    })

    try:
        council.insert(ignore_permissions=True)
        frappe.db.commit()
    except (frappe.UniqueValidationError, frappe.exceptions.UniqueValidationError):
        # Council already exists from a previous run, return it
        try:
            return frappe.get_doc("Council", council_code)
        except:
            # If we can't get it, it's a test environment issue
            # Just skip this for now
            pass

    return council


def create_test_organization(org_code):
    """
    Create a test Organization if it doesn't exist.
    
    Args:
        org_code: Organization code/name
        
    Returns:
        Organization document
    """
    existing = frappe.db.exists("Organization", org_code)
    if existing:
        return frappe.get_doc("Organization", existing)
    
    org = frappe.get_doc({
        "doctype": "Organization",
        "name": org_code,
        "organization_name": f"Test Organization {org_code}",
        "organization_type": "Testing",
        "phone": "021-000-0000",
        "email": f"{org_code.lower()}@test.org",
        "physical_address": "123 Test Street"
    })
    
    org.insert(ignore_permissions=True)
    frappe.db.commit()
    return org


def create_test_request(council_code, request_id=None, requester_email=None):
    """
    Create a test request fixture.

    Args:
        council_code: Council code for the request
        request_id: Custom request ID (optional, auto-generated if not provided)
        requester_email: Requester email (optional)

    Returns:
        Request document
    """
    if not request_id:
        # Generate unique request ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        request_id = f"REQ-{council_code}-{timestamp}"

    # Check if request already exists
    existing = frappe.db.exists("Request", request_id)
    if existing:
        return frappe.get_doc("Request", existing)

    # Ensure organization exists
    create_test_organization(council_code)
    
    # Use Administrator for requester (always exists)
    if not requester_email:
        requester_email = "Administrator"

    request = frappe.get_doc({
        "doctype": "Request",
        "request_number": request_id,
        "organization": council_code,
        "requester": requester_email,
        "requester_phone": "+64 21 000 0000",
        "workflow_state": "Draft",
        "brief_description": "Test request for automated testing"
    })

    # Disable workflow emails globally for tests
    frappe.flags.in_test = True
    frappe.flags.mute_emails = True

    # Patch workflow email sending to prevent PDF generation errors
    with patch('frappe.workflow.doctype.workflow_action.workflow_action.send_workflow_action_email'):
        request.insert(ignore_permissions=True)
        frappe.db.commit()

    return request


def create_test_assessment_project(request_id, **kwargs):
    """
    Create a test Assessment Project fixture.

    Args:
        request_id: Request ID to link to
        **kwargs: Additional fields to override

    Returns:
        Assessment Project document
    """
    # Check if Assessment Project already exists for this request
    existing = frappe.db.get_value(
        "Assessment Project",
        {"request": request_id},
        "name"
    )

    if existing:
        return frappe.get_doc("Assessment Project", existing)

    data = {
        "doctype": "Assessment Project",
        "request": request_id,
        "project_owner": kwargs.get("project_owner", "Administrator"),
        "target_completion_date": kwargs.get(
            "target_completion_date",
            (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        ),
        "status": kwargs.get("status", "Active")
    }

    # Override with any additional kwargs
    data.update(kwargs)

    project = frappe.get_doc(data)
    project.insert(ignore_permissions=True)
    frappe.db.commit()

    return project


def create_test_project_task(request_id, **kwargs):
    """
    Create a test Project Task fixture.

    Args:
        request_id: Request ID to link to
        **kwargs: Additional fields to override

    Returns:
        Project Task document
    """
    data = {
        "doctype": "Project Task",
        "title": kwargs.get("title", "Test Project Task"),
        "request": request_id,
        "assigned_to": kwargs.get("assigned_to", "Administrator"),
        "assigned_by": kwargs.get("assigned_by", "Administrator"),
        "priority": kwargs.get("priority", "Medium"),
        "status": kwargs.get("status", "Open"),
        "estimated_hours": kwargs.get("estimated_hours", 5.0),
        "start_date": kwargs.get(
            "start_date",
            datetime.now().strftime("%Y-%m-%d")
        ),
        "due_date": kwargs.get(
            "due_date",
            (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        )
    }

    # Override with any additional kwargs
    for key in ["assigned_role", "assessment_project", "description"]:
        if key in kwargs:
            data[key] = kwargs[key]

    task = frappe.get_doc(data)
    task.insert(ignore_permissions=True)
    frappe.db.commit()

    return task


def cleanup_test_data(doctype, filters=None):
    """
    Clean up test data after tests.

    Args:
        doctype: DocType name to clean
        filters: Optional filters for deletion (dict)

    Returns:
        Number of records deleted
    """
    if filters is None:
        filters = {}

    # Get all matching records
    records = frappe.get_all(doctype, filters=filters, pluck="name")

    count = 0
    for name in records:
        try:
            frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
            count += 1
        except Exception as e:
            frappe.log_error(f"Failed to delete {doctype} {name}: {str(e)}")

    frappe.db.commit()
    return count


def get_series_counter(series_key):
    """
    Get the current Series counter value from the database.

    Args:
        series_key: Series key (e.g., "TASK-2025-")

    Returns:
        Current counter value (int) or None if not found
    """
    result = frappe.db.sql(
        """SELECT current FROM `tabSeries` WHERE name = %s""",
        (series_key,),
        as_dict=True
    )

    if result:
        return result[0].get("current", 0)
    return None


def set_series_counter(series_key, value):
    """
    Set the Series counter value (useful for test setup).

    Args:
        series_key: Series key (e.g., "TASK-2025-")
        value: Counter value to set

    Returns:
        None
    """
    existing = frappe.db.exists("Series", series_key)

    if existing:
        frappe.db.sql(
            """UPDATE `tabSeries` SET current = %s WHERE name = %s""",
            (value, series_key)
        )
    else:
        frappe.db.sql(
            """INSERT INTO `tabSeries` (name, current) VALUES (%s, %s)""",
            (series_key, value)
        )

    frappe.db.commit()


def wait_for_threads(threads, timeout=30):
    """
    Wait for thread completion with timeout.

    Args:
        threads: List of Thread objects
        timeout: Maximum wait time in seconds (default: 30)

    Returns:
        True if all threads completed, False if timeout occurred
    """
    import time
    start_time = time.time()

    for thread in threads:
        remaining_time = timeout - (time.time() - start_time)
        if remaining_time <= 0:
            return False

        thread.join(timeout=remaining_time)

        if thread.is_alive():
            return False

    return True


def assert_no_duplicate_errors(errors):
    """
    Common assertion for duplicate key errors in concurrent tests.

    Args:
        errors: List of error dictionaries from concurrent operations

    Raises:
        AssertionError: If duplicate entry errors are found
    """
    duplicate_errors = [
        e for e in errors
        if "Duplicate entry" in str(e.get("error", ""))
    ]

    if duplicate_errors:
        error_details = "\n".join([
            f"  - {e.get('task', e.get('item', 'unknown'))}: {e.get('error')}"
            for e in duplicate_errors
        ])
        raise AssertionError(
            f"Found {len(duplicate_errors)} duplicate key errors:\n{error_details}"
        )


def create_test_council_meeting(request_id, **kwargs):
    """
    Create a test Council Meeting fixture.

    Args:
        request_id: Request ID to link to
        **kwargs: Additional fields to override

    Returns:
        Council Meeting document
    """
    data = {
        "doctype": "Council Meeting",
        "request": request_id,
        "meeting_date": kwargs.get(
            "meeting_date",
            (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        ),
        "meeting_time": kwargs.get("meeting_time", "10:00:00"),
        "duration_minutes": kwargs.get("duration_minutes", 60),
        "meeting_type": kwargs.get("meeting_type", "Pre-Application"),
        "status": kwargs.get("status", "Scheduled")
    }

    # Override with any additional kwargs
    data.update(kwargs)

    meeting = frappe.get_doc(data)
    meeting.insert(ignore_permissions=True)
    frappe.db.commit()

    return meeting


def reset_series_counter(prefix):
    """
    Reset a series counter to zero (useful for test isolation).

    Args:
        prefix: Series prefix (e.g., "TASK-2025-")

    Returns:
        None
    """
    year = datetime.now().year
    series_key = f"{prefix}{year}-"

    frappe.db.sql(
        """DELETE FROM `tabSeries` WHERE name = %s""",
        (series_key,)
    )
    frappe.db.commit()


def get_test_user_email():
    """
    Get or create a test user email for tests.

    Returns:
        Test user email address
    """
    test_user = "test.user@lodgeick.test"

    if not frappe.db.exists("User", test_user):
        user = frappe.get_doc({
            "doctype": "User",
            "email": test_user,
            "first_name": "Test",
            "last_name": "User",
            "enabled": 1,
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)
        frappe.db.commit()

    return test_user
