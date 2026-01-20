# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Bank File Generation Utility for Bulk Payout Processing

Generates bank-compatible CSV files for bulk fund transfers to beneficiaries.
Supports multiple Philippines banks: UnionBank, BDO, Instapay, GCash.
"""

import frappe
import csv
from io import StringIO
from frappe.utils import nowdate, flt


class BankFileGenerator:
	"""Generate bank transfer files for payout batches"""

	def __init__(self, batch_id):
		self.batch = frappe.get_doc("Payout Batch", batch_id)
		self.payouts = []
		self.load_payouts()

	def load_payouts(self):
		"""Load all approved payouts in this batch"""
		self.payouts = frappe.get_all("Benefit Payout",
									 filters={
										 "payout_batch": self.batch.name,
										 "payout_status": "Approved",
										 "payment_method": "Bank Transfer"
									 },
									 fields=["*"])

	def generate_csv_generic(self):
		"""
		Generate generic CSV format
		Format: Account Number, Account Name, Amount, Reference
		"""
		output = StringIO()
		writer = csv.writer(output)

		# Header
		writer.writerow(["Account Number", "Account Holder Name", "Amount", "Reference", "Bank"])

		# Data rows
		for payout in self.payouts:
			writer.writerow([
				payout.bank_account_number,
				payout.account_holder_name,
				f"{flt(payout.payout_amount):.2f}",
				payout.name,
				payout.bank_name
			])

		return output.getvalue()

	def generate_unionbank_format(self):
		"""
		Generate UnionBank bulk upload format
		Format: Account Number|Amount|Reference|Beneficiary Name
		"""
		output = StringIO()

		# UnionBank uses pipe-delimited format
		for payout in self.payouts:
			output.write(f"{payout.bank_account_number}|")
			output.write(f"{flt(payout.payout_amount):.2f}|")
			output.write(f"{payout.name}|")
			output.write(f"{payout.account_holder_name}\n")

		return output.getvalue()

	def generate_bdo_format(self):
		"""
		Generate BDO bulk disbursement format
		Format: CSV with specific column order
		"""
		output = StringIO()
		writer = csv.writer(output)

		# BDO Header
		writer.writerow([
			"Account Number",
			"Beneficiary Name",
			"Amount",
			"Particulars",
			"Email Address"
		])

		# Data rows
		for payout in self.payouts:
			beneficiary = frappe.get_doc("User", payout.beneficiary)
			writer.writerow([
				payout.bank_account_number,
				payout.account_holder_name,
				f"{flt(payout.payout_amount):.2f}",
				f"Social Assistance - {payout.name}",
				beneficiary.email
			])

		return output.getvalue()

	def generate_instapay_format(self):
		"""
		Generate Instapay transfer format
		Format: CSV for InstaPay network
		"""
		output = StringIO()
		writer = csv.writer(output)

		# Header
		writer.writerow([
			"Receiving Bank",
			"Account Number",
			"Account Name",
			"Amount",
			"Purpose",
			"Reference Number"
		])

		# Data rows
		for payout in self.payouts:
			writer.writerow([
				payout.bank_name,
				payout.bank_account_number,
				payout.account_holder_name,
				f"{flt(payout.payout_amount):.2f}",
				"Social Assistance Payment",
				payout.name
			])

		return output.getvalue()

	def generate_gcash_format(self):
		"""
		Generate GCash bulk disbursement format
		Format: Mobile Number, Amount, Reference
		"""
		# Get GCash payouts
		gcash_payouts = frappe.get_all("Benefit Payout",
									  filters={
										  "payout_batch": self.batch.name,
										  "payout_status": "Approved",
										  "payment_method": "GCash"
									  },
									  fields=["*"])

		output = StringIO()
		writer = csv.writer(output)

		# Header
		writer.writerow(["Mobile Number", "Amount", "Reference", "Message"])

		# Data rows
		for payout in gcash_payouts:
			writer.writerow([
				payout.gcash_number,
				f"{flt(payout.payout_amount):.2f}",
				payout.name,
				f"Social Assistance from TayTay Council"
			])

		return output.getvalue()

	def save_file(self, content, format_type):
		"""Save generated file and attach to batch"""
		import os
		from frappe.utils.file_manager import save_file

		filename = f"{self.batch.name}_{format_type}_{nowdate()}.csv"

		# Save file
		file_doc = save_file(
			filename,
			content,
			"Payout Batch",
			self.batch.name,
			is_private=1
		)

		# Update batch
		self.batch.bank_file = file_doc.file_url
		self.batch.bank_file_format = format_type
		self.batch.file_generated_date = frappe.utils.now()
		self.batch.save(ignore_permissions=True)

		# Mark payouts as file generated
		frappe.db.sql("""
			UPDATE `tabBenefit Payout`
			SET bank_file_generated = 1
			WHERE payout_batch = %s
				AND payout_status = 'Approved'
		""", self.batch.name)

		frappe.db.commit()

		return file_doc.file_url

	def generate_and_save(self, format_type="CSV"):
		"""Generate file and save to batch"""
		if format_type == "CSV":
			content = self.generate_csv_generic()
		elif format_type == "UnionBank Format":
			content = self.generate_unionbank_format()
		elif format_type == "BDO Format":
			content = self.generate_bdo_format()
		elif format_type == "Instapay":
			content = self.generate_instapay_format()
		elif format_type == "GCash":
			content = self.generate_gcash_format()
		else:
			content = self.generate_csv_generic()

		return self.save_file(content, format_type)
