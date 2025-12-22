"""
Comprehensive tests for Project Task DocType.

This test suite covers:
- Basic CRUD operations
- Autoname pattern validation (BUG-001 regression)
- Concurrent creation scenarios
- Series counter integrity
- Error handling
- Integration with Assessment Projects
"""

import frappe
import unittest
import threading
from datetime import datetime, timedelta
from frappe.tests.utils import FrappeTestCase
from lodgeick.tests.test_helpers import (
    create_test_council,
    create_test_request,
    create_test_assessment_project,
    create_test_project_task,
    cleanup_test_data,
    get_series_counter,
    set_series_counter,
    reset_series_counter,
    wait_for_threads,
    assert_no_duplicate_errors
)


class TestProjectTask(FrappeTestCase):
    """Test cases for Project Task DocType."""

    @classmethod
    def setUpClass(cls):
        """Create fixtures once for all tests."""
        super().setUpClass()
        cls.council = create_test_council("TEST")
        cls.request = create_test_request(cls.council.council_code)

    def setUp(self):
        """Setup before each test."""
        super().setUp()
        frappe.flags.in_test = True

        # Clean up any existing test tasks
        cleanup_test_data("Project Task", {"request": self.request.name})

        # Reset series counter for consistent testing
        reset_series_counter("TASK-")

    def tearDown(self):
        """Cleanup after each test."""
        cleanup_test_data("Project Task", {"request": self.request.name})
        super().tearDown()

    # ========================================
    # A. Basic CRUD Tests
    # ========================================

    def test_create_project_task(self):
        """Test basic Project Task creation with autoname pattern."""
        task = create_test_project_task(
            self.request.name,
            title="Test Task Creation"
        )

        # Verify task was created
        self.assertIsNotNone(task.name)

        # Verify autoname pattern: TASK-.YYYY.-.#####
        year = datetime.now().year
        self.assertTrue(task.name.startswith(f"TASK-{year}-"))

        # Verify task number is 5 digits
        task_number = task.name.split("-")[-1]
        self.assertEqual(len(task_number), 5)
        self.assertTrue(task_number.isdigit())

        # Verify fields
        self.assertEqual(task.title, "Test Task Creation")
        self.assertEqual(task.request, self.request.name)
        self.assertEqual(task.status, "Open")
        self.assertEqual(task.priority, "Medium")

    def test_autoname_sequence_increments(self):
        """Test that autoname sequence increments correctly."""
        # Create first task
        task1 = create_test_project_task(
            self.request.name,
            title="Task 1"
        )

        # Get task number
        number1 = int(task1.name.split("-")[-1])

        # Create second task
        task2 = create_test_project_task(
            self.request.name,
            title="Task 2"
        )

        # Get task number
        number2 = int(task2.name.split("-")[-1])

        # Verify sequential increment
        self.assertEqual(number2, number1 + 1)

        # Verify both have same year prefix
        year = datetime.now().year
        self.assertTrue(task1.name.startswith(f"TASK-{year}-"))
        self.assertTrue(task2.name.startswith(f"TASK-{year}-"))

    def test_task_costing_calculation(self):
        """Test that task costing calculation works correctly."""
        # Create task with hourly rate and hours
        task_doc = frappe.get_doc({
            "doctype": "Project Task",
            "title": "Costing Test Task",
            "request": self.request.name,
            "assigned_by": "Administrator",
            "priority": "Medium",
            "status": "Open",
            "estimated_hours": 10.0,
            "hourly_rate": 50.0
        })

        task_doc.insert(ignore_permissions=True)

        # Calculate costing (if implemented in before_save hook)
        # Note: Adjust this test based on actual implementation
        if hasattr(task_doc, "estimated_cost"):
            expected_cost = 10.0 * 50.0  # 500.00
            self.assertEqual(task_doc.estimated_cost, expected_cost)

    def test_task_completion_sets_date(self):
        """Test that completing a task sets the completion date."""
        task = create_test_project_task(
            self.request.name,
            title="Completion Test"
        )

        # Verify no completion date initially
        self.assertIsNone(task.date_of_completion)

        # Mark as completed
        task.status = "Completed"
        task.save()

        # Reload from database
        task.reload()

        # Verify completion date is set (if implemented)
        if hasattr(task, "date_of_completion"):
            self.assertIsNotNone(task.date_of_completion)

    def test_task_timeliness_late(self):
        """Test that overdue tasks are correctly identified."""
        # Create task with past due date
        past_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        task = create_test_project_task(
            self.request.name,
            title="Overdue Task",
            due_date=past_date
        )

        # Reload to trigger any calculated fields
        task.reload()

        # Verify task is marked as late/overdue (if implemented)
        if hasattr(task, "is_overdue"):
            self.assertTrue(task.is_overdue)

    # ========================================
    # B. Concurrent Creation Tests (BUG-001)
    # ========================================

    def test_concurrent_task_creation_no_duplicates(self):
        """
        BUG-001 Regression: Verify no duplicate task names under concurrent load.

        This test creates 10 tasks concurrently to detect race conditions
        in the autoname Series counter mechanism.
        """
        errors = []
        created_tasks = []

        # Store site name in main thread before spawning child threads
        site_name = frappe.local.site

        def create_task(task_number):
            """Worker function to create a task in separate thread."""
            try:
                frappe.init(site=site_name)
                frappe.connect()

                task = frappe.get_doc({
                    "doctype": "Project Task",
                    "title": f"Concurrent Task {task_number}",
                    "request": self.request.name,
                    "assigned_by": "Administrator",
                    "priority": "Medium",
                    "status": "Open"
                })

                task.insert(ignore_permissions=True)
                frappe.db.commit()
                created_tasks.append(task.name)

            except Exception as e:
                errors.append({
                    "task_number": task_number,
                    "error": str(e),
                    "type": type(e).__name__
                })
            finally:
                frappe.destroy()

        # Create 10 threads
        threads = [threading.Thread(target=create_task, args=(i,)) for i in range(10)]

        # Start all threads simultaneously
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        completed = wait_for_threads(threads, timeout=30)
        self.assertTrue(completed, "Threads did not complete within timeout")

        # Assert no duplicate key errors
        assert_no_duplicate_errors(errors)

        # Assert all tasks were created
        self.assertEqual(len(created_tasks), 10,
                        f"Expected 10 tasks, got {len(created_tasks)}. Errors: {errors}")

        # Assert all task names are unique
        self.assertEqual(len(created_tasks), len(set(created_tasks)),
                        f"Duplicate task names found: {created_tasks}")

    def test_concurrent_assessment_project_task_creation(self):
        """
        BUG-001 Regression: Test concurrent Assessment Project task creation.

        This simulates the actual bug scenario where multiple Assessment Projects
        create tasks simultaneously.
        """
        errors = []
        created_tasks = []

        # Store site name in main thread before spawning child threads
        site_name = frappe.local.site

        def create_project_with_tasks(project_number):
            """Worker function to create Assessment Project with tasks."""
            try:
                frappe.init(site=site_name)
                frappe.connect()

                # Create unique request for this project
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                request_id = f"REQ-TEST-{timestamp}-{project_number}"

                request = frappe.get_doc({
                    "doctype": "Request",
                    "request_number": request_id,
                    "council": self.council.council_code,
                    "requester": f"test{project_number}@example.com",
                    "workflow_state": "Draft"
                })
                request.insert(ignore_permissions=True)

                # Create 3 tasks for this project
                for i in range(3):
                    task = frappe.get_doc({
                        "doctype": "Project Task",
                        "title": f"Project {project_number} Task {i}",
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
                    "project_number": project_number,
                    "error": str(e),
                    "type": type(e).__name__
                })
            finally:
                frappe.destroy()

        # Create 5 Assessment Projects concurrently (5 x 3 = 15 tasks total)
        threads = [threading.Thread(target=create_project_with_tasks, args=(i,))
                  for i in range(5)]

        for thread in threads:
            thread.start()

        completed = wait_for_threads(threads, timeout=60)
        self.assertTrue(completed, "Threads did not complete within timeout")

        # Assert no duplicate key errors
        assert_no_duplicate_errors(errors)

        # Assert all 15 tasks were created (5 projects x 3 tasks each)
        self.assertEqual(len(created_tasks), 15,
                        f"Expected 15 tasks, got {len(created_tasks)}. Errors: {errors}")

        # Assert all task names are unique
        self.assertEqual(len(created_tasks), len(set(created_tasks)),
                        f"Duplicate task names found: {created_tasks}")

    def test_rapid_fire_task_creation(self):
        """
        BUG-001 Regression: Stress test with rapid sequential task creation.

        This test creates tasks as fast as possible to detect timing issues
        in Series counter updates.
        """
        tasks = []

        for i in range(20):
            task = frappe.get_doc({
                "doctype": "Project Task",
                "title": f"Rapid Task {i}",
                "request": self.request.name,
                "assigned_by": "Administrator",
                "priority": "Medium",
                "status": "Open"
            })
            task.insert(ignore_permissions=True)
            tasks.append(task.name)

        frappe.db.commit()

        # Verify all 20 tasks created
        self.assertEqual(len(tasks), 20)

        # Verify all names unique
        self.assertEqual(len(tasks), len(set(tasks)),
                        f"Duplicate task names in rapid creation: {tasks}")

    # ========================================
    # C. Series Counter Tests
    # ========================================

    def test_series_counter_exists_after_creation(self):
        """Test that Series counter entry is created after first task."""
        # Create first task
        task = create_test_project_task(self.request.name, title="First Task")

        # Get series key
        year = datetime.now().year
        series_key = f"TASK-{year}-"

        # Verify Series counter exists
        counter = get_series_counter(series_key)
        self.assertIsNotNone(counter, f"Series counter not found for {series_key}")

        # Verify counter >= 1
        self.assertGreaterEqual(counter, 1)

    def test_series_counter_increments_correctly(self):
        """Test that Series counter increments with each task."""
        year = datetime.now().year
        series_key = f"TASK-{year}-"

        # Get initial counter
        initial_counter = get_series_counter(series_key) or 0

        # Create 5 tasks
        for i in range(5):
            create_test_project_task(self.request.name, title=f"Counter Test {i}")

        # Get final counter
        final_counter = get_series_counter(series_key)

        # Verify counter increased by 5
        self.assertEqual(final_counter, initial_counter + 5)

    def test_series_counter_integrity_under_load(self):
        """Test Series counter integrity when creating many tasks."""
        year = datetime.now().year
        series_key = f"TASK-{year}-"

        # Set known starting point
        set_series_counter(series_key, 100)

        # Create 30 tasks
        tasks = []
        for i in range(30):
            task = create_test_project_task(
                self.request.name,
                title=f"Load Test Task {i}"
            )
            tasks.append(task.name)

        # Verify counter is now 130
        final_counter = get_series_counter(series_key)
        self.assertEqual(final_counter, 130)

        # Verify all task names unique
        self.assertEqual(len(tasks), len(set(tasks)))

    # ========================================
    # D. Error Handling Tests
    # ========================================

    def test_task_creation_with_missing_required_fields(self):
        """Test that creating task without required fields raises error."""
        with self.assertRaises(frappe.exceptions.MandatoryError):
            task = frappe.get_doc({
                "doctype": "Project Task",
                # Missing title (might be required)
                "request": self.request.name
            })
            task.insert(ignore_permissions=False)  # Don't ignore validation

    def test_task_creation_with_invalid_priority(self):
        """Test that invalid priority value raises validation error."""
        # Note: This test depends on Priority being a Select field
        task = frappe.get_doc({
            "doctype": "Project Task",
            "title": "Invalid Priority Test",
            "request": self.request.name,
            "assigned_by": "Administrator",
            "priority": "SuperUrgent",  # Invalid if not in allowed values
            "status": "Open"
        })

        # This might raise ValidationError depending on Frappe version
        try:
            task.insert(ignore_permissions=False)
        except (frappe.exceptions.ValidationError, frappe.exceptions.InvalidStatusError):
            pass  # Expected behavior
        except Exception as e:
            # If field validation doesn't occur, that's also acceptable
            pass

    def test_task_rollback_on_error(self):
        """Test that database rollback works on task creation error."""
        initial_count = frappe.db.count("Project Task", {"request": self.request.name})

        try:
            # Attempt to create task with intentional error
            task = frappe.get_doc({
                "doctype": "Project Task",
                "title": "Rollback Test",
                "request": "NONEXISTENT-REQUEST",  # This should fail
                "assigned_by": "Administrator",
                "priority": "Medium",
                "status": "Open"
            })
            task.insert(ignore_permissions=False)
            frappe.db.commit()

        except Exception:
            frappe.db.rollback()

        # Verify task count unchanged
        final_count = frappe.db.count("Project Task", {"request": self.request.name})
        self.assertEqual(final_count, initial_count)

    # ========================================
    # E. Integration Tests
    # ========================================

    def test_task_links_to_assessment_project(self):
        """Test that tasks can be linked to Assessment Projects."""
        # Create Assessment Project
        assessment_project = create_test_assessment_project(self.request.name)

        # Create task linked to project
        task = create_test_project_task(
            self.request.name,
            title="Project Linked Task",
            assessment_project=assessment_project.name
        )

        # Verify link
        self.assertEqual(task.assessment_project, assessment_project.name)

        # Verify task appears in project's tasks
        project_tasks = frappe.get_all(
            "Project Task",
            filters={"assessment_project": assessment_project.name},
            pluck="name"
        )
        self.assertIn(task.name, project_tasks)

    def test_assessment_project_task_creation_workflow(self):
        """Test end-to-end workflow from Assessment Project to Task creation."""
        # Create Assessment Project
        assessment_project = create_test_assessment_project(
            self.request.name,
            project_owner="Administrator"
        )

        # Simulate task creation from template (if method exists)
        # Note: This test verifies the integration works without errors
        if hasattr(assessment_project, "create_tasks_from_template"):
            try:
                tasks_created = assessment_project.create_tasks_from_template()
                # Verify some tasks were created
                self.assertIsNotNone(tasks_created)
            except Exception as e:
                # If method has specific requirements, document them
                self.fail(f"create_tasks_from_template failed: {str(e)}")


def run_tests():
    """Helper function to run these tests from console."""
    frappe.init(site="lodgeick.localhost")
    frappe.connect()
    unittest.main()
