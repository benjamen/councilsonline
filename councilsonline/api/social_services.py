# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Social Services API
Handles KYC verification, household records, eligibility assessment, and fraud detection
for social benefit programs
"""

import frappe
from frappe import _
import frappe.utils
import json

# ================================

@frappe.whitelist()
def submit_kyc_verification(philsys_id=None, sss_number=None, tin_number=None,
							gsis_number=None, umid_number=None, documents=None):
	"""
	Submit KYC documents for verification

	Args:
		philsys_id: Philippines National ID
		sss_number: Social Security System number
		tin_number: Tax Identification Number
		gsis_number: Government Service Insurance System number
		umid_number: Unified Multi-Purpose ID number
		documents: List of document dictionaries with type, number, and file

	Returns:
		dict: Created KYC verification record details
	"""
	try:
		user = frappe.session.user

		# Check if user already has KYC record
		existing_kyc = frappe.db.get_value("User Identity Verification",
										  {"user": user}, "name")

		if existing_kyc:
			# Update existing KYC
			kyc_doc = frappe.get_doc("User Identity Verification", existing_kyc)
			kyc_doc.verification_status = "Pending"
			kyc_doc.verification_attempts = kyc_doc.verification_attempts + 1
			kyc_doc.last_verification_attempt = frappe.utils.now()
		else:
			# Create new KYC record
			kyc_doc = frappe.get_doc({
				"doctype": "User Identity Verification",
				"user": user,
				"verification_status": "Pending",
				"verification_attempts": 1,
				"last_verification_attempt": frappe.utils.now()
			})

		# Update ID numbers
		if philsys_id:
			kyc_doc.philsys_id = philsys_id
		if sss_number:
			kyc_doc.sss_number = sss_number
		if tin_number:
			kyc_doc.tin_number = tin_number
		if gsis_number:
			kyc_doc.gsis_number = gsis_number
		if umid_number:
			kyc_doc.umid_number = umid_number

		# Parse and add documents
		if documents:
			import json
			if isinstance(documents, str):
				documents = json.loads(documents)

			# Clear existing documents
			kyc_doc.kyc_documents = []

			for doc in documents:
				kyc_doc.append("kyc_documents", {
					"document_type": doc.get("document_type"),
					"document_number": doc.get("document_number"),
					"attachment": doc.get("attachment"),
					"verification_status": "Pending"
				})

		if existing_kyc:
			kyc_doc.save(ignore_permissions=True)
		else:
			kyc_doc.insert(ignore_permissions=True)

		frappe.db.commit()

		# Notify admin for review
		notify_kyc_submission(kyc_doc)

		return {
			"success": True,
			"message": _("KYC verification submitted successfully"),
			"kyc_id": kyc_doc.name,
			"status": kyc_doc.verification_status
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Submit KYC Verification Error: {str(e)}")
		frappe.throw(_("Failed to submit KYC verification. Please try again."))


@frappe.whitelist()
def verify_kyc(kyc_id, verification_status, notes=None):
	"""
	Admin function to approve/reject KYC
	Requires: Social Services Manager or Social Worker role

	Args:
		kyc_id: ID of User Identity Verification record
		verification_status: "Verified" or "Rejected"
		notes: Optional verification notes

	Returns:
		dict: Success message
	"""
	# Check permission
	if not frappe.has_permission("User Identity Verification", "write"):
		frappe.throw(_("You do not have permission to verify KYC"))

	try:
		kyc_doc = frappe.get_doc("User Identity Verification", kyc_id)

		kyc_doc.verification_status = verification_status
		kyc_doc.verified_by = frappe.session.user
		kyc_doc.verification_date = frappe.utils.now()

		if notes:
			kyc_doc.rejection_reason = notes if verification_status == "Rejected" else None
			kyc_doc.verification_notes = notes

		# Update all document statuses
		for doc in kyc_doc.kyc_documents:
			doc.verification_status = verification_status
			doc.verified_by = frappe.session.user

		kyc_doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("KYC verification updated successfully"),
			"status": kyc_doc.verification_status
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Verify KYC Error: {str(e)}")
		frappe.throw(_("Failed to verify KYC. Please try again."))


@frappe.whitelist()
def check_kyc_status(user=None):
	"""
	Check if user's KYC is verified and not expired

	Args:
		user: Optional user email (defaults to current user)

	Returns:
		dict: Verification status details
	"""
	if not user:
		user = frappe.session.user

	kyc = frappe.db.get_value("User Identity Verification",
							 {"user": user},
							 ["name", "verification_status", "expiry_date",
							  "verification_date", "rejection_reason"],
							 as_dict=True)

	if not kyc:
		return {
			"verified": False,
			"status": "Not Started",
			"message": "No KYC verification found. Please submit your documents."
		}

	# Check if expired
	if kyc.verification_status == "Verified":
		if kyc.expiry_date and frappe.utils.getdate(kyc.expiry_date) < frappe.utils.getdate():
			# Update status to Expired
			frappe.db.set_value("User Identity Verification", kyc.name,
							   "verification_status", "Expired")
			frappe.db.commit()
			return {
				"verified": False,
				"status": "Expired",
				"expiry_date": kyc.expiry_date,
				"message": "Your KYC verification has expired. Please renew."
			}

		return {
			"verified": True,
			"status": "Verified",
			"verification_date": kyc.verification_date,
			"expiry_date": kyc.expiry_date,
			"message": "Your KYC is verified and active."
		}

	return {
		"verified": False,
		"status": kyc.verification_status,
		"rejection_reason": kyc.rejection_reason if kyc.verification_status == "Rejected" else None,
		"message": f"KYC status: {kyc.verification_status}"
	}


def notify_kyc_submission(kyc_doc):
	"""Send notification to admin when KYC is submitted"""
	try:
		# Get all Social Services Managers
		managers = frappe.get_all("Has Role",
								 filters={"role": "Social Services Manager"},
								 fields=["parent"])

		if managers:
			recipients = [m.parent for m in managers]
			frappe.sendmail(
				recipients=recipients,
				subject=f"New KYC Verification Submission - {kyc_doc.user}",
				message=f"""
				<p>A new KYC verification has been submitted for review.</p>
				<p><strong>User:</strong> {kyc_doc.user}</p>
				<p><strong>KYC ID:</strong> {kyc_doc.name}</p>
				<p><strong>Documents Submitted:</strong> {len(kyc_doc.kyc_documents)}</p>
				<p>Please review and verify the submitted documents.</p>
				"""
			)
	except Exception as e:
		frappe.log_error(f"Failed to send KYC notification: {str(e)}")


# ================================
# Household Management APIs
# ================================

@frappe.whitelist()
def create_household_record(head_of_household, address, barangay, municipality, province,
							housing_type=None, total_monthly_income=None, members=None):
	"""
	Create household with members

	Args:
		head_of_household: Email of head of household (User)
		address: Full address
		barangay: Barangay name
		municipality: Municipality/City
		province: Province
		housing_type: Optional housing type
		total_monthly_income: Optional total monthly income
		members: List of household member dictionaries

	Returns:
		dict: Created household record details
	"""
	try:
		# Validate head of household has verified KYC
		kyc_status = check_kyc_status(head_of_household)
		if not kyc_status.get("verified"):
			frappe.throw(_("Head of household must have verified KYC before creating household record"))

		# Check if household already exists
		existing = frappe.db.get_value("Household Record",
									  {"head_of_household": head_of_household},
									  "name")
		if existing:
			frappe.throw(_("Household record already exists for this user: {0}").format(existing))

		# Create household record
		household = frappe.get_doc({
			"doctype": "Household Record",
			"head_of_household": head_of_household,
			"address": address,
			"barangay": barangay,
			"municipality": municipality,
			"province": province,
			"housing_type": housing_type,
			"total_monthly_income": total_monthly_income,
			"household_status": "Active"
		})

		# Add household members
		if members:
			import json
			if isinstance(members, str):
				members = json.loads(members)

			for member in members:
				household.append("household_members", {
					"full_name": member.get("full_name"),
					"relationship_to_head": member.get("relationship_to_head"),
					"birth_date": member.get("birth_date"),
					"sex": member.get("sex"),
					"civil_status": member.get("civil_status"),
					"is_pwd": member.get("is_pwd", 0),
					"is_employed": member.get("is_employed", 0),
					"monthly_income": member.get("monthly_income", 0),
					"occupation": member.get("occupation")
				})

		household.insert(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Household record created successfully"),
			"household_id": household.name,
			"household_identifier": household.household_id
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Create Household Record Error: {str(e)}")
		raise


@frappe.whitelist()
def update_household_member(household_id, member_data):
	"""
	Add or update household member

	Args:
		household_id: ID of the household record
		member_data: Dictionary containing member data

	Returns:
		dict: Success message
	"""
	try:
		household = frappe.get_doc("Household Record", household_id)

		# Parse member data
		import json
		if isinstance(member_data, str):
			member_data = json.loads(member_data)

		# Add new member
		household.append("household_members", {
			"full_name": member_data.get("full_name"),
			"relationship_to_head": member_data.get("relationship_to_head"),
			"birth_date": member_data.get("birth_date"),
			"sex": member_data.get("sex"),
			"civil_status": member_data.get("civil_status"),
			"is_pwd": member_data.get("is_pwd", 0),
			"is_employed": member_data.get("is_employed", 0),
			"monthly_income": member_data.get("monthly_income", 0),
			"occupation": member_data.get("occupation")
		})

		household.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Household member added successfully"),
			"total_members": len(household.household_members)
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Update Household Member Error: {str(e)}")
		raise


@frappe.whitelist()
def verify_household_by_barangay(household_id, barangay_official):
	"""
	Barangay official verifies household data
	Requires: Barangay Social Services role

	Args:
		household_id: ID of household record
		barangay_official: Name of barangay official

	Returns:
		dict: Success message
	"""
	# Check permission
	if not frappe.has_permission("Household Record", "write"):
		frappe.throw(_("You do not have permission to verify household records"))

	try:
		household = frappe.get_doc("Household Record", household_id)

		household.verified_by_barangay = 1
		household.barangay_verification_date = frappe.utils.nowdate()
		household.barangay_official = barangay_official

		household.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Household verified by barangay successfully"),
			"verified_date": household.barangay_verification_date
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Verify Household Error: {str(e)}")
		raise


@frappe.whitelist()
def get_household_record(user=None):
	"""
	Get household record for a user

	Args:
		user: Optional user email (defaults to current user)

	Returns:
		dict: Household record details
	"""
	if not user:
		user = frappe.session.user

	household = frappe.db.get_value("Household Record",
								   {"head_of_household": user},
								   ["*"],
								   as_dict=True)

	if not household:
		return {
			"success": False,
			"message": "No household record found. Please create one."
		}

	# Get household members
	members = frappe.get_all("Household Member",
							filters={"parent": household.name},
							fields=["*"],
							order_by="age desc")

	household["members"] = members

	return {
		"success": True,
		"household": household
	}


# ================================
# Eligibility Assessment APIs
# ================================

@frappe.whitelist()
def calculate_eligibility(request_id):
	"""
	Calculate eligibility for a social assistance request

	Args:
		request_id: ID of the Request document

	Returns:
		dict: Eligibility result with score and status
	"""
	try:
		from councilsonline.eligibility_engine import EligibilityEngine

		# Check if eligibility already calculated
		existing = frappe.db.get_value("Eligibility Criteria Result",
									  {"request": request_id},
									  "name")
		if existing:
			result = frappe.get_doc("Eligibility Criteria Result", existing)
			return {
				"success": True,
				"message": "Eligibility already calculated",
				"eligibility_id": result.name,
				"score": result.overall_score,
				"max_score": result.max_possible_score,
				"percentage": result.score_percentage,
				"status": result.eligibility_status,
				"decision": result.final_decision
			}

		# Calculate eligibility
		engine = EligibilityEngine(request_id)
		result = engine.calculate_eligibility()

		frappe.db.commit()

		return {
			"success": True,
			"message": "Eligibility calculated successfully",
			"eligibility_id": result.name,
			"score": result.overall_score,
			"max_score": result.max_possible_score,
			"percentage": result.score_percentage,
			"status": result.eligibility_status,
			"decision": result.final_decision,
			"criteria_checks": [
				{
					"name": c.criterion_name,
					"status": c.status,
					"score": c.score_earned,
					"max": c.max_score
				} for c in result.criteria_checks
			]
		}

	except Exception as e:
		frappe.log_error(f"Calculate Eligibility Error: {str(e)}")
		raise


@frappe.whitelist()
def override_eligibility(eligibility_id, new_status, override_reason):
	"""
	Manually override eligibility decision
	Requires: Social Services Manager role

	Args:
		eligibility_id: ID of Eligibility Criteria Result
		new_status: New eligibility status (Eligible/Not Eligible/Needs Review)
		override_reason: Reason for override

	Returns:
		dict: Success message
	"""
	# Check permission
	if not frappe.has_permission("Eligibility Criteria Result", "write"):
		frappe.throw(_("You do not have permission to override eligibility"))

	try:
		result = frappe.get_doc("Eligibility Criteria Result", eligibility_id)

		result.manual_override = 1
		result.eligibility_status = new_status
		result.override_reason = override_reason
		result.override_by = frappe.session.user
		result.override_date = frappe.utils.now()

		# Update final decision based on override
		if new_status == "Eligible":
			result.final_decision = "Approved"
		elif new_status == "Not Eligible":
			result.final_decision = "Rejected"
		else:
			result.final_decision = "Pending Review"

		result.save(ignore_permissions=True)
		frappe.db.commit()

		# Add comment to request
		request = frappe.get_doc("Request", result.request)
		request.add_comment("Comment", f"Eligibility manually overridden to {new_status} by {frappe.session.user}")

		return {
			"success": True,
			"message": _("Eligibility overridden successfully"),
			"new_status": result.eligibility_status,
			"decision": result.final_decision
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Override Eligibility Error: {str(e)}")
		raise


@frappe.whitelist()
def get_eligibility_result(request_id):
	"""
	Get eligibility result for a request

	Args:
		request_id: ID of the Request document

	Returns:
		dict: Eligibility result details
	"""
	result = frappe.db.get_value("Eligibility Criteria Result",
								{"request": request_id},
								["*"],
								as_dict=True)

	if not result:
		return {
			"success": False,
			"message": "No eligibility result found. Please calculate eligibility first."
		}

	# Get criteria checks
	checks = frappe.get_all("Criteria Check Item",
						   filters={"parent": result.name},
						   fields=["*"],
						   order_by="max_score desc")

	result["criteria_checks"] = checks

	return {
		"success": True,
		"result": result
	}


# ================================
# Payout & Disbursement APIs
# ================================

@frappe.whitelist()
def create_payout(request_id, payout_amount, payment_method, payout_date=None,
				 bank_name=None, bank_account_number=None, account_holder_name=None,
				 gcash_number=None, pickup_location=None):
	"""
	Create a payout for an approved request

	Args:
		request_id: ID of approved Request
		payout_amount: Amount to pay
		payment_method: Bank Transfer/GCash/Cash Pickup/Check
		payout_date: Date of payout (defaults to today)
		bank_name, bank_account_number, account_holder_name: For bank transfers
		gcash_number: For GCash payments
		pickup_location: For cash pickup

	Returns:
		dict: Created payout details
	"""
	try:
		# Validate request is approved
		request = frappe.get_doc("Request", request_id)
		if request.workflow_state not in ["Approved", "Approved with Conditions"]:
			frappe.throw(_("Request must be approved before creating payout"))

		# Check eligibility
		eligibility = frappe.db.get_value("Eligibility Criteria Result",
										 {"request": request_id},
										 ["eligibility_status", "final_decision"],
										 as_dict=True)
		if not eligibility or eligibility.final_decision != "Approved":
			frappe.throw(_("Request must have approved eligibility"))

		# Create payout
		payout = frappe.get_doc({
			"doctype": "Benefit Payout",
			"request": request_id,
			"request_type": request.request_type,
			"beneficiary": request.requester_email,
			"payout_amount": payout_amount,
			"currency": "PHP",
			"payout_date": payout_date or frappe.utils.nowdate(),
			"payment_method": payment_method,
			"bank_name": bank_name,
			"bank_account_number": bank_account_number,
			"account_holder_name": account_holder_name,
			"gcash_number": gcash_number,
			"pickup_location": pickup_location,
			"payout_status": "Pending"
		})

		payout.insert(ignore_permissions=True)
		frappe.db.commit()

		# Add to beneficiary masterlist if not exists
		add_to_masterlist(request.requester_email, request.request_type, payout_amount)

		return {
			"success": True,
			"message": _("Payout created successfully"),
			"payout_id": payout.name,
			"status": payout.payout_status
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Create Payout Error: {str(e)}")
		raise


@frappe.whitelist()
def create_payout_batch(batch_name, batch_type, request_type=None,
					   period_start=None, period_end=None):
	"""
	Create a payout batch for bulk processing (single-tenant)

	Args:
		batch_name: Name of the batch
		batch_type: Monthly Pension/One-time Assistance/Emergency Aid/Burial-Medical
		request_type: Filter by request type
		period_start, period_end: Payout period

	Returns:
		dict: Created batch details
	"""
	try:
		batch = frappe.get_doc({
			"doctype": "Payout Batch",
			"batch_name": batch_name,
			"batch_type": batch_type,
			"request_type": request_type,
			"period_start": period_start,
			"period_end": period_end,
			"batch_status": "Draft",
			"created_by": frappe.session.user
		})

		batch.insert(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Payout batch created successfully"),
			"batch_id": batch.name
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Create Payout Batch Error: {str(e)}")
		raise


@frappe.whitelist()
def generate_bank_file(batch_id, format_type="CSV"):
	"""
	Generate bank file for payout batch

	Args:
		batch_id: ID of Payout Batch
		format_type: CSV/UnionBank Format/BDO Format/GCash

	Returns:
		dict: File URL and details
	"""
	try:
		from councilsonline.bank_file_generator import BankFileGenerator

		generator = BankFileGenerator(batch_id)
		file_url = generator.generate_and_save(format_type)

		return {
			"success": True,
			"message": _("Bank file generated successfully"),
			"file_url": file_url,
			"format": format_type
		}

	except Exception as e:
		frappe.log_error(f"Generate Bank File Error: {str(e)}")
		raise


@frappe.whitelist()
def approve_payout_batch(batch_id):
	"""
	Approve payout batch for processing
	Requires: Finance Officer or Social Services Manager role

	Args:
		batch_id: ID of Payout Batch

	Returns:
		dict: Success message
	"""
	if not frappe.has_permission("Payout Batch", "write"):
		frappe.throw(_("You do not have permission to approve payout batches"))

	try:
		batch = frappe.get_doc("Payout Batch", batch_id)
		batch.approve_batch()

		return {
			"success": True,
			"message": _("Payout batch approved successfully"),
			"batch_status": batch.batch_status
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Approve Payout Batch Error: {str(e)}")
		raise


def add_to_masterlist(beneficiary, program_type, monthly_amount):
	"""Internal function to add/update beneficiary masterlist"""
	existing = frappe.db.get_value("Beneficiary Masterlist",
								  {"beneficiary": beneficiary, "program_type": program_type},
								  "name")

	if not existing:
		# Get beneficiary data
		kyc = frappe.db.get_value("User Identity Verification",
								 {"user": beneficiary},
								 ["philsys_id", "sss_number"],
								 as_dict=True)

		household = frappe.db.get_value("Household Record",
									   {"head_of_household": beneficiary},
									   ["name", "barangay"],
									   as_dict=True)

		masterlist = frappe.get_doc({
			"doctype": "Beneficiary Masterlist",
			"beneficiary": beneficiary,
			"program_type": program_type,
			"monthly_benefit_amount": monthly_amount,
			"start_date": frappe.utils.nowdate(),
			"philsys_id": kyc.philsys_id if kyc else None,
			"sss_number": kyc.sss_number if kyc else None,
			"household_record": household.name if household else None,
			"barangay": household.barangay if household else None,
			"beneficiary_status": "Active"
		})

		masterlist.insert(ignore_permissions=True)
		frappe.db.commit()


# ================================
# Fraud Detection APIs
# ================================

@frappe.whitelist()
def run_fraud_check(user_email):
	"""
	Run automated fraud detection checks on a user

	Args:
		user_email: Email of user to check

	Returns:
		dict: Fraud check results with risk score and flags
	"""
	try:
		from councilsonline.fraud_detector import FraudDetector

		detector = FraudDetector(user_email)
		results = detector.run_all_checks()

		# Create investigation case if high risk
		if results["requires_investigation"]:
			case_id = detector.create_investigation_case()
			results["investigation_case"] = case_id

		return {
			"success": True,
			"user": user_email,
			"risk_score": results["risk_score"],
			"flags": results["flags"],
			"requires_investigation": results["requires_investigation"],
			"investigation_case": results.get("investigation_case")
		}

	except Exception as e:
		frappe.log_error(f"Fraud Check Error: {str(e)}")
		raise


@frappe.whitelist()
def check_duplicate_application(user_email, request_type):
	"""
	Check if user has duplicate applications for same program

	Args:
		user_email: Email of user
		request_type: Type of request

	Returns:
		dict: Duplicate check results
	"""
	try:
		# Check for active requests (using workflow_state)
		active_requests = frappe.get_all("Request",
										filters={
											"requester_email": user_email,
											"request_type": request_type,
											"workflow_state": ["in", ["Submitted", "Acknowledged", "Processing", "Approved", "Approved with Conditions"]]
										},
										fields=["name", "workflow_state", "creation"])

		has_duplicate = len(active_requests) > 0

		return {
			"success": True,
			"has_duplicate": has_duplicate,
			"duplicate_count": len(active_requests),
			"active_requests": active_requests,
			"message": f"Found {len(active_requests)} active application(s)" if has_duplicate else "No duplicate applications found"
		}

	except Exception as e:
		frappe.log_error(f"Duplicate Application Check Error: {str(e)}")
		raise


@frappe.whitelist()
def check_beneficiary_status(user_email):
	"""
	Check if beneficiary is in good standing

	Args:
		user_email: Email of beneficiary

	Returns:
		dict: Beneficiary status details
	"""
	try:
		# Check masterlist status
		masterlist = frappe.get_all("Beneficiary Masterlist",
								   filters={"beneficiary": user_email},
								   fields=["beneficiary_status", "suspended",
										  "suspension_reason", "flagged_for_review",
										  "flag_reason"])

		# Check for open fraud cases
		fraud_cases = frappe.get_all("Fraud Investigation Case",
									filters={
										"subject_user": user_email,
										"case_status": ["in", ["Open", "Under Investigation", "Pending Review"]]
									},
									fields=["name", "case_type", "priority", "risk_score"])

		in_good_standing = True
		issues = []

		if masterlist:
			for entry in masterlist:
				if entry.beneficiary_status == "Suspended":
					in_good_standing = False
					issues.append(f"Suspended: {entry.suspension_reason}")
				elif entry.beneficiary_status == "Deceased":
					in_good_standing = False
					issues.append("Marked as deceased")
				elif entry.flagged_for_review:
					in_good_standing = False
					issues.append(f"Flagged for review: {entry.flag_reason}")

		if fraud_cases:
			in_good_standing = False
			for case in fraud_cases:
				issues.append(f"Active fraud investigation: {case.name} ({case.case_type})")

		return {
			"success": True,
			"in_good_standing": in_good_standing,
			"issues": issues,
			"fraud_cases": fraud_cases,
			"masterlist_entries": masterlist
		}

	except Exception as e:
		frappe.log_error(f"Beneficiary Status Check Error: {str(e)}")
		raise


@frappe.whitelist()
def detect_identity_fraud(philsys_id=None, sss_number=None):
	"""
	Detect potential identity fraud by checking for duplicate IDs

	Args:
		philsys_id: PhilSys National ID
		sss_number: SSS Number

	Returns:
		dict: Identity fraud detection results
	"""
	try:
		duplicates = []

		if philsys_id:
			philsys_users = frappe.get_all("User Identity Verification",
										  filters={
											  "philsys_id": philsys_id,
											  "verification_status": "Verified"
										  },
										  fields=["user", "verification_date"])
			if len(philsys_users) > 1:
				duplicates.append({
					"id_type": "PhilSys ID",
					"id_number": philsys_id,
					"users": philsys_users
				})

		if sss_number:
			sss_users = frappe.get_all("User Identity Verification",
									  filters={
										  "sss_number": sss_number,
										  "verification_status": "Verified"
									  },
									  fields=["user", "verification_date"])
			if len(sss_users) > 1:
				duplicates.append({
					"id_type": "SSS Number",
					"id_number": sss_number,
					"users": sss_users
				})

		fraud_detected = len(duplicates) > 0

		return {
			"success": True,
			"fraud_detected": fraud_detected,
			"duplicates": duplicates,
			"message": f"Found {len(duplicates)} duplicate ID(s)" if fraud_detected else "No duplicate IDs found"
		}

	except Exception as e:
		frappe.log_error(f"Identity Fraud Detection Error: {str(e)}")
		raise


@frappe.whitelist()
def update_user_company_role(company_name, user_email, new_role):
	"""
	Update user's role and permissions in company
	Requires: Admin role with can_manage_users permission

	Args:
		company_name: Name of company account
		user_email: Email of user
		new_role: New role (Admin/Submitter/Viewer)

	Returns:
		dict: Success message
	"""
	company = frappe.get_doc("Company Account", company_name)

	# Check permission
	if not company.can_user_perform_action(frappe.session.user, "invite_users"):
		frappe.throw(_("You do not have permission to update user roles"))

	# Find and update user
	updated = False

	# Check if in linked_users
	for linked_user in company.linked_users:
		if linked_user.user == user_email:
			linked_user.role = new_role
			updated = True
