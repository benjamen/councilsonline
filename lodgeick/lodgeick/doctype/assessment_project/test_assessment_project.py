# Copyright (c) 2025, Essdee and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days
from unittest.mock import patch


class TestAssessmentProject(FrappeTestCase):
	@patch('frappe.attach_print')
	def setUp(self, mock_attach_print):
		"""Set up test data"""
		# Mock PDF generation to avoid wkhtmltopdf errors during workflow emails
		mock_attach_print.return_value = None

		# Disable email and print generation during tests
		frappe.flags.in_test = True
		frappe.flags.mute_emails = True

		# Create test council if it doesn't exist (council_code becomes the name)
		council_code = "TST"
		if not frappe.db.exists("Council", council_code):
			council = frappe.get_doc({
				"doctype": "Council",
				"council_name": "Test Council",
				"council_code": council_code,
				"council_type": "Territorial Authority",
				"contact_email": "test@testcouncil.govt.nz"
			})
			council.insert(ignore_permissions=True, ignore_if_duplicate=True)
			frappe.db.commit()

		# Create test request if it doesn't exist
		if not frappe.db.exists("Request", "TEST-REQ-001"):
			request = frappe.get_doc({
				"doctype": "Request",
				"name": "TEST-REQ-001",
				"council": council_code,  # Use council_code which is the name
				"request_type": "Resource Consent",
				"requester": "Administrator",
				"brief_description": "Test request for assessment project testing",
				"title": "Test Request"
			})
			request.insert(ignore_permissions=True, ignore_if_duplicate=True)
			frappe.db.commit()

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

		# Should raise either ValidationError (from our validate method) or
		# DuplicateEntryError (from database constraint) - both indicate the same issue
		with self.assertRaises((frappe.ValidationError, frappe.DuplicateEntryError)):
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
