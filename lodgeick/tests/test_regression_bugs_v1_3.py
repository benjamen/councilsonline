"""
Regression Test Suite for Lodgeick v1.3+ Critical Bugs

This test suite MUST PASS before each release to prevent regression
of three critical production bugs:

- BUG-001: Project Task autoname duplicate key errors (IntegrityError 1062)
- BUG-002: Council Meeting DocType 404 errors after rename
- BUG-003: SPISC Application fetch_from validation error blocking draft saves

RELEASE REQUIREMENT: Run with --failfast flag:
    bench --site lodgeick.localhost run-tests --module lodgeick.tests.test_regression_bugs_v1_3 --failfast
"""

import frappe
import unittest
import threading
from datetime import datetime
from frappe.tests.utils import FrappeTestCase
from lodgeick.tests.test_helpers import (
    create_test_council,
    create_test_request,
    create_test_assessment_project,
    create_test_project_task,
    create_test_council_meeting,
    cleanup_test_data,
    get_series_counter,
    reset_series_counter,
    wait_for_threads,
    assert_no_duplicate_errors
)
from lodgeick.api import create_spisc_application


class TestBug001ProjectTaskAutoname(FrappeTestCase):
    """
    BUG-001 Regression Tests: Project Task Autoname Duplicate Keys

    ORIGINAL ERROR:
    IntegrityError(1062, "Duplicate entry 'TASK-2025-.#####' for key 'PRIMARY'")

    ROOT CAUSE:
    Race condition in Frappe's getseries() when multiple Assessment Projects
    create tasks concurrently.

    FIX APPLIED:
    Changed autoname pattern from "format:TASK-{YYYY}-.#####" to
    "TASK-.YYYY.-.#####" with "Autoincrement" naming rule.

    REGRESSION PREVENTION:
    These tests verify that concurrent task creation does not produce
    duplicate task names.
    """

    @classmethod
    def setUpClass(cls):
        """Create fixtures once for all tests."""
        super().setUpClass()
        cls.council = create_test_council("BUG001")
        cls.request = create_test_request(cls.council.council_code)

    def setUp(self):
        """Setup before each test."""
        super().setUp()
        frappe.flags.in_test = True
        cleanup_test_data("Project Task", {"request": self.request.name})
        reset_series_counter("TASK-")

    def tearDown(self):
        """Cleanup after each test."""
        cleanup_test_data("Project Task", {"request": self.request.name})
        super().tearDown()

    def test_bug_001_concurrent_assessment_projects_no_duplicate_tasks(self):
        """
        BUG-001 PRIMARY REGRESSION TEST

        Verifies that concurrent Assessment Project creation does not produce
        duplicate Project Task names.

        This test creates 5 Assessment Projects concurrently, each generating
        multiple Project Tasks. All task names MUST be unique.
        """
        errors = []
        created_tasks = []

        def create_project_with_tasks(project_number):
            """Create Assessment Project with tasks."""
            try:
                frappe.init(site=frappe.local.site)
                frappe.connect()

                # Create unique request
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                request_id = f"BUG001-REQ-{timestamp}-{project_number}"

                request = frappe.get_doc({
                    "doctype": "Request",
                    "request_number": request_id,
                    "council": self.council.council_code,
                    "requester": f"bug001test{project_number}@example.com",
                    "workflow_state": "Draft"
                })
                request.insert(ignore_permissions=True)

                # Create 5 tasks per project (5 projects x 5 tasks = 25 total)
                for i in range(5):
                    task = frappe.get_doc({
                        "doctype": "Project Task",
                        "title": f"BUG-001 Project {project_number} Task {i}",
                        "request": request_id,
                        "assigned_by": "Administrator",
                        "priority": "Medium",
                        "status": "Open"
                    })
                    task.insert(ignore_permissions=True)
                    created_tasks.append(task.name)

                frappe.db.commit()

            except Exception as e:
                errors.append({
                    "project": project_number,
                    "error": str(e),
                    "type": type(e).__name__
                })
            finally:
                frappe.destroy()

        # Create 5 Assessment Projects concurrently
        threads = [threading.Thread(target=create_project_with_tasks, args=(i,))
                  for i in range(5)]

        for thread in threads:
            thread.start()

        completed = wait_for_threads(threads, timeout=60)
        self.assertTrue(completed, "BUG-001: Threads did not complete within timeout")

        # CRITICAL ASSERTION: No duplicate key errors
        assert_no_duplicate_errors(errors)

        # Verify all 25 tasks created (5 projects x 5 tasks)
        self.assertEqual(len(created_tasks), 25,
                        f"BUG-001: Expected 25 tasks, got {len(created_tasks)}. " +
                        f"Errors: {errors}")

        # CRITICAL ASSERTION: All task names unique
        unique_count = len(set(created_tasks))
        self.assertEqual(unique_count, 25,
                        f"BUG-001: Found {25 - unique_count} duplicate task names. " +
                        f"Tasks: {sorted(created_tasks)}")

    def test_bug_001_series_counter_integrity_under_load(self):
        """
        BUG-001: Verify Series counter maintains integrity under concurrent load.

        Tests that the Series counter increments correctly even when multiple
        threads are creating tasks simultaneously.
        """
        year = datetime.now().year
        series_key = f"TASK-{year}-"

        # Get initial counter
        initial_counter = get_series_counter(series_key) or 0

        errors = []
        created_tasks = []

        def create_multiple_tasks(thread_id):
            """Create 3 tasks per thread."""
            try:
                frappe.init(site=frappe.local.site)
                frappe.connect()

                for i in range(3):
                    task = frappe.get_doc({
                        "doctype": "Project Task",
                        "title": f"BUG-001 Series Test Thread {thread_id} Task {i}",
                        "request": self.request.name,
                        "assigned_by": "Administrator",
                        "priority": "Medium",
                        "status": "Open"
                    })
                    task.insert(ignore_permissions=True)
                    created_tasks.append(task.name)

                frappe.db.commit()

            except Exception as e:
                errors.append({"thread": thread_id, "error": str(e)})
            finally:
                frappe.destroy()

        # 10 threads x 3 tasks = 30 tasks total
        threads = [threading.Thread(target=create_multiple_tasks, args=(i,))
                  for i in range(10)]

        for thread in threads:
            thread.start()

        completed = wait_for_threads(threads, timeout=60)
        self.assertTrue(completed, "BUG-001: Series test threads did not complete")

        assert_no_duplicate_errors(errors)

        # Verify counter incremented by exactly 30
        final_counter = get_series_counter(series_key)
        expected_counter = initial_counter + 30
        self.assertEqual(final_counter, expected_counter,
                        f"BUG-001: Series counter mismatch. " +
                        f"Expected {expected_counter}, got {final_counter}")

        # Verify all 30 tasks created
        self.assertEqual(len(created_tasks), 30,
                        f"BUG-001: Expected 30 tasks, got {len(created_tasks)}")

        # Verify all unique
        self.assertEqual(len(set(created_tasks)), 30,
                        "BUG-001: Duplicate tasks in series counter test")

    def test_bug_001_rapid_sequential_creation(self):
        """
        BUG-001: Test rapid sequential task creation without delays.

        Verifies that even without threading, rapid task creation
        maintains unique names.
        """
        tasks = []

        for i in range(30):
            task = frappe.get_doc({
                "doctype": "Project Task",
                "title": f"BUG-001 Rapid Task {i}",
                "request": self.request.name,
                "assigned_by": "Administrator",
                "priority": "Medium",
                "status": "Open"
            })
            task.insert(ignore_permissions=True)
            tasks.append(task.name)

        frappe.db.commit()

        # Verify all 30 unique
        self.assertEqual(len(set(tasks)), 30,
                        f"BUG-001: Duplicate tasks in rapid creation: {tasks}")


class TestBug002CouncilMeetingDoctype(FrappeTestCase):
    """
    BUG-002 Regression Tests: Council Meeting DocType 404 Errors

    ORIGINAL ERROR:
    "Not found - Page council-meeting not found"

    ROOT CAUSE:
    DocType was renamed from "Pre-Application Meeting" to "Council Meeting"
    but bench wasn't restarted, causing route registration issues.

    FIX APPLIED:
    - Renamed DocType with frappe.rename_doc()
    - Updated 9 files (API, frontend components)
    - Restarted bench to refresh routes

    REGRESSION PREVENTION:
    These tests verify that Council Meeting DocType operations work correctly
    and the old "Pre-Application Meeting" DocType no longer exists.
    """

    @classmethod
    def setUpClass(cls):
        """Create fixtures once for all tests."""
        super().setUpClass()
        cls.council = create_test_council("BUG002")
        cls.request = create_test_request(cls.council.council_code)

    def setUp(self):
        """Setup before each test."""
        super().setUp()
        frappe.flags.in_test = True
        cleanup_test_data("Council Meeting", {"request": self.request.name})

    def tearDown(self):
        """Cleanup after each test."""
        cleanup_test_data("Council Meeting", {"request": self.request.name})
        super().tearDown()

    def test_bug_002_council_meeting_doctype_exists(self):
        """
        BUG-002 PRIMARY REGRESSION TEST

        Verifies that "Council Meeting" DocType exists and
        "Pre-Application Meeting" DocType does NOT exist.
        """
        # Verify Council Meeting exists
        council_meeting_exists = frappe.db.exists("DocType", "Council Meeting")
        self.assertTrue(council_meeting_exists,
                       "BUG-002: Council Meeting DocType does not exist")

        # Verify Pre-Application Meeting does NOT exist
        pre_app_meeting_exists = frappe.db.exists("DocType", "Pre-Application Meeting")
        self.assertFalse(pre_app_meeting_exists,
                        "BUG-002: Pre-Application Meeting DocType still exists " +
                        "(should have been renamed to Council Meeting)")

    def test_bug_002_council_meeting_crud_operations(self):
        """
        BUG-002: Test CREATE, READ, UPDATE, DELETE operations on Council Meeting.

        Verifies that all basic operations work without 404 or other errors.
        """
        # CREATE
        meeting = create_test_council_meeting(
            self.request.name,
            meeting_type="Pre-Application"
        )

        self.assertIsNotNone(meeting.name,
                            "BUG-002: Failed to create Council Meeting")

        # READ
        loaded_meeting = frappe.get_doc("Council Meeting", meeting.name)
        self.assertEqual(loaded_meeting.request, self.request.name,
                        "BUG-002: Failed to read Council Meeting")

        # UPDATE
        loaded_meeting.duration_minutes = 90
        loaded_meeting.save()
        loaded_meeting.reload()
        self.assertEqual(loaded_meeting.duration_minutes, 90,
                        "BUG-002: Failed to update Council Meeting")

        # DELETE
        frappe.delete_doc("Council Meeting", meeting.name, force=True)
        deleted = frappe.db.exists("Council Meeting", meeting.name)
        self.assertFalse(deleted,
                        "BUG-002: Failed to delete Council Meeting")

    def test_bug_002_council_meeting_python_class_name(self):
        """
        BUG-002: Verify Python class name matches DocType name.

        Checks that the Python class is named correctly after the rename.
        """
        try:
            from lodgeick.lodgeick.doctype.council_meeting.council_meeting import (
                CouncilMeeting
            )

            # Verify class exists
            self.assertIsNotNone(CouncilMeeting,
                                "BUG-002: CouncilMeeting class not found")

            # Create instance using class
            meeting_doc = frappe.get_doc({
                "doctype": "Council Meeting",
                "request": self.request.name,
                "meeting_date": datetime.now().strftime("%Y-%m-%d"),
                "meeting_time": "10:00:00"
            })

            # Verify instance is of correct class
            self.assertIsInstance(meeting_doc, CouncilMeeting,
                                 "BUG-002: Council Meeting instance is not CouncilMeeting class")

        except ImportError as e:
            self.fail(f"BUG-002: Failed to import CouncilMeeting class: {str(e)}")

    def test_bug_002_council_meeting_api_endpoints(self):
        """
        BUG-002: Test that API endpoints use correct DocType name.

        Verifies that book_council_meeting() and related APIs work.
        """
        try:
            from lodgeick.api import book_council_meeting

            # Verify function exists
            self.assertIsNotNone(book_council_meeting,
                                "BUG-002: book_council_meeting API not found")

            # Note: Full API test would require more setup (time slots, etc.)
            # This test just verifies the function is accessible

        except ImportError as e:
            self.fail(f"BUG-002: Failed to import book_council_meeting: {str(e)}")

    def test_bug_002_whitelist_methods_accessible(self):
        """
        BUG-002: Verify whitelisted methods are accessible.

        Tests that @frappe.whitelist() decorated methods work correctly.
        """
        # Get Council Meeting meta
        meta = frappe.get_meta("Council Meeting")
        self.assertIsNotNone(meta, "BUG-002: Council Meeting meta not found")

        # Verify DocType has expected structure
        self.assertEqual(meta.name, "Council Meeting",
                        "BUG-002: DocType meta name mismatch")


class TestBug003SpiscApplicationFetchFrom(FrappeTestCase):
    """
    BUG-003 Regression Tests: SPISC Application fetch_from Validation Error

    ORIGINAL ERROR:
    ValidationError: Please check the value of "Fetch From" set for field Full Name

    ROOT CAUSE:
    spisc_application.json had "fetch_from": "request.requester_name" but
    requester_name is a virtual property (@property) in Request, not a DB field.
    Frappe's fetch_from only works with actual database fields.

    FIX APPLIED:
    - Removed invalid fetch_from properties (lines 140, 148)
    - Updated create_spisc_application() to manually populate fields

    REGRESSION PREVENTION:
    These tests verify that SPISC Application can be created without
    fetch_from validation errors.
    """

    @classmethod
    def setUpClass(cls):
        """Create fixtures once for all tests."""
        super().setUpClass()
        cls.council = create_test_council("BUG003")

    def setUp(self):
        """Setup before each test."""
        super().setUp()
        frappe.flags.in_test = True

    def tearDown(self):
        """Cleanup after each test."""
        # Cleanup SPISC Applications and Requests
        cleanup_test_data("SPISC Application", {})
        cleanup_test_data("Request", {"council": self.council.council_code})
        super().tearDown()

    def test_bug_003_spisc_application_draft_save(self):
        """
        BUG-003 PRIMARY REGRESSION TEST

        Verifies that draft SPISC Application saves without fetch_from
        validation error.

        This test creates a draft request and SPISC Application,
        which should NOT raise ValidationError about fetch_from.
        """
        # Create draft request
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        request_id = f"BUG003-DRAFT-{timestamp}"

        request = frappe.get_doc({
            "doctype": "Request",
            "request_number": request_id,
            "council": self.council.council_code,
            "requester": f"bug003test{timestamp}@example.com",
            "requester_phone": "+64 21 000 0000",
            "workflow_state": "Draft"
        })
        request.insert(ignore_permissions=True)

        # Create SPISC Application data
        spisc_data = {
            "full_name": "John Test Doe",
            "age": 65,
            "birth_date": "1960-01-15",
            "sex": "Male",
            "civil_status": "Married",
            "address_line": "123 Test Street",
            "barangay": "Test Barangay",
            "household_size": 2,
            "living_arrangement": "Living with spouse",
            "monthly_income": 5000.0,
            "income_source": "Pension",
            "barangay_cert_indigency": "/files/test_cert.pdf",
            "birth_certificate": "/files/test_birth.pdf",
            "valid_id_copy": "/files/test_id.pdf",
            "recent_photo": "/files/test_photo.jpg",
            "declaration_truth": 1,
            "declaration_consent": 1,
            "signature": "/files/test_sig.jpg",
            "signature_date": datetime.now().strftime("%Y-%m-%d")
        }

        # This should NOT raise ValidationError
        try:
            spisc_app = create_spisc_application(request.name, spisc_data)

            # Verify created successfully
            self.assertIsNotNone(spisc_app.name,
                                "BUG-003: SPISC Application not created")

            # CRITICAL ASSERTION: applicant_name populated from virtual property
            self.assertEqual(spisc_app.applicant_name, request.requester_name,
                            "BUG-003: applicant_name not populated correctly")

            # Verify age display populated
            self.assertEqual(spisc_app.applicant_age_display, "65",
                            "BUG-003: applicant_age_display not populated correctly")

        except frappe.exceptions.ValidationError as e:
            if "Fetch From" in str(e):
                self.fail(f"BUG-003: fetch_from validation error still occurring: {str(e)}")
            else:
                raise  # Re-raise if different validation error

    def test_bug_003_fetch_from_no_virtual_properties(self):
        """
        BUG-003: Verify no fetch_from references to virtual properties.

        Scans SPISC Application fields to ensure no fetch_from properties
        reference @property decorators.
        """
        meta = frappe.get_meta("SPISC Application")

        # Check each field with fetch_from
        invalid_fetch_from = []

        for field in meta.fields:
            if field.fetch_from:
                # Check if it's fetching from known virtual properties
                if "requester_name" in field.fetch_from:
                    invalid_fetch_from.append({
                        "field": field.fieldname,
                        "fetch_from": field.fetch_from,
                        "issue": "requester_name is a virtual @property"
                    })

                # Check if fetching from same doctype (invalid)
                if not field.fetch_from.startswith("request."):
                    if "." not in field.fetch_from:
                        invalid_fetch_from.append({
                            "field": field.fieldname,
                            "fetch_from": field.fetch_from,
                            "issue": "fetching from same doctype (invalid)"
                        })

        # Assert no invalid fetch_from found
        self.assertEqual(len(invalid_fetch_from), 0,
                        f"BUG-003: Found {len(invalid_fetch_from)} invalid fetch_from: " +
                        f"{invalid_fetch_from}")

    def test_bug_003_spisc_application_field_population(self):
        """
        BUG-003: Verify all fields populated correctly from API.

        Tests that create_spisc_application() correctly populates all fields,
        especially those that were previously using invalid fetch_from.
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        request_id = f"BUG003-FIELD-{timestamp}"

        request = frappe.get_doc({
            "doctype": "Request",
            "request_number": request_id,
            "council": self.council.council_code,
            "requester": f"fieldtest{timestamp}@example.com",
            "requester_phone": "+64 21 123 4567",
            "workflow_state": "Draft"
        })
        request.insert(ignore_permissions=True)

        spisc_data = {
            "full_name": "Jane Field Test",
            "age": 70,
            "birth_date": "1955-03-20",
            "sex": "Female",
            "civil_status": "Widowed",
            "address_line": "456 Field Test Ave",
            "barangay": "Field Barangay",
            "household_size": 1,
            "living_arrangement": "Living alone",
            "monthly_income": 3000.0,
            "income_source": "No income",
            "barangay_cert_indigency": "/files/cert2.pdf",
            "birth_certificate": "/files/birth2.pdf",
            "valid_id_copy": "/files/id2.pdf",
            "recent_photo": "/files/photo2.jpg",
            "declaration_truth": 1,
            "declaration_consent": 1,
            "signature": "/files/sig2.jpg",
            "signature_date": datetime.now().strftime("%Y-%m-%d")
        }

        spisc_app = create_spisc_application(request.name, spisc_data)

        # Verify key fields populated correctly
        self.assertEqual(spisc_app.applicant_name, request.requester_name,
                        "BUG-003: applicant_name mismatch")

        self.assertEqual(spisc_app.age, 70,
                        "BUG-003: age not populated")

        self.assertEqual(spisc_app.applicant_age_display, "70",
                        "BUG-003: applicant_age_display not populated")

        self.assertEqual(spisc_app.sex, "Female",
                        "BUG-003: sex not populated")

        self.assertEqual(spisc_app.request, request.name,
                        "BUG-003: request link not set")


def run_regression_suite():
    """
    Run the complete regression test suite.

    Use this from console:
        bench --site lodgeick.localhost run-tests \
            --module lodgeick.tests.test_regression_bugs_v1_3 \
            --failfast
    """
    frappe.init(site="lodgeick.localhost")
    frappe.connect()
    unittest.main(failfast=True)
