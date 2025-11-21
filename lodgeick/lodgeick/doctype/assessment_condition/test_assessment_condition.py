# Copyright (c) 2025, Essdee and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAssessmentCondition(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Create test assessment project if needed
		if not frappe.db.exists("Assessment Project", "TEST-ASSESS-001"):
			project = frappe.get_doc({
				"doctype": "Assessment Project",
				"name": "TEST-ASSESS-001",
				"request": "TEST-REQ-001"
			})
			project.insert(ignore_permissions=True)

	def test_create_condition(self):
		"""Test basic condition creation"""
		doc = frappe.get_doc({
			"doctype": "Assessment Condition",
			"assessment_project": "TEST-ASSESS-001",
			"condition_number": 1,
			"condition_type": "Pre-Commencement",
			"condition_text": "Test condition text",
			"s108aa_purpose": "Administrative matters"
		})
		doc.insert()

		self.assertEqual(doc.condition_number, 1)
		self.assertEqual(doc.condition_status, "Draft")

		# Clean up
		doc.delete()

	def test_auto_assign_condition_number(self):
		"""Test auto-assignment of condition number"""
		doc = frappe.get_doc({
			"doctype": "Assessment Condition",
			"assessment_project": "TEST-ASSESS-001",
			"condition_type": "Lapsing",
			"condition_text": "Test condition"
		})
		doc.insert()

		# Should auto-assign condition number
		self.assertIsNotNone(doc.condition_number)
		self.assertGreater(doc.condition_number, 0)

		# Clean up
		doc.delete()

	def test_unique_condition_number(self):
		"""Test that condition numbers are unique within project"""
		# Create first condition
		doc1 = frappe.get_doc({
			"doctype": "Assessment Condition",
			"assessment_project": "TEST-ASSESS-001",
			"condition_number": 5,
			"condition_type": "Ongoing",
			"condition_text": "First condition"
		})
		doc1.insert()

		# Try to create second condition with same number
		doc2 = frappe.get_doc({
			"doctype": "Assessment Condition",
			"assessment_project": "TEST-ASSESS-001",
			"condition_number": 5,
			"condition_type": "Ongoing",
			"condition_text": "Second condition"
		})

		with self.assertRaises(frappe.ValidationError):
			doc2.insert()

		# Clean up
		doc1.delete()

	def tearDown(self):
		"""Clean up test data"""
		frappe.db.delete("Assessment Condition", {"assessment_project": "TEST-ASSESS-001"})
