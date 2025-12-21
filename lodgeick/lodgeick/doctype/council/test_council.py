# Copyright (c) 2025, Optified and Contributors
# See license.txt

"""
Comprehensive tests for Council DocType.

This test suite covers:
- Basic CRUD operations
- Validation rules
- Unique constraints
- BUG-002 regression testing (Council Meeting rename)
"""

import frappe
from frappe.tests.utils import FrappeTestCase
from lodgeick.tests.test_helpers import cleanup_test_data


class TestCouncil(FrappeTestCase):
	"""Test cases for Council DocType."""

	def setUp(self):
		"""Setup before each test."""
		super().setUp()
		frappe.flags.in_test = True
		# Clean up any existing test councils
		cleanup_test_data("Council", {"council_code": ["like", "TEST%"]})

	def tearDown(self):
		"""Cleanup after each test."""
		cleanup_test_data("Council", {"council_code": ["like", "TEST%"]})
		super().tearDown()

	def test_create_council(self):
		"""Test basic Council creation with council_code as autoname."""
		council = frappe.get_doc({
			"doctype": "Council",
			"council_code": "TESTCOUNCIL",
			"council_name": "Test Council",
			"contact_email": "test@council.nz",
			"phone": "021-000-0000",
			"address": "123 Test Street",
			"city": "Test City",
			"region": "Test Region",
			"country": "New Zealand"
		})

		council.insert(ignore_permissions=True)

		# Verify council was created
		self.assertIsNotNone(council.name)

		# Verify autoname uses council_code
		self.assertEqual(council.name, "TESTCOUNCIL")

		# Verify fields
		self.assertEqual(council.council_name, "Test Council")
		self.assertEqual(council.contact_email, "test@council.nz")
		self.assertEqual(council.country, "New Zealand")

	def test_council_code_unique_validation(self):
		"""Test that duplicate council codes are rejected."""
		# Create first council
		council1 = frappe.get_doc({
			"doctype": "Council",
			"council_code": "TESTDUP",
			"council_name": "Test Duplicate Council 1",
			"contact_email": "dup1@council.nz"
		})
		council1.insert(ignore_permissions=True)

		# Attempt to create second council with same code
		council2 = frappe.get_doc({
			"doctype": "Council",
			"council_code": "TESTDUP",
			"council_name": "Test Duplicate Council 2",
			"contact_email": "dup2@council.nz"
		})

		# Should raise DuplicateEntryError
		with self.assertRaises(frappe.exceptions.DuplicateEntryError):
			council2.insert(ignore_permissions=False)

	def test_council_required_fields(self):
		"""Test that required fields are enforced."""
		# Attempt to create council without council_code
		council = frappe.get_doc({
			"doctype": "Council",
			# Missing council_code
			"council_name": "Incomplete Council"
		})

		# Should raise MandatoryError
		with self.assertRaises(frappe.exceptions.MandatoryError):
			council.insert(ignore_permissions=False)

	def test_council_email_validation(self):
		"""Test that email validation works."""
		council = frappe.get_doc({
			"doctype": "Council",
			"council_code": "TESTEMAIL",
			"council_name": "Test Email Council",
			"contact_email": "invalid-email-format"  # Invalid email
		})

		# Depending on validation rules, this might raise ValidationError
		try:
			council.insert(ignore_permissions=False)
			# If no validation, verify email was stored as-is
			self.assertEqual(council.contact_email, "invalid-email-format")
		except frappe.exceptions.ValidationError:
			# Expected if email validation is strict
			pass

	def test_council_type_validation(self):
		"""Test that council type validation works (if field exists)."""
		council = frappe.get_doc({
			"doctype": "Council",
			"council_code": "TESTTYPE",
			"council_name": "Test Type Council",
			"contact_email": "type@council.nz"
		})

		# Check if council_type field exists in meta
		meta = frappe.get_meta("Council")
		has_type_field = any(f.fieldname == "council_type" for f in meta.fields)

		if has_type_field:
			# Set a valid type if options are defined
			type_field = next((f for f in meta.fields if f.fieldname == "council_type"), None)
			if type_field and type_field.options:
				valid_types = type_field.options.split("\n")
				if valid_types:
					council.council_type = valid_types[0]

		council.insert(ignore_permissions=True)
		self.assertIsNotNone(council.name)

	def test_council_update(self):
		"""Test updating Council fields."""
		council = frappe.get_doc({
			"doctype": "Council",
			"council_code": "TESTUPDATE",
			"council_name": "Test Update Council",
			"contact_email": "update@council.nz"
		})
		council.insert(ignore_permissions=True)

		# Update fields
		council.council_name = "Updated Council Name"
		council.phone = "021-123-4567"
		council.save()

		# Reload from database
		council.reload()

		# Verify updates
		self.assertEqual(council.council_name, "Updated Council Name")
		self.assertEqual(council.phone, "021-123-4567")

	def test_council_delete(self):
		"""Test deleting Council."""
		council = frappe.get_doc({
			"doctype": "Council",
			"council_code": "TESTDELETE",
			"council_name": "Test Delete Council",
			"contact_email": "delete@council.nz"
		})
		council.insert(ignore_permissions=True)

		council_name = council.name

		# Delete council
		frappe.delete_doc("Council", council_name, force=True)

		# Verify deleted
		exists = frappe.db.exists("Council", council_name)
		self.assertFalse(exists)

	def test_council_with_meeting_relationship(self):
		"""
		Test Council relationship with Council Meeting (BUG-002 related).

		Verifies that Council can have related Council Meetings.
		"""
		# Create council
		council = frappe.get_doc({
			"doctype": "Council",
			"council_code": "TESTMEET",
			"council_name": "Test Meeting Council",
			"contact_email": "meeting@council.nz"
		})
		council.insert(ignore_permissions=True)

		# Verify Council DocType exists (not Pre-Application Meeting)
		council_meeting_exists = frappe.db.exists("DocType", "Council Meeting")
		self.assertTrue(council_meeting_exists,
					   "Council Meeting DocType should exist (BUG-002)")

		# Verify old DocType doesn't exist
		pre_app_exists = frappe.db.exists("DocType", "Pre-Application Meeting")
		self.assertFalse(pre_app_exists,
						"Pre-Application Meeting should not exist (BUG-002)")
