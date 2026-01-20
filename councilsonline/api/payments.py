# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Payment & Invoice Management API
Handles fee payments, invoices, benefit payouts, and financial transactions
"""

import frappe
from frappe import _
import frappe.utils


@frappe.whitelist()
def request_invoice(request_id):
	"""
	Create invoice request and send to user email

	Args:
		request_id: Name of the Request document

	Returns:
		dict: Success status with invoice details
	"""
	try:
		request = frappe.get_doc("Request", request_id)

		# Validate request has fees
		if not request.total_fees_incl_gst or request.total_fees_incl_gst <= 0:
			return {
				"success": False,
				"error": "No fees to invoice for this request"
			}

		# Check if payment record already exists
		existing_payment = frappe.db.get_value("Payment",
			{"request": request_id, "payment_status": ["in", ["Pending", "Processing", "Completed"]]},
			"name"
		)

		if existing_payment:
			# Invoice already requested, just resend email
			from councilsonline.councilsonline.doctype.request.request import email_invoice
			email_result = email_invoice(request_id)

			if email_result.get("success"):
				return {
					"success": True,
					"invoice_number": existing_payment,
					"email": request.requester_email or frappe.db.get_value("User", request.requester, "email"),
					"message": "Invoice resent successfully"
				}
			else:
				return email_result

		# Create new Payment record
		payment = frappe.get_doc({
			"doctype": "Payment",
			"request": request_id,
			"payment_type": "Application Fee",
			"payment_method": "Bank Transfer",
			"payment_status": "Pending",
			"amount": request.total_fees_excl_gst or 0,
			"gst": request.gst_amount or 0,
			"total_amount": request.total_fees_incl_gst,
			"currency": "NZD",
			"notes": f"Invoice requested for {request.request_type} application"
		})
		payment.insert(ignore_permissions=True)
		frappe.db.commit()

		# Update request payment status
		request.payment_status = "Invoice Requested"
		request.save(ignore_permissions=True)
		frappe.db.commit()

		# Send email with invoice
		from councilsonline.councilsonline.doctype.request.request import email_invoice
		email_result = email_invoice(request_id)

		if not email_result.get("success"):
			# Payment created but email failed - still return success with warning
			return {
				"success": True,
				"invoice_number": payment.name,
				"email": request.requester_email or frappe.db.get_value("User", request.requester, "email"),
				"warning": "Invoice created but email sending failed. Please contact support."
			}

		return {
			"success": True,
			"invoice_number": payment.name,
			"email": request.requester_email or frappe.db.get_value("User", request.requester, "email")
		}

	except Exception as e:
		frappe.log_error(f"Request Invoice Error: {str(e)}", "Payment API Error")
		return {
			"success": False,
			"error": str(e)
		}


# ================================
# BENEFIT PAYOUT APIs
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
