# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_lodgeick_custom_fields():
	"""Create custom fields for WB Task and Request doctypes"""

	custom_fields = {
		# WB Task custom fields for costing
		"WB Task": [
			{
				"fieldname": "lodgeick_costing_section",
				"fieldtype": "Section Break",
				"label": "Lodgeick Costing",
				"insert_after": "wb_task_checklist_details",
				"collapsible": 0
			},
			{
				"fieldname": "request",
				"fieldtype": "Link",
				"label": "Request",
				"options": "Request",
				"insert_after": "lodgeick_costing_section",
				"in_list_view": 0
			},
			{
				"fieldname": "activity_type",
				"fieldtype": "Link",
				"label": "Activity Type",
				"options": "Activity Type",
				"insert_after": "request"
			},
			{
				"fieldname": "column_break_costing1",
				"fieldtype": "Column Break",
				"insert_after": "activity_type"
			},
			{
				"fieldname": "assigned_role",
				"fieldtype": "Link",
				"label": "Assigned Role",
				"options": "Role",
				"insert_after": "column_break_costing1"
			},
			{
				"fieldname": "section_break_hours",
				"fieldtype": "Section Break",
				"label": "Time Tracking",
				"insert_after": "assigned_role",
				"collapsible": 0
			},
			{
				"fieldname": "estimated_hours",
				"fieldtype": "Float",
				"label": "Estimated Hours",
				"insert_after": "section_break_hours",
				"precision": "2"
			},
			{
				"fieldname": "actual_hours",
				"fieldtype": "Float",
				"label": "Actual Hours",
				"insert_after": "estimated_hours",
				"precision": "2"
			},
			{
				"fieldname": "column_break_costing2",
				"fieldtype": "Column Break",
				"insert_after": "actual_hours"
			},
			{
				"fieldname": "hourly_rate",
				"fieldtype": "Currency",
				"label": "Hourly Rate",
				"insert_after": "column_break_costing2",
				"read_only": 1,
				"description": "Auto-fetched from Role Rate"
			},
			{
				"fieldname": "total_cost",
				"fieldtype": "Currency",
				"label": "Total Cost",
				"insert_after": "hourly_rate",
				"read_only": 1,
				"bold": 1,
				"description": "Calculated as Actual Hours × Hourly Rate"
			}
		],

		# Request custom fields for disbursements and total costing
		"Request": [
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
				"fieldname": "lodgeick_council_section",
				"fieldtype": "Section Break",
				"label": "Council Preferences",
				"insert_after": "applicant_type",
				"collapsible": 1
			},
			{
				"fieldname": "default_council",
				"fieldtype": "Link",
				"label": "Default Council",
				"options": "Council",
				"insert_after": "lodgeick_council_section",
				"description": "Your preferred council for new requests"
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
