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

	# Configure Step Flows
	print("\n3. Configuring Request Type Steps...")
	configure_all_philippines_steps()

	# Commit all changes
	frappe.db.commit()

	print("\n" + "="*50)
	print("Philippines setup completed successfully!")
	print("="*50 + "\n")

	print("Created:")
	print(f"  - TayTay Council (Code: TAYTAY-PH)")
	print(f"  - SPISC Request Type (with 5-step configuration)")
	print(f"  - LSFA Request Type")
	print(f"  - BMSS Request Type")


if __name__ == "__main__":
	frappe.init(site="lodgeick.localhost")
	frappe.connect()
	setup_philippines_data()


def configure_spisc_steps():
	"""Configure 5-step flow for SPISC request type"""
	
	request_type_name = "Social Pension for Indigent Senior Citizens (SPISC)"
	
	if not frappe.db.exists("Request Type", request_type_name):
		print(f"Request Type {request_type_name} not found. Please create it first.")
		return
	
	request_type = frappe.get_doc("Request Type", request_type_name)
	
	# Clear existing step configs
	request_type.step_configs = []
	
	print(f"\nConfiguring steps for {request_type_name}...")
	
	# ============================================================
	# STEP 1: Personal Information
	# ============================================================
	step1 = request_type.append("step_configs", {
		"step_number": 1,
		"step_code": "personal_info",
		"step_title": "Personal Information",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	# Section: Basic Details
	section1_1 = step1.append("sections", {
		"section_code": "basic_details",
		"section_title": "Basic Details",
		"section_type": "Section",
		"sequence": 1,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_1.append("fields", {
		"field_name": "full_name",
		"field_label": "Full Name",
		"field_type": "Data",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_1.append("fields", {
		"field_name": "birth_date",
		"field_label": "Date of Birth",
		"field_type": "Date",
		"is_required": 1,
		"show_on_review": 1,
		"review_label": "Age / Date of Birth"
	})
	
	section1_1.append("fields", {
		"field_name": "sex",
		"field_label": "Sex",
		"field_type": "Select",
		"options": "Male\nFemale",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_1.append("fields", {
		"field_name": "civil_status",
		"field_label": "Civil Status",
		"field_type": "Select",
		"options": "Single\nMarried\nWidowed\nSeparated",
		"is_required": 1,
		"show_on_review": 1
	})
	
	# Section: Contact Information
	section1_2 = step1.append("sections", {
		"section_code": "contact_info",
		"section_title": "Contact Information",
		"section_type": "Section",
		"sequence": 2,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_2.append("fields", {
		"field_name": "mobile_number",
		"field_label": "Mobile Number",
		"field_type": "Data",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_2.append("fields", {
		"field_name": "email",
		"field_label": "Email Address",
		"field_type": "Data",
		"is_required": 0,
		"show_on_review": 1
	})
	
	# Section: Address
	section1_3 = step1.append("sections", {
		"section_code": "address",
		"section_title": "Residential Address",
		"section_type": "Section",
		"sequence": 3,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_3.append("fields", {
		"field_name": "address_line",
		"field_label": "Street / House Number",
		"field_type": "Data",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_3.append("fields", {
		"field_name": "barangay",
		"field_label": "Barangay",
		"field_type": "Data",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_3.append("fields", {
		"field_name": "municipality",
		"field_label": "Municipality",
		"field_type": "Data",
		"default_value": "Taytay",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section1_3.append("fields", {
		"field_name": "province",
		"field_label": "Province",
		"field_type": "Data",
		"default_value": "Rizal",
		"is_required": 1,
		"show_on_review": 1
	})
	
	print("  ✓ Step 1: Personal Information configured")
	
	# ============================================================
	# STEP 2: Household Information
	# ============================================================
	step2 = request_type.append("step_configs", {
		"step_number": 2,
		"step_code": "household_info",
		"step_title": "Household Information",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	# Section: Household Composition
	section2_1 = step2.append("sections", {
		"section_code": "household_composition",
		"section_title": "Household Composition",
		"section_type": "Section",
		"sequence": 1,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	section2_1.append("fields", {
		"field_name": "household_size",
		"field_label": "Number of Household Members",
		"field_type": "Int",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section2_1.append("fields", {
		"field_name": "living_arrangement",
		"field_label": "Living Arrangement",
		"field_type": "Select",
		"options": "Living alone\nLiving with spouse\nLiving with children\nLiving with relatives\nOther",
		"is_required": 1,
		"show_on_review": 1
	})
	
	# Section: Economic Status
	section2_2 = step2.append("sections", {
		"section_code": "economic_status",
		"section_title": "Economic Status",
		"section_type": "Section",
		"sequence": 2,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	section2_2.append("fields", {
		"field_name": "monthly_income",
		"field_label": "Total Monthly Household Income (PHP)",
		"field_type": "Currency",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section2_2.append("fields", {
		"field_name": "income_source",
		"field_label": "Main Source of Income",
		"field_type": "Select",
		"options": "None\nFamily Support\nPension\nOccasional Work\nOther",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section2_2.append("fields", {
		"field_name": "housing_type",
		"field_label": "Housing Type",
		"field_type": "Select",
		"options": "Own House\nRented\nLiving with Family\nInformal Settler",
		"is_required": 1,
		"show_on_review": 1
	})
	
	print("  ✓ Step 2: Household Information configured")
	
	# ============================================================
	# STEP 3: Identity Verification
	# ============================================================
	step3 = request_type.append("step_configs", {
		"step_number": 3,
		"step_code": "identity_verification",
		"step_title": "Identity Verification",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	# Section: National IDs
	section3_1 = step3.append("sections", {
		"section_code": "national_ids",
		"section_title": "National Identification",
		"section_type": "Section",
		"sequence": 1,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	section3_1.append("fields", {
		"field_name": "philsys_id",
		"field_label": "PhilSys ID Number",
		"field_type": "Data",
		"is_required": 0,
		"show_on_review": 1
	})
	
	section3_1.append("fields", {
		"field_name": "sss_number",
		"field_label": "SSS Number",
		"field_type": "Data",
		"is_required": 0,
		"show_on_review": 1
	})
	
	section3_1.append("fields", {
		"field_name": "gsis_number",
		"field_label": "GSIS Number (if applicable)",
		"field_type": "Data",
		"is_required": 0,
		"show_on_review": 0
	})
	
	section3_1.append("fields", {
		"field_name": "has_existing_pension",
		"field_label": "Do you currently receive any government pension?",
		"field_type": "Check",
		"is_required": 1,
		"show_on_review": 1,
		"review_label": "Currently Receiving Pension"
	})
	
	print("  ✓ Step 3: Identity Verification configured")
	
	# ============================================================
	# STEP 4: Supporting Documents
	# ============================================================
	step4 = request_type.append("step_configs", {
		"step_number": 4,
		"step_code": "supporting_documents",
		"step_title": "Supporting Documents",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	# Section: Required Documents
	section4_1 = step4.append("sections", {
		"section_code": "required_documents",
		"section_title": "Required Documents",
		"section_type": "Section",
		"sequence": 1,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	section4_1.append("fields", {
		"field_name": "valid_id",
		"field_label": "Valid Government-Issued ID",
		"field_type": "Attach Image",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section4_1.append("fields", {
		"field_name": "barangay_certificate",
		"field_label": "Barangay Certificate of Residency",
		"field_type": "Attach",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section4_1.append("fields", {
		"field_name": "birth_certificate",
		"field_label": "Birth Certificate or Baptismal Certificate",
		"field_type": "Attach",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section4_1.append("fields", {
		"field_name": "recent_photo",
		"field_label": "Recent 2x2 Photo",
		"field_type": "Attach Image",
		"is_required": 1,
		"show_on_review": 0
	})
	
	# Section: Optional Documents
	section4_2 = step4.append("sections", {
		"section_code": "optional_documents",
		"section_title": "Optional Supporting Documents",
		"section_type": "Section",
		"sequence": 2,
		"is_enabled": 1,
		"is_required": 0,
		"show_on_review": 0
	})
	
	section4_2.append("fields", {
		"field_name": "medical_certificate",
		"field_label": "Medical Certificate (if frail/sickly/disabled)",
		"field_type": "Attach",
		"is_required": 0,
		"show_on_review": 0
	})
	
	section4_2.append("fields", {
		"field_name": "indigency_certificate",
		"field_label": "Certificate of Indigency",
		"field_type": "Attach",
		"is_required": 0,
		"show_on_review": 0
	})
	
	print("  ✓ Step 4: Supporting Documents configured")
	
	# ============================================================
	# STEP 5: Declaration & Submission
	# ============================================================
	step5 = request_type.append("step_configs", {
		"step_number": 5,
		"step_code": "declaration",
		"step_title": "Declaration & Submission",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	# Section: Declaration
	section5_1 = step5.append("sections", {
		"section_code": "declaration",
		"section_title": "Applicant Declaration",
		"section_type": "Section",
		"sequence": 1,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})
	
	section5_1.append("fields", {
		"field_name": "declaration_truth",
		"field_label": "I declare that all information provided in this application is true and correct",
		"field_type": "Check",
		"is_required": 1,
		"show_on_review": 1,
		"review_label": "Truth Declaration"
	})
	
	section5_1.append("fields", {
		"field_name": "declaration_consent",
		"field_label": "I consent to the collection, processing, and verification of my personal information in accordance with RA 10173 (Data Privacy Act)",
		"field_type": "Check",
		"is_required": 1,
		"show_on_review": 1,
		"review_label": "Data Privacy Consent"
	})
	
	section5_1.append("fields", {
		"field_name": "signature",
		"field_label": "Signature or Thumbmark",
		"field_type": "Attach Image",
		"is_required": 1,
		"show_on_review": 1
	})
	
	section5_1.append("fields", {
		"field_name": "signature_date",
		"field_label": "Date Signed",
		"field_type": "Date",
		"default_value": "Today",
		"is_required": 1,
		"show_on_review": 1
	})
	
	print("  ✓ Step 5: Declaration & Submission configured")
	
	# Save the request type
	request_type.save(ignore_permissions=True)
	frappe.db.commit()
	
	print(f"\n✅ Successfully configured 5-step flow for {request_type_name}")
	print(f"   Total steps: {len(request_type.step_configs)}")
	
	# Print summary
	for step in request_type.step_configs:
		section_count = len(step.sections) if hasattr(step, 'sections') else 0
		print(f"   - Step {step.step_number}: {step.step_title} ({section_count} sections)")


def configure_all_philippines_steps():
	"""Configure steps for all Philippines request types"""
	
	print("\n" + "="*60)
	print("CONFIGURING PHILIPPINES REQUEST TYPE STEPS")
	print("="*60)
	
	# Configure SPISC
	configure_spisc_steps()
	
	print("\n" + "="*60)
	print("Philippines step configuration completed!")
	print("="*60 + "\n")


