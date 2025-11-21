# Copyright (c) 2025, Essdee and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days


class TestAssessmentProject(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Create test request if it doesn't exist
		if not frappe.db.exists("Request", "TEST-REQ-001"):
			request = frappe.get_doc({
				"doctype": "Request",
				"name": "TEST-REQ-001",
				"request_type": "Resource Consent"
			})
			request.insert(ignore_permissions=True)

	def test_create_assessment_project(self):
		"""Test basic assessment project creation"""
		doc = frappe.get_doc({
			"doctype": "Assessment Project",
			"request": "TEST-REQ-001",
			"project_owner": "Administrator",
			"statutory_clock_days": 20,
			"started_date": now_datetime()
		})
		doc.insert()

		self.assertEqual(doc.request, "TEST-REQ-001")
		self.assertEqual(doc.statutory_clock_days, 20)
		self.assertEqual(doc.overall_status, "Not Started")

		# Clean up
		doc.delete()

	def test_unique_request_validation(self):
		"""Test that only one assessment project can exist per request"""
		# Create first project
		doc1 = frappe.get_doc({
			"doctype": "Assessment Project",
			"request": "TEST-REQ-001",
			"project_owner": "Administrator"
		})
		doc1.insert()

		# Try to create second project for same request
		doc2 = frappe.get_doc({
			"doctype": "Assessment Project",
			"request": "TEST-REQ-001",
			"project_owner": "Administrator"
		})

		with self.assertRaises(frappe.ValidationError):
			doc2.insert()

		# Clean up
		doc1.delete()

	def test_clock_calculation(self):
		"""Test statutory clock calculation"""
		doc = frappe.get_doc({
			"doctype": "Assessment Project",
			"request": "TEST-REQ-001",
			"statutory_clock_days": 20,
			"started_date": add_days(now_datetime(), -10)
		})
		doc.insert()

		# Should calculate elapsed and remaining days
		self.assertIsNotNone(doc.working_days_elapsed)
		self.assertIsNotNone(doc.working_days_remaining)
		self.assertIsNotNone(doc.statutory_deadline)

		# Clean up
		doc.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Delete any test assessment projects
		frappe.db.delete("Assessment Project", {"request": "TEST-REQ-001"})
