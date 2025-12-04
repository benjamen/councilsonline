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
	"""
	Configure 5-step flow for SPISC request type

	WORKAROUND: Frappe doesn't support nested child tables (3 levels deep).
	We need to:
	1. Save Request Type with step_configs only (no sections/fields)
	2. Manually insert sections into database using step config row names as parents
	3. Manually insert fields into database using section row names as parents
	"""

	request_type_name = "Social Pension for Indigent Senior Citizens (SPISC)"

	if not frappe.db.exists("Request Type", request_type_name):
		print(f"Request Type {request_type_name} not found. Please create it first.")
		return

	request_type = frappe.get_doc("Request Type", request_type_name)

	# Clear existing configurations
	request_type.step_configs = []
	frappe.db.delete("Request Type Step Config", {"parent": request_type_name})
	frappe.db.delete("Request Type Step Section", {"parenttype": "Request Type Step Config"})
	frappe.db.delete("Request Type Step Field", {"parenttype": "Request Type Step Section"})
	frappe.db.commit()

	print(f"\nConfiguring steps for {request_type_name}...")

	# ============================================================
	# PHASE 1: Create steps only
	# ============================================================

	# STEP 1: Personal Information
	request_type.append("step_configs", {
		"step_number": 1,
		"step_code": "personal_info",
		"step_title": "Personal Information",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})

	# STEP 2: Household Information
	request_type.append("step_configs", {
		"step_number": 2,
		"step_code": "household_info",
		"step_title": "Household Information",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})

	# STEP 3: Identity Verification
	request_type.append("step_configs", {
		"step_number": 3,
		"step_code": "identity_verification",
		"step_title": "Identity Verification",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})

	# STEP 4: Supporting Documents
	request_type.append("step_configs", {
		"step_number": 4,
		"step_code": "supporting_documents",
		"step_title": "Supporting Documents",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 0
	})

	# STEP 5: Declaration & Submission
	request_type.append("step_configs", {
		"step_number": 5,
		"step_code": "declaration",
		"step_title": "Declaration & Submission",
		"step_component": "DynamicStepRenderer",
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})

	# Save request type to generate step_config row names
	request_type.save(ignore_permissions=True)
	frappe.db.commit()

	print("  ✓ Created 5 steps")

	# ============================================================
	# PHASE 2: Manually insert sections using direct SQL
	# ============================================================

	# Reload to get the auto-generated row names
	request_type.reload()

	sections_data = []

	# Step 1 Sections
	step1_name = request_type.step_configs[0].name
	sections_data.extend([
		{
			"parent": step1_name,
			"parenttype": "Request Type Step Config",
			"parentfield": "sections",
			"section_code": "basic_details",
			"section_title": "Basic Details",
			"section_type": "Section",
			"sequence": 1,
			"is_enabled": 1,
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": step1_name,
			"parenttype": "Request Type Step Config",
			"parentfield": "sections",
			"section_code": "contact_info",
			"section_title": "Contact Information",
			"section_type": "Section",
			"sequence": 2,
			"is_enabled": 1,
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": step1_name,
			"parenttype": "Request Type Step Config",
			"parentfield": "sections",
			"section_code": "address",
			"section_title": "Residential Address",
			"section_type": "Section",
			"sequence": 3,
			"is_enabled": 1,
			"is_required": 1,
			"show_on_review": 1
		}
	])

	# Step 2 Sections
	step2_name = request_type.step_configs[1].name
	sections_data.extend([
		{
			"parent": step2_name,
			"parenttype": "Request Type Step Config",
			"parentfield": "sections",
			"section_code": "household_composition",
			"section_title": "Household Composition",
			"section_type": "Section",
			"sequence": 1,
			"is_enabled": 1,
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": step2_name,
			"parenttype": "Request Type Step Config",
			"parentfield": "sections",
			"section_code": "economic_status",
			"section_title": "Economic Status",
			"section_type": "Section",
			"sequence": 2,
			"is_enabled": 1,
			"is_required": 1,
			"show_on_review": 1
		}
	])

	# Step 3 Sections
	step3_name = request_type.step_configs[2].name
	sections_data.append({
		"parent": step3_name,
		"parenttype": "Request Type Step Config",
		"parentfield": "sections",
		"section_code": "identity_documents",
		"section_title": "Identity Documents",
		"section_type": "Section",
		"sequence": 1,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})

	# Step 4 Sections
	step4_name = request_type.step_configs[3].name
	sections_data.extend([
		{
			"parent": step4_name,
			"parenttype": "Request Type Step Config",
			"parentfield": "sections",
			"section_code": "required_documents",
			"section_title": "Required Documents",
			"section_type": "Section",
			"sequence": 1,
			"is_enabled": 1,
			"is_required": 1,
			"show_on_review": 0
		},
		{
			"parent": step4_name,
			"parenttype": "Request Type Step Config",
			"parentfield": "sections",
			"section_code": "optional_documents",
			"section_title": "Optional Supporting Documents",
			"section_type": "Section",
			"sequence": 2,
			"is_enabled": 1,
			"is_required": 0,
			"show_on_review": 0
		}
	])

	# Step 5 Sections
	step5_name = request_type.step_configs[4].name
	sections_data.append({
		"parent": step5_name,
		"parenttype": "Request Type Step Config",
		"parentfield": "sections",
		"section_code": "declaration",
		"section_title": "Applicant Declaration",
		"section_type": "Section",
		"sequence": 1,
		"is_enabled": 1,
		"is_required": 1,
		"show_on_review": 1
	})

	# Insert all sections
	section_names = {}  # Map section_code to generated name
	for section_data in sections_data:
		section_doc = frappe.get_doc({
			"doctype": "Request Type Step Section",
			**section_data
		})
		section_doc.insert(ignore_permissions=True)
		section_names[f"{section_data['parent']}_{section_data['section_code']}"] = section_doc.name

	frappe.db.commit()
	print(f"  ✓ Created {len(sections_data)} sections")

	# ============================================================
	# PHASE 3: Manually insert fields
	# ============================================================

	fields_data = []

	# Step 1 - Section 1 Fields (Basic Details)
	section1_1_name = section_names[f"{step1_name}_basic_details"]
	fields_data.extend([
		{
			"parent": section1_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "full_name",
			"field_label": "Full Name",
			"field_type": "Data",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section1_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "birth_date",
			"field_label": "Date of Birth",
			"field_type": "Date",
			"is_required": 1,
			"show_on_review": 1,
			"review_label": "Age / Date of Birth"
		},
		{
			"parent": section1_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "sex",
			"field_label": "Sex",
			"field_type": "Select",
			"options": "Male\nFemale",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section1_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "civil_status",
			"field_label": "Civil Status",
			"field_type": "Select",
			"options": "Single\nMarried\nWidowed\nSeparated",
			"is_required": 1,
			"show_on_review": 1
		}
	])

	# Step 1 - Section 2 Fields (Contact Info)
	section1_2_name = section_names[f"{step1_name}_contact_info"]
	fields_data.extend([
		{
			"parent": section1_2_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "mobile_number",
			"field_label": "Mobile Number",
			"field_type": "Data",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section1_2_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "email",
			"field_label": "Email Address",
			"field_type": "Data",
			"is_required": 0,
			"show_on_review": 1
		}
	])

	# Step 1 - Section 3 Fields (Address)
	section1_3_name = section_names[f"{step1_name}_address"]
	fields_data.extend([
		{
			"parent": section1_3_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "address_line",
			"field_label": "Street / House Number",
			"field_type": "Data",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section1_3_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "barangay",
			"field_label": "Barangay",
			"field_type": "Data",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section1_3_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "municipality",
			"field_label": "Municipality",
			"field_type": "Data",
			"default_value": "Taytay",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section1_3_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "province",
			"field_label": "Province",
			"field_type": "Data",
			"default_value": "Rizal",
			"is_required": 1,
			"show_on_review": 1
		}
	])

	# Step 2 - Section 1 Fields (Household Composition)
	section2_1_name = section_names[f"{step2_name}_household_composition"]
	fields_data.extend([
		{
			"parent": section2_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "household_size",
			"field_label": "Number of Household Members",
			"field_type": "Int",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section2_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "living_arrangement",
			"field_label": "Living Arrangement",
			"field_type": "Select",
			"options": "Living alone\nLiving with spouse\nLiving with children\nLiving with relatives\nOther",
			"is_required": 1,
			"show_on_review": 1
		}
	])

	# Step 2 - Section 2 Fields (Economic Status)
	section2_2_name = section_names[f"{step2_name}_economic_status"]
	fields_data.extend([
		{
			"parent": section2_2_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "monthly_income",
			"field_label": "Monthly Income (PHP)",
			"field_type": "Currency",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section2_2_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "income_source",
			"field_label": "Source of Income",
			"field_type": "Select",
			"options": "No income\nFamily support\nPension\nSmall business\nOther",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section2_2_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "is_4ps_beneficiary",
			"field_label": "Are you a 4Ps beneficiary?",
			"field_type": "Check",
			"is_required": 0,
			"show_on_review": 1,
			"review_label": "4Ps Beneficiary"
		}
	])

	# Step 3 - Section 1 Fields (Identity Documents)
	section3_1_name = section_names[f"{step3_name}_identity_documents"]
	fields_data.extend([
		{
			"parent": section3_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "philsys_id",
			"field_label": "PhilSys ID Number (National ID)",
			"field_type": "Data",
			"is_required": 0,
			"show_on_review": 1
		},
		{
			"parent": section3_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "sss_number",
			"field_label": "SSS/GSIS Number",
			"field_type": "Data",
			"is_required": 0,
			"show_on_review": 1
		},
		{
			"parent": section3_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "osca_id",
			"field_label": "OSCA ID Number",
			"field_type": "Data",
			"is_required": 0,
			"show_on_review": 1,
			"review_label": "Senior Citizen ID"
		},
		{
			"parent": section3_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "other_id",
			"field_label": "Other Valid ID",
			"field_type": "Data",
			"is_required": 0,
			"show_on_review": 1
		}
	])

	# Step 4 - Section 1 Fields (Required Documents)
	section4_1_name = section_names[f"{step4_name}_required_documents"]
	fields_data.extend([
		{
			"parent": section4_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "barangay_cert_indigency",
			"field_label": "Barangay Certificate of Indigency",
			"field_type": "Attach",
			"is_required": 1,
			"show_on_review": 0
		},
		{
			"parent": section4_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "birth_certificate",
			"field_label": "Birth Certificate or Baptismal Certificate",
			"field_type": "Attach",
			"is_required": 1,
			"show_on_review": 0
		},
		{
			"parent": section4_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "valid_id_copy",
			"field_label": "Photocopy of Valid ID",
			"field_type": "Attach",
			"is_required": 1,
			"show_on_review": 0
		},
		{
			"parent": section4_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "recent_photo",
			"field_label": "Recent 2x2 Photo",
			"field_type": "Attach Image",
			"is_required": 1,
			"show_on_review": 0
		}
	])

	# Step 4 - Section 2 Fields (Optional Documents)
	section4_2_name = section_names[f"{step4_name}_optional_documents"]
	fields_data.extend([
		{
			"parent": section4_2_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "medical_certificate",
			"field_label": "Medical Certificate (if frail/sickly/disabled)",
			"field_type": "Attach",
			"is_required": 0,
			"show_on_review": 0
		},
		{
			"parent": section4_2_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "indigency_certificate",
			"field_label": "Certificate of Indigency",
			"field_type": "Attach",
			"is_required": 0,
			"show_on_review": 0
		}
	])

	# Step 5 - Section 1 Fields (Declaration)
	section5_1_name = section_names[f"{step5_name}_declaration"]
	fields_data.extend([
		{
			"parent": section5_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "declaration_truth",
			"field_label": "I declare that all information provided in this application is true and correct",
			"field_type": "Check",
			"is_required": 1,
			"show_on_review": 1,
			"review_label": "Truth Declaration"
		},
		{
			"parent": section5_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "declaration_consent",
			"field_label": "I consent to the collection, processing, and verification of my personal information in accordance with RA 10173 (Data Privacy Act)",
			"field_type": "Check",
			"is_required": 1,
			"show_on_review": 1,
			"review_label": "Data Privacy Consent"
		},
		{
			"parent": section5_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "signature",
			"field_label": "Signature or Thumbmark",
			"field_type": "Attach Image",
			"is_required": 1,
			"show_on_review": 1
		},
		{
			"parent": section5_1_name,
			"parenttype": "Request Type Step Section",
			"parentfield": "fields",
			"field_name": "signature_date",
			"field_label": "Date Signed",
			"field_type": "Date",
			"default_value": "Today",
			"is_required": 1,
			"show_on_review": 1
		}
	])

	# Insert all fields
	for field_data in fields_data:
		field_doc = frappe.get_doc({
			"doctype": "Request Type Step Field",
			**field_data
		})
		field_doc.insert(ignore_permissions=True)

	frappe.db.commit()
	print(f"  ✓ Created {len(fields_data)} fields")

	print(f"\n✅ Successfully configured 5-step flow for {request_type_name}")
	print(f"   Total: 5 steps, {len(sections_data)} sections, {len(fields_data)} fields")
	print(f"   - Step 1: Personal Information (3 sections, 10 fields)")
	print(f"   - Step 2: Household Information (2 sections, 5 fields)")
	print(f"   - Step 3: Identity Verification (1 section, 4 fields)")
	print(f"   - Step 4: Supporting Documents (2 sections, 6 fields)")
	print(f"   - Step 5: Declaration & Submission (1 section, 4 fields)")
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


