# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe


def setup_taytay_council():
	"""Create TayTay Council record for Philippines"""
	from frappe.utils import nowdate, add_months

	# Check if council already exists
	if frappe.db.exists("Council", "TAYTAY-PH"):
		print("TayTay Council already exists")
		return frappe.get_doc("Council", "TAYTAY-PH")

	council = frappe.get_doc({
		"doctype": "Council",
		"council_code": "TAYTAY-PH",
		"council_name": "TayTay Council",
		"official_name": "Municipal Government of Taytay, Rizal",
		"contact_email": "info@taytay.gov.ph",
		"contact_phone": "+63 2 8123 4567",
		"website": "https://taytay.gov.ph",
		"address_line_1": "Municipal Hall",
		"city": "Taytay, Rizal",
		"postal_code": "1920",
		"timezone": "Asia/Manila",
		"primary_color": "#0066CC",
		"secondary_color": "#1E40AF",
		"is_active": 1,
		"license_start_date": nowdate(),
		"license_expiry_date": add_months(nowdate(), 12),
		"max_requests_per_month": 500,
		"subscription_tier": "Premium",
		"default_sla_days": 30
	})

	# Enable only Philippines Social Assistance request types for this council
	philippines_request_types = [
		"Social Pension for Indigent Senior Citizens (SPISC)",
		"Local Senior Assistance / Financial Aid for Elderly",
		"Burial / Medical Support for Seniors"
	]

	for request_type_name in philippines_request_types:
		if frappe.db.exists("Request Type", request_type_name):
			council.append("enabled_request_types", {
				"request_type": request_type_name,
				"is_enabled": 1
			})

	council.flags.ignore_permissions = True
	council.insert()
	print(f"Created TayTay Council: {council.name}")
	return council


def setup_spisc_request_type():
	"""Create Social Pension for Indigent Senior Citizens (SPISC) request type"""

	# Check if request type already exists
	if frappe.db.exists("Request Type", "Social Pension for Indigent Senior Citizens (SPISC)"):
		print("SPISC Request Type already exists")
		return

	request_type = frappe.get_doc({
		"doctype": "Request Type",
		"type_name": "Social Pension for Indigent Senior Citizens (SPISC)",
		"type_code": "SPISC",
		"category": "Social Assistance",
		"description": """<p>The Social Pension for Indigent Senior Citizens (SPISC) is a monthly cash assistance program for senior citizens aged 60 and above who are frail, sickly, disabled, or living alone with no regular source of income or support from their families.</p>
		<p><strong>Eligibility Requirements:</strong></p>
		<ul>
			<li>60 years old or above</li>
			<li>Resident of Taytay for at least 6 months</li>
			<li>Income below the poverty threshold</li>
			<li>Not receiving pension from SSS, GSIS, or other government agencies</li>
		</ul>""",
		"processing_sla_days": 30,
		"base_fee": 0,
		"fee_calculation_method": "Fixed",
		"is_active": 1,
		"pre_app_meeting_available": 0,
		"fast_track_available": 0,
		"help_text": """<p>The monthly pension amount is PHP 500. Payment is made through bank deposit or cash pickup at the barangay hall.</p>
		<p>After approval, you will need to provide your bank account details or preferred pickup location.</p>"""
	})

	request_type.insert(ignore_permissions=True)
	print(f"Created SPISC Request Type: {request_type.name}")


def setup_lsfa_request_type():
	"""Create Local Senior Assistance / Financial Aid for Elderly request type"""

	# Check if request type already exists
	if frappe.db.exists("Request Type", "Local Senior Assistance / Financial Aid for Elderly"):
		print("LSFA Request Type already exists")
		return

	request_type = frappe.get_doc({
		"doctype": "Request Type",
		"type_name": "Local Senior Assistance / Financial Aid for Elderly",
		"type_code": "LSFA",
		"category": "Social Assistance",
		"description": """<p>Local Senior Assistance provides one-time financial aid to elderly residents of Taytay who are facing emergency situations, medical needs, or financial crisis.</p>
		<p><strong>Eligibility Requirements:</strong></p>
		<ul>
			<li>60 years old or above</li>
			<li>Resident of Taytay</li>
			<li>Experiencing medical or financial emergency</li>
			<li>Has verified identity documentation</li>
		</ul>""",
		"processing_sla_days": 15,
		"base_fee": 0,
		"fee_calculation_method": "Fixed",
		"is_active": 1,
		"pre_app_meeting_available": 0,
		"fast_track_available": 1,
		"help_text": """<p>Financial aid ranges from PHP 1,000 to PHP 10,000 depending on the nature and severity of the emergency.</p>
		<p>Applications are processed on a case-by-case basis with priority given to urgent medical needs.</p>"""
	})

	request_type.insert(ignore_permissions=True)
	print(f"Created LSFA Request Type: {request_type.name}")


def setup_bmss_request_type():
	"""Create Burial / Medical Support for Seniors request type"""

	# Check if request type already exists
	if frappe.db.exists("Request Type", "Burial / Medical Support for Seniors"):
		print("BMSS Request Type already exists")
		return

	request_type = frappe.get_doc({
		"doctype": "Request Type",
		"type_name": "Burial / Medical Support for Seniors",
		"type_code": "BMSS",
		"category": "Social Assistance",
		"description": """<p>Burial and Medical Support provides financial assistance to families of deceased senior citizens or for critical medical expenses of senior citizens.</p>
		<p><strong>Eligibility Requirements:</strong></p>
		<ul>
			<li>Deceased/Patient was 60 years old or above</li>
			<li>Deceased/Patient was a resident of Taytay</li>
			<li>Applicant is a family member with verified identity</li>
			<li>Has required documentation (death certificate or medical certificate)</li>
		</ul>""",
		"processing_sla_days": 7,
		"base_fee": 0,
		"fee_calculation_method": "Fixed",
		"is_active": 1,
		"pre_app_meeting_available": 0,
		"fast_track_available": 1,
		"help_text": """<p><strong>Burial Assistance:</strong> Up to PHP 10,000 to cover funeral expenses</p>
		<p><strong>Medical Assistance:</strong> Up to PHP 15,000 per critical illness/hospitalization</p>
		<p>Payment can be made directly to service providers or as reimbursement to the family.</p>"""
	})

	request_type.insert(ignore_permissions=True)
	print(f"Created BMSS Request Type: {request_type.name}")


def setup_philippines_data():
	"""Main function to set up all Philippines-related data"""

	print("\n" + "="*50)
	print("Setting up Philippines Social Services Data")
	print("="*50 + "\n")

	# Create TayTay Council
	print("1. Creating TayTay Council...")
	council = setup_taytay_council()

	# Create Request Types
	print("\n2. Creating Social Assistance Request Types...")
	setup_spisc_request_type()
	setup_lsfa_request_type()
	setup_bmss_request_type()

	# Commit all changes
	frappe.db.commit()

	print("\n" + "="*50)
	print("Philippines setup completed successfully!")
	print("="*50 + "\n")

	print("Created:")
	print(f"  - TayTay Council (Code: TAYTAY-PH)")
	print(f"  - SPISC Request Type")
	print(f"  - LSFA Request Type")
	print(f"  - BMSS Request Type")


if __name__ == "__main__":
	frappe.init(site="hohmesy.com")
	frappe.connect()
	setup_philippines_data()
