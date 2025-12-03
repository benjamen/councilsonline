# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_lodgeick_custom_fields():
	"""Create custom fields for Request and User doctypes"""

	custom_fields = {
		# Request custom fields for draft metadata, disbursements and total costing
		"Request": [
			{
				"fieldname": "draft_metadata_section",
				"label": "Draft Metadata",
				"fieldtype": "Section Break",
				"insert_after": "amended_from",
				"collapsible": 1,
				"hidden": 0,
				"depends_on": "eval:doc.status=='Draft'"
			},
			{
				"fieldname": "draft_current_step",
				"label": "Current Step (Draft)",
				"fieldtype": "Int",
				"insert_after": "draft_metadata_section",
				"read_only": 1,
				"default": "1",
				"description": "The step number where the draft was last saved (1-indexed)"
			},
			{
				"fieldname": "draft_total_steps",
				"label": "Total Steps (Draft)",
				"fieldtype": "Int",
				"insert_after": "draft_current_step",
				"read_only": 1,
				"description": "Total number of steps in the request form"
			},
			{
				"fieldname": "column_break_draft",
				"fieldtype": "Column Break",
				"insert_after": "draft_total_steps"
			},
			{
				"fieldname": "draft_created_at",
				"label": "Draft Created At",
				"fieldtype": "Datetime",
				"insert_after": "column_break_draft",
				"read_only": 1,
				"default": "now"
			},
			{
				"fieldname": "draft_updated_at",
				"label": "Draft Last Updated",
				"fieldtype": "Datetime",
				"insert_after": "draft_created_at",
				"read_only": 1
			},
			{
				"fieldname": "draft_full_data",
				"label": "Draft Full Data (JSON)",
				"fieldtype": "Long Text",
				"insert_after": "draft_updated_at",
				"read_only": 1,
				"hidden": 1,
				"description": "Complete form data stored as JSON for draft resumption"
			},
			{
				"fieldname": "lodgeick_company_section",
				"fieldtype": "Section Break",
				"label": "Company Submission",
				"insert_after": "applicant_email",
				"collapsible": 1
			},
			{
				"fieldname": "company_account",
				"fieldtype": "Link",
				"label": "Company Account",
				"options": "Company Account",
				"insert_after": "lodgeick_company_section",
				"description": "Company submitting this application (if applicable)"
			},
			{
				"fieldname": "submitted_by",
				"fieldtype": "Link",
				"label": "Submitted By (User)",
				"options": "User",
				"insert_after": "company_account",
				"read_only": 1,
				"description": "Individual user who submitted this application"
			},
			{
				"fieldname": "submitted_on_behalf_of",
				"fieldtype": "Select",
				"label": "Submitted On Behalf Of",
				"options": "\nMyself\nCompany",
				"insert_after": "submitted_by",
				"description": "Whether submitting for self or on behalf of company"
			},
			{
				"fieldname": "lodgeick_disbursements_section",
				"fieldtype": "Section Break",
				"label": "Disbursements",
				"insert_after": "request_fee",
				"collapsible": 1
			},
			{
				"fieldname": "disbursements",
				"fieldtype": "Table",
				"label": "Disbursement Items",
				"options": "Disbursement Item",
				"insert_after": "lodgeick_disbursements_section"
			},
			{
				"fieldname": "lodgeick_total_costing_section",
				"fieldtype": "Section Break",
				"label": "Total Costing",
				"insert_after": "disbursements",
				"collapsible": 0
			},
			{
				"fieldname": "total_task_cost",
				"fieldtype": "Currency",
				"label": "Total Task Cost",
				"insert_after": "lodgeick_total_costing_section",
				"read_only": 1,
				"description": "Sum of all linked task costs"
			},
			{
				"fieldname": "total_disbursements",
				"fieldtype": "Currency",
				"label": "Total Disbursements",
				"insert_after": "total_task_cost",
				"read_only": 1,
				"description": "Sum of all disbursement items"
			},
			{
				"fieldname": "column_break_total",
				"fieldtype": "Column Break",
				"insert_after": "total_disbursements"
			},
			{
				"fieldname": "application_fee",
				"fieldtype": "Currency",
				"label": "Application Fee",
				"insert_after": "column_break_total",
				"read_only": 1,
				"description": "From request fees"
			},
			{
				"fieldname": "total_amount_due",
				"fieldtype": "Currency",
				"label": "Total Amount Due",
				"insert_after": "application_fee",
				"read_only": 1,
				"bold": 1,
				"description": "Application Fee + Task Costs + Disbursements"
			}
		],

		# User custom fields for council association and account type
		"User": [
			{
				"fieldname": "lodgeick_account_section",
				"fieldtype": "Section Break",
				"label": "Account Information",
				"insert_after": "user_image",
				"collapsible": 1
			},
			{
				"fieldname": "account_type",
				"fieldtype": "Select",
				"label": "Account Type",
				"options": "\nApplicant\nAgent",
				"insert_after": "lodgeick_account_section",
				"description": "Applicant: Submit applications for yourself. Agent: Submit applications on behalf of clients.",
				"default": "Applicant"
			},
			{
				"fieldname": "applicant_type",
				"fieldtype": "Select",
				"label": "Default Applicant Type",
				"options": "\nIndividual\nCompany\nTrust\nPartnership\nOther",
				"insert_after": "account_type",
				"description": "Default applicant type for new applications",
				"depends_on": "eval:doc.account_type=='Applicant'"
			},
			{
				"fieldname": "lodgeick_company_section",
				"fieldtype": "Section Break",
				"label": "Company Account",
				"insert_after": "applicant_type",
				"collapsible": 1
			},
			{
				"fieldname": "company_account",
				"fieldtype": "Link",
				"label": "Company Account",
				"options": "Company Account",
				"insert_after": "lodgeick_company_section",
				"description": "Link to company account if user is part of a company"
			},
			{
				"fieldname": "company_role",
				"fieldtype": "Select",
				"label": "Company Role",
				"options": "\nAdmin\nSubmitter\nViewer",
				"insert_after": "company_account",
				"depends_on": "eval:doc.company_account",
				"description": "Role within the company account"
			},
			{
				"fieldname": "lodgeick_council_section",
				"fieldtype": "Section Break",
				"label": "Council Preferences",
				"insert_after": "company_role",
				"collapsible": 1
			},
			{
				"fieldname": "default_council",
				"fieldtype": "Link",
				"label": "Default Council",
				"options": "Council",
				"insert_after": "lodgeick_council_section",
				"description": "Your preferred council for new requests"
			},
			{
				"fieldname": "lodgeick_philippines_section",
				"fieldtype": "Section Break",
				"label": "Philippines Information",
				"insert_after": "default_council",
				"collapsible": 1,
				"depends_on": "eval:doc.country_of_residence=='Philippines'"
			},
			{
				"fieldname": "country_of_residence",
				"fieldtype": "Select",
				"label": "Country of Residence",
				"options": "\nNew Zealand\nPhilippines\nOther",
				"insert_after": "default_council",
				"description": "Country where you currently reside"
			},
			{
				"fieldname": "philippines_barangay",
				"fieldtype": "Data",
				"label": "Barangay",
				"insert_after": "lodgeick_philippines_section",
				"depends_on": "eval:doc.country_of_residence=='Philippines'",
				"description": "Smallest administrative division in Philippines"
			},
			{
				"fieldname": "philippines_municipality",
				"fieldtype": "Data",
				"label": "Municipality/City",
				"insert_after": "philippines_barangay",
				"depends_on": "eval:doc.country_of_residence=='Philippines'",
				"description": "Municipality or city in Philippines"
			},
			{
				"fieldname": "philippines_province",
				"fieldtype": "Data",
				"label": "Province",
				"insert_after": "philippines_municipality",
				"depends_on": "eval:doc.country_of_residence=='Philippines'",
				"description": "Province in Philippines"
			}
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	print("Custom fields created successfully!")


if __name__ == "__main__":
	frappe.init(site="lodgeick.localhost")
	frappe.connect()
	create_lodgeick_custom_fields()
