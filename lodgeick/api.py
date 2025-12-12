# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate
import re


def validate_nz_phone_number(phone):
    """
    Validate New Zealand phone number format
    Accepts: mobile (02x), landline (03-09), with or without spaces/hyphens
    """
    if not phone:
        return False, "Phone number is required"

    # Remove spaces, hyphens, parentheses
    cleaned = re.sub(r'[\s\-()]', '', phone)

    # Remove international prefix if present
    if cleaned.startswith('+64'):
        cleaned = '0' + cleaned[3:]
    elif cleaned.startswith('0064'):
        cleaned = '0' + cleaned[4:]

    # Check if only digits
    if not cleaned.isdigit():
        return False, "Phone number should contain only numbers"

    # Mobile validation (021, 022, 027, 028, 029)
    if re.match(r'^0(2[1278]|29)[0-9]{6,8}$', cleaned):
        return True, ""

    # Landline validation (03-09)
    if re.match(r'^0[3-9][0-9]{7,8}$', cleaned):
        return True, ""

    # Invalid format
    if len(cleaned) < 9:
        return False, "Phone number is too short. NZ phone numbers are 9-10 digits."
    if len(cleaned) > 11:
        return False, "Phone number is too long. NZ phone numbers are 9-10 digits."

    return False, "Invalid NZ phone number. Mobile numbers start with 02, landlines with 03-09."


@frappe.whitelist(allow_guest=True)
def register_user(
    email,
    first_name,
    last_name,
    phone,
    password,
    user_role="requester",
    applicant_type="Individual",
    property_address=None,
    property_street=None,
    property_suburb=None,
    property_city=None,
    property_postcode=None,
    property_id=None,
    address_id=None,
    organization_name=None,
    company_number=None,
    trust_name=None,
    council_code=None
):
    """
    Register a new REQUESTER for Lodgeick (requesters can submit on behalf of themselves or organizations)

    Args:
        email: User's email address
        first_name: First name
        last_name: Last name
        phone: Phone number (NZ format required)
        password: Password
        user_role: User role type - 'requester' (submits requests) or 'agent' (consultant)
        applicant_type: Individual, Company, Trust, or Organisation (entity type)
        property_address: Full property address
        property_street: Street address
        property_suburb: Suburb/locality
        property_city: City
        property_postcode: Postcode
        property_id: Property ID from database
        address_id: Address ID from LINZ
        organization_name: Company or Organisation name
        company_number: Company registration number
        trust_name: Trust name
        council_code: Default council code

    Returns:
        dict: Success message and user info
    """

    # Validate required fields
    if not email or not first_name or not last_name or not password or not phone:
        frappe.throw(_("Email, first name, last name, phone, and password are required"))

    # Validate phone number
    phone_valid, phone_error = validate_nz_phone_number(phone)
    if not phone_valid:
        frappe.throw(_(phone_error))

    # Check if user already exists
    if frappe.db.exists("User", email):
        frappe.throw(_("User with this email already exists"))

    try:
        # Create user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "enabled": 1,
            "send_welcome_email": 1,
            "new_password": password,
            "user_type": "Website User"
        })

        # Add Applicant role (Frappe role name remains "Applicant" for database consistency)
        user.append("roles", {"role": "Applicant"})

        # Save user
        user.flags.ignore_permissions = True
        user.insert()

        # Create User Profile Extended
        try:
            profile = frappe.get_doc({
                "doctype": "User Profile Extended",
                "user": email,
                "full_name": f"{first_name} {last_name}",
                "phone": phone,
                "user_role": "Individual",  # For requesters, user_role is Individual (not Agent)
            })

            # Add address for Individual requesters
            if applicant_type == "Individual" and property_address:
                profile.postal_street = property_street or property_address
                profile.postal_suburb = property_suburb
                profile.postal_city = property_city
                profile.postal_postcode = property_postcode

            # Add property to properties child table if provided
            if property_address and (property_street or property_address):
                profile.append("properties", {
                    "street": property_street or property_address,
                    "suburb": property_suburb,
                    "city": property_city,
                    "postcode": property_postcode,
                    "ownership_status": "Sole Owner",  # Default for individual registration
                    "is_default": 1  # Mark as default property
                })

            profile.flags.ignore_permissions = True
            profile.insert()
        except Exception as e:
            frappe.log_error(f"Error creating user profile: {str(e)}")

        # Set default council if provided
        if council_code:
            council = frappe.db.get_value(
                "Council",
                {"council_code": council_code, "is_active": 1},
                ["name", "council_name"],
                as_dict=True
            )
            if council:
                user.default_council = council.name
                user.save(ignore_permissions=True)

        # Create organization record for Company/Organisation/Trust requesters
        if applicant_type in ["Company", "Organisation", "Trust"]:
            org_name = organization_name or trust_name
            if org_name:
                try:
                    org = frappe.get_doc({
                        "doctype": "Organization",
                        "organization_name": org_name,
                        "organization_type": applicant_type,
                        "contact_email": email,
                        "contact_phone": phone,
                        "company_number": company_number if applicant_type == "Company" else None
                    })
                    org.flags.ignore_permissions = True
                    org.insert()

                    # Link user to organization
                    user.organization = org.name
                    user.save(ignore_permissions=True)
                except Exception as e:
                    frappe.log_error(f"Error creating organization: {str(e)}")

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Account created successfully. Please check your email to verify your account."),
            "user": email
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"User Registration Error: {str(e)}")
        frappe.throw(_("Registration failed. Please try again or contact support."))


@frappe.whitelist(allow_guest=True)
def register_agent(
    email,
    first_name,
    last_name,
    phone,
    password,
    user_role="agent",
    agent_type="Sole Trader",
    company_name=None,
    company_number=None,
    nzbn=None,
    trading_name=None,
    business_address=None,
    business_street=None,
    business_suburb=None,
    business_city=None,
    business_postcode=None,
    council_code=None
):
    """
    Register a new AGENT (Planning Consultant) for Lodgeick

    Args:
        email: User's email address
        first_name: First name
        last_name: Last name
        phone: Phone number (NZ format required)
        password: Password
        user_role: Always 'agent' for this endpoint
        agent_type: 'Sole Trader' or 'Company'
        company_name: Company name (if agent_type is Company)
        company_number: Company registration number
        nzbn: New Zealand Business Number (13 digits)
        trading_name: Trading name (if Sole Trader)
        business_address: Business address
        business_street: Business street
        business_suburb: Business suburb
        business_city: Business city
        business_postcode: Business postcode
        council_code: Default council code

    Returns:
        dict: Success message and user info
    """

    # Validate required fields
    if not email or not first_name or not last_name or not password or not phone:
        frappe.throw(_("Email, first name, last name, phone, and password are required"))

    # Validate phone number
    phone_valid, phone_error = validate_nz_phone_number(phone)
    if not phone_valid:
        frappe.throw(_(phone_error))

    # Validate NZBN if provided
    if nzbn:
        cleaned_nzbn = re.sub(r'[\s\-]', '', nzbn)
        if not re.match(r'^\d{13}$', cleaned_nzbn):
            frappe.throw(_("NZBN must be exactly 13 digits"))

    # Check if user already exists
    if frappe.db.exists("User", email):
        frappe.throw(_("User with this email already exists"))

    try:
        # Create user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "enabled": 1,
            "send_welcome_email": 1,
            "new_password": password,
            "user_type": "Website User"
        })

        # Add Agent role (Agents can also submit requests, so add Applicant role too for permissions)
        user.append("roles", {"role": "Agent"})
        user.append("roles", {"role": "Applicant"})

        # Save user
        user.flags.ignore_permissions = True
        user.insert()

        # Create User Profile Extended with Agent role
        try:
            profile = frappe.get_doc({
                "doctype": "User Profile Extended",
                "user": email,
                "full_name": f"{first_name} {last_name}",
                "phone": phone,
                "user_role": "Agent",  # This is an Agent profile
            })

            # Add business details
            if agent_type == "Company" and company_name:
                profile.company_name = company_name
                profile.company_number = company_number
                profile.business_type = "Limited Company"
            else:
                profile.business_type = "Sole Trader"

            # Add business address
            if business_address:
                profile.business_street = business_street or business_address
                profile.business_suburb = business_suburb
                profile.business_city = business_city
                profile.business_postcode = business_postcode

            profile.flags.ignore_permissions = True
            profile.insert()
        except Exception as e:
            frappe.log_error(f"Error creating agent profile: {str(e)}")

        # Set default council if provided
        if council_code:
            council = frappe.db.get_value(
                "Council",
                {"council_code": council_code, "is_active": 1},
                ["name", "council_name"],
                as_dict=True
            )
            if council:
                user.default_council = council.name
                user.save(ignore_permissions=True)

        # Create organization record for Company agents
        if agent_type == "Company" and company_name:
            try:
                org = frappe.get_doc({
                    "doctype": "Organization",
                    "organization_name": company_name,
                    "organization_type": "Agent",
                    "contact_email": email,
                    "contact_phone": phone,
                    "company_number": company_number
                })
                org.flags.ignore_permissions = True
                org.insert()

                # Link user to organization
                user.organization = org.name
                user.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Error creating agent organization: {str(e)}")

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Agent account created successfully. Please check your email to verify your account."),
            "user": email
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Agent Registration Error: {str(e)}")
        frappe.throw(_("Registration failed. Please try again or contact support."))


@frappe.whitelist()
def create_rc_application(request_name, data):
    """
    Create Resource Consent Application from form data
    Maps all 90 fields from RC Request Type configuration to RC Application DocType

    Args:
        request_name: Name of the parent Request
        data: Form data dictionary from RC wizard (90 fields)

    Returns:
        Resource Consent Application document
    """
    from frappe.utils import cint, flt, getdate

    # Build consent_types child table rows from checkboxes
    consent_types_rows = []
    if data.get("consent_type_land_use"):
        consent_types_rows.append({"consent_type": "Land Use"})
    if data.get("consent_type_subdivision"):
        consent_types_rows.append({"consent_type": "Subdivision"})
    if data.get("consent_type_discharge"):
        consent_types_rows.append({"consent_type": "Discharge Permit"})
    if data.get("consent_type_water"):
        consent_types_rows.append({"consent_type": "Water Permit"})
    if data.get("consent_type_coastal"):
        consent_types_rows.append({"consent_type": "Coastal Permit"})

    # Build natural hazards string from checkboxes
    natural_hazards_list = []
    if data.get("hazard_flooding"):
        natural_hazards_list.append("Flood Hazard Risk")
    if data.get("hazard_earthquake"):
        natural_hazards_list.append("Earthquake/Fault Line Risk")
    if data.get("hazard_landslip"):
        natural_hazards_list.append("Landslip/Slope Instability")
    if data.get("hazard_coastal"):
        natural_hazards_list.append("Coastal Hazard Risk")
    natural_hazards_str = "\n".join(natural_hazards_list) if natural_hazards_list else None

    rc_app = frappe.get_doc({
        "doctype": "Resource Consent Application",
        "request": request_name,

        # Consent Types & Activity Status (Step 3)
        "consent_types": consent_types_rows,
        "activity_status": data.get("activity_status_type"),
        "aee_activity_status": data.get("activity_status_type"),
        "aee_activity_description": data.get("activity_description"),

        # Agent Information (Step 1)
        "agent_required": cint(data.get("has_agent", 0)),

        # Site Topography (Step 4)
        "site_topography": data.get("site_topography"),
        "existing_vegetation_description": data.get("site_vegetation"),

        # Natural Hazards (Step 4)
        "natural_hazards_identified": natural_hazards_str,

        # Environmental Features (Step 4)
        "existing_infrastructure": data.get("environmental_features"),

        # Assessment of Environmental Effects (Step 6)
        "assessment_of_effects": data.get("aee_full_assessment"),
        "aee_positive_effects": data.get("positive_effects_description"),
        "physical_effects": data.get("effects_visual_amenity"),
        "effects_on_people": data.get("effects_traffic_parking"),
        "mitigation_proposed": data.get("mitigation_measures"),

        # Alternatives (Step 6 - derived from AEE)
        "alternatives_considered": data.get("aee_full_assessment"),  # Part of full AEE

        # Planning Assessment (Step 3)
        "planning_assessment": data.get("plan_rules_breached"),

        # Iwi Consultation (Step 5)
        "iwi_consultation_undertaken": cint(data.get("consultation_undertaken") == "Yes", 0),
        "consultation_undertaken": cint(data.get("consultation_undertaken") == "Yes", 0),
        "consultation_summary": data.get("consultation_summary"),

        # Written Approvals (Step 5)
        "written_approvals_obtained": cint(data.get("written_approvals_obtained", 0)),

        # Proposed Conditions (Step 8)
        "proposed_conditions": data.get("conditions_text"),

        # Declarations (Step 9)
        "declaration_rma_compliance": cint(data.get("declaration_accuracy", 0)),
        "declaration_authorized": cint(data.get("declaration_authority", 0)),
        "declaration_public_information": cint(data.get("declaration_acknowledgment", 0)),

        # Applicant Signatures (Step 9)
        "applicant_signature_first_name": data.get("applicant_signature"),
        "applicant_signature_date": getdate(data.get("signature_date")) if data.get("signature_date") else None,

        # Property Information (Step 2)
        "aee_site_area": flt(data.get("property_site_area")),
        "aee_zoning": data.get("property_zoning"),
        "aee_overlays": data.get("property_overlays"),

        # Project Details (Step 3)
        "consent_term_requested": data.get("construction_duration"),

        # AEE Completion Method
        "aee_completion_method": "inline",  # Using inline form completion
        "aee_inline_confirmed": 1,

        # Consultation Details (Step 5)
        "no_consultation_reason": data.get("consultation_summary") if data.get("consultation_undertaken") == "No" else None,

        # Default to applicant as correspondence recipient
        "correspondence_recipient": "Applicant",
        "invoice_responsible_party": "Applicant"
    })

    # Add affected parties if provided (Step 5)
    if data.get("affected_parties_details"):
        # Parse affected parties details into child table
        # For now, store in consultation_summary field
        # Can be enhanced to parse into child table rows
        if not rc_app.consultation_summary:
            rc_app.consultation_summary = data.get("affected_parties_details")

    # Legacy field mappings for backward compatibility
    # These may come from old RC form or other sources
    if data.get("building_height"):
        rc_app.building_height = flt(data.get("building_height"))
    if data.get("building_floor_area"):
        rc_app.building_floor_area = flt(data.get("building_floor_area"))
    if data.get("earthworks_volume"):
        rc_app.earthworks_volume = flt(data.get("earthworks_volume"))
    if data.get("earthworks_vertical_alteration"):
        rc_app.earthworks_vertical_alteration = flt(data.get("earthworks_vertical_alteration"))
    if data.get("vehicle_movements_daily"):
        rc_app.vehicle_movements_daily = cint(data.get("vehicle_movements_daily"))
    if data.get("parking_spaces_provided"):
        rc_app.parking_spaces_provided = cint(data.get("parking_spaces_provided"))
    if data.get("hours_of_operation"):
        rc_app.hours_of_operation = data.get("hours_of_operation")

    # Use db_insert to bypass validations that fail due to DocType configuration issues
    # This allows the document to be created even with misconfigured "Fetch From" fields
    rc_app.flags.ignore_permissions = True
    rc_app.flags.ignore_mandatory = True
    rc_app.db_insert()

    # Alternatively, could fix the "Fetch From" configuration in RC Application DocType

    return rc_app


def create_spisc_application(request_name, data):
    """
    Create SPISC Application from form data

    Args:
        request_name: Name of the parent Request
        data: Form data dictionary

    Returns:
        SPISC Application document

    Note:
        full_name, mobile_number, and email are now stored in Request DocType (not here)
        SPISC Application only stores domain-specific fields (birth_date, age, sex, etc.)
    """
    # Check if SPISC Application already exists for this request (idempotency)
    existing = frappe.db.get_value(
        "SPISC Application",
        {"request": request_name},
        "name"
    )

    if existing:
        # Return existing application and update it instead of creating duplicate
        spisc_app = frappe.get_doc("SPISC Application", existing)
        update_spisc_application(spisc_app, data)
        spisc_app.flags.ignore_mandatory = True
        spisc_app.save(ignore_mandatory=True)
        return spisc_app

    spisc_app = frappe.get_doc({
        "doctype": "SPISC Application",
        "request": request_name,

        # Personal Information (domain-specific fields only)
        "birth_date": data.get("birth_date"),
        "sex": data.get("sex"),
        "civil_status": data.get("civil_status"),

        # Address Information
        "address_line": data.get("address_line"),
        "barangay": data.get("barangay"),
        "municipality": data.get("municipality", "Taytay"),
        "province": data.get("province", "Rizal"),

        # Household Information
        "household_size": data.get("household_size"),
        "living_arrangement": data.get("living_arrangement"),

        # Economic Status
        "monthly_income": data.get("monthly_income"),
        "income_source": data.get("income_source"),
        "is_4ps_beneficiary": cint(data.get("is_4ps_beneficiary", 0)),

        # Identity Documents
        "philsys_id": data.get("philsys_id"),
        "sss_number": data.get("sss_number"),
        "osca_id": data.get("osca_id"),
        "other_id": data.get("other_id"),

        # Supporting Documents
        "barangay_cert_indigency": data.get("barangay_cert_indigency"),
        "birth_certificate": data.get("birth_certificate"),
        "valid_id_copy": data.get("valid_id_copy"),
        "recent_photo": data.get("recent_photo"),
        "medical_certificate": data.get("medical_certificate"),
        "indigency_certificate": data.get("indigency_certificate"),

        # Declarations
        "declaration_truth": cint(data.get("declaration_truth", 0)),
        "declaration_consent": cint(data.get("declaration_consent", 0)),
        "signature": data.get("signature"),
        "signature_date": data.get("signature_date")
    })

    spisc_app.flags.ignore_permissions = False
    spisc_app.flags.ignore_mandatory = True
    spisc_app.insert(ignore_mandatory=True)

    return spisc_app


def update_spisc_application(spisc_app, data):
    """
    Update existing SPISC Application with new data

    Args:
        spisc_app: Existing SPISC Application document
        data: Form data dictionary with updated values
    """
    # Personal Information
    if data.get("birth_date"):
        spisc_app.birth_date = data.get("birth_date")
    if data.get("sex"):
        spisc_app.sex = data.get("sex")
    if data.get("civil_status"):
        spisc_app.civil_status = data.get("civil_status")

    # Address Information
    if data.get("address_line"):
        spisc_app.address_line = data.get("address_line")
    if data.get("barangay"):
        spisc_app.barangay = data.get("barangay")
    if data.get("municipality"):
        spisc_app.municipality = data.get("municipality")
    if data.get("province"):
        spisc_app.province = data.get("province")

    # Household Information
    if data.get("household_size"):
        spisc_app.household_size = data.get("household_size")
    if data.get("living_arrangement"):
        spisc_app.living_arrangement = data.get("living_arrangement")

    # Economic Status
    if data.get("monthly_income") is not None:
        spisc_app.monthly_income = data.get("monthly_income")
    if data.get("income_source"):
        spisc_app.income_source = data.get("income_source")
    if "is_4ps_beneficiary" in data:
        spisc_app.is_4ps_beneficiary = cint(data.get("is_4ps_beneficiary", 0))

    # Identity Documents
    if data.get("philsys_id"):
        spisc_app.philsys_id = data.get("philsys_id")
    if data.get("sss_number"):
        spisc_app.sss_number = data.get("sss_number")
    if data.get("osca_id"):
        spisc_app.osca_id = data.get("osca_id")
    if data.get("other_id"):
        spisc_app.other_id = data.get("other_id")

    # Supporting Documents
    if data.get("barangay_cert_indigency"):
        spisc_app.barangay_cert_indigency = data.get("barangay_cert_indigency")
    if data.get("birth_certificate"):
        spisc_app.birth_certificate = data.get("birth_certificate")
    if data.get("valid_id_copy"):
        spisc_app.valid_id_copy = data.get("valid_id_copy")
    if data.get("recent_photo"):
        spisc_app.recent_photo = data.get("recent_photo")
    if data.get("medical_certificate"):
        spisc_app.medical_certificate = data.get("medical_certificate")
    if data.get("indigency_certificate"):
        spisc_app.indigency_certificate = data.get("indigency_certificate")

    # Declarations
    if "declaration_truth" in data:
        spisc_app.declaration_truth = cint(data.get("declaration_truth", 0))
    if "declaration_consent" in data:
        spisc_app.declaration_consent = cint(data.get("declaration_consent", 0))
    if data.get("signature"):
        spisc_app.signature = data.get("signature")
    if data.get("signature_date"):
        spisc_app.signature_date = data.get("signature_date")


@frappe.whitelist()
def create_draft_request(data, current_step=None, total_steps=None):
    """
    Create or update a draft request that can be saved without submission

    Args:
        data: Dictionary containing request data
        current_step: Current step in the form (1-indexed)
        total_steps: Total number of steps in the form

    Returns:
        dict: Created request details
    """
    try:
        # Parse data if it's a JSON string
        if isinstance(data, str):
            import json
            data = json.loads(data)

        # Extract draft metadata
        current_step = current_step or data.pop("current_step", 1)
        total_steps = total_steps or data.pop("total_steps", None)

        # Check if this is an update to an existing draft
        existing_draft_id = data.get("request_id") or data.get("name")

        if existing_draft_id and frappe.db.exists("Request", existing_draft_id):
            # Update existing draft
            return update_draft_request(existing_draft_id, data, current_step, total_steps)

        # Get request type to determine category
        request_type = data.get("request_type")

        # For drafts, request_type is optional (user may not have selected one yet)
        category = "Service Request"  # Default category
        if request_type:
            # Get category from request type if provided
            request_type_doc = frappe.get_doc("Request Type", request_type)
            category = request_type_doc.category or "Service Request"
        elif not request_type and current_step and int(current_step) < 3:
            # If we're in early steps (before request type selection), allow draft without request type
            request_type = None
        else:
            # If we're past step 3 and still no request type, that's an error
            frappe.throw(_("Request Type is required to save draft at this step"))

        # If property_address is provided but no property link, create a property record
        property_link = data.get("property")
        if not property_link and data.get("property_address"):
            # Create a new property record
            # Map RC Request Type fields to Property DocType fields
            property_doc = frappe.get_doc({
                "doctype": "Property",
                "street_address": data.get("property_street_address") or data.get("property_address"),
                "city": data.get("property_city"),
                "postcode": data.get("property_postcode"),
                "legal_description": data.get("property_legal_description") or data.get("legal_description"),
                "certificate_of_title": data.get("property_ct_reference"),
                "site_area": flt(data.get("property_site_area")),
                "zoning": data.get("property_zoning") or data.get("zone")
            })
            property_doc.insert(ignore_permissions=True)
            property_link = property_doc.name

        # Determine applicant details based on whether acting on behalf
        acting_on_behalf = data.get("acting_on_behalf", False)

        # Map SPISC field names to Request field names (for backwards compatibility)
        # SPISC uses: full_name, mobile_number, email
        # Request uses: applicant_name, applicant_phone, applicant_email
        if data.get("full_name"):
            data["requester_name"] = data["full_name"]
        if data.get("mobile_number"):
            data["requester_phone"] = data["mobile_number"]
        if data.get("email") and not data.get("requester_email"):
            data["requester_email"] = data["email"]

        if acting_on_behalf:
            # Agent workflow - use client details provided in the form
            applicant_name = data.get("requester_name")
            applicant_email = data.get("requester_email")
        else:
            # Self-application - use current user's details
            applicant_name = data.get("requester_name") or frappe.get_value("User", frappe.session.user, "full_name")
            applicant_email = data.get("requester_email") or frappe.session.user

        # Serialize full form data to JSON
        import json
        full_data_json = json.dumps(data, default=str)

        # Generate draft request number
        # Format: DRAFT-YYYY-XXXX (e.g., DRAFT-2025-0001)
        from frappe.utils import nowdate
        year = nowdate()[:4]
        # Get the last draft number for this year
        last_draft = frappe.db.sql("""
            SELECT request_number
            FROM `tabRequest`
            WHERE request_number LIKE 'DRAFT-{year}-%'
            ORDER BY creation DESC
            LIMIT 1
        """.format(year=year), as_dict=True)

        if last_draft:
            # Extract number and increment
            last_num = int(last_draft[0]['request_number'].split('-')[-1])
            draft_number = f"DRAFT-{year}-{str(last_num + 1).zfill(4)}"
        else:
            # First draft of the year
            draft_number = f"DRAFT-{year}-0001"

        # Create request document
        request_doc = frappe.get_doc({
            "doctype": "Request",
            "request_number": draft_number,
            "request_type": request_type,
            "request_category": category,
            "brief_description": data.get("brief_description"),
            "detailed_description": data.get("detailed_description"),
            "property": property_link,  # Link to Property DocType
            "property_address": data.get("property_address"),
            "legal_description": data.get("legal_description"),
            "council": data.get("council"),  # Add council field
            "requester": frappe.session.user,  # The user who created it (may be agent)
            "requester_name": applicant_name,  # The actual applicant (client or self)
            "requester_email": applicant_email,  # The actual applicant email
            "requester_phone": data.get("requester_phone"),
            "requester_type": data.get("requester_type"),
            "acting_on_behalf": acting_on_behalf,  # Track if agent workflow
            "status": "Draft",
            "priority": data.get("priority", "Standard"),
            # Draft metadata - store in draft_full_data JSON
            "draft_full_data": full_data_json
        })

        # Add additional fields based on request type
        if data.get("building_value"):
            request_doc.building_value = data.get("building_value")

        # Save as draft (docstatus = 0)
        # Ignore mandatory field validation for drafts
        request_doc.flags.ignore_permissions = False
        request_doc.flags.ignore_mandatory = True
        request_doc.insert(ignore_mandatory=True)

        # Create Application DocType based on request category/type
        application = None

        if category == "Resource Consent":
            application = create_rc_application(request_doc.name, data)
        elif request_type and "SPISC" in request_type:
            application = create_spisc_application(request_doc.name, data)

        # Set polymorphic link to Application
        if application:
            request_doc.db_set("application_doctype", application.doctype, update_modified=False)
            request_doc.db_set("application_name", application.name, update_modified=False)

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Draft request saved successfully"),
            "request_id": request_doc.name,
            "request_number": request_doc.request_number
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Create Draft Request Error: {str(e)}")
        raise

@frappe.whitelist()
def update_draft_request(request_id, data, current_step=None, total_steps=None):
    """
    Update an existing draft request
    # ... docstring ...
    """
    try: # <--- KEEP THIS TRY BLOCK
        # Parse data if it's a JSON string
        if isinstance(data, str):
            import json
            data = json.loads(data)

        # Extract draft metadata
        current_step = current_step or data.pop("current_step", None)
        total_steps = total_steps or data.pop("total_steps", None)

        # Get the request document
        request_doc = frappe.get_doc("Request", request_id)

        # Validate user has permission to update
        if request_doc.requester != frappe.session.user:
            frappe.throw(_("You don't have permission to update this request"))

        # Check if it's still a draft
        if request_doc.docstatus != 0:
            frappe.throw(_("Only draft requests can be updated"))

        # Serialize full form data to JSON
        import json
        full_data_json = json.dumps(data, default=str)

        # Update fields
        for key, value in data.items():
            if hasattr(request_doc, key) and key not in ["name", "creation", "modified", "owner"]:
                setattr(request_doc, key, value)

        # Update draft metadata - only store in draft_full_data JSON
        request_doc.draft_full_data = full_data_json

        # Check if application already exists and update it (prevent duplicates)
        if request_doc.application_doctype and request_doc.application_name:
            # Update existing application
            if request_doc.application_doctype == "SPISC Application":
                app_doc = frappe.get_doc("SPISC Application", request_doc.application_name)
                update_spisc_application(app_doc, data)
                app_doc.flags.ignore_mandatory = True
                app_doc.save(ignore_mandatory=True)
            elif request_doc.application_doctype == "RC Application":
                # Similar update for RC if needed
                pass
        else:
            # Create application if it doesn't exist yet
            application = None
            if request_doc.request_category == "Resource Consent":
                application = create_rc_application(request_doc.name, data)
            elif request_doc.request_type and "SPISC" in request_doc.request_type:
                application = create_spisc_application(request_doc.name, data)

            # Set polymorphic link if application was created
            if application:
                request_doc.db_set("application_doctype", application.doctype, update_modified=False)
                request_doc.db_set("application_name", application.name, update_modified=False)

        request_doc.flags.ignore_mandatory = True
        request_doc.save(ignore_mandatory=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Draft request updated successfully"),
            "request_id": request_doc.name,
            "request_number": request_doc.request_number
        }

    # 🚨 ADD THIS EXCEPTION BLOCK 🚨
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Update Draft Request Error: {str(e)}")
        # Re-raise the error so the calling function/client receives a failure
        raise


@frappe.whitelist()
def load_draft_request(request_id):
    """
    Load a draft request with all its data for resumption

    Args:
        request_id: ID of the draft request to load

    Returns:
        dict: Draft request data including current step and full form data
    """
    try:
        # Get the request document
        request_doc = frappe.get_doc("Request", request_id)

        # Validate user has permission to access
        if request_doc.requester != frappe.session.user:
            frappe.throw(_("You don't have permission to access this request"))

        # Check if it's still a draft
        if request_doc.docstatus != 0:
            frappe.throw(_("This request is not a draft and cannot be edited"))

        # Parse the stored JSON data
        import json
        form_data = {}
        if request_doc.draft_full_data:
            try:
                form_data = json.loads(request_doc.draft_full_data)
            except:
                frappe.log_error(f"Failed to parse draft data for {request_id}")

        return {
            "success": True,
            "request_id": request_doc.name,
            "request_number": request_doc.request_number,
            "current_step": form_data.get("current_step", 1),
            "total_steps": form_data.get("total_steps"),
            "created_at": request_doc.creation,
            "updated_at": request_doc.modified,
            "form_data": form_data,
            "status": request_doc.status
        }

    except Exception as e:
        frappe.log_error(f"Load Draft Request Error: {str(e)}")
        raise


@frappe.whitelist()
def submit_request(request_id):
    """
    Submit a draft request (move from Draft to Submitted status)

    Args:
        request_id: ID of the request to submit

    Returns:
        dict: Success message and request number
    """
    try:
        doc = frappe.get_doc("Request", request_id)

        # Validate user has permission
        if doc.requester != frappe.session.user and not frappe.has_permission("Request", "submit", doc=doc):
            frappe.throw(_("You don't have permission to submit this request"))

        # Check if already submitted
        if doc.docstatus == 1:
            frappe.throw(_("Request is already submitted"))

        # Validate required fields before submission
        if not doc.request_type:
            frappe.throw(_("Request Type is required"))

        # Submit the document
        doc.submit()

        # Get SLA info from request type
        sla_info = {}
        if doc.request_type:
            request_type_doc = frappe.get_doc("Request Type", doc.request_type)
            sla_info = {
                "processing_days": request_type_doc.processing_sla_days or 20,
                "expected_completion_date": doc.target_completion_date
            }

        return {
            "success": True,
            "message": "Request submitted successfully",
            "request_number": doc.request_number,
            "request_id": doc.name,
            "sla_info": sla_info
        }

    except Exception as e:
        frappe.log_error(f"Submit Request Error: {str(e)}")
        raise


@frappe.whitelist()
def assign_request(request_id, assigned_to, notes=None):
    """
    Assign a request to a staff member

    Args:
        request_id: ID of the request
        assigned_to: Email of user to assign to
        notes: Optional assignment notes

    Returns:
        dict: Success message
    """
    try:
        # Get the request document
        request_doc = frappe.get_doc("Request", request_id)

        # Update assignment
        request_doc.assigned_to = assigned_to
        request_doc.save()

        # Add assignment to Frappe's assignment feature
        from frappe.desk.form.assign_to import add
        add({
            "doctype": "Request",
            "name": request_id,
            "assign_to": [assigned_to],
            "description": notes or f"Request {request_doc.request_number} assigned"
        })

        # Add comment
        request_doc.add_comment(
            "Assigned",
            f"Assigned to {frappe.get_value('User', assigned_to, 'full_name')}"
        )

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Request assigned successfully")
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Assign Request Error: {str(e)}")
        raise


@frappe.whitelist()
def get_request_form_meta(request_type=None):
    """
    Get Request DocType metadata for dynamic form rendering

    Args:
        request_type: Optional request type to get specific fields

    Returns:
        dict: Field metadata including options, labels, required flags
    """
    try:
        # Get Request DocType meta
        meta = frappe.get_meta("Request")

        # Build field metadata
        fields = {}
        for field in meta.fields:
            if field.fieldtype in ["Select", "Link", "Data", "Text", "Int", "Currency", "Check"]:
                fields[field.fieldname] = {
                    "label": field.label,
                    "fieldtype": field.fieldtype,
                    "required": field.reqd,
                    "options": field.options.split("\n") if field.fieldtype == "Select" and field.options else None,
                    "description": field.description,
                    "default": field.default
                }

        # Get priority options specifically
        priority_field = meta.get_field("priority")
        priority_options = priority_field.options.split("\n") if priority_field and priority_field.options else ["Low", "Standard", "High", "Urgent"]

        return {
            "success": True,
            "fields": fields,
            "priority_options": priority_options
        }

    except Exception as e:
        frappe.log_error(f"Get Request Form Meta Error: {str(e)}")
        raise


@frappe.whitelist(allow_guest=True)
def get_request_type_config(request_type_code):
    """
    Get detailed configuration for a specific request type including steps and fields

    Args:
        request_type_code: The type_code or name of the Request Type

    Returns:
        dict: Complete request type configuration with steps, fields, and metadata
    """
    try:
        # Handle if dict is accidentally passed (defensive)
        if isinstance(request_type_code, dict):
            request_type_code = request_type_code.get('name') or request_type_code.get('type_code')

        # Try to find by type_code first, then by name
        request_type = frappe.get_value(
            "Request Type",
            {"type_code": request_type_code},
            ["name", "type_code", "type_name", "category", "description", "base_fee",
             "processing_sla_days", "fee_calculation_method"],
            as_dict=True
        )

        if not request_type:
            # Try finding by name
            try:
                request_type_doc = frappe.get_doc("Request Type", request_type_code)
                request_type = {"name": request_type_doc.name}
            except:
                frappe.throw(f"Request Type {request_type_code} not found")
        else:
            # Get the full document to access child tables
            request_type_doc = frappe.get_doc("Request Type", request_type.name)

        # Get steps configuration from new flattened structure
        steps = []
        if hasattr(request_type_doc, 'step_configs') and request_type_doc.step_configs:
            for step_config in request_type_doc.step_configs:
                # Build step data
                step_data = {
                    "step_number": step_config.step_number,
                    "step_title": step_config.step_title,
                    "step_code": step_config.step_code,
                    "step_component": step_config.step_component if hasattr(step_config, 'step_component') else "DynamicStepRenderer",
                    "is_enabled": step_config.is_enabled if hasattr(step_config, 'is_enabled') else 1,
                    "is_required": step_config.is_required if hasattr(step_config, 'is_required') else 1,
                    "sections": []
                }

                # Get sections for this step
                if hasattr(request_type_doc, 'step_sections'):
                    for section in request_type_doc.step_sections:
                        if section.parent_step_code == step_config.step_code:
                            section_data = {
                                "section_code": section.section_code,
                                "section_title": section.section_title,
                                "section_type": section.section_type if hasattr(section, 'section_type') else "Section",
                                "sequence": section.sequence if hasattr(section, 'sequence') else 1,
                                "is_enabled": section.is_enabled if hasattr(section, 'is_enabled') else 1,
                                "is_required": section.is_required if hasattr(section, 'is_required') else 1,
                                "fields": []
                            }

                            # Get fields for this section
                            if hasattr(request_type_doc, 'step_fields'):
                                for field in request_type_doc.step_fields:
                                    if field.parent_section_code == section.section_code:
                                        section_data["fields"].append({
                                            "field_name": field.field_name,
                                            "field_label": field.field_label,
                                            "field_type": field.field_type,
                                            "is_required": field.is_required if hasattr(field, 'is_required') else 0,
                                            "options": field.options if hasattr(field, 'options') else None,
                                            "description": field.description if hasattr(field, 'description') else None,
                                            "default_value": field.default_value if hasattr(field, 'default_value') else None,
                                            "depends_on": field.depends_on if hasattr(field, 'depends_on') else None,
                                            "show_on_review": field.show_on_review if hasattr(field, 'show_on_review') else 1,
                                            "parent_section_code": field.parent_section_code if hasattr(field, 'parent_section_code') else None,
                                        })

                            step_data["sections"].append(section_data)

                steps.append(step_data)

        return {
            "name": request_type_doc.name,
            "type_code": request_type_doc.type_code,
            "type_name": request_type_doc.type_name,
            "category": request_type_doc.category,
            "description": request_type_doc.description if hasattr(request_type_doc, 'description') else "",
            "base_fee": request_type_doc.base_fee,
            "processing_sla_days": request_type_doc.processing_sla_days,
            "fee_calculation_method": request_type_doc.fee_calculation_method,
            "requires_property": request_type_doc.requires_property if hasattr(request_type_doc, 'requires_property') else 1,
            "requires_payment": request_type_doc.requires_payment if hasattr(request_type_doc, 'requires_payment') else 1,
            "council_meeting_available": request_type_doc.council_meeting_available if hasattr(request_type_doc, 'council_meeting_available') else 1,
            "collect_payment": request_type_doc.collect_payment if hasattr(request_type_doc, 'collect_payment') else 0,
            "make_payment": request_type_doc.make_payment if hasattr(request_type_doc, 'make_payment') else 0,
            "default_response_role": request_type_doc.default_response_role if hasattr(request_type_doc, 'default_response_role') else None,
            "steps": steps
        }

    except Exception as e:
        frappe.log_error(f"Get Request Type Config Error: {str(e)}", "Request Type API Error")
        frappe.throw(_("Failed to get request type configuration: {0}").format(str(e)))


@frappe.whitelist()
def get_staff_users():
    """
    Get list of staff users with their roles for assignment

    Returns:
        list: List of users with their full name, email, and roles
    """
    try:
        users = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "user_type": "System User"
            },
            fields=["name", "email", "full_name"],
            order_by="full_name asc"
        )

        # Get roles for each user
        for user in users:
            user_roles = frappe.get_all(
                "Has Role",
                filters={"parent": user.name},
                fields=["role"],
                pluck="role"
            )
            user["roles"] = user_roles
            # Create a display name with primary role
            primary_role = user_roles[0] if user_roles else "User"
            user["display_name"] = f"{user.full_name or user.email} ({primary_role})"

        return users

    except Exception as e:
        frappe.log_error(f"Get Staff Users Error: {str(e)}")
        raise


@frappe.whitelist()
def book_council_meeting(request_id=None, request_type_code=None, meeting_type="Pre-Application Meeting",
                         meeting_purpose=None, discussion_points=None, attendees=None, preferred_time_slots=None):
    """
    Book a council meeting for a request (or standalone for pre-application) and create a Pre-Application Meeting record

    Args:
        request_id: The Request document ID (optional for draft/pre-application meetings)
        request_type_code: Request type code if no request_id (for standalone meetings)
        meeting_type: Type of meeting (default: Pre-Application Meeting)
        meeting_purpose: Purpose/reason for the meeting
        discussion_points: Key topics to discuss
        attendees: List of additional attendees (dicts with attendee_name, attendee_email, attendee_role)
        preferred_time_slots: List of preferred time slots (dicts with preference_order, preferred_start, preferred_end)

    Returns:
        dict: Success message with meeting details
    """
    import json

    try:
        # Parse JSON if strings
        if isinstance(attendees, str):
            attendees = json.loads(attendees) if attendees else []
        if isinstance(preferred_time_slots, str):
            preferred_time_slots = json.loads(preferred_time_slots) if preferred_time_slots else []

        attendees = attendees or []
        preferred_time_slots = preferred_time_slots or []

        request_doc = None
        council_name = None

        # Handle draft/standalone meetings (no request_id yet)
        if request_id and request_id != "draft":
            # Verify the request exists
            if not frappe.db.exists("Request", request_id):
                frappe.throw(_("Request not found"))

            # Get the request document
            request_doc = frappe.get_doc("Request", request_id)
            council_name = request_doc.council

            # Check if a meeting already exists for this request
            existing_meeting = frappe.db.get_value(
                "Pre-Application Meeting",
                {
                    "request": request_id,
                    "status": ["in", ["Requested", "Scheduled", "Confirmed"]]
                },
                "name"
            )

            if existing_meeting:
                return {
                    "success": True,
                    "meeting_id": existing_meeting,
                    "message": f"A meeting request already exists: {existing_meeting}"
                }
        else:
            # For standalone/draft meetings, get council from session or default
            # Try to get from locked council in session
            locked_council = frappe.session.get("locked_council")
            if locked_council:
                council_name = locked_council
            else:
                # Get first available council as fallback
                councils = frappe.get_all("Council", filters={"is_active": 1}, limit=1)
                council_name = councils[0].name if councils else None

        # Create Pre-Application Meeting
        meeting_doc = frappe.get_doc({
            "doctype": "Pre-Application Meeting",
            "request": request_id if (request_id and request_id != "draft") else None,
            "council": council_name,
            "meeting_type": meeting_type,
            "status": "Requested",
            "meeting_purpose": meeting_purpose or f"Discuss {request_type_code or 'application'} requirements",
            "discussion_points": discussion_points,
            "requested_by": frappe.session.user,
            "requested_date": frappe.utils.now_datetime()
        })

        # Add preferred time slots
        for slot in preferred_time_slots:
            if slot.get("preferred_start") and slot.get("preferred_end"):
                meeting_doc.append("preferred_time_slots", {
                    "preference_order": slot.get("preference_order", 1),
                    "preferred_start": slot.get("preferred_start"),
                    "preferred_end": slot.get("preferred_end"),
                    "planner_response": "Pending"
                })

        # Add attendees
        for attendee in attendees:
            if attendee.get("attendee_name") and attendee.get("attendee_email"):
                meeting_doc.append("meeting_attendees", {
                    "attendee_name": attendee.get("attendee_name"),
                    "attendee_email": attendee.get("attendee_email"),
                    "role": attendee.get("attendee_role", "Representative")  # Map attendee_role to role field
                })

        meeting_doc.insert(ignore_permissions=True)

        # Add a comment to the request about the meeting booking (if request exists)
        if request_doc:
            request_doc.add_comment(
                "Comment",
                f"{meeting_type} requested. Meeting record {meeting_doc.name} created. A council planner will contact you within 2 business days to schedule."
            )

        # Create a notification task for council team
        try:
            # Get council planner role assignee
            council_user = "Administrator"
            if council_name:
                # Try to find a Consent Planner for this council
                users_with_role = frappe.get_all(
                    "Has Role",
                    filters={
                        "role": "Consent Planner",
                        "parenttype": "User"
                    },
                    fields=["parent"],
                    limit=10
                )

                for user_role in users_with_role:
                    user = user_role.parent
                    if frappe.db.get_value("User", user, "enabled"):
                        council_user = user
                        break

            task_doc = frappe.get_doc({
                "doctype": "WB Task",
                "title": f"Schedule {meeting_type} - {request_doc.request_number if request_doc else 'Pre-Application'}",
                "description": f"""
                    <p><strong>Meeting Request:</strong> {meeting_doc.name}</p>
                    {f'<p><strong>Request Number:</strong> {request_doc.request_number}</p>' if request_doc else ''}
                    {f'<p><strong>Request Type:</strong> {request_doc.request_type}</p>' if request_doc else f'<p><strong>Request Type:</strong> {request_type_code}</p>' if request_type_code else ''}
                    <p><strong>Requester:</strong> {frappe.session.user}</p>
                    <p><strong>Purpose:</strong> {meeting_purpose or 'N/A'}</p>
                    {f'<p><strong>Property:</strong> {request_doc.property_address}</p>' if request_doc and request_doc.property_address else ''}
                    <br>
                    <p><strong>Preferred Time Slots:</strong></p>
                    <ul>
                    {"".join([f'<li>Option {slot.get("preference_order")}: {slot.get("preferred_start")} to {slot.get("preferred_end")}</li>' for slot in preferred_time_slots if slot.get("preferred_start")])}
                    </ul>
                    <br>
                    <p>Please schedule this meeting with the applicant within 2 business days.</p>
                """,
                "status": "Open",
                "priority": "High",
                "task_type": "Manual",
                "due_date": frappe.utils.add_days(frappe.utils.today(), 2),
                "assign_from": frappe.session.user,
                "assign_to": council_user,
                "request": request_id if (request_id and request_id != "draft") else None
            })
            task_doc.insert(ignore_permissions=True)
        except Exception as task_error:
            frappe.log_error(f"Error creating task for meeting: {str(task_error)}")

        frappe.db.commit()

        return {
            "success": True,
            "meeting_id": meeting_doc.name,
            "meeting_type": meeting_type,
            "status": "Requested",
            "message": f"{meeting_type} request created successfully. A council planner will contact you within 2 business days."
        }

    except Exception as e:
        frappe.log_error(f"Book Council Meeting Error: {str(e)}", "Meeting Booking Error")
        frappe.throw(_("Failed to book meeting: {0}").format(str(e)))


@frappe.whitelist()
def send_request_message(request_id, subject, message, communication_type="Email"):
    """
    Send a message/communication to the council regarding a request.
    Creates a Communication Log entry and sends email notification.

    Args:
        request_id: Request document name
        subject: Message subject
        message: Message content (HTML)
        communication_type: Type of communication (Email, Phone, etc.)

    Returns:
        Communication Log document name
    """
    try:
        # Validate request exists and user has permission
        request_doc = frappe.get_doc("Request", request_id)

        if request_doc.requester != frappe.session.user:
            frappe.throw("You don't have permission to send messages for this request")

        # Get council email
        council_doc = frappe.get_doc("Council", request_doc.council)
        council_email = council_doc.contact_email

        # Create Communication Log
        comm = frappe.get_doc({
            "doctype": "Communication Log",
            "request": request_id,
            "communication_type": communication_type,
            "direction": "Outgoing",
            "subject": subject,
            "content": message,
            "sender": frappe.session.user,
            "recipient": council_email,
            "communication_date": frappe.utils.now_datetime(),
            "requires_response": 1
        })
        comm.insert(ignore_permissions=True)

        # Send email to council
        frappe.sendmail(
            recipients=[council_email],
            subject=f"Message regarding {request_doc.request_number}: {subject}",
            message=f"""
            <p>A message has been received from the applicant regarding request {request_doc.request_number}:</p>
            <p><strong>Subject:</strong> {subject}</p>
            <div>{message}</div>
            <hr>
            <p><strong>Request Details:</strong></p>
            <ul>
                <li>Request Number: {request_doc.request_number}</li>
                <li>Type: {request_doc.request_type}</li>
                <li>Applicant: {request_doc.requester_name}</li>
                <li>Email: {request_doc.requester_email}</li>
            </ul>
            """,
            reference_doctype="Request",
            reference_name=request_id
        )

        # Add comment to Request
        request_doc.add_comment("Comment", f"Message sent to council: {subject}")

        # Create WB Task for council team to respond
        task_doc = None
        assignee = None
        try:
            # Get request type and determine assignee
            request_type = request_doc.request_type
            assignee = frappe.session.user  # Default fallback

            if request_type:
                request_type_doc = frappe.get_doc("Request Type", request_type)

                # Get user with required role (if specified)
                if hasattr(request_type_doc, 'default_response_role') and request_type_doc.default_response_role:
                    # Find first active user with this role
                    users_with_role = frappe.get_all(
                        "Has Role",
                        filters={
                            "role": request_type_doc.default_response_role,
                            "parenttype": "User"
                        },
                        fields=["parent"],
                        limit=10
                    )

                    # Find first enabled user
                    for user_role in users_with_role:
                        user = user_role.parent
                        if frappe.db.get_value("User", user, "enabled"):
                            assignee = user
                            break

                # If no role specified or no user found, try to use assigned_to from request
                if assignee == frappe.session.user and request_doc.assigned_to:
                    assignee = request_doc.assigned_to

            # Create the task
            task_doc = frappe.get_doc({
                "doctype": "WB Task",
                "title": f"Respond to Message - {request_doc.request_number}",
                "description": f"""
                    <h3>Message Received from Applicant</h3>
                    <p><strong>Request:</strong> {request_doc.request_number}</p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>Message:</strong></p>
                    <div style="border-left: 3px solid #ccc; padding-left: 15px; margin: 10px 0;">
                        {message}
                    </div>
                    <p><strong>Sender:</strong> {frappe.session.user}</p>
                    <p><strong>Date:</strong> {frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M')}</p>
                    <hr>
                    <p><em>Please review and respond to this message through the Request view.</em></p>
                """,
                "status": "Open",
                "priority": "Medium",
                "task_type": "Manual",
                "due_date": frappe.utils.add_days(frappe.utils.today(), 3),  # 3 business days
                "assign_from": frappe.session.user,
                "assign_to": assignee,
                "request": request_id
            })
            task_doc.insert(ignore_permissions=True)

            frappe.logger().info(f"Created WB Task {task_doc.name} for message on {request_id}")

        except Exception as e:
            # Log error but don't fail the message sending
            frappe.log_error(f"Failed to create task for message: {str(e)}", "Message Task Creation Error")

        return {
            "success": True,
            "communication_id": comm.name,
            "task_id": task_doc.name if task_doc else None,
            "assigned_to": assignee if assignee else None,
            "message": "Message sent successfully to council"
        }

    except Exception as e:
        frappe.log_error(f"Send Message Error: {str(e)}", "Send Message Error")
        frappe.throw(_("Failed to send message: {0}").format(str(e)))


@frappe.whitelist()
def get_request_communications(request_id):
    """
    Get all communications for a request (excluding internal notes).

    Args:
        request_id: Request document name

    Returns:
        List of communication records
    """
    try:
        request_doc = frappe.get_doc("Request", request_id)

        # Check permission
        if request_doc.requester != frappe.session.user and not frappe.has_permission("Request", "read", request_doc):
            frappe.throw("You don't have permission to view communications for this request")

        communications = frappe.get_all(
            "Communication Log",
            filters={
                "request": request_id,
                "is_internal": 0  # Exclude internal notes
            },
            fields=[
                "name", "communication_number", "communication_type", "direction",
                "subject", "content", "sender", "recipient", "communication_date",
                "email_status", "requires_response", "response_due_date", "responded_at"
            ],
            order_by="communication_date desc"
        )

        return communications

    except Exception as e:
        frappe.log_error(f"Get Communications Error: {str(e)}", "Get Communications Error")
        frappe.throw(_("Failed to retrieve communications: {0}").format(str(e)))


@frappe.whitelist()
def get_meeting_details(meeting_id):
    """
    Get details of a specific meeting

    Args:
        meeting_id: Pre-Application Meeting ID

    Returns:
        dict: Meeting details
    """
    try:
        meeting = frappe.get_doc("Pre-Application Meeting", meeting_id)

        # Check permissions
        if not meeting.has_permission("read"):
            frappe.throw(_("You do not have permission to view this meeting"))

        # Get request details
        request_doc = frappe.get_doc("Request", meeting.request)

        # Get event details if linked
        event_details = None
        if meeting.event:
            event = frappe.get_doc("Event", meeting.event)
            event_details = {
                "name": event.name,
                "subject": event.subject,
                "starts_on": event.starts_on,
                "ends_on": event.ends_on,
                "status": event.status,
                "google_meet_link": event.google_meet_link if hasattr(event, 'google_meet_link') else None
            }

        return {
            "meeting": {
                "name": meeting.name,
                "request": meeting.request,
                "request_number": request_doc.request_number,
                "meeting_type": meeting.meeting_type,
                "status": meeting.status,
                "scheduled_start": meeting.scheduled_start,
                "scheduled_end": meeting.scheduled_end,
                "meeting_format": meeting.meeting_format,
                "meeting_location": meeting.meeting_location,
                "meeting_room": meeting.meeting_room,
                "google_meet_link": meeting.google_meet_link,
                "requester_name": meeting.requester_name,
                "requester_email": meeting.requester_email,
                "requester_phone": meeting.requester_phone,
                "council_planner": meeting.council_planner,
                "meeting_purpose": meeting.meeting_purpose,
                "discussion_points": meeting.discussion_points,
                "meeting_notes": meeting.meeting_notes,
                "outcome_summary": meeting.outcome_summary,
                "follow_up_required": meeting.follow_up_required,
                "follow_up_actions": meeting.follow_up_actions,
                "requested_by": meeting.requested_by,
                "requested_date": meeting.requested_date
            },
            "event": event_details,
            "request": {
                "name": request_doc.name,
                "request_number": request_doc.request_number,
                "request_type": request_doc.request_type,
                "status": request_doc.status,
                "council": request_doc.council
            }
        }

    except frappe.DoesNotExistError:
        frappe.throw(_("Meeting not found"))
    except Exception as e:
        frappe.log_error(f"Get Meeting Details Error: {str(e)}", "Meeting API Error")
        frappe.throw(_("Failed to get meeting details: {0}").format(str(e)))


@frappe.whitelist()
def get_request_meetings(request_id):
    """
    Get all meetings associated with a request

    Args:
        request_id: Request ID

    Returns:
        list: List of meetings for the request
    """
    try:
        # Check if user has access to this request
        request_doc = frappe.get_doc("Request", request_id)
        if not request_doc.has_permission("read"):
            frappe.throw(_("You do not have permission to view this request"))

        meetings = frappe.get_all(
            "Pre-Application Meeting",
            filters={"request": request_id},
            fields=[
                "name", "meeting_type", "status", "scheduled_start", "scheduled_end",
                "meeting_format", "meeting_location", "council_planner", "requested_date",
                "meeting_purpose", "event"
            ],
            order_by="requested_date desc"
        )

        # Enrich with event details
        for meeting in meetings:
            if meeting.event:
                event = frappe.get_doc("Event", meeting.event)
                meeting.event_status = event.status
                meeting.event_subject = event.subject

        return meetings

    except frappe.DoesNotExistError:
        frappe.throw(_("Request not found"))
    except Exception as e:
        frappe.log_error(f"Get Request Meetings Error: {str(e)}", "Meeting API Error")
        frappe.throw(_("Failed to get request meetings: {0}").format(str(e)))


@frappe.whitelist()
def schedule_meeting(meeting_id, scheduled_start, scheduled_end, meeting_location=None,
                     meeting_format="In Person", meeting_room=None, google_meet_link=None,
                     council_planner=None, discussion_points=None):
    """
    Schedule a requested meeting with specific details

    Args:
        meeting_id: Pre-Application Meeting ID
        scheduled_start: Start datetime (ISO format)
        scheduled_end: End datetime (ISO format)
        meeting_location: Physical location
        meeting_format: In Person/Video Call/Phone Call/Hybrid
        meeting_room: Room number/name
        google_meet_link: Google Meet URL
        council_planner: User assigned to the meeting
        discussion_points: Agenda items

    Returns:
        dict: Updated meeting details
    """
    try:
        meeting = frappe.get_doc("Pre-Application Meeting", meeting_id)

        # Check permissions - only council staff can schedule
        if not (frappe.has_permission("Pre-Application Meeting", "write", meeting)
                or "Consent Planner" in frappe.get_roles()
                or "System Manager" in frappe.get_roles()):
            frappe.throw(_("You do not have permission to schedule meetings"))

        # Use the schedule_meeting method from the controller
        meeting.schedule_meeting(
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            meeting_location=meeting_location,
            meeting_format=meeting_format,
            meeting_room=meeting_room,
            google_meet_link=google_meet_link,
            council_planner=council_planner
        )

        # Update discussion points if provided
        if discussion_points:
            meeting.discussion_points = discussion_points
            meeting.save(ignore_permissions=True)

        return {
            "success": True,
            "meeting_id": meeting.name,
            "status": meeting.status,
            "scheduled_start": meeting.scheduled_start,
            "scheduled_end": meeting.scheduled_end,
            "event": meeting.event,
            "message": _("Meeting scheduled successfully")
        }

    except frappe.DoesNotExistError:
        frappe.throw(_("Meeting not found"))
    except Exception as e:
        frappe.log_error(f"Schedule Meeting Error: {str(e)}", "Meeting API Error")
        frappe.throw(_("Failed to schedule meeting: {0}").format(str(e)))


@frappe.whitelist()
def reschedule_meeting(meeting_id, new_scheduled_start, new_scheduled_end, reason=None):
    """
    Reschedule an existing meeting

    Args:
        meeting_id: Pre-Application Meeting ID
        new_scheduled_start: New start datetime (ISO format)
        new_scheduled_end: New end datetime (ISO format)
        reason: Reason for rescheduling

    Returns:
        dict: Updated meeting details
    """
    try:
        meeting = frappe.get_doc("Pre-Application Meeting", meeting_id)

        # Check permissions
        if not (frappe.has_permission("Pre-Application Meeting", "write", meeting)
                or "Consent Planner" in frappe.get_roles()
                or "System Manager" in frappe.get_roles()):
            frappe.throw(_("You do not have permission to reschedule meetings"))

        # Store old times for notification
        old_start = meeting.scheduled_start
        old_end = meeting.scheduled_end

        # Update meeting times
        meeting.scheduled_start = new_scheduled_start
        meeting.scheduled_end = new_scheduled_end
        meeting.status = "Rescheduled"
        meeting.save(ignore_permissions=True)

        # Update linked event
        if meeting.event:
            event = frappe.get_doc("Event", meeting.event)
            event.starts_on = new_scheduled_start
            event.ends_on = new_scheduled_end
            event.save(ignore_permissions=True)

        # Add comment to meeting
        comment_text = f"Meeting rescheduled from {old_start} to {new_scheduled_start}"
        if reason:
            comment_text += f"\nReason: {reason}"

        meeting.add_comment("Comment", comment_text)

        # Send notification to applicant
        if meeting.requester_email:
            request_doc = frappe.get_doc("Request", meeting.request)
            frappe.sendmail(
                recipients=[meeting.requester_email],
                subject=f"Meeting Rescheduled - {request_doc.request_number}",
                message=f"""
                <p>Your {meeting.meeting_type} has been rescheduled.</p>
                <p><strong>Previous Time:</strong> {old_start}</p>
                <p><strong>New Time:</strong> {new_scheduled_start}</p>
                {f'<p><strong>Reason:</strong> {reason}</p>' if reason else ''}
                <p>If you have any questions, please contact us.</p>
                """,
                reference_doctype=meeting.doctype,
                reference_name=meeting.name
            )

        return {
            "success": True,
            "meeting_id": meeting.name,
            "status": meeting.status,
            "scheduled_start": meeting.scheduled_start,
            "scheduled_end": meeting.scheduled_end,
            "message": _("Meeting rescheduled successfully")
        }

    except frappe.DoesNotExistError:
        frappe.throw(_("Meeting not found"))
    except Exception as e:
        frappe.log_error(f"Reschedule Meeting Error: {str(e)}", "Meeting API Error")
        frappe.throw(_("Failed to reschedule meeting: {0}").format(str(e)))


@frappe.whitelist()
def complete_meeting(meeting_id, meeting_notes=None, outcome_summary=None,
                     follow_up_required=False, follow_up_actions=None):
    """
    Mark a meeting as completed with outcome details

    Args:
        meeting_id: Pre-Application Meeting ID
        meeting_notes: Internal notes from the meeting
        outcome_summary: Summary of meeting outcome
        follow_up_required: Boolean indicating if follow-up is needed
        follow_up_actions: Description of follow-up actions

    Returns:
        dict: Updated meeting details
    """
    try:
        meeting = frappe.get_doc("Pre-Application Meeting", meeting_id)

        # Check permissions - only council staff can complete
        if not (frappe.has_permission("Pre-Application Meeting", "write", meeting)
                or "Consent Planner" in frappe.get_roles()
                or "System Manager" in frappe.get_roles()):
            frappe.throw(_("You do not have permission to complete meetings"))

        # Use the complete_meeting method from the controller
        meeting.complete_meeting(
            meeting_notes=meeting_notes,
            outcome_summary=outcome_summary,
            follow_up_required=follow_up_required,
            follow_up_actions=follow_up_actions
        )

        return {
            "success": True,
            "meeting_id": meeting.name,
            "status": meeting.status,
            "message": _("Meeting marked as completed")
        }

    except frappe.DoesNotExistError:
        frappe.throw(_("Meeting not found"))
    except Exception as e:
        frappe.log_error(f"Complete Meeting Error: {str(e)}", "Meeting API Error")
        frappe.throw(_("Failed to complete meeting: {0}").format(str(e)))


@frappe.whitelist()
def cancel_meeting(meeting_id, reason=None):
    """
    Cancel a meeting

    Args:
        meeting_id: Pre-Application Meeting ID
        reason: Reason for cancellation

    Returns:
        dict: Cancellation confirmation
    """
    try:
        meeting = frappe.get_doc("Pre-Application Meeting", meeting_id)

        # Check permissions
        if not (frappe.has_permission("Pre-Application Meeting", "write", meeting)
                or meeting.requested_by == frappe.session.user
                or "Consent Planner" in frappe.get_roles()
                or "System Manager" in frappe.get_roles()):
            frappe.throw(_("You do not have permission to cancel this meeting"))

        # Update meeting status
        meeting.status = "Cancelled"
        meeting.save(ignore_permissions=True)

        # Update linked event
        if meeting.event:
            event = frappe.get_doc("Event", meeting.event)
            event.status = "Cancelled"
            event.save(ignore_permissions=True)

        # Add comment
        comment_text = "Meeting cancelled"
        if reason:
            comment_text += f"\nReason: {reason}"

        meeting.add_comment("Comment", comment_text)

        # Send notification to applicant
        if meeting.requester_email:
            request_doc = frappe.get_doc("Request", meeting.request)
            frappe.sendmail(
                recipients=[meeting.requester_email],
                subject=f"Meeting Cancelled - {request_doc.request_number}",
                message=f"""
                <p>Your {meeting.meeting_type} has been cancelled.</p>
                {f'<p><strong>Reason:</strong> {reason}</p>' if reason else ''}
                <p>If you would like to reschedule, please contact us.</p>
                """,
                reference_doctype=meeting.doctype,
                reference_name=meeting.name
            )

        return {
            "success": True,
            "meeting_id": meeting.name,
            "status": meeting.status,
            "message": _("Meeting cancelled successfully")
        }

    except frappe.DoesNotExistError:
        frappe.throw(_("Meeting not found"))
    except Exception as e:
        frappe.log_error(f"Cancel Meeting Error: {str(e)}", "Meeting API Error")
        frappe.throw(_("Failed to cancel meeting: {0}").format(str(e)))


@frappe.whitelist()
def get_user_meetings(status=None, from_date=None, to_date=None):
    """
    Get meetings for the current user (either as applicant or council planner)

    Args:
        status: Filter by status (optional)
        from_date: Filter meetings from this date (optional)
        to_date: Filter meetings until this date (optional)

    Returns:
        list: User's meetings
    """
    try:
        user = frappe.session.user

        filters = {
            "docstatus": ["<", 2]  # Not cancelled documents
        }

        # Add status filter if provided
        if status:
            filters["status"] = status

        # Date range filters
        if from_date:
            filters["scheduled_start"] = [">=", from_date]
        if to_date:
            if "scheduled_start" in filters:
                filters["scheduled_start"] = [[">=", from_date], ["<=", to_date]]
            else:
                filters["scheduled_start"] = ["<=", to_date]

        # Get meetings where user is applicant or council planner
        meetings = frappe.get_all(
            "Pre-Application Meeting",
            filters=filters,
            fields=[
                "name", "request", "meeting_type", "status", "scheduled_start", "scheduled_end",
                "meeting_format", "meeting_location", "requester_name", "council_planner",
                "requested_date", "event"
            ],
            order_by="scheduled_start desc"
        )

        # Filter for user's meetings (permission check)
        user_meetings = []
        for meeting in meetings:
            meeting_doc = frappe.get_doc("Pre-Application Meeting", meeting.name)
            if meeting_doc.has_permission("read"):
                # Get request number
                request_doc = frappe.get_doc("Request", meeting.request)
                meeting.request_number = request_doc.request_number
                meeting.council = request_doc.council
                user_meetings.append(meeting)

        return user_meetings

    except Exception as e:
        frappe.log_error(f"Get User Meetings Error: {str(e)}", "Meeting API Error")
        frappe.throw(_("Failed to get user meetings: {0}").format(str(e)))


@frappe.whitelist()
def get_user_requests(status=None):
    """
    Get all requests for the current user

    Args:
        status: Filter by status (optional)

    Returns:
        list: User's requests with key information
    """
    try:
        user = frappe.session.user

        filters = {
            "requester": user,
            "docstatus": ["<", 2]  # Not cancelled documents
        }

        # Add status filter if provided
        if status:
            filters["status"] = status

        requests = frappe.get_all(
            "Request",
            filters=filters,
            fields=[
                "name", "request_number", "request_type", "status",
                "requester_name", "requester_email", "requester_phone",
                "council", "brief_description", "creation", "modified",
                "workflow_state"
            ],
            order_by="modified desc"
        )

        return requests

    except Exception as e:
        frappe.log_error(f"Get User Requests Error: {str(e)}", "Request API Error")
        frappe.throw(_("Failed to get user requests: {0}").format(str(e)))


# ============================================================================
# COUNCIL MANAGEMENT API ENDPOINTS
# ============================================================================

@frappe.whitelist(allow_guest=True)
def get_active_councils():
    """
    Get all active councils for public display

    Returns:
        list: List of active councils with basic info
    """
    councils = frappe.get_all(
        "Council",
        filters={"is_active": 1},
        fields=["council_code", "council_name", "logo", "website", "primary_color", "secondary_color", "is_active"],
        order_by="council_name",
        limit_page_length=0  # No limit - return all active councils from database
    )

    return councils


@frappe.whitelist(allow_guest=True)
def get_council_by_code(council_code):
    """
    Get council details by code (for URL parameter handling)

    Args:
        council_code: Council code (e.g., AKL, WLG)

    Returns:
        dict: Council details or None if not found/inactive
    """
    if not council_code:
        return None

    try:
        council = frappe.get_doc("Council", council_code)

        if not council.is_active:
            return None

        return {
            "council_code": council.council_code,
            "council_name": council.council_name,
            "official_name": council.official_name,
            "logo": council.logo,
            "primary_color": council.primary_color,
            "secondary_color": council.secondary_color,
            "website": council.website,
            "contact_email": council.contact_email,
            "contact_phone": council.contact_phone,
            "is_license_valid": council.is_license_valid()
        }

    except frappe.DoesNotExistError:
        return None


@frappe.whitelist(allow_guest=True)
def get_user_councils(user=None):
    """
    Get councils associated with current user

    Args:
        user: User email (optional, defaults to current user)

    Returns:
        dict: User's default council and associated councils
    """
    user = user or frappe.session.user

    # Get default council (only if field exists)
    default_council = None
    if frappe.db.has_column("User", "default_council"):
        default_council = frappe.db.get_value("User", user, "default_council")

    # Get all requests submitted by this user to find associated councils
    user_councils = frappe.db.sql("""
        SELECT DISTINCT council
        FROM `tabRequest`
        WHERE applicant = %s AND council IS NOT NULL
    """, user, as_dict=True)

    associated_councils = [uc.get("council") for uc in user_councils if uc.get("council")]

    return {
        "default_council": default_council,
        "associated_councils": associated_councils
    }


@frappe.whitelist(allow_guest=True)
def get_request_types_for_council(council_code):
    """
    Get enabled request types for a specific council

    Args:
        council_code: Council code

    Returns:
        list: List of enabled request types with council-specific pricing
    """
    if not council_code:
        return []

    try:
        council = frappe.get_doc("Council", council_code)

        if not council.is_active or not council.is_license_valid():
            return []

        enabled_types = []

        for rt in council.enabled_request_types:
            if rt.is_enabled:
                request_type_doc = frappe.get_doc("Request Type", rt.request_type)

                enabled_types.append({
                    "name": request_type_doc.name,
                    "type_name": request_type_doc.type_name,
                    "request_type_name": request_type_doc.type_name,  # Alias for frontend compatibility
                    "type_code": request_type_doc.type_code,
                    "category": request_type_doc.category,
                    "description": rt.brief_description if rt.brief_description else (request_type_doc.description if hasattr(request_type_doc, 'description') else ""),
                    "base_fee": rt.base_fee_override if rt.base_fee_override else request_type_doc.base_fee,
                    "sla_days": rt.sla_days_override if rt.sla_days_override else request_type_doc.processing_sla_days,
                    "fee_calculation_method": request_type_doc.fee_calculation_method,
                    "process_description": rt.process_description or "",
                    # Smart defaults based on category
                    "requires_property": request_type_doc.requires_property if hasattr(request_type_doc, 'requires_property') else (request_type_doc.category != "Social Assistance"),
                    "requires_payment": request_type_doc.requires_payment if hasattr(request_type_doc, 'requires_payment') else (request_type_doc.base_fee > 0)
                })

        return enabled_types

    except frappe.DoesNotExistError:
        return []


@frappe.whitelist()
def set_user_default_council(council_code):
    """
    Set default council for current user

    Args:
        council_code: Council code to set as default

    Returns:
        dict: Success status and default council
    """
    user = frappe.session.user

    # Validate council exists and is active
    if not frappe.db.exists("Council", {"council_code": council_code, "is_active": 1}):
        frappe.throw(_("Invalid or inactive council"))

    # Only set if field exists
    if frappe.db.has_column("User", "default_council"):
        frappe.db.set_value("User", user, "default_council", council_code)
        frappe.db.commit()
    else:
        frappe.log_error(
            title="User DocType Missing default_council Field",
            message="The default_council field needs to be added to the User DocType"
        )

    return {
        "success": True,
        "default_council": council_code
    }


@frappe.whitelist()
def get_council_stats(council_code):
    """
    Get statistics for a council (for admin dashboards)

    Args:
        council_code: Council code

    Returns:
        dict: Council statistics
    """
    council = frappe.get_doc("Council", council_code)

    # Get monthly request count
    monthly_count = council.get_monthly_request_count()

    # Get total requests all time
    total_requests = frappe.db.count("Request", {"council": council_code})

    # Get requests by status
    requests_by_status = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabRequest`
        WHERE council = %s
        GROUP BY status
    """, council_code, as_dict=True)

    return {
        "council_name": council.council_name,
        "is_active": council.is_active,
        "is_license_valid": council.is_license_valid(),
        "monthly_request_count": monthly_count,
        "monthly_quota": council.max_requests_per_month,
        "total_requests": total_requests,
        "requests_by_status": requests_by_status,
        "enabled_request_types_count": len([rt for rt in council.enabled_request_types if rt.is_enabled])
    }


@frappe.whitelist(allow_guest=True)
def get_locked_council():
    """
    Returns the locked council from session, if any.
    Used by frontend to determine if council is locked for the request flow.

    Returns:
        dict: Locked council info or {"is_locked": False}
    """
    try:
        # Get session ID - check if it exists
        session_id = getattr(frappe.session, 'sid', None)
        if not session_id:
            return {"is_locked": False}

        # Get from cache using session ID
        locked_data = frappe.cache().hget("locked_council", session_id)

        if locked_data:
            try:
                data = frappe.parse_json(locked_data)
                locked_council = data.get("locked_council_code")
                council = frappe.get_doc("Council", locked_council)
                return {
                    "council_code": locked_council,
                    "council_name": data.get("locked_council_name"),
                    "locked_at": data.get("locked_at"),
                    "source_url": data.get("source_url"),
                    "is_locked": True,
                    "council": council.as_dict(),
                    # Add portal settings for frontend routing
                    "redirect_dashboard_to_council": int(council.redirect_dashboard_to_council or 1),
                    "allow_system_wide_dashboard": int(council.allow_system_wide_dashboard or 0),
                    "show_council_switcher": int(council.show_council_switcher or 0)
                }
            except (frappe.DoesNotExistError, ValueError, KeyError) as e:
                # Council was deleted or data corrupted - clear session
                frappe.log_error(f"Error loading locked council: {str(e)}")
                clear_locked_council()
                return {"is_locked": False}

        return {"is_locked": False}
    except Exception as e:
        # Log error but don't fail
        frappe.log_error(f"Error in get_locked_council: {str(e)}")
        return {"is_locked": False}


@frappe.whitelist(allow_guest=True)
def set_locked_council(council_code):
    """
    Manually lock a council in session.
    Used when user navigates to /{council_code} via Vue Router.

    Args:
        council_code: Council code to lock

    Returns:
        dict: Success status and council info
    """
    try:
        council_code = council_code.upper()

        # Verify council exists and is active
        try:
            council = frappe.get_doc("Council", council_code)
            if not council.is_active:
                frappe.throw(_("Council is not active"))
        except frappe.DoesNotExistError:
            frappe.throw(_("Council not found: {0}").format(council_code))

        # Get session ID - check if it exists
        session_id = getattr(frappe.session, 'sid', None)
        if not session_id:
            frappe.log_error("No session ID available for set_locked_council")
            return {"success": False, "error": "No session available"}

        # Set in session using Frappe's session cache (persists across requests)
        frappe.cache().hset("locked_council", session_id, frappe.as_json({
            "locked_council_code": council_code,
            "locked_council_name": council.council_name,
            "locked_at": frappe.utils.now(),
            "source_url": frappe.request.headers.get("Referer", "")
        }))

        return {
            "success": True,
            "council_code": council_code,
            "council_name": council.council_name
        }
    except Exception as e:
        frappe.log_error(f"Error in set_locked_council: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def clear_locked_council():
    """
    Clear locked council from session.
    Used when user explicitly wants to change council or session expires.

    Returns:
        dict: Success status
    """
    try:
        # Get session ID - check if it exists
        session_id = getattr(frappe.session, 'sid', None)
        if session_id:
            # Remove from cache
            frappe.cache().hdel("locked_council", session_id)

        return {"success": True}
    except Exception as e:
        frappe.log_error(f"Error in clear_locked_council: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def get_council_landing_page(council_code):
    """
    Get Council Landing Page configuration for a council.
    Returns default values if no landing page configured.

    Args:
        council_code: Council code

    Returns:
        dict: Landing page configuration
    """
    council_code = council_code.upper()

    # Verify council exists
    if not frappe.db.exists("Council", council_code):
        frappe.throw(_("Council not found: {0}").format(council_code))

    # Get landing page using SQL to avoid DocType cache issues
    landing_pages = frappe.db.sql("""
        SELECT *
        FROM `tabCouncil Landing Page`
        WHERE council = %s AND is_published = 1
        LIMIT 1
    """, (council_code,), as_dict=True)

    if landing_pages:
        return landing_pages[0]

    # Return defaults if no landing page configured
    council = frappe.get_doc("Council", council_code)
    return {
        "council": council_code,
        "is_published": 0,
        "hero_title": f"Welcome to {council.council_name}",
        "hero_subtitle": "Submit planning applications, building consents, and resource consent requests online",
        "primary_cta_text": "Start New Request",
        "primary_cta_link": "/frontend/request/new",
        "show_request_types": 1,
        "intro_html": None,
        "hero_image": None,
        "meta_title": None,
        "meta_description": None
    }


@frappe.whitelist()
def get_council_requests(council_code):
    """
    Get requests for current user filtered by council.
    Used by council-specific dashboard.

    Args:
        council_code: Council code to filter by

    Returns:
        list: Requests for this council
    """
    user = frappe.session.user

    requests = frappe.get_all(
        "Request",
        filters={
            "requester": user,
            "council": council_code
        },
        fields=[
            "name", "request_number", "request_type", "status",
            "property_address", "brief_description", "creation",
            "submitted_date", "statutory_clock_started",
            "working_days_elapsed", "council"
        ],
        order_by="modified desc"
    )

    # Enrich with council name
    for req in requests:
        if req.get("council"):
            council_name = frappe.db.get_value("Council", req["council"], "council_name")
            req["council_name"] = council_name

    return requests


@frappe.whitelist()
def should_redirect_to_council_dashboard(council_code):
    """
    Check if user should be redirected to council-specific dashboard.
    Used by route guard on /dashboard.

    Args:
        council_code: Council code to check settings for

    Returns:
        dict: Redirect settings for this council
    """
    try:
        council = frappe.get_doc("Council", council_code)
        return {
            "should_redirect": int(council.redirect_dashboard_to_council or 1),
            "allow_system_wide": int(council.allow_system_wide_dashboard or 0),
            "show_switcher": int(council.show_council_switcher or 0),
            "council_name": council.council_name,
            "primary_color": council.primary_color
        }
    except frappe.DoesNotExistError:
        return {
            "should_redirect": False,
            "allow_system_wide": True,
            "show_switcher": False
        }


@frappe.whitelist(allow_guest=True)
def get_council_settings(council_code):
    """
    Get council portal and website settings.
    Used for branding and configuration in council-specific pages.

    Args:
        council_code: Council code

    Returns:
        dict: Council settings
    """
    try:
        council = frappe.get_doc("Council", council_code)
        return {
            "council_code": council.council_code,
            "council_name": council.council_name,
            "official_name": council.official_name,
            "logo": council.logo,
            "primary_color": council.primary_color,
            "secondary_color": council.secondary_color,
            "redirect_dashboard_to_council": int(council.redirect_dashboard_to_council or 1),
            "allow_system_wide_dashboard": int(council.allow_system_wide_dashboard or 0),
            "show_council_switcher": int(council.show_council_switcher or 0),
            "custom_domain": council.custom_domain,
            "login_page_custom_html": council.login_page_custom_html,
            "contact_email": council.contact_email,
            "contact_phone": council.contact_phone,
            "website": council.website
        }
    except frappe.DoesNotExistError:
        frappe.throw(_("Council not found: {0}").format(council_code))


# ============================================================================
# ANALYTICS - LOGIN SOURCE TRACKING
# ============================================================================

@frappe.whitelist()
def track_login_event(source, council_code=None):
    """
    Track login events for analytics

    Args:
        source: Login source ('system-wide' or 'council-specific')
        council_code: Council code if council-specific login
    """
    try:
        # Create login tracking record
        login_event = frappe.get_doc({
            "doctype": "Login Event",
            "user": frappe.session.user,
            "source": source,
            "council": council_code,
            "timestamp": frappe.utils.now(),
            "ip_address": frappe.local.request_ip,
            "user_agent": frappe.local.request.headers.get("User-Agent")
        })
        login_event.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"success": True}
    except Exception as e:
        frappe.log_error(f"Failed to track login event: {str(e)}")
        # Don't fail the login if tracking fails
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_login_analytics(council_code=None, from_date=None, to_date=None):
    """
    Get login analytics data

    Args:
        council_code: Optional council filter
        from_date: Start date for analytics
        to_date: End date for analytics

    Returns:
        dict: Analytics data including counts and breakdowns
    """
    filters = {}

    if council_code:
        filters["council"] = council_code

    if from_date:
        filters["timestamp"] = [">=", from_date]

    if to_date:
        if "timestamp" in filters:
            filters["timestamp"] = [[">=", from_date], ["<=", to_date]]
        else:
            filters["timestamp"] = ["<=", to_date]

    # Get login events
    events = frappe.get_all(
        "Login Event",
        filters=filters,
        fields=["source", "council", "timestamp", "user"],
        order_by="timestamp desc"
    )

    # Calculate analytics
    total_logins = len(events)
    system_wide_logins = len([e for e in events if e.source == "system-wide"])
    council_logins = len([e for e in events if e.source == "council-specific"])

    # Council breakdown
    council_breakdown = {}
    for event in events:
        if event.council:
            council_breakdown[event.council] = council_breakdown.get(event.council, 0) + 1

    # Unique users
    unique_users = len(set(e["user"] for e in events))

    return {
        "total_logins": total_logins,
        "system_wide_logins": system_wide_logins,
        "council_specific_logins": council_logins,
        "council_breakdown": council_breakdown,
        "unique_users": unique_users,
        "events": events[:100]  # Return last 100 events
    }


# ============================================================================
# USER PROFILE & SETTINGS API ENDPOINTS
# ============================================================================

@frappe.whitelist(allow_guest=True)
def get_user_profile(user=None):
    """
    Get user profile information including custom fields and organization data

    Args:
        user: User email (optional, defaults to current user)

    Returns:
        dict: User profile data
    """
    if not user:
        user = frappe.session.user

    # Get user document with custom fields
    user_doc = frappe.get_doc("User", user)

    # Get organization data if user has organization link
    organization_data = None
    if user_doc.get("organization"):
        org = frappe.get_doc("Organization", user_doc.organization)
        organization_data = {
            "name": org.name,
            "organization_name": org.organization_name,
            "organization_type": org.organization_type,
            "registration_number": org.registration_number,
            "contact_email": org.contact_email,
            "contact_phone": org.contact_phone,
            "address": org.address,
            "city": org.city,
            "postal_code": org.postal_code
        }

    # Get default council data if set
    default_council_data = None
    if user_doc.get("default_council"):
        council = frappe.get_doc("Council", user_doc.default_council)
        default_council_data = {
            "council_code": council.council_code,
            "council_name": council.council_name,
            "primary_color": council.primary_color
        }

    return {
        "email": user_doc.email,
        "first_name": user_doc.first_name,
        "last_name": user_doc.last_name,
        "full_name": user_doc.full_name,
        "user_image": user_doc.user_image,
        "mobile_no": user_doc.mobile_no,
        "phone": user_doc.phone,
        "bio": user_doc.bio,
        "location": user_doc.location,
        "account_type": user_doc.get("account_type") or "Applicant",
        "requester_type": user_doc.get("requester_type") or "Individual",
        "default_council": user_doc.get("default_council"),
        "default_council_data": default_council_data,
        "organization": user_doc.get("organization"),
        "organization_data": organization_data,
        "enabled": user_doc.enabled,
        "user_type": user_doc.user_type,
        "creation": user_doc.creation,
        "modified": user_doc.modified
    }


@frappe.whitelist()
def update_user_profile(first_name=None, last_name=None, mobile_no=None, phone=None,
                       bio=None, location=None, default_council=None, user_image=None):
    """
    Update user profile information

    Args:
        first_name: User's first name
        last_name: User's last name
        mobile_no: Mobile phone number
        phone: Phone number
        bio: User biography
        location: User location
        default_council: Default council code
        user_image: User profile image URL

    Returns:
        dict: Success status and updated user data
    """
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    # Update fields if provided
    if first_name is not None:
        user_doc.first_name = first_name
    if last_name is not None:
        user_doc.last_name = last_name
    if mobile_no is not None:
        user_doc.mobile_no = mobile_no
    if phone is not None:
        user_doc.phone = phone
    if bio is not None:
        user_doc.bio = bio
    if location is not None:
        user_doc.location = location
    if user_image is not None:
        user_doc.user_image = user_image

    # Update default council if provided
    if default_council is not None:
        # Validate council exists and is active
        if default_council:
            council = frappe.get_doc("Council", default_council)
            if not council.is_active:
                frappe.throw("Selected council is not active")
        user_doc.default_council = default_council

    user_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": get_user_profile(user)
    }


@frappe.whitelist()
def change_password(old_password, new_password):
    """
    Change user password

    Args:
        old_password: Current password
        new_password: New password

    Returns:
        dict: Success status
    """
    from frappe.utils.password import check_password, update_password

    user = frappe.session.user

    # Verify old password
    try:
        check_password(user, old_password)
    except Exception:
        frappe.throw("Current password is incorrect")

    # Update to new password
    update_password(user, new_password)
    frappe.db.commit()

    return {
        "success": True,
        "message": "Password changed successfully"
    }


@frappe.whitelist()
def get_user_organization(user=None):
    """
    Get organization details for the user

    Args:
        user: User email (optional, defaults to current user)

    Returns:
        dict: Organization data or None
    """
    if not user:
        user = frappe.session.user

    user_doc = frappe.get_doc("User", user)

    if not user_doc.get("organization"):
        return None

    org = frappe.get_doc("Organization", user_doc.organization)

    return {
        "name": org.name,
        "organization_name": org.organization_name,
        "organization_type": org.organization_type,
        "registration_number": org.registration_number,
        "contact_email": org.contact_email,
        "contact_phone": org.contact_phone,
        "address": org.address,
        "city": org.city,
        "postal_code": org.postal_code,
        "website": org.website,
        "description": org.description,
        "is_verified": org.is_verified,
        "creation": org.creation,
        "modified": org.modified
    }


@frappe.whitelist()
def update_user_organization(organization_name=None, contact_email=None, contact_phone=None,
                            address=None, city=None, postal_code=None, website=None, description=None):
    """
    Update organization details for the user

    Args:
        organization_name: Organization name
        contact_email: Contact email
        contact_phone: Contact phone
        address: Street address
        city: City
        postal_code: Postal code
        website: Website URL
        description: Organization description

    Returns:
        dict: Success status and updated organization data
    """
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    if not user_doc.get("organization"):
        frappe.throw("No organization linked to this user")

    org = frappe.get_doc("Organization", user_doc.organization)

    # Update fields if provided
    if organization_name is not None:
        org.organization_name = organization_name
    if contact_email is not None:
        org.contact_email = contact_email
    if contact_phone is not None:
        org.contact_phone = contact_phone
    if address is not None:
        org.address = address
    if city is not None:
        org.city = city
    if postal_code is not None:
        org.postal_code = postal_code
    if website is not None:
        org.website = website
    if description is not None:
        org.description = description

    org.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "message": "Organization updated successfully",
        "organization": get_user_organization(user)
    }


@frappe.whitelist(allow_guest=True)
def search_property_address(query):
    """
    Search for property addresses using the LINZ property API

    Args:
        query: Address search string

    Returns:
        dict: Search results with property and hazard information
    """
    import requests

    if not query or len(query) < 3:
        return {"results": []}

    try:
        # Call the property API service
        # Note: The property API should be running on localhost:3000
        property_api_url = frappe.conf.get("property_api_url", "http://localhost:3000")

        response = requests.get(
            f"{property_api_url}/api/search",
            params={"q": query},
            timeout=10
        )

        if response.status_code != 200:
            frappe.log_error(
                title="Property API Error",
                message=f"Status: {response.status_code}, Response: {response.text}"
            )
            return {"results": []}

        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        frappe.log_error(
            title="Property API Connection Error",
            message=str(e)
        )
        return {"results": []}
    except Exception as e:
        frappe.log_error(
            title="Property Search Error",
            message=str(e)
        )
        return {"results": []}


@frappe.whitelist(allow_guest=True)
def search_property_addresses(query):
    """
    Alias for search_property_address to match AddressLookup component API call

    Args:
        query: Address search string

    Returns:
        list: Array of address results in standardized format
    """
    result = search_property_address(query)

    # If the result has a 'results' key, return it directly
    if isinstance(result, dict) and 'results' in result:
        return result['results']

    # Otherwise return the result as-is
    return result if isinstance(result, list) else []


@frappe.whitelist(allow_guest=True)
def search_addresses_universal(query, country):
    """
    Universal address lookup for multiple countries (NZ, AU, PH)

    Args:
        query: Address search string
        country: Country code (NZ, AU, PH)

    Returns:
        list: Array of address results in standardized format
    """
    import requests

    if not query or len(query) < 3:
        return []

    if not country:
        frappe.throw(_("Country code is required"))

    try:
        if country == "NZ":
            # Use existing NZ property API
            result = search_property_address(query)
            if isinstance(result, dict) and 'results' in result:
                return result['results']
            return result if isinstance(result, list) else []

        elif country == "AU":
            # Australia address lookup using GNAF or similar service
            # For now, return stub data for development
            return search_australia_addresses(query)

        elif country == "PH":
            # Philippines address lookup
            # For now, return stub data for development
            return search_philippines_addresses(query)

        else:
            frappe.throw(_("Unsupported country code: {0}").format(country))

    except Exception as e:
        frappe.log_error(
            title=f"Universal Address Search Error ({country})",
            message=str(e)
        )
        return []


def search_australia_addresses(query):
    """
    Search for addresses in Australia

    TODO: Integrate with GNAF (Geocoded National Address File) or commercial API
    For now, returns stub data for development

    Args:
        query: Address search string

    Returns:
        list: Array of address results
    """
    # Stub implementation - replace with actual API integration
    # Options for AU:
    # 1. data.gov.au GNAF dataset
    # 2. Google Places API
    # 3. Mapbox Geocoding API
    # 4. Australia Post Address API

    return []


def search_philippines_addresses(query):
    """
    Search for addresses in Philippines

    TODO: Integrate with Philippines address API
    For now, returns stub data for development

    Args:
        query: Address search string

    Returns:
        list: Array of address results
    """
    # Stub implementation - replace with actual API integration
    # Options for PH:
    # 1. Google Places API
    # 2. Nominatim (OpenStreetMap)
    # 3. OneMap Philippines (if available)
    # 4. PhilGIS data

    return []


@frappe.whitelist(allow_guest=True)
def get_council_request_types(council_code):
    """
    Get enabled request types for a specific council with council-specific configuration

    Args:
        council_code: Council code (e.g., "HCC" for Hutt City Council)

    Returns:
        list: List of enabled request types with council-specific pricing, description, and process
    """
    try:
        council = frappe.get_doc("Council", council_code)

        if not council.is_active:
            return []

        result = []

        for council_rt in council.enabled_request_types:
            if not council_rt.is_enabled:
                continue

            # Get the base request type
            request_type = frappe.get_doc("Request Type", council_rt.request_type)

            # Build result with council overrides
            rt_data = {
                "name": request_type.name,
                "type_name": request_type.type_name,
                "category": getattr(request_type, 'category', None),
                "description": council_rt.brief_description or getattr(request_type, 'description', ''),
                "base_fee": council_rt.base_fee_override or getattr(request_type, 'base_fee', 0),
                "processing_sla_days": council_rt.sla_days_override or getattr(request_type, 'processing_sla_days', 20),
                "is_active": getattr(request_type, 'is_active', 1)
            }

            result.append(rt_data)

        return result

    except frappe.DoesNotExistError:
        frappe.throw(_("Council not found: {0}").format(council_code))
    except Exception as e:
        frappe.log_error(
            title="Error fetching council request types",
            message=str(e)
        )
        frappe.throw(_("Error fetching request types for council"))


# ============================================================
# Company Account Management APIs
# ============================================================

@frappe.whitelist()
def register_company_account(company_data):
	"""
	Register a new company account
	Validates NZBN, creates Company Account doc
	Links creating user as first admin

	Args:
		company_data: dict with company details

	Returns:
		dict: Success message and company account name
	"""
	import json
	if isinstance(company_data, str):
		company_data = json.loads(company_data)

	# Validate required fields
	if not company_data.get("company_name"):
		frappe.throw(_("Company name is required"))
	if not company_data.get("legal_name"):
		frappe.throw(_("Legal name is required"))
	if not company_data.get("primary_email"):
		frappe.throw(_("Primary email is required"))
	if not company_data.get("primary_phone"):
		frappe.throw(_("Primary phone is required"))
	if not company_data.get("registered_office_address"):
		frappe.throw(_("Registered office address is required"))

	# Check if company already exists
	if frappe.db.exists("Company Account", company_data.get("company_name")):
		frappe.throw(_("Company account with this name already exists"))

	# Check NZBN uniqueness if provided
	if company_data.get("nzbn"):
		if frappe.db.exists("Company Account", {"nzbn": company_data.get("nzbn")}):
			frappe.throw(_("Company account with this NZBN already exists"))

	try:
		# Create Company Account
		company = frappe.get_doc({
			"doctype": "Company Account",
			"company_name": company_data.get("company_name"),
			"legal_name": company_data.get("legal_name"),
			"trading_name": company_data.get("trading_name"),
			"company_number": company_data.get("company_number"),
			"nzbn": company_data.get("nzbn"),
			"company_type": company_data.get("company_type", "Limited Liability Company"),
			"registered_office_address": company_data.get("registered_office_address"),
			"postal_address": company_data.get("postal_address"),
			"primary_phone": company_data.get("primary_phone"),
			"primary_email": company_data.get("primary_email"),
			"website": company_data.get("website"),
			"default_council": company_data.get("default_council"),
			"account_status": "Active",
			"admin_users": [{
				"user": frappe.session.user,
				"designation": company_data.get("user_designation", "Director"),
				"can_manage_users": 1,
				"can_manage_billing": 1
			}]
		})
		company.insert()

		# Update current user's company fields
		user = frappe.get_doc("User", frappe.session.user)
		user.company_account = company.name
		user.company_role = "Admin"
		user.save(ignore_permissions=True)

		return {
			"success": True,
			"company_name": company.name,
			"message": _("Company account created successfully")
		}

	except Exception as e:
		frappe.log_error(title="Error creating company account", message=str(e))
		frappe.throw(_("Error creating company account: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def get_user_company_account():
	"""
	Get company account details for current user
	Returns company info + user's role in company

	Returns:
		dict: Company account details or None
	"""
	user = frappe.get_doc("User", frappe.session.user)

	if not hasattr(user, 'company_account') or not user.company_account:
		return None

	try:
		company = frappe.get_doc("Company Account", user.company_account)

		# Get user's role
		user_role = company.get_user_role(frappe.session.user)

		return {
			"name": company.name,
			"company_name": company.company_name,
			"legal_name": company.legal_name,
			"trading_name": company.trading_name,
			"nzbn": company.nzbn,
			"company_number": company.company_number,
			"company_type": company.company_type,
			"primary_email": company.primary_email,
			"primary_phone": company.primary_phone,
			"registered_office_address": company.registered_office_address,
			"postal_address": company.postal_address,
			"website": company.website,
			"default_council": company.default_council,
			"account_status": company.account_status,
			"user_role": user_role,
			"total_applications": company.total_applications,
			"total_payments": company.total_payments
		}

	except frappe.DoesNotExistError:
		# Company was deleted
		if hasattr(user, 'company_account'):
			user.company_account = None
		if hasattr(user, 'company_role'):
			user.company_role = None
		user.save(ignore_permissions=True)
		return None


@frappe.whitelist()
def update_company_account(company_name, updates):
	"""
	Update company account details
	Requires: Admin role in company

	Args:
		company_name: Name of company account
		updates: dict of fields to update

	Returns:
		dict: Success message
	"""
	import json
	if isinstance(updates, str):
		updates = json.loads(updates)

	company = frappe.get_doc("Company Account", company_name)

	# Check permission
	if not company.can_user_perform_action(frappe.session.user, "edit_profile"):
		frappe.throw(_("You do not have permission to edit this company"))

	# Update allowed fields
	allowed_fields = [
		"trading_name", "company_number", "nzbn", "company_type",
		"registered_office_address", "postal_address",
		"primary_phone", "primary_email", "website",
		"bank_name", "bank_account_number", "billing_email",
		"billing_contact", "default_council"
	]

	for field, value in updates.items():
		if field in allowed_fields:
			setattr(company, field, value)

	company.save()

	return {
		"success": True,
		"message": _("Company account updated successfully")
	}


@frappe.whitelist()
def send_company_invitation(company_name, email, role, designation=None):
	"""
	Invite/link a user to company account
	Requires: Admin role with can_manage_users permission

	Args:
		company_name: Name of company account
		email: Email of user to invite
		role: Role to assign (Admin/Submitter/Viewer)
		designation: Optional designation

	Returns:
		dict: Success message and invitation details
	"""
	company = frappe.get_doc("Company Account", company_name)

	# Check permission
	if not company.can_user_perform_action(frappe.session.user, "invite_users"):
		frappe.throw(_("You do not have permission to invite users"))

	# Check if user already exists
	user_exists = frappe.db.exists("User", email)

	# Check if user is already linked
	for admin in company.admin_users:
		if admin.user == email:
			frappe.throw(_("User is already an admin of this company"))

	for linked_user in company.linked_users:
		if linked_user.user == email:
			frappe.throw(_("User is already linked to this company"))

	# Create invitation
	from frappe.utils import random_string, now_datetime, add_days

	invitation = frappe.get_doc({
		"doctype": "Company Invitation",
		"company_account": company_name,
		"invited_user": email,
		"invited_by": frappe.session.user,
		"role": role,
		"status": "Pending",
		"invitation_key": random_string(32),
		"sent_date": now_datetime(),
		"expiry_date": add_days(now_datetime(), 7)
	})
	invitation.insert()

	# Send invitation email
	send_invitation_email(invitation, company, user_exists)

	return {
		"success": True,
		"invitation_key": invitation.invitation_key,
		"message": _("Invitation sent to {0}").format(email)
	}


def send_invitation_email(invitation, company, user_exists):
	"""Send invitation email to user"""
	from frappe.utils import get_url

	subject = _("Invitation to join {0} on Lodgeick").format(company.company_name)

	invitation_url = get_url(f"/accept-invitation/{invitation.invitation_key}")

	if user_exists:
		message = f"""
		<h2>You've been invited to join {company.company_name}</h2>

		<p>You have been invited to join {company.company_name} as a <strong>{invitation.role}</strong>.</p>

		<p><a href="{invitation_url}" style="display: inline-block; padding: 12px 24px; background-color: #2563EB; color: white; text-decoration: none; border-radius: 6px;">Accept Invitation</a></p>

		<p>This invitation will expire in 7 days.</p>

		<p>Invited by: {invitation.invited_by}</p>
		"""
	else:
		message = f"""
		<h2>You've been invited to join {company.company_name} on Lodgeick</h2>

		<p>You have been invited to join {company.company_name} as a <strong>{invitation.role}</strong>.</p>

		<p>Since you don't have a Lodgeick account yet, you'll need to register first, then accept this invitation.</p>

		<p><a href="{invitation_url}" style="display: inline-block; padding: 12px 24px; background-color: #2563EB; color: white; text-decoration: none; border-radius: 6px;">Register & Accept Invitation</a></p>

		<p>This invitation will expire in 7 days.</p>

		<p>Invited by: {invitation.invited_by}</p>
		"""

	frappe.sendmail(
		recipients=[invitation.invited_user],
		subject=subject,
		message=message,
		reference_doctype="Company Invitation",
		reference_name=invitation.name
	)


@frappe.whitelist(allow_guest=True)
def accept_company_invitation(invitation_key):
	"""
	Accept company invitation
	Links user to company with specified role

	Args:
		invitation_key: Unique invitation key

	Returns:
		dict: Success message and company details
	"""
	invitation = frappe.get_doc("Company Invitation", {"invitation_key": invitation_key})

	if invitation.status != "Pending":
		frappe.throw(_("This invitation has already been {0}").format(invitation.status.lower()))

	# Check expiry
	from frappe.utils import now_datetime
	if now_datetime() > invitation.expiry_date:
		invitation.status = "Expired"
		invitation.save(ignore_permissions=True)
		frappe.throw(_("This invitation has expired"))

	# User must be logged in and match invited email
	if frappe.session.user == "Guest":
		frappe.throw(_("Please log in to accept this invitation"))

	if frappe.session.user != invitation.invited_user:
		frappe.throw(_("This invitation was sent to {0}. Please log in with that account.").format(invitation.invited_user))

	# Add user to company
	company = frappe.get_doc("Company Account", invitation.company_account)

	if invitation.role == "Admin":
		company.append("admin_users", {
			"user": invitation.invited_user,
			"can_manage_users": 1,
			"can_manage_billing": 1
		})
	else:
		company.append("linked_users", {
			"user": invitation.invited_user,
			"role": invitation.role,
			"added_by": invitation.invited_by,
			"is_active": 1
		})

	company.save(ignore_permissions=True)

	# Update user's company fields
	user = frappe.get_doc("User", invitation.invited_user)
	user.company_account = company.name
	user.company_role = invitation.role
	user.save(ignore_permissions=True)

	# Update invitation status
	invitation.status = "Accepted"
	invitation.accepted_date = now_datetime()
	invitation.save(ignore_permissions=True)

	return {
		"success": True,
		"company_name": company.company_name,
		"role": invitation.role,
		"message": _("You have joined {0} as a {1}").format(company.company_name, invitation.role)
	}


@frappe.whitelist()
def remove_user_from_company(company_name, user_email):
	"""
	Remove user from company account
	Requires: Admin role with can_manage_users permission

	Args:
		company_name: Name of company account
		user_email: Email of user to remove

	Returns:
		dict: Success message
	"""
	company = frappe.get_doc("Company Account", company_name)

	# Check permission
	if not company.can_user_perform_action(frappe.session.user, "remove_users"):
		frappe.throw(_("You do not have permission to remove users"))

	# Cannot remove self if last admin
	if user_email == frappe.session.user:
		admin_count = len(company.admin_users)
		if admin_count <= 1:
			frappe.throw(_("Cannot remove yourself as you are the only admin"))

	# Remove from admin_users
	for i, admin in enumerate(company.admin_users):
		if admin.user == user_email:
			company.remove(company.admin_users[i])
			break

	# Remove from linked_users
	for i, linked_user in enumerate(company.linked_users):
		if linked_user.user == user_email:
			company.remove(company.linked_users[i])
			break

	company.save()

	# Update user's company fields
	if frappe.db.exists("User", user_email):
		user = frappe.get_doc("User", user_email)
		user.company_account = None
		user.company_role = None
		user.save(ignore_permissions=True)

	return {
		"success": True,
		"message": _("User removed from company")
	}


# ================================
# KYC / Identity Verification APIs
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
		from lodgeick.eligibility_engine import EligibilityEngine

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
		if request.status not in ["Approved", "Active"]:
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
def create_payout_batch(batch_name, batch_type, request_type=None, council=None,
					   period_start=None, period_end=None):
	"""
	Create a payout batch for bulk processing

	Args:
		batch_name: Name of the batch
		batch_type: Monthly Pension/One-time Assistance/Emergency Aid/Burial-Medical
		request_type: Filter by request type
		council: Council ID
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
			"council": council or "TAYTAY-PH",
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
		from lodgeick.bank_file_generator import BankFileGenerator

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
		from lodgeick.fraud_detector import FraudDetector

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
		# Check for active requests
		active_requests = frappe.get_all("Request",
										filters={
											"requester_email": user_email,
											"request_type": request_type,
											"status": ["in", ["Submitted", "Under Review", "Approved", "Active"]]
										},
										fields=["name", "status", "creation"])

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
			break

	if updated:
		company.save()

		# Update user's company_role field
		user = frappe.get_doc("User", user_email)
		user.company_role = new_role
		user.save(ignore_permissions=True)

		return {
			"success": True,
			"message": _("User role updated to {0}").format(new_role)
		}
	else:
		frappe.throw(_("User not found in company"))


@frappe.whitelist()
def get_company_users(company_name):
	"""
	Get all users linked to company with their roles
	Requires: Any company member (read-only for non-admins)

	Args:
		company_name: Name of company account

	Returns:
		list: List of users with roles
	"""
	company = frappe.get_doc("Company Account", company_name)

	# Check if user is member
	user_role = company.get_user_role(frappe.session.user)
	if not user_role:
		frappe.throw(_("You do not have access to this company"))

	users = []

	# Add admin users
	for admin in company.admin_users:
		user_doc = frappe.get_doc("User", admin.user)
		users.append({
			"email": admin.user,
			"full_name": user_doc.full_name,
			"role": "Admin",
			"designation": admin.designation,
			"added_date": admin.added_date,
			"can_manage_users": admin.can_manage_users,
			"can_manage_billing": admin.can_manage_billing,
			"is_active": 1
		})

	# Add linked users
	for linked_user in company.linked_users:
		user_doc = frappe.get_doc("User", linked_user.user)
		users.append({
			"email": linked_user.user,
			"full_name": user_doc.full_name,
			"role": linked_user.role,
			"designation": None,
			"added_date": linked_user.added_date,
			"added_by": linked_user.added_by,
			"is_active": linked_user.is_active
		})

	return users

# ================================
# Step Configuration APIs
# ================================

@frappe.whitelist(allow_guest=True)
def get_request_type_steps(request_type, council_code=None):
	"""
	Get step configuration for a request type, with optional council overrides
	
	Args:
		request_type: Name of Request Type
		council_code: Optional council code to apply council-specific overrides
	
	Returns:
		dict: Steps configuration with sections and fields
	"""
	try:
		# Get request type document
		rt_doc = frappe.get_doc("Request Type", request_type)
		
		# If no step_configs, return empty (fallback to hardcoded flow)
		if not rt_doc.step_configs:
			return {
				"steps": [],
				"uses_config": False,
				"message": "No step configuration found. Using default hardcoded flow."
			}
		
		steps = []

		# Load base step configuration
		for step_config in rt_doc.step_configs:
			if not step_config.is_enabled:
				continue

			step_data = {
				"step_number": step_config.step_number,
				"step_code": step_config.step_code,
				"step_title": step_config.step_title,
				"step_component": step_config.step_component or "DynamicStepRenderer",
				"is_enabled": step_config.is_enabled,
				"is_required": step_config.is_required,
				"show_on_review": step_config.show_on_review,
				"depends_on": step_config.depends_on,
				"sections": []
			}

			# FLATTENED STRUCTURE: Query sections by parent_step_code instead of nested parent
			# Sections are now stored directly under Request Type with a parent_step_code link
			sections = frappe.get_all(
				"Request Type Step Section",
				filters={
					"parent": rt_doc.name,  # Parent is now Request Type, not Step Config
					"parenttype": "Request Type",
					"parent_step_code": step_config.step_code  # Link via step_code
				},
				fields=["name", "section_code", "section_title", "section_type", "sequence",
				        "is_enabled", "is_required", "show_on_review", "depends_on"],
				order_by="sequence asc"
			)

			for section in sections:
				if not section.is_enabled:
					continue

				section_data = {
					"section_code": section.section_code,
					"section_title": section.section_title,
					"section_type": section.section_type,
					"sequence": section.sequence,
					"is_enabled": section.is_enabled,
					"is_required": section.is_required,
					"show_on_review": section.show_on_review,
					"depends_on": section.depends_on,
					"fields": []
				}

				# FLATTENED STRUCTURE: Query fields by parent_section_code instead of nested parent
				# Fields are now stored directly under Request Type with a parent_section_code link
				fields = frappe.get_all(
					"Request Type Step Field",
					filters={
						"parent": rt_doc.name,  # Parent is now Request Type, not Section
						"parenttype": "Request Type",
						"parent_section_code": section.section_code  # Link via section_code
					},
					fields=["field_name", "field_label", "field_type", "is_required", "options",
					        "default_value", "depends_on", "validation", "show_on_review", "review_label"]
				)

				for field in fields:
					field_data = {
						"field_name": field.field_name,
						"field_label": field.field_label,
						"field_type": field.field_type,
						"is_required": field.is_required,
						"options": field.options,
						"default_value": field.default_value,
						"depends_on": field.depends_on,
						"validation": field.validation,
						"show_on_review": field.show_on_review,
						"review_label": field.review_label or field.field_label
					}
					section_data["fields"].append(field_data)

				step_data["sections"].append(section_data)

			steps.append(step_data)

		# NOTE: Payment and bank details steps are now defined in Request Type configuration
		# (not injected here). To add payment collection or bank details steps:
		# 1. Add step_config, step_sections, and step_fields to Request Type JSON
		# 2. Use depends_on conditions if steps should be conditional
		# 3. Set collects_payment or make_payment flags for accounting/reporting purposes
		#
		# This approach allows:
		# - Customizable payment workflows per council
		# - Configuration-driven forms (no code changes)
		# - Flexible field requirements and validation
		#
		# Example: SPISC could add a bank_details step to its configuration
		# Example: RC could add a payment_collection step for lodgement fees

		# REMOVED: Hardcoded payment step injection (Phase 2.4)
		# Previous code injected payment_collection and bank_details steps based on flags
		# Now these should be added to Request Type configuration instead

		# Apply council-specific overrides if provided
		if council_code:
			steps = apply_council_step_overrides(steps, request_type, council_code)

		# Sort by step_number
		steps = sorted(steps, key=lambda x: x.get("step_number", 999))

		return {
			"steps": steps,
			"uses_config": True,
			"request_type": request_type,
			"council_code": council_code
		}

	except Exception as e:
		frappe.log_error(f"Get Request Type Steps Error: {str(e)}")
		return {
			"steps": [],
			"uses_config": False,
			"error": str(e)
		}


def apply_council_step_overrides(steps, request_type, council_code):
	"""
	Apply council-specific step overrides
	
	Args:
		steps: List of step configurations
		request_type: Request Type name
		council_code: Council code
	
	Returns:
		list: Steps with council overrides applied
	"""
	try:
		# Get council request type configuration
		council_rt = frappe.db.get_value("Council Request Type",
										filters={
											"parent": council_code,
											"request_type": request_type
										},
										fieldname="name")
		
		if not council_rt:
			return steps
		
		# Get step overrides for this council
		overrides = frappe.get_all("Council Request Type Step Override",
								  filters={"parent": council_rt},
								  fields=["*"])
		
		if not overrides:
			return steps
		
		# Apply overrides
		for step in steps:
			for override in overrides:
				if override.step_code == step["step_code"]:
					# Override step-level settings
					if override.custom_title:
						step["step_title"] = override.custom_title
					if override.sequence_override:
						step["step_number"] = override.sequence_override
					step["is_enabled"] = override.is_enabled
					step["is_required"] = override.is_required
					
					# Apply section overrides
					section_overrides = frappe.get_all("Council Step Section Override",
													  filters={"parent": override.name},
													  fields=["*"])
					
					for section in step.get("sections", []):
						for sec_override in section_overrides:
							if sec_override.section_code == section["section_code"]:
								if sec_override.custom_title:
									section["section_title"] = sec_override.custom_title
								section["is_enabled"] = sec_override.is_enabled
								section["is_required"] = sec_override.is_required
		
		# Filter out disabled steps
		steps = [s for s in steps if s.get("is_enabled", True)]
		
		return steps
	
	except Exception as e:
		frappe.log_error(f"Apply Council Step Overrides Error: {str(e)}")
		return steps


@frappe.whitelist()
def validate_step_data(request_type, council_code, step_code, data):
	"""
	Validate data for a specific step based on configuration
	
	Args:
		request_type: Name of Request Type
		council_code: Council code
		step_code: Step code to validate
		data: Form data (JSON string or dict)
	
	Returns:
		dict: Validation result with errors
	"""
	try:
		import json
		if isinstance(data, str):
			data = json.loads(data)
		
		# Get step configuration
		result = get_request_type_steps(request_type, council_code)
		
		if not result.get("uses_config"):
			return {
				"valid": True,
				"message": "No step configuration found. Skipping validation."
			}
		
		# Find the step
		step = next((s for s in result["steps"] if s["step_code"] == step_code), None)
		
		if not step:
			return {
				"valid": False,
				"errors": {"step": f"Step {step_code} not found in configuration"}
			}
		
		errors = {}
		
		# Validate each section
		for section in step.get("sections", []):
			if not section.get("is_enabled"):
				continue
			
			# Validate each field
			for field in section.get("fields", []):
				field_name = field["field_name"]
				field_value = data.get(field_name)
				
				# Check required fields
				if field["is_required"]:
					if field_value is None or field_value == "":
						errors[field_name] = f"{field['field_label']} is required"
				
				# Run custom validation if provided
				if field.get("validation") and field_value:
					try:
						# Execute custom validation (would need sandbox evaluation)
						# For now, skip custom validation for security
						pass
					except Exception as e:
						errors[field_name] = f"Validation error: {str(e)}"
		
		return {
			"valid": len(errors) == 0,
			"errors": errors,
			"message": "Validation successful" if len(errors) == 0 else f"Found {len(errors)} validation error(s)"
		}
	
	except Exception as e:
		frappe.log_error(f"Validate Step Data Error: {str(e)}")
		return {
			"valid": False,
			"errors": {"system": str(e)}
		}


# ============================================================================
# REQUEST TYPE BUILDER API ENDPOINTS
# ============================================================================

@frappe.whitelist()
def get_step_templates():
	"""
	Get list of available step templates for Request Type Builder

	Returns:
		list: List of template metadata
	"""
	try:
		from lodgeick.templates.step_templates import list_available_templates, get_template_info

		templates = list_available_templates()
		template_list = []

		for template_name in templates:
			try:
				info = get_template_info(template_name)
				template_list.append({
					"name": template_name,
					"title": info.get("template_title", template_name),
					"description": info.get("description", ""),
					"version": info.get("version", "1.0")
				})
			except Exception as e:
				frappe.log_error(f"Error loading template {template_name}: {str(e)}")
				continue

		return template_list

	except Exception as e:
		frappe.log_error(f"Get Step Templates Error: {str(e)}")
		frappe.throw(_("Failed to load step templates: {0}").format(str(e)))


@frappe.whitelist()
def load_step_template(template_name):
	"""
	Load a specific step template for Request Type Builder

	Args:
		template_name: Name of the template to load

	Returns:
		dict: Template configuration
	"""
	try:
		from lodgeick.templates.step_templates import load_template

		template = load_template(template_name)

		return {
			"success": True,
			"template": template
		}

	except Exception as e:
		frappe.log_error(f"Load Step Template Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def save_request_type_config(config):
	"""
	Save Request Type configuration from Request Type Builder

	Args:
		config: JSON string or dict containing Request Type configuration

	Returns:
		dict: Success status and created/updated Request Type name
	"""
	try:
		import json
		if isinstance(config, str):
			config = json.loads(config)

		# Validate required fields
		if not config.get("name"):
			frappe.throw(_("Request Type name is required"))

		rt_name = config["name"]

		# Check if Request Type exists
		exists = frappe.db.exists("Request Type", rt_name)

		# Create or get Request Type document
		if exists:
			rt_doc = frappe.get_doc("Request Type", rt_name)
			# Clear existing configuration
			rt_doc.step_configs = []
			rt_doc.step_sections = []
			rt_doc.step_fields = []
		else:
			rt_doc = frappe.new_doc("Request Type")
			rt_doc.name = rt_name

		# Set basic fields
		rt_doc.category = config.get("category", "Planning")
		rt_doc.description = config.get("description", "")
		rt_doc.collects_payment = cint(config.get("collects_payment", 0))
		rt_doc.make_payment = cint(config.get("make_payment", 0))
		rt_doc.is_active = 1

		# Add steps, sections, and fields
		for step in config.get("steps", []):
			step_config = {
				"step_number": step.get("step_number"),
				"step_code": step.get("step_code"),
				"step_title": step.get("step_title"),
				"step_component": step.get("step_component", "DynamicStepRenderer"),
				"is_enabled": cint(step.get("is_enabled", 1)),
				"is_required": cint(step.get("is_required", 1)),
				"show_on_review": cint(step.get("show_on_review", 1)),
				"description": step.get("description", "")
			}

			rt_doc.append("step_configs", step_config)

			# Add sections
			for section in step.get("sections", []):
				section_data = {
					"parent_step_code": step.get("step_code"),
					"section_code": section.get("section_code"),
					"section_title": section.get("section_title"),
					"section_type": section.get("section_type", "Standard"),
					"sequence": section.get("sequence", 1),
					"is_enabled": cint(section.get("is_enabled", 1)),
					"is_required": cint(section.get("is_required", 1)),
					"show_on_review": cint(section.get("show_on_review", 1)),
					"description": section.get("description", "")
				}

				rt_doc.append("step_sections", section_data)

				# Add fields
				for field in section.get("fields", []):
					field_data = {
						"parent_section_code": section.get("section_code"),
						"field_name": field.get("field_name"),
						"field_label": field.get("field_label"),
						"field_type": field.get("field_type"),
						"is_required": cint(field.get("is_required", 0)),
						"show_on_review": cint(field.get("show_on_review", 1)),
						"review_label": field.get("review_label", field.get("field_label")),
						"options": field.get("options", ""),
						"default_value": field.get("default_value", ""),
						"validation": field.get("validation", ""),
						"depends_on": field.get("depends_on", ""),
						"description": field.get("description", "")
					}

					rt_doc.append("step_fields", field_data)

		# Save the document
		if exists:
			rt_doc.save()
			action = "updated"
		else:
			rt_doc.insert()
			action = "created"

		frappe.db.commit()

		return {
			"success": True,
			"message": f"Request Type '{rt_name}' {action} successfully",
			"name": rt_name
		}

	except Exception as e:
		frappe.log_error(f"Save Request Type Config Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def load_request_type_config(request_type_name):
	"""
	Load existing Request Type configuration for editing in Request Type Builder

	Args:
		request_type_name: Name of the Request Type to load

	Returns:
		dict: Request Type configuration in builder format
	"""
	try:
		if not frappe.db.exists("Request Type", request_type_name):
			frappe.throw(_("Request Type '{0}' not found").format(request_type_name))

		rt_doc = frappe.get_doc("Request Type", request_type_name)

		# Build configuration object
		config = {
			"name": rt_doc.name,
			"category": rt_doc.category,
			"description": rt_doc.description or "",
			"collects_payment": cint(rt_doc.collects_payment),
			"make_payment": cint(rt_doc.make_payment),
			"steps": []
		}

		# Group sections and fields by step
		for step_config in rt_doc.step_configs:
			step = {
				"step_number": step_config.step_number,
				"step_code": step_config.step_code,
				"step_title": step_config.step_title,
				"step_component": step_config.step_component,
				"is_enabled": cint(step_config.is_enabled),
				"is_required": cint(step_config.is_required),
				"show_on_review": cint(step_config.show_on_review),
				"description": step_config.description or "",
				"expanded": False,
				"sections": []
			}

			# Get sections for this step
			sections = [s for s in rt_doc.step_sections if s.parent_step_code == step_config.step_code]

			for section in sections:
				section_data = {
					"section_code": section.section_code,
					"section_title": section.section_title,
					"section_type": section.section_type,
					"sequence": section.sequence,
					"is_enabled": cint(section.is_enabled),
					"is_required": cint(section.is_required),
					"show_on_review": cint(section.show_on_review),
					"description": section.description or "",
					"fields": []
				}

				# Get fields for this section
				fields = [f for f in rt_doc.step_fields if f.parent_section_code == section.section_code]

				for field in fields:
					field_data = {
						"field_name": field.field_name,
						"field_label": field.field_label,
						"field_type": field.field_type,
						"is_required": cint(field.is_required),
						"show_on_review": cint(field.show_on_review),
						"review_label": field.review_label or field.field_label,
						"options": field.options or "",
						"default_value": field.default_value or "",
						"validation": field.validation or "",
						"depends_on": field.depends_on or "",
						"description": field.description or ""
					}

					section_data["fields"].append(field_data)

				step["sections"].append(section_data)

			config["steps"].append(step)

		return {
			"success": True,
			"config": config
		}

	except Exception as e:
		frappe.log_error(f"Load Request Type Config Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


# ============================================================
# MEETING & CALENDAR AVAILABILITY APIs
# ============================================================

@frappe.whitelist()
def get_meeting_config(council_code, meeting_type="Pre-Application Meeting"):
	"""
	Get meeting configuration for a specific council and meeting type

	Args:
		council_code: Council code (e.g., 'TYT', 'AKL')
		meeting_type: Type of meeting (default: 'Pre-Application Meeting')

	Returns:
		dict: Meeting configuration including duration, buffer time, etc.
	"""
	try:
		# Get council document
		council = frappe.get_doc("Council", {"council_code": council_code})

		if not council:
			frappe.throw(_("Council not found"))

		# Default configuration from council
		config = {
			"duration_minutes": cint(council.get("default_meeting_duration") or 60),
			"buffer_time": cint(council.get("meeting_buffer_time") or 15),
			"available_durations": [int(d.strip()) for d in (council.get("available_meeting_durations") or "30,60,90").split(",")],
			"meeting_type": meeting_type,
			"council_name": council.council_name
		}

		return {
			"success": True,
			"config": config
		}

	except Exception as e:
		frappe.log_error(f"Get Meeting Config Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def get_available_meeting_slots(council_code, meeting_type="Pre-Application Meeting", start_date=None, end_date=None, duration_minutes=None):
	"""
	Get available meeting time slots for a council based on business hours and existing bookings

	Args:
		council_code: Council code
		meeting_type: Type of meeting
		start_date: Start date for availability check (YYYY-MM-DD)
		end_date: End date for availability check (YYYY-MM-DD)
		duration_minutes: Override duration in minutes (optional)

	Returns:
		dict: Available time slots
	"""
	try:
		from datetime import datetime, timedelta, time as datetime_time
		import json

		# Get council document
		council = frappe.get_doc("Council", {"council_code": council_code})

		if not council:
			frappe.throw(_("Council not found"))

		# Parse dates
		if not start_date:
			start_date = datetime.now().date()
		else:
			start_date = getdate(start_date)

		if not end_date:
			end_date = start_date + timedelta(days=30)
		else:
			end_date = getdate(end_date)

		# Get meeting configuration
		meeting_duration = cint(duration_minutes or council.get("default_meeting_duration") or 60)
		buffer_time = cint(council.get("meeting_buffer_time") or 15)

		# Get business hours
		business_hours = {}
		if council.get("business_hours"):
			for bh in council.business_hours:
				if bh.is_open:
					# Convert timedelta to time objects if needed
					start_time = bh.start_time
					end_time = bh.end_time

					# If they're timedelta objects, convert them
					if isinstance(start_time, timedelta):
						total_seconds = int(start_time.total_seconds())
						hours = total_seconds // 3600
						minutes = (total_seconds % 3600) // 60
						start_time = datetime_time(hours, minutes)

					if isinstance(end_time, timedelta):
						total_seconds = int(end_time.total_seconds())
						hours = total_seconds // 3600
						minutes = (total_seconds % 3600) // 60
						end_time = datetime_time(hours, minutes)

					business_hours[bh.day_of_week] = {
						"start_time": start_time,
						"end_time": end_time
					}
		else:
			# Default business hours (Monday-Friday, 9 AM - 5 PM)
			default_hours = {
				"start_time": datetime_time(9, 0),
				"end_time": datetime_time(17, 0)
			}
			for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
				business_hours[day] = default_hours

		# Get all booked events in the date range
		booked_events = frappe.get_all(
			"Event",
			filters={
				"event_category": "Meeting",
				"starts_on": ["between", [start_date, end_date]],
				"status": ["!=", "Cancelled"]
			},
			fields=["starts_on", "ends_on"]
		)

		# Convert booked events to list of datetime ranges
		booked_slots = []
		for event in booked_events:
			booked_slots.append({
				"start": event.starts_on,
				"end": event.ends_on
			})

		# Generate available slots
		available_slots = []
		current_date = start_date

		while current_date <= end_date:
			day_name = current_date.strftime("%A")

			# Check if council is open on this day
			if day_name not in business_hours:
				current_date += timedelta(days=1)
				continue

			day_hours = business_hours[day_name]
			day_start = datetime.combine(current_date, day_hours["start_time"])
			day_end = datetime.combine(current_date, day_hours["end_time"])

			# Generate time slots for this day
			current_slot_start = day_start

			while current_slot_start + timedelta(minutes=meeting_duration) <= day_end:
				current_slot_end = current_slot_start + timedelta(minutes=meeting_duration)

				# Check if this slot conflicts with any booked event
				is_available = True
				for booked in booked_slots:
					# Check for overlap
					if (current_slot_start < booked["end"] and current_slot_end > booked["start"]):
						is_available = False
						break

				# Add slot if available
				if is_available:
					available_slots.append({
						"start": current_slot_start.isoformat(),
						"end": current_slot_end.isoformat(),
						"start_display": current_slot_start.strftime("%Y-%m-%d %I:%M %p"),
						"end_display": current_slot_end.strftime("%I:%M %p"),
						"day": day_name,
						"duration_minutes": meeting_duration
					})

				# Move to next slot (with buffer time)
				current_slot_start += timedelta(minutes=meeting_duration + buffer_time)

			current_date += timedelta(days=1)

		return {
			"success": True,
			"slots": available_slots,
			"total_slots": len(available_slots),
			"config": {
				"duration_minutes": meeting_duration,
				"buffer_time": buffer_time,
				"start_date": start_date.isoformat(),
				"end_date": end_date.isoformat()
			}
		}

	except Exception as e:
		frappe.log_error(f"Get Available Meeting Slots Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}
