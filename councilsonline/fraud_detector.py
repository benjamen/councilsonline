# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Fraud Detection Utility for Social Assistance Programs

Automated fraud detection algorithms to identify suspicious patterns
and potential fraud in applications and payouts.
"""

import frappe
from frappe.utils import add_months, nowdate


class FraudDetector:
	"""Automated fraud detection engine"""

	def __init__(self, user_email):
		self.user = user_email
		self.risk_score = 0
		self.flags = []

	def run_all_checks(self):
		"""Run all fraud detection checks"""
		self.check_duplicate_applications()
		self.check_duplicate_identity()
		self.check_deceased_beneficiary()
		self.check_multiple_households()
		self.check_recent_payout_frequency()
		self.check_cross_program_benefits()

		return {
			"risk_score": self.risk_score,
			"flags": self.flags,
			"requires_investigation": self.risk_score >= 70
		}

	def check_duplicate_applications(self):
		"""Check for duplicate active applications"""
		# Check for multiple active requests for same program
		active_requests = frappe.db.sql("""
			SELECT request_type, COUNT(*) as count
			FROM `tabRequest`
			WHERE applicant_email = %s
				AND status IN ('Submitted', 'Under Review', 'Approved', 'Active')
			GROUP BY request_type
			HAVING count > 1
		""", self.user, as_dict=True)

		if active_requests:
			self.risk_score += 30
			for req in active_requests:
				self.flags.append(f"Multiple active applications for {req.request_type}: {req.count} found")

	def check_duplicate_identity(self):
		"""Check for duplicate PhilSys ID or SSS numbers"""
		# Get user's KYC
		kyc = frappe.db.get_value("User Identity Verification",
								 {"user": self.user},
								 ["philsys_id", "sss_number"],
								 as_dict=True)

		if not kyc:
			return

		# Check PhilSys ID
		if kyc.philsys_id:
			duplicates = frappe.db.count("User Identity Verification", {
				"philsys_id": kyc.philsys_id,
				"user": ["!=", self.user],
				"verification_status": "Verified"
			})

			if duplicates > 0:
				self.risk_score += 50
				self.flags.append(f"PhilSys ID {kyc.philsys_id} is used by {duplicates} other verified user(s)")

		# Check SSS number
		if kyc.sss_number:
			duplicates = frappe.db.count("User Identity Verification", {
				"sss_number": kyc.sss_number,
				"user": ["!=", self.user],
				"verification_status": "Verified"
			})

			if duplicates > 0:
				self.risk_score += 50
				self.flags.append(f"SSS Number {kyc.sss_number} is used by {duplicates} other verified user(s)")

	def check_deceased_beneficiary(self):
		"""Check if beneficiary is marked as deceased in masterlist"""
		deceased = frappe.db.exists("Beneficiary Masterlist", {
			"beneficiary": self.user,
			"beneficiary_status": "Deceased"
		})

		if deceased:
			self.risk_score += 100
			self.flags.append("Beneficiary is marked as deceased but has active records")

	def check_multiple_households(self):
		"""Check if user is head of multiple households"""
		household_count = frappe.db.count("Household Record", {
			"head_of_household": self.user,
			"household_status": "Active"
		})

		if household_count > 1:
			self.risk_score += 40
			self.flags.append(f"User is head of {household_count} active households")

	def check_recent_payout_frequency(self):
		"""Check for unusually high payout frequency"""
		# Get payouts in last 3 months
		three_months_ago = add_months(nowdate(), -3)
		payout_count = frappe.db.count("Benefit Payout", {
			"beneficiary": self.user,
			"payout_date": [">=", three_months_ago],
			"payout_status": "Completed"
		})

		# Flag if more than 5 payouts in 3 months (except for monthly pensions)
		if payout_count > 5:
			# Check if it's monthly pension (expected frequency)
			pension_count = frappe.db.count("Benefit Payout", {
				"beneficiary": self.user,
				"payout_date": [">=", three_months_ago],
				"request_type": "Social Pension for Indigent Senior Citizens (SPISC)",
				"payout_status": "Completed"
			})

			if payout_count - pension_count > 3:
				self.risk_score += 25
				self.flags.append(f"High payout frequency: {payout_count} payouts in last 3 months")

	def check_cross_program_benefits(self):
		"""Check for receiving benefits from multiple programs simultaneously"""
		active_programs = frappe.db.sql("""
			SELECT DISTINCT bm.program_type
			FROM `tabBeneficiary Masterlist` bm
			WHERE bm.beneficiary = %s
				AND bm.beneficiary_status = 'Active'
		""", self.user, as_dict=True)

		if len(active_programs) > 2:
			self.risk_score += 20
			self.flags.append(f"Receiving benefits from {len(active_programs)} different programs simultaneously")

	def create_investigation_case(self):
		"""Create fraud investigation case if risk score is high"""
		if self.risk_score >= 70:
			# Check if case already exists
			existing = frappe.db.exists("Fraud Investigation Case", {
				"subject_user": self.user,
				"case_status": ["in", ["Open", "Under Investigation", "Pending Review"]]
			})

			if existing:
				return existing

			# Create new case
			case = frappe.get_doc({
				"doctype": "Fraud Investigation Case",
				"case_title": f"Automated Fraud Alert - {self.user}",
				"case_type": "Identity Fraud" if self.risk_score >= 90 else "Duplicate Application",
				"priority": "Critical" if self.risk_score >= 90 else "High",
				"case_status": "Open",
				"subject_user": self.user,
				"fraud_type": "Identity Theft" if self.risk_score >= 90 else "Duplicate Benefit",
				"risk_score": self.risk_score,
				"automated_flags": "\n".join(self.flags)
			})

			case.insert(ignore_permissions=True)
			frappe.db.commit()

			return case.name

		return None


def check_staff_beneficiary_relationship(staff_email, beneficiary_email):
	"""
	Check if staff member has disclosed relationship with beneficiary

	Args:
		staff_email: Email of staff member
		beneficiary_email: Email of beneficiary

	Returns:
		dict: Relationship disclosure status
	"""
	disclosure = frappe.db.get_value("Staff Relationship Disclosure",
									 {
										 "staff_member": staff_email,
										 "related_beneficiary": beneficiary_email,
										 "disclosure_status": ["!=", "Resolved"]
									 },
									 ["name", "relationship_type", "potential_conflict",
									  "review_decision"],
									 as_dict=True)

	if disclosure:
		return {
			"has_disclosure": True,
			"disclosure_id": disclosure.name,
			"relationship_type": disclosure.relationship_type,
			"potential_conflict": disclosure.potential_conflict,
			"review_decision": disclosure.review_decision,
			"requires_recusal": disclosure.review_decision in ["Recusal Required", "Reassignment Required"]
		}

	return {
		"has_disclosure": False,
		"requires_recusal": False
	}
