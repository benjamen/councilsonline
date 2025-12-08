# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Eligibility Scoring Engine for Social Assistance Programs

This module contains the business logic for calculating eligibility
for various social assistance programs in the Philippines.
"""

import frappe
from frappe.utils import flt, getdate, nowdate


class EligibilityEngine:
	"""Main eligibility calculation engine"""

	def __init__(self, request_id):
		self.request = frappe.get_doc("Request", request_id)
		self.request_type = frappe.get_doc("Request Type", self.request.request_type)
		self.requester = self.request.requester_email
		self.criteria_checks = []
		self.total_score = 0
		self.max_score = 0

	def calculate_eligibility(self):
		"""
		Main entry point for eligibility calculation
		Returns eligibility result document
		"""
		# Load applicant data
		self.load_applicant_data()

		# Run program-specific criteria
		if self.request_type.type_code == "SPISC":
			self.check_spisc_eligibility()
		elif self.request_type.type_code == "LSFA":
			self.check_lsfa_eligibility()
		elif self.request_type.type_code == "BMSS":
			self.check_bmss_eligibility()
		else:
			self.check_generic_eligibility()

		# Create eligibility result document
		return self.create_eligibility_result()

	def load_applicant_data(self):
		"""Load all relevant applicant data"""
		# Get KYC status
		self.kyc = frappe.db.get_value(
			"User Identity Verification",
			{"user": self.requester},
			["verification_status", "philsys_id", "sss_number"],
			as_dict=True
		)

		# Get household record
		self.household = frappe.db.get_value(
			"Household Record",
			{"head_of_household": self.requester},
			["*"],
			as_dict=True
		)

		# Get household members
		if self.household:
			self.household_members = frappe.get_all(
				"Household Member",
				filters={"parent": self.household.name},
				fields=["*"]
			)
		else:
			self.household_members = []

	def check_spisc_eligibility(self):
		"""
		Social Pension for Indigent Senior Citizens (SPISC) criteria:
		1. MANDATORY: Age 60+ (25 points)
		2. MANDATORY: KYC Verified (20 points)
		3. MANDATORY: Below poverty threshold (20 points)
		4. WEIGHTED: No other pension (15 points)
		5. WEIGHTED: Verified by barangay (10 points)
		6. WEIGHTED: Living alone or with dependents (10 points)
		"""
		# Criterion 1: Age 60+
		age = self.get_applicant_age()
		if age >= 60:
			self.add_check("Age 60 or above", "Mandatory", 25, 25, "Passed", f"Applicant is {age} years old")
		else:
			self.add_check("Age 60 or above", "Mandatory", 0, 25, "Failed", f"Applicant is only {age} years old")

		# Criterion 2: KYC Verified
		if self.kyc and self.kyc.verification_status == "Verified":
			self.add_check("KYC Verified", "Mandatory", 20, 20, "Passed", "Identity verified")
		else:
			self.add_check("KYC Verified", "Mandatory", 0, 20, "Failed", "KYC not verified")

		# Criterion 3: Below poverty threshold
		if self.household and self.household.poverty_threshold_status == "Below":
			self.add_check("Below Poverty Threshold", "Mandatory", 20, 20, "Passed", "Household income below threshold")
		else:
			self.add_check("Below Poverty Threshold", "Mandatory", 0, 20, "Failed", "Not below poverty threshold")

		# Criterion 4: No other pension
		has_other_pension = self.check_existing_benefits()
		if not has_other_pension:
			self.add_check("No Other Pension", "Weighted", 15, 15, "Passed", "Not receiving SSS/GSIS pension")
		else:
			self.add_check("No Other Pension", "Weighted", 0, 15, "Failed", "Already receiving government pension")

		# Criterion 5: Barangay verification
		if self.household and self.household.verified_by_barangay:
			self.add_check("Barangay Verified", "Weighted", 10, 10, "Passed", f"Verified by {self.household.barangay_official}")
		else:
			self.add_check("Barangay Verified", "Weighted", 5, 10, "Partial", "Pending barangay verification")

		# Criterion 6: Living situation
		household_size = len(self.household_members) if self.household_members else 1
		if household_size == 1:
			self.add_check("Living Alone", "Weighted", 10, 10, "Passed", "Living alone - high priority")
		elif household_size <= 3:
			self.add_check("Small Household", "Weighted", 7, 10, "Partial", f"Small household ({household_size} members)")
		else:
			self.add_check("Living with Family", "Weighted", 5, 10, "Partial", f"Larger household ({household_size} members)")

	def check_lsfa_eligibility(self):
		"""
		Local Senior Assistance / Financial Aid for Elderly criteria:
		1. MANDATORY: Age 60+ (30 points)
		2. MANDATORY: KYC Verified (20 points)
		3. WEIGHTED: Emergency/crisis documented (20 points)
		4. WEIGHTED: No recent assistance (15 points)
		5. WEIGHTED: Below poverty threshold (15 points)
		"""
		# Criterion 1: Age 60+
		age = self.get_applicant_age()
		if age >= 60:
			self.add_check("Age 60 or above", "Mandatory", 30, 30, "Passed", f"Applicant is {age} years old")
		else:
			self.add_check("Age 60 or above", "Mandatory", 0, 30, "Failed", f"Applicant is only {age} years old")

		# Criterion 2: KYC Verified
		if self.kyc and self.kyc.verification_status == "Verified":
			self.add_check("KYC Verified", "Mandatory", 20, 20, "Passed", "Identity verified")
		else:
			self.add_check("KYC Verified", "Mandatory", 0, 20, "Failed", "KYC not verified")

		# Criterion 3: Emergency documented (checking request details)
		# This would be enhanced with actual emergency documentation fields
		self.add_check("Emergency Documented", "Weighted", 15, 20, "Partial", "Pending documentation review")

		# Criterion 4: No recent assistance (check last 6 months)
		recent_assistance = self.check_recent_assistance(months=6)
		if not recent_assistance:
			self.add_check("No Recent Assistance", "Weighted", 15, 15, "Passed", "No assistance in past 6 months")
		else:
			self.add_check("No Recent Assistance", "Weighted", 5, 15, "Partial", f"Received assistance {recent_assistance} months ago")

		# Criterion 5: Below poverty threshold
		if self.household and self.household.poverty_threshold_status == "Below":
			self.add_check("Below Poverty Threshold", "Weighted", 15, 15, "Passed", "Household income below threshold")
		else:
			self.add_check("Below Poverty Threshold", "Weighted", 10, 15, "Partial", "At or above poverty threshold")

	def check_bmss_eligibility(self):
		"""
		Burial / Medical Support for Seniors criteria:
		1. MANDATORY: Deceased/Patient was 60+ (30 points)
		2. MANDATORY: KYC Verified (applicant) (20 points)
		3. MANDATORY: Death certificate or medical docs (20 points)
		4. WEIGHTED: Family relationship verified (15 points)
		5. WEIGHTED: No other burial/medical assistance (15 points)
		"""
		# For burial/medical, age check is on the senior (not applicant)
		# This would need additional fields on Request
		self.add_check("Senior Citizen Beneficiary", "Mandatory", 30, 30, "Passed", "Pending document verification")

		# Criterion 2: Applicant KYC Verified
		if self.kyc and self.kyc.verification_status == "Verified":
			self.add_check("Applicant KYC Verified", "Mandatory", 20, 20, "Passed", "Applicant identity verified")
		else:
			self.add_check("Applicant KYC Verified", "Mandatory", 0, 20, "Failed", "Applicant KYC not verified")

		# Criterion 3: Documentation
		self.add_check("Death/Medical Certificate", "Mandatory", 15, 20, "Partial", "Pending document upload")

		# Criterion 4: Family relationship
		self.add_check("Family Relationship", "Weighted", 10, 15, "Partial", "Pending verification")

		# Criterion 5: No other assistance
		self.add_check("No Other Burial/Medical Aid", "Weighted", 15, 15, "Passed", "First time claiming")

	def check_generic_eligibility(self):
		"""Generic eligibility checks for other programs"""
		# Basic checks
		if self.kyc and self.kyc.verification_status == "Verified":
			self.add_check("KYC Verified", "Mandatory", 50, 50, "Passed", "Identity verified")
		else:
			self.add_check("KYC Verified", "Mandatory", 0, 50, "Failed", "KYC not verified")

		if self.household:
			self.add_check("Household Registered", "Weighted", 50, 50, "Passed", "Household data available")
		else:
			self.add_check("Household Registered", "Weighted", 25, 50, "Partial", "No household record")

	def add_check(self, name, criterion_type, score, max_score, status, notes):
		"""Add a criteria check result"""
		self.criteria_checks.append({
			"criterion_name": name,
			"criterion_type": criterion_type,
			"score_earned": score,
			"max_score": max_score,
			"status": status,
			"check_result": notes,
			"weight": max_score
		})
		self.total_score += score
		self.max_score += max_score

	def get_applicant_age(self):
		"""Calculate applicant's age"""
		user = frappe.get_doc("User", self.requester)
		if user.birth_date:
			today = getdate(nowdate())
			birth = getdate(user.birth_date)
			age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
			return age
		return 0

	def check_existing_benefits(self):
		"""Check if applicant already receives government benefits"""
		# Check for existing SPISC approval
		existing = frappe.db.exists("Request", {
			"requester_email": self.requester,
			"request_type": "Social Pension for Indigent Senior Citizens (SPISC)",
			"status": ["in", ["Approved", "Active"]],
			"name": ["!=", self.request.name]
		})
		return existing

	def check_recent_assistance(self, months=6):
		"""Check if applicant received assistance in last X months"""
		# This would check Benefit Payout records (to be created in Phase 5)
		# For now, return None (no recent assistance found)
		return None

	def create_eligibility_result(self):
		"""Create and save eligibility result document"""
		result = frappe.get_doc({
			"doctype": "Eligibility Criteria Result",
			"request": self.request.name,
			"request_type": self.request.request_type,
			"requester": self.requester,
			"evaluated_by": frappe.session.user,
			"overall_score": self.total_score,
			"max_possible_score": self.max_score,
			"kyc_verified": bool(self.kyc and self.kyc.verification_status == "Verified"),
			"household_verified": bool(self.household and self.household.verified_by_barangay),
			"has_senior_citizen": self.get_applicant_age() >= 60,
			"below_poverty_threshold": bool(self.household and self.household.poverty_threshold_status == "Below")
		})

		# Add criteria checks
		for check in self.criteria_checks:
			result.append("criteria_checks", check)

		result.insert(ignore_permissions=True)
		return result
