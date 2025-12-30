# Copyright (c) 2025, Hohmesy and contributors
# For license information, please see license.txt

"""
Default data installation for Lodgeick
Includes Request Types, Consent Condition Templates, and their relationships
"""

import frappe
from frappe import _


def install_consent_condition_templates(force=False):
	"""Install default consent condition templates"""

	templates = [
		{
			"template_name": "Standard Consent Duration",
			"condition_code": "STD-DUR-01",
			"condition_category": "Timing",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "All",
			"timing": "Ongoing",
			"condition_text": """<p>This consent shall lapse on [DATE - 5 years from commencement], pursuant to Section 125 of the Resource Management Act 1991, unless:</p>
<ul>
<li>The consent is given effect to before the end of that period; or</li>
<li>The Council grants an extension of the lapse period pursuant to Section 125(1B) of the Act.</li>
</ul>""",
			"s108aa_purpose": "Lapse conditions",
			"s108aa_relationship": "This condition ensures the consent is exercised within a reasonable timeframe and does not remain dormant indefinitely.",
			"s108aa_reasonableness": "A 5-year lapse period is standard practice and provides sufficient time for the consent holder to commence the activity while ensuring the consent does not remain unused indefinitely.",
			"usage_notes": "Standard lapse condition. Adjust the date based on consent commencement date."
		},
		{
			"template_name": "Standard Noise Limits - Residential",
			"condition_code": "STD-NOISE-01",
			"condition_category": "Noise",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "Land Use",
			"timing": "Ongoing",
			"monitoring_required": 1,
			"condition_text": """<p>Noise from activities at {property_address} shall not exceed the following limits when measured at the boundary of any residential site:</p>
<ul>
<li>Monday to Saturday: 7:00am to 10:00pm: 55 dB LAeq</li>
<li>Monday to Saturday: 10:00pm to 7:00am: 40 dB LAeq and 70 dB LAFmax</li>
<li>Sundays and Public Holidays: 45 dB LAeq and 70 dB LAFmax</li>
</ul>
<p>Noise shall be measured and assessed in accordance with NZS 6801:2008 Acoustics - Measurement of Environmental Sound and NZS 6802:2008 Acoustics - Environmental Noise.</p>""",
			"s108aa_purpose": "Avoid, remedy, or mitigate adverse effects",
			"s108aa_relationship": "This condition relates directly to the potential noise effects from the proposed activity on neighboring residential properties.",
			"s108aa_reasonableness": "The noise limits are consistent with District Plan standards and are necessary to protect residential amenity values.",
			"usage_notes": "Standard residential noise condition. Adjust limits based on zone and specific activity."
		},
		{
			"template_name": "Hours of Operation - Commercial",
			"condition_code": "STD-HOURS-01",
			"condition_category": "Operation",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "Land Use",
			"timing": "Ongoing",
			"condition_text": """<p>The activity at {property_address} shall only operate between the following hours:</p>
<ul>
<li>Monday to Friday: 7:00am to 9:00pm</li>
<li>Saturday: 8:00am to 8:00pm</li>
<li>Sunday and Public Holidays: 9:00am to 6:00pm</li>
</ul>""",
			"s108aa_purpose": "Avoid, remedy, or mitigate adverse effects",
			"s108aa_relationship": "Operating hours directly relate to the timing and intensity of effects on neighboring properties and the surrounding environment.",
			"s108aa_reasonableness": "Restricting hours of operation is necessary to manage amenity effects and is consistent with maintaining the character of the area.",
			"usage_notes": "Adjust hours based on activity type and zone requirements."
		},
		{
			"template_name": "Landscaping Implementation",
			"condition_code": "STD-LAND-01",
			"condition_category": "Landscape",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "Land Use",
			"timing": "Upon Completion",
			"monitoring_required": 1,
			"condition_text": """<p>The landscaping shown on the approved plans (Drawing No. [INSERT]) shall be implemented and maintained as follows:</p>
<ul>
<li>All landscaping shall be completed within 6 months of the commencement of the use of the site or building, whichever is sooner.</li>
<li>All planting shall be maintained in a healthy and vigorous state. Any plants that die or become diseased shall be replaced within the next planting season.</li>
<li>Landscaping shall be maintained for the duration of the consent.</li>
</ul>""",
			"s108aa_purpose": "Avoid, remedy, or mitigate adverse effects",
			"s108aa_relationship": "Landscaping mitigates visual effects and enhances amenity values of the development.",
			"s108aa_reasonableness": "Landscaping requirements are necessary to ensure the development integrates appropriately with the surrounding environment and maintains visual amenity.",
			"usage_notes": "Reference specific approved landscape plans. Adjust timeframes as needed."
		},
		{
			"template_name": "Traffic Management Plan Required",
			"condition_code": "STD-TMP-01",
			"condition_category": "Traffic",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "Land Use",
			"timing": "Before Commencement",
			"monitoring_required": 1,
			"condition_text": """<p>Prior to the commencement of the activity, a Traffic Management Plan (TMP) shall be prepared by a suitably qualified traffic engineer and submitted to the Council for certification. The TMP shall address:</p>
<ul>
<li>Construction traffic routes and timing</li>
<li>Parking and loading arrangements during construction</li>
<li>Traffic management measures during peak times</li>
<li>Measures to minimize disruption to neighboring properties and road users</li>
<li>Monitoring and review procedures</li>
</ul>
<p>The certified TMP shall be implemented and maintained for the duration of construction activities.</p>""",
			"s108aa_purpose": "Avoid, remedy, or mitigate adverse effects",
			"s108aa_relationship": "The TMP directly relates to managing traffic and access effects arising from the development.",
			"s108aa_reasonableness": "A TMP is necessary to ensure traffic effects are appropriately managed and to maintain safety and efficiency of the transport network.",
			"usage_notes": "Typically required for larger developments or those with significant traffic generation."
		},
		{
			"template_name": "Stormwater Management - Onsite Disposal",
			"condition_code": "STD-SW-01",
			"condition_category": "Discharge",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "All",
			"timing": "Before Commencement",
			"monitoring_required": 1,
			"condition_text": """<p>All stormwater runoff from impervious surfaces at {property_address} shall be managed onsite through an approved stormwater disposal system that:</p>
<ul>
<li>Is designed and constructed in accordance with the Council's Engineering Standards</li>
<li>Provides for the disposal of stormwater from a 1 in 10 year storm event</li>
<li>Includes appropriate pre-treatment measures to remove sediment and contaminants</li>
<li>Is maintained in perpetuity by the consent holder</li>
</ul>
<p>Certification from a suitably qualified engineer that the system has been constructed in accordance with the approved design shall be provided to the Council prior to occupation.</p>""",
			"s108aa_purpose": "Avoid, remedy, or mitigate adverse effects",
			"s108aa_relationship": "Stormwater management directly relates to avoiding adverse effects on neighboring properties and the receiving environment from increased runoff.",
			"s108aa_reasonableness": "Onsite stormwater management is necessary to ensure the development does not increase flooding risk or water quality degradation.",
			"usage_notes": "Adjust requirements based on site-specific conditions and catchment sensitivity."
		},
		{
			"template_name": "Earthworks Erosion and Sediment Control",
			"condition_code": "STD-ESC-01",
			"condition_category": "Earthworks",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "All",
			"timing": "During Construction",
			"monitoring_required": 1,
			"condition_text": """<p>Prior to the commencement of earthworks, an Erosion and Sediment Control Plan (ESCP) shall be prepared in accordance with the Auckland Council Guideline Document GD05 and submitted to the Council for certification. The ESCP shall:</p>
<ul>
<li>Identify all potential sources of sediment</li>
<li>Provide details of erosion and sediment control measures</li>
<li>Include a site plan showing the location of all controls</li>
<li>Specify maintenance and monitoring procedures</li>
<li>Include contingency measures for adverse weather</li>
</ul>
<p>All earthworks shall be undertaken in accordance with the certified ESCP. Erosion and sediment control measures shall be maintained in effective working order until the site is stabilized.</p>""",
			"s108aa_purpose": "Avoid, remedy, or mitigate adverse effects",
			"s108aa_relationship": "The ESCP relates directly to managing sediment discharge effects from earthworks activities.",
			"s108aa_reasonableness": "An ESCP is necessary to prevent sediment discharge to waterways and neighboring properties during earthworks.",
			"usage_notes": "Essential for any significant earthworks. Reference relevant regional guidelines."
		},
		{
			"template_name": "Accidental Discovery Protocol - Heritage",
			"condition_code": "STD-ADP-01",
			"condition_category": "Heritage",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "All",
			"timing": "During Construction",
			"condition_text": """<p>In the event that archaeological material is discovered during earthworks or construction:</p>
<ul>
<li>All work in the immediate vicinity shall cease immediately</li>
<li>Heritage New Zealand Pouhere Taonga shall be notified within 24 hours</li>
<li>The Council shall be notified within 24 hours</li>
<li>Appropriate iwi groups shall be notified within 24 hours</li>
<li>Work shall not resume until Heritage New Zealand provides written approval</li>
</ul>
<p>Note: It is an offense under the Heritage New Zealand Pouhere Taonga Act 2014 to modify, damage, or destroy an archaeological site without an authority from Heritage New Zealand.</p>""",
			"s108aa_purpose": "Avoid, remedy, or mitigate adverse effects",
			"s108aa_relationship": "This protocol relates to the protection of archaeological and heritage values that may be present on the site.",
			"s108aa_reasonableness": "The accidental discovery protocol is necessary to ensure compliance with heritage legislation and to protect culturally significant materials.",
			"usage_notes": "Standard condition for any consent involving ground disturbance."
		},
		{
			"template_name": "Construction Management Plan",
			"condition_code": "STD-CMP-01",
			"condition_category": "Construction",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "Land Use",
			"timing": "Before Commencement",
			"monitoring_required": 1,
			"condition_text": """<p>Prior to the commencement of construction, a Construction Management Plan (CMP) shall be prepared and submitted to the Council for certification. The CMP shall address:</p>
<ul>
<li>Construction staging and timing</li>
<li>Site access and parking arrangements</li>
<li>Hours of construction activity</li>
<li>Noise and vibration management</li>
<li>Dust suppression measures</li>
<li>Waste management and disposal</li>
<li>Emergency contact details</li>
<li>Communication with neighboring properties</li>
</ul>
<p>Construction activities shall be undertaken in accordance with the certified CMP at all times.</p>""",
			"s108aa_purpose": "Avoid, remedy, or mitigate adverse effects",
			"s108aa_relationship": "The CMP relates to managing all construction-related effects on neighboring properties and the surrounding environment.",
			"s108aa_reasonableness": "A comprehensive CMP is necessary to ensure construction effects are appropriately managed and minimized.",
			"usage_notes": "Essential for larger developments or those in sensitive locations."
		},
		{
			"template_name": "Consent Notice Registration",
			"condition_code": "STD-CN-01",
			"condition_category": "General",
			"is_standard": 1,
			"is_active": 1,
			"applies_to_consent_types": "All",
			"timing": "Before Commencement",
			"condition_text": """<p>Within 10 working days of this consent being granted, a consent notice pursuant to Section 221 of the Resource Management Act 1991 shall be prepared and submitted to the Council for approval. The consent notice shall identify the conditions of this consent that shall apply in perpetuity and run with the land.</p>
<p>The approved consent notice shall be registered on the Record of Title for {property_address} at the consent holder's expense prior to the commencement of the activity or occupation of the site, whichever is sooner.</p>""",
			"s108aa_purpose": "Administrative matters",
			"s108aa_relationship": "Registration of a consent notice ensures ongoing conditions are recorded against the title and bind future owners.",
			"s108aa_reasonableness": "A consent notice is necessary to ensure perpetual conditions are legally enforceable against future landowners.",
			"usage_notes": "Use when conditions need to run with the land (e.g., landscaping, building restrictions)."
		}
	]

	installed_count = 0
	for template_data in templates:
		template_name = template_data["template_name"]

		# Check if already exists
		if frappe.db.exists("Consent Condition Template", template_name):
			if not force:
				frappe.log(f"Template '{template_name}' already exists, skipping...")
				continue
			else:
				# Update existing
				doc = frappe.get_doc("Consent Condition Template", template_name)
				doc.update(template_data)
				doc.save()
				frappe.log(f"Updated: {template_name}")
		else:
			# Create new
			doc = frappe.get_doc({
				"doctype": "Consent Condition Template",
				**template_data
			})
			doc.insert()
			frappe.log(f"Created: {template_name}")

		installed_count += 1

	frappe.log(f"✓ Installed {installed_count} Consent Condition Templates")
	return installed_count


def install_request_types(force=False):
	"""Install default request types"""

	request_types = [
		{
			"type_name": "Land Use Consent - Residential",
			"type_code": "RC-LU-RES",
			"category": "Resource Consent",
			"description": "<p>Land use consent for residential activities including dwellings, minor buildings, and accessory activities in residential zones.</p>",
			"processing_sla_days": 20,
			"base_fee": 750.00,
			"fee_calculation_method": "Fixed",
			"is_active": 1
		},
		{
			"type_name": "Land Use Consent - Commercial",
			"type_code": "RC-LU-COM",
			"category": "Resource Consent",
			"description": "<p>Land use consent for commercial activities including retail, office, hospitality, and business activities.</p>",
			"processing_sla_days": 20,
			"base_fee": 1500.00,
			"fee_calculation_method": "Hourly",
			"hourly_rate": 180.00,
			"is_active": 1
		},
		{
			"type_name": "Land Use Consent - Industrial",
			"type_code": "RC-LU-IND",
			"category": "Resource Consent",
			"description": "<p>Land use consent for industrial activities including manufacturing, processing, storage, and distribution.</p>",
			"processing_sla_days": 20,
			"base_fee": 2000.00,
			"fee_calculation_method": "Hourly",
			"hourly_rate": 180.00,
			"is_active": 1
		},
		{
			"type_name": "Subdivision Consent - Standard",
			"type_code": "RC-SUB-STD",
			"category": "Resource Consent",
			"description": "<p>Subdivision consent for standard residential or rural subdivision creating additional lots.</p>",
			"processing_sla_days": 20,
			"base_fee": 2500.00,
			"fee_calculation_method": "Hourly",
			"hourly_rate": 180.00,
			"is_active": 1
		},
		{
			"type_name": "Discharge Permit - Stormwater",
			"type_code": "RC-DIS-SW",
			"category": "Resource Consent",
			"description": "<p>Discharge permit for stormwater disposal to land or water.</p>",
			"processing_sla_days": 20,
			"base_fee": 1000.00,
			"fee_calculation_method": "Fixed",
			"is_active": 1
		},
		{
			"type_name": "Water Permit - Groundwater Take",
			"type_code": "RC-WAT-GW",
			"category": "Resource Consent",
			"description": "<p>Water permit for the taking and use of groundwater.</p>",
			"processing_sla_days": 20,
			"base_fee": 1500.00,
			"fee_calculation_method": "Hourly",
			"hourly_rate": 180.00,
			"is_active": 1
		},
		{
			"type_name": "Building Consent - Residential New Build",
			"type_code": "BC-RES-NEW",
			"category": "Building Consent",
			"description": "<p>Building consent for new residential dwelling construction.</p>",
			"processing_sla_days": 20,
			"base_fee": 1200.00,
			"fee_calculation_method": "Value-Based",
			"is_active": 1
		},
		{
			"type_name": "Building Consent - Alterations & Additions",
			"type_code": "BC-ALT-ADD",
			"category": "Building Consent",
			"description": "<p>Building consent for alterations and additions to existing buildings.</p>",
			"processing_sla_days": 20,
			"base_fee": 600.00,
			"fee_calculation_method": "Value-Based",
			"is_active": 1
		},
		{
			"type_name": "Service Request - General Inquiry",
			"type_code": "SR-GEN",
			"category": "Service Request",
			"description": "<p>General inquiry or service request not requiring formal consent.</p>",
			"processing_sla_days": 5,
			"base_fee": 0.00,
			"fee_calculation_method": "Fixed",
			"is_active": 1
		},
		{
			"type_name": "License - Temporary Event",
			"type_code": "LIC-EVENT",
			"category": "License",
			"description": "<p>License for temporary events on public land or requiring special permission.</p>",
			"processing_sla_days": 10,
			"base_fee": 250.00,
			"fee_calculation_method": "Fixed",
			"is_active": 1
		}
	]

	installed_count = 0
	for rt_data in request_types:
		type_name = rt_data["type_name"]

		# Check if already exists
		if frappe.db.exists("Request Type", type_name):
			if not force:
				frappe.log(f"Request Type '{type_name}' already exists, skipping...")
				continue
			else:
				# Update existing
				doc = frappe.get_doc("Request Type", type_name)
				doc.update(rt_data)
				doc.save()
				frappe.log(f"Updated: {type_name}")
		else:
			# Create new
			doc = frappe.get_doc({
				"doctype": "Request Type",
				**rt_data
			})
			doc.insert()
			frappe.log(f"Created: {type_name}")

		installed_count += 1

	frappe.log(f"✓ Installed {installed_count} Request Types")
	return installed_count


def install_assessment_templates(force=False):
	"""Install default assessment templates"""

	templates = [
		{
			"template_name": "Resource Consent - Non-Notified",
			"request_type": "Resource Consent",
			"is_active": 1,
			"default_budget_hours": 40,
			"description": "<p>Standard assessment workflow for non-notified resource consent applications processed under RMA. Includes vetting, technical assessment, decision, and implementation stages with 20 working day statutory timeframe.</p>",
			"stages": [
				{
					"stage_number": 1,
					"stage_name": "Vetting & S88 Compliance",
					"stage_type": "Vetting",
					"required": 1,
					"estimated_hours": 4
				},
				{
					"stage_number": 2,
					"stage_name": "Technical Assessment",
					"stage_type": "Technical Assessment",
					"required": 1,
					"estimated_hours": 20
				},
				{
					"stage_number": 3,
					"stage_name": "Decision Preparation",
					"stage_type": "Decision",
					"required": 1,
					"estimated_hours": 10
				},
				{
					"stage_number": 4,
					"stage_name": "Implementation & Issuance",
					"stage_type": "Implementation",
					"required": 1,
					"estimated_hours": 6
				}
			]
		},
		{
			"template_name": "Building Consent - Standard",
			"request_type": "Building Consent",
			"is_active": 1,
			"default_budget_hours": 30,
			"description": "<p>Standard building consent assessment workflow for residential and commercial buildings. Includes plan vetting, technical assessment, and decision within 20 working days.</p>",
			"stages": [
				{
					"stage_number": 1,
					"stage_name": "Plan Vetting",
					"stage_type": "Vetting",
					"required": 1,
					"estimated_hours": 6
				},
				{
					"stage_number": 2,
					"stage_name": "Technical Assessment",
					"stage_type": "Technical Assessment",
					"required": 1,
					"estimated_hours": 16
				},
				{
					"stage_number": 3,
					"stage_name": "Decision & Issuance",
					"stage_type": "Decision",
					"required": 1,
					"estimated_hours": 8
				}
			]
		},
		{
			"template_name": "LIM Assessment",
			"request_type": "LIM",
			"is_active": 1,
			"default_budget_hours": 12,
			"description": "<p>Land Information Memorandum assessment workflow. Comprehensive property information gathering and report preparation within 10 working days.</p>",
			"stages": [
				{
					"stage_number": 1,
					"stage_name": "Information Gathering",
					"stage_type": "Vetting",
					"required": 1,
					"estimated_hours": 6
				},
				{
					"stage_number": 2,
					"stage_name": "Report Compilation",
					"stage_type": "Technical Assessment",
					"required": 1,
					"estimated_hours": 4
				},
				{
					"stage_number": 3,
					"stage_name": "Quality Check & Issuance",
					"stage_type": "Decision",
					"required": 1,
					"estimated_hours": 2
				}
			]
		}
	]

	installed_count = 0
	for template_data in templates:
		template_name = template_data["template_name"]

		# Check if already exists
		if frappe.db.exists("Assessment Template", template_name):
			if not force:
				frappe.log(f"Assessment Template '{template_name}' already exists, skipping...")
				continue
			else:
				# Update existing
				doc = frappe.get_doc("Assessment Template", template_name)
				doc.update(template_data)
				doc.save()
				frappe.log(f"Updated: {template_name}")
		else:
			# Create new
			doc = frappe.get_doc({
				"doctype": "Assessment Template",
				**template_data
			})
			doc.insert()
			frappe.log(f"Created: {template_name}")

		installed_count += 1

	frappe.log(f"✓ Installed {installed_count} Assessment Templates")
	return installed_count


def link_assessment_templates_to_request_types(force=False):
	"""Link assessment templates to request types as default_assessment_template"""

	# Define which assessment template is default for which request type
	template_links = {
		"Land Use Consent - Residential": "Resource Consent - Non-Notified",
		"Land Use Consent - Commercial": "Resource Consent - Non-Notified",
		"Land Use Consent - Industrial": "Resource Consent - Non-Notified",
		"Subdivision Consent - Standard": "Resource Consent - Non-Notified",
		"Discharge Permit - Stormwater": "Resource Consent - Non-Notified",
		"Water Permit - Groundwater Take": "Resource Consent - Non-Notified",
		"Building Consent - Residential New Build": "Building Consent - Standard",
		"Building Consent - Alterations & Additions": "Building Consent - Standard",
	}

	linked_count = 0
	for request_type_name, assessment_template_name in template_links.items():
		if not frappe.db.exists("Request Type", request_type_name):
			frappe.log(f"Request Type '{request_type_name}' not found, skipping...")
			continue

		if not frappe.db.exists("Assessment Template", assessment_template_name):
			frappe.log(f"Assessment Template '{assessment_template_name}' not found, skipping...")
			continue

		# Update request type with default assessment template
		rt_doc = frappe.get_doc("Request Type", request_type_name)

		if force or not rt_doc.default_assessment_template:
			rt_doc.default_assessment_template = assessment_template_name
			rt_doc.save()
			linked_count += 1
			frappe.log(f"✓ Linked '{assessment_template_name}' to '{request_type_name}'")
		else:
			frappe.log(f"Request Type '{request_type_name}' already has a default template, skipping...")

	frappe.log(f"✓ Linked {linked_count} assessment template connections")
	return linked_count


def link_templates_to_request_types(force=False):
	"""Link condition templates to request types"""

	# Define which templates apply to which request types
	template_links = {
		"Land Use Consent - Residential": [
			{"template": "Standard Consent Duration", "auto_apply": 1, "is_mandatory": 1, "number": "1"},
			{"template": "Standard Noise Limits - Residential", "auto_apply": 1, "is_mandatory": 1, "number": "2"},
			{"template": "Hours of Operation - Commercial", "auto_apply": 0, "is_mandatory": 0, "number": "3"},
			{"template": "Landscaping Implementation", "auto_apply": 1, "is_mandatory": 0, "number": "4"},
			{"template": "Accidental Discovery Protocol - Heritage", "auto_apply": 1, "is_mandatory": 1, "number": "5"},
			{"template": "Construction Management Plan", "auto_apply": 0, "is_mandatory": 0, "number": "6"},
		],
		"Land Use Consent - Commercial": [
			{"template": "Standard Consent Duration", "auto_apply": 1, "is_mandatory": 1, "number": "1"},
			{"template": "Hours of Operation - Commercial", "auto_apply": 1, "is_mandatory": 1, "number": "2"},
			{"template": "Traffic Management Plan Required", "auto_apply": 1, "is_mandatory": 1, "number": "3"},
			{"template": "Landscaping Implementation", "auto_apply": 1, "is_mandatory": 0, "number": "4"},
			{"template": "Stormwater Management - Onsite Disposal", "auto_apply": 1, "is_mandatory": 1, "number": "5"},
			{"template": "Accidental Discovery Protocol - Heritage", "auto_apply": 1, "is_mandatory": 1, "number": "6"},
			{"template": "Construction Management Plan", "auto_apply": 1, "is_mandatory": 1, "number": "7"},
			{"template": "Consent Notice Registration", "auto_apply": 1, "is_mandatory": 1, "number": "8"},
		],
		"Land Use Consent - Industrial": [
			{"template": "Standard Consent Duration", "auto_apply": 1, "is_mandatory": 1, "number": "1"},
			{"template": "Hours of Operation - Commercial", "auto_apply": 1, "is_mandatory": 1, "number": "2"},
			{"template": "Traffic Management Plan Required", "auto_apply": 1, "is_mandatory": 1, "number": "3"},
			{"template": "Stormwater Management - Onsite Disposal", "auto_apply": 1, "is_mandatory": 1, "number": "4"},
			{"template": "Accidental Discovery Protocol - Heritage", "auto_apply": 1, "is_mandatory": 1, "number": "5"},
			{"template": "Construction Management Plan", "auto_apply": 1, "is_mandatory": 1, "number": "6"},
			{"template": "Consent Notice Registration", "auto_apply": 1, "is_mandatory": 1, "number": "7"},
		],
		"Subdivision Consent - Standard": [
			{"template": "Standard Consent Duration", "auto_apply": 1, "is_mandatory": 1, "number": "1"},
			{"template": "Earthworks Erosion and Sediment Control", "auto_apply": 1, "is_mandatory": 1, "number": "2"},
			{"template": "Stormwater Management - Onsite Disposal", "auto_apply": 1, "is_mandatory": 1, "number": "3"},
			{"template": "Accidental Discovery Protocol - Heritage", "auto_apply": 1, "is_mandatory": 1, "number": "4"},
			{"template": "Consent Notice Registration", "auto_apply": 1, "is_mandatory": 1, "number": "5"},
		],
		"Discharge Permit - Stormwater": [
			{"template": "Standard Consent Duration", "auto_apply": 1, "is_mandatory": 1, "number": "1"},
			{"template": "Stormwater Management - Onsite Disposal", "auto_apply": 1, "is_mandatory": 1, "number": "2"},
			{"template": "Consent Notice Registration", "auto_apply": 1, "is_mandatory": 1, "number": "3"},
		],
		"Water Permit - Groundwater Take": [
			{"template": "Standard Consent Duration", "auto_apply": 1, "is_mandatory": 1, "number": "1"},
			{"template": "Consent Notice Registration", "auto_apply": 1, "is_mandatory": 1, "number": "2"},
		],
	}

	linked_count = 0
	for request_type_name, templates in template_links.items():
		if not frappe.db.exists("Request Type", request_type_name):
			frappe.log(f"Request Type '{request_type_name}' not found, skipping template links...")
			continue

		rt_doc = frappe.get_doc("Request Type", request_type_name)

		# Clear existing templates if force
		if force and rt_doc.condition_templates:
			rt_doc.condition_templates = []

		# Add template links if not already present
		for template_link in templates:
			template_name = template_link["template"]

			if not frappe.db.exists("Consent Condition Template", template_name):
				frappe.log(f"Template '{template_name}' not found, skipping...")
				continue

			# Check if already linked
			already_linked = False
			for existing in rt_doc.condition_templates:
				if existing.condition_template == template_name:
					already_linked = True
					break

			if not already_linked:
				rt_doc.append("condition_templates", {
					"condition_template": template_name,
					"auto_apply": template_link["auto_apply"],
					"is_mandatory": template_link["is_mandatory"],
					"default_condition_number": template_link["number"]
				})
				linked_count += 1

		rt_doc.save()
		frappe.log(f"✓ Linked templates to: {request_type_name}")

	frappe.log(f"✓ Linked {linked_count} template connections")
	return linked_count


@frappe.whitelist()
def reinstall_default_data():
	"""
	API method to reinstall default data.
	Can be called from UI or command line.
	"""
	# Reinstall all data
	template_count = install_consent_condition_templates(force=True)
	rt_count = install_request_types(force=True)
	link_count = link_templates_to_request_types(force=True)

	frappe.db.commit()

	return {
		"message": "Default data reinstalled successfully",
		"templates": template_count,
		"request_types": rt_count,
		"links": link_count
	}
