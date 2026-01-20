# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Request Management API - Handles request lifecycle including drafts, submission, assignments, and communications
"""

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate
import json
from datetime import datetime
from councilsonline.utils.rate_limit import rate_limit


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

        # AEE Completion Method (fixed - no longer hardcoded)
        "aee_completion_method": data.get("aee_completion_method", "inline"),
        "aee_inline_confirmed": cint(data.get("aee_inline_confirmed", 0)),
        "aee_document_confirmed": cint(data.get("aee_document_confirmed", 0)),
        "aee_alternatives_considered": data.get("aee_alternatives_considered"),
        "aee_monitoring_proposed": data.get("aee_monitoring_proposed"),

        # Consultation Details (Step 5)
        "consultation_undertaken": cint(data.get("consultation_undertaken", 0)),
        "no_consultation_reason": data.get("no_consultation_reason") or (data.get("consultation_summary") if data.get("consultation_undertaken") == "No" else None),

        # Soil Investigation Fields (Step 3)
        "soil_investigation_completed": cint(data.get("soil_investigation_completed", 0)),
        "soil_investigation_summary": data.get("soil_investigation_summary"),
        "soil_investigation_document": data.get("soil_investigation_document"),
        "no_nes_confirmed": cint(data.get("no_nes_confirmed", 0)),

        # Inundation Advice (Step 2)
        "inundation_advice_document": data.get("inundation_advice_document"),

        # Permitted Boundary Activity Fields (Step 4)
        "pba_approval_required": cint(data.get("pba_approval_required", 0)),
        "pba_status": data.get("pba_status"),
        "pba_details": data.get("pba_details"),
        "pba_documents": data.get("pba_documents"),
        "boundary_description": data.get("boundary_description"),
        "boundary_activity_description": data.get("boundary_activity_description"),
        "boundary_owner_approval_obtained": cint(data.get("boundary_owner_approval_obtained", 0)),
        "boundary_approval_date": getdate(data.get("boundary_approval_date")) if data.get("boundary_approval_date") else None,
        "boundary_approval_document": data.get("boundary_approval_document"),

        # Confidential Information (Step 1)
        "confidential_information_claimed": cint(data.get("confidential_information_claimed", 0)),
        "confidential_information_reason": data.get("confidential_information_reason"),

        # Lodgement Fees (Step 9)
        "lodgement_fees_paid": cint(data.get("lodgement_fees_paid", 0)),

        # Signature Fields (Step 9)
        "requester_signature_last_name": data.get("applicant_signature_last_name") or data.get("requester_signature_last_name"),
        "agent_signature_first_name": data.get("agent_signature_first_name"),
        "agent_signature_last_name": data.get("agent_signature_last_name"),
        "agent_signature_date": getdate(data.get("agent_signature_date")) if data.get("agent_signature_date") else None,

        # Natural Hazards confirmation
        "no_natural_hazards_confirmed": cint(data.get("no_natural_hazards_confirmed", 0)),

        # Default to applicant as correspondence recipient
        "correspondence_recipient": "Applicant",
        "invoice_responsible_party": "Applicant"
    })

    # Add natural_hazards child table (Step 2)
    if data.get("natural_hazards"):
        for hazard in data.get("natural_hazards", []):
            rc_app.append("natural_hazards", {
                "hazard_type": hazard.get("hazard_type"),
                "present": cint(hazard.get("present", 0)),
                "risk_level": hazard.get("risk_level"),
                "assessment_notes": hazard.get("assessment_notes"),
                "mitigation_required": cint(hazard.get("mitigation_required", 0))
            })

    # Add HAIL activities child table (Step 3)
    if data.get("hail_activities"):
        for activity in data.get("hail_activities", []):
            rc_app.append("hail_activities", {
                "activity_description": activity.get("activity_description"),
                "hail_category": activity.get("hail_category"),
                "currently_undertaken": cint(activity.get("currently_undertaken", 0)),
                "previously_undertaken": cint(activity.get("previously_undertaken", 0)),
                "likely_undertaken": cint(activity.get("likely_undertaken", 0)),
                "preliminary_investigation_done": cint(activity.get("preliminary_investigation_done", 0)),
                "proposed_fuel_storage": activity.get("proposed_fuel_storage"),
                "proposed_effluent": activity.get("proposed_effluent"),
                "proposed_waste_disposal": activity.get("proposed_waste_disposal"),
                "investigation_completed": cint(activity.get("investigation_completed", 0)),
                "investigation_summary": activity.get("investigation_summary")
            })

    # Add application_documents child table (Step 6)
    if data.get("application_documents"):
        for doc in data.get("application_documents", []):
            rc_app.append("application_documents", {
                "document_type": doc.get("document_type"),
                "document_name": doc.get("document_name"),
                "document_file": doc.get("document_file")
            })

    # Add consulted_organizations child table (Step 5)
    if data.get("consulted_organizations"):
        for org in data.get("consulted_organizations", []):
            rc_app.append("consulted_organizations", {
                "organization_name": org.get("organization_name"),
                "contact_name": org.get("contact_name"),
                "email": org.get("email"),
                "phone": org.get("phone"),
                "consultation_date": getdate(org.get("consultation_date")) if org.get("consultation_date") else None,
                "consultation_method": org.get("consultation_method"),
                "key_issues_raised": org.get("key_issues_raised")
            })

    # Add additional_consents child table (Step 1)
    if data.get("additional_consents"):
        for consent in data.get("additional_consents", []):
            rc_app.append("additional_consents", {
                "consent_type": consent.get("consent_type"),
                "consent_status": consent.get("consent_status"),
                "reference_number": consent.get("reference_number")
            })

    # Add pba_contacts child table (Step 4)
    if data.get("pba_contacts"):
        for contact in data.get("pba_contacts", []):
            rc_app.append("pba_contacts", {
                "neighbor_name": contact.get("neighbor_name"),
                "neighbor_address": contact.get("neighbor_address"),
                "neighbor_email": contact.get("neighbor_email"),
                "approval_obtained": cint(contact.get("approval_obtained", 0)),
                "approval_date": getdate(contact.get("approval_date")) if contact.get("approval_date") else None,
                "approval_document": contact.get("approval_document")
            })

    # Add lodgement_payments child table (Step 9)
    if data.get("lodgement_payments"):
        for payment in data.get("lodgement_payments", []):
            rc_app.append("lodgement_payments", {
                "payment_method": payment.get("payment_method"),
                "payment_reference": payment.get("payment_reference"),
                "payment_amount": flt(payment.get("payment_amount")),
                "payment_date": getdate(payment.get("payment_date")) if payment.get("payment_date") else None
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


def update_rc_application(request_name, data):
    """
    Update existing Resource Consent Application with new data

    Args:
        request_name: Name of the parent Request (which is also the RC Application name)
        data: Form data dictionary with updated values

    Returns:
        Updated Resource Consent Application document
    """
    from frappe.utils import cint, flt, getdate

    try:
        rc_app = frappe.get_doc("Resource Consent Application", request_name)

        # Update single-value fields
        single_fields = [
            # Activity Status
            ("activity_status", None),
            ("aee_activity_status", None),
            ("aee_activity_description", None),

            # Agent
            ("agent_required", "cint"),

            # Site Information
            ("site_topography", None),
            ("existing_vegetation_description", None),
            ("natural_hazards_identified", None),
            ("existing_infrastructure", None),

            # AEE Fields
            ("assessment_of_effects", None),
            ("aee_positive_effects", None),
            ("physical_effects", None),
            ("effects_on_people", None),
            ("mitigation_proposed", None),
            ("alternatives_considered", None),
            ("planning_assessment", None),
            ("aee_completion_method", None),
            ("aee_inline_confirmed", "cint"),
            ("aee_document_confirmed", "cint"),
            ("aee_alternatives_considered", None),
            ("aee_monitoring_proposed", None),

            # Consultation
            ("iwi_consultation_undertaken", "cint"),
            ("consultation_undertaken", "cint"),
            ("consultation_summary", None),
            ("no_consultation_reason", None),
            ("written_approvals_obtained", "cint"),

            # Conditions
            ("proposed_conditions", None),

            # Declarations
            ("declaration_rma_compliance", "cint"),
            ("declaration_authorized", "cint"),
            ("declaration_public_information", "cint"),

            # Signatures
            ("applicant_signature_first_name", None),
            ("requester_signature_last_name", None),
            ("applicant_signature_date", "date"),
            ("agent_signature_first_name", None),
            ("agent_signature_last_name", None),
            ("agent_signature_date", "date"),

            # Property Info
            ("aee_site_area", "flt"),
            ("aee_zoning", None),
            ("aee_overlays", None),

            # Consent Term
            ("consent_term_requested", None),

            # Soil Investigation
            ("soil_investigation_completed", "cint"),
            ("soil_investigation_summary", None),
            ("soil_investigation_document", None),
            ("no_nes_confirmed", "cint"),

            # Inundation
            ("inundation_advice_document", None),

            # PBA Fields
            ("pba_approval_required", "cint"),
            ("pba_status", None),
            ("pba_details", None),
            ("pba_documents", None),
            ("boundary_description", None),
            ("boundary_activity_description", None),
            ("boundary_owner_approval_obtained", "cint"),
            ("boundary_approval_date", "date"),
            ("boundary_approval_document", None),

            # Confidential Information
            ("confidential_information_claimed", "cint"),
            ("confidential_information_reason", None),

            # Lodgement
            ("lodgement_fees_paid", "cint"),

            # Natural Hazards confirmation
            ("no_natural_hazards_confirmed", "cint"),
        ]

        for field_name, field_type in single_fields:
            if field_name in data:
                value = data.get(field_name)
                if field_type == "cint":
                    value = cint(value)
                elif field_type == "flt":
                    value = flt(value)
                elif field_type == "date" and value:
                    value = getdate(value)
                setattr(rc_app, field_name, value)

        # Update child tables (clear and re-add)
        child_table_mappings = {
            "consent_types": ["consent_type"],
            "natural_hazards": ["hazard_type", "present", "risk_level", "assessment_notes", "mitigation_required"],
            "hail_activities": ["activity_description", "hail_category", "currently_undertaken", "previously_undertaken",
                               "likely_undertaken", "preliminary_investigation_done", "proposed_fuel_storage",
                               "proposed_effluent", "proposed_waste_disposal", "investigation_completed", "investigation_summary"],
            "application_documents": ["document_type", "document_name", "document_file"],
            "consulted_organizations": ["organization_name", "contact_name", "email", "phone",
                                        "consultation_date", "consultation_method", "key_issues_raised"],
            "additional_consents": ["consent_type", "consent_status", "reference_number"],
            "pba_contacts": ["neighbor_name", "neighbor_address", "neighbor_email",
                            "approval_obtained", "approval_date", "approval_document"],
            "lodgement_payments": ["payment_method", "payment_reference", "payment_amount", "payment_date"],
        }

        for table_name, fields in child_table_mappings.items():
            if table_name in data and data.get(table_name) is not None:
                # Clear existing rows
                rc_app.set(table_name, [])
                # Add new rows
                for item in data.get(table_name, []):
                    row_data = {}
                    for field in fields:
                        if field in item:
                            value = item.get(field)
                            # Convert date fields
                            if "date" in field.lower() and value:
                                value = getdate(value)
                            # Convert check fields
                            elif field in ["present", "mitigation_required", "currently_undertaken", "previously_undertaken",
                                          "likely_undertaken", "preliminary_investigation_done", "investigation_completed",
                                          "approval_obtained"]:
                                value = cint(value)
                            # Convert amount fields
                            elif field == "payment_amount":
                                value = flt(value)
                            row_data[field] = value
                    rc_app.append(table_name, row_data)

        rc_app.flags.ignore_permissions = True
        rc_app.flags.ignore_mandatory = True
        rc_app.save()

        return rc_app

    except frappe.DoesNotExistError:
        # RC Application doesn't exist yet, create it
        return create_rc_application(request_name, data)
    except Exception as e:
        frappe.log_error(f"Failed to update RC Application {request_name}: {str(e)}", "Update RC Application Error")
        raise


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
        spisc_app.flags.ignore_permissions = True
        spisc_app.flags.ignore_validate = True
        spisc_app.save()
        return spisc_app

    # Handle address_line - it might be a string or a nested object from PhilippineAddressInput
    address_line_value = data.get("address_line")
    if isinstance(address_line_value, dict):
        # Extract individual components from nested object
        address_line_str = address_line_value.get("address_line", "")
        barangay = address_line_value.get("barangay", "")
        municipality = address_line_value.get("municipality", "Taytay")
        province = address_line_value.get("province", "Rizal")
    else:
        # Use top-level values
        address_line_str = address_line_value or ""
        barangay = data.get("barangay", "")
        municipality = data.get("municipality", "Taytay")
        province = data.get("province", "Rizal")

    # Get request document to access virtual properties
    request_doc = frappe.get_doc("Request", request_name)

    # Calculate age from birth_date if not provided
    age_value = data.get("age")
    if not age_value and data.get("birth_date"):
        from datetime import datetime
        birth_date = data.get("birth_date")
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.today()
        age_value = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    spisc_app = frappe.get_doc({
        "doctype": "SPISC Application",
        "request": request_name,

        # Manually populate fields (removed invalid fetch_from)
        "applicant_name": request_doc.requester_name,  # Virtual @property from Request
        "applicant_email": request_doc.requester_email,  # Virtual @property from Request
        "applicant_phone": request_doc.requester_phone,  # Direct field from Request
        "applicant_age_display": str(age_value) if age_value else "",
        "age": age_value,

        # Personal Information (domain-specific fields only)
        "birth_date": data.get("birth_date"),
        "sex": data.get("sex"),
        "civil_status": data.get("civil_status"),

        # Address Information
        "address_line": address_line_str,
        "barangay": barangay,
        "municipality": municipality,
        "province": province,

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
        "signature_date": data.get("signature_date"),

        # Payment Information
        "payment_method": data.get("payment_method"),
        "bank_name": data.get("bank_name"),
        "bank_account_number": data.get("bank_account_number"),
        "pickup_location": data.get("pickup_location")
    })

    spisc_app.flags.ignore_permissions = True
    spisc_app.flags.ignore_mandatory = True
    spisc_app.insert(ignore_mandatory=True, ignore_permissions=True)

    # Create or update User Bank Account if payment method is Bank Deposit
    if data.get("payment_method") == "Bank Deposit":
        if data.get("bank_name") and data.get("bank_account_number"):
            from councilsonline.utils.bank_account_helper import create_or_update_user_bank_account

            account_holder_name = data.get("account_holder_name") or data.get("full_name")
            create_or_update_user_bank_account(
                user=frappe.session.user,
                bank_name=data.get("bank_name"),
                account_number=data.get("bank_account_number"),
                account_holder_name=account_holder_name,
                is_default=1
            )

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

    # Address Information - handle nested address object from PhilippineAddressInput
    address_line_value = data.get("address_line")
    if address_line_value:
        if isinstance(address_line_value, dict):
            # Extract from nested object
            spisc_app.address_line = address_line_value.get("address_line", "")
            if address_line_value.get("barangay"):
                spisc_app.barangay = address_line_value.get("barangay")
            if address_line_value.get("municipality"):
                spisc_app.municipality = address_line_value.get("municipality")
            if address_line_value.get("province"):
                spisc_app.province = address_line_value.get("province")
        else:
            # Use as string directly
            spisc_app.address_line = address_line_value

    # Update from top-level fields if present
    if data.get("barangay") and not isinstance(address_line_value, dict):
        spisc_app.barangay = data.get("barangay")
    if data.get("municipality") and not isinstance(address_line_value, dict):
        spisc_app.municipality = data.get("municipality")
    if data.get("province") and not isinstance(address_line_value, dict):
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

    # Payment Information
    if data.get("payment_method"):
        spisc_app.payment_method = data.get("payment_method")
    if data.get("bank_name"):
        spisc_app.bank_name = data.get("bank_name")
    if data.get("bank_account_number"):
        spisc_app.bank_account_number = data.get("bank_account_number")
    if data.get("pickup_location"):
        spisc_app.pickup_location = data.get("pickup_location")

    # Create or update User Bank Account if payment method is Bank Deposit
    if data.get("payment_method") == "Bank Deposit":
        if data.get("bank_name") and data.get("bank_account_number"):
            from councilsonline.utils.bank_account_helper import create_or_update_user_bank_account

            account_holder_name = data.get("account_holder_name") or data.get("full_name")
            create_or_update_user_bank_account(
                user=frappe.session.user,
                bank_name=data.get("bank_name"),
                account_number=data.get("bank_account_number"),
                account_holder_name=account_holder_name,
                is_default=1
            )


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(calls=10, period=60, guest_only=True)  # 10 drafts per minute for guests, unlimited for authenticated users
def create_draft_request(data=None, current_step=None, total_steps=None):
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
        # Ensure this is a POST request
        if frappe.request.method != "POST":
            frappe.throw("This endpoint only accepts POST requests. Please use the form to create a draft request.", frappe.PermissionError)

        # Log incoming request for debugging
        frappe.logger().info(f"create_draft_request called - data type: {type(data)}, current_step: {current_step}")
        frappe.logger().info(f"create_draft_request - data value: {data}")
        frappe.logger().info(f"create_draft_request - frappe.form_dict: {frappe.form_dict}")

        # Validate required data parameter
        if not data:
            # Log the full request to understand what's being sent
            frappe.log_error(
                f"Empty data received. Form dict: {frappe.form_dict}",
                "create_draft_request - Empty Data"
            )
            frappe.throw("Request data is required. Please ensure all form fields are filled and try again.")

        # Parse data if it's a JSON string
        if isinstance(data, str):
            import json
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                frappe.log_error(
                    f"JSON decode error: {str(e)}. Data received: {data[:500]}",
                    "create_draft_request - JSON Parse Error"
                )
                frappe.throw("Invalid data format. Please refresh the page and try again.")

        # Check if data is essentially empty (e.g., only has metadata fields)
        # This can happen when File objects fail to serialize
        metadata_fields = {'current_step', 'total_steps', 'request_id', 'name'}
        actual_data_fields = set(data.keys()) - metadata_fields

        if len(actual_data_fields) == 0 and not data.get("request_id"):
            frappe.log_error(
                f"No actual data fields found. Data keys: {list(data.keys())}",
                "create_draft_request - Empty Data Fields"
            )
            frappe.throw(
                "No form data received. This may be due to file upload in progress. Please wait for uploads to complete before proceeding.",
                title="Upload in Progress"
            )

        # Extract draft metadata
        current_step = current_step or data.pop("current_step", 1)
        total_steps = total_steps or data.pop("total_steps", None)

        # Check if this is an update to an existing draft
        existing_draft_id = data.get("request_id") or data.get("name")

        if existing_draft_id and frappe.db.exists("Request", existing_draft_id):
            # Update existing draft
            frappe.logger().info(f"Updating existing draft: {existing_draft_id}")
            return update_draft_request(existing_draft_id, data, current_step, total_steps)

        # Before creating new draft, check for recent duplicates
        # This is a safety net in case frontend state is lost
        request_type = data.get("request_type")
        if frappe.session.user != "Guest":
            recent_draft = frappe.db.get_value(
                "Request",
                filters={
                    "requester": frappe.session.user,
                    "request_type": request_type or "",
                    "workflow_state": "Draft",
                    "creation": [">", frappe.utils.add_to_date(frappe.utils.now(), minutes=-5)]
                },
                fieldname="name"
            )

            if recent_draft:
                frappe.log_error(
                    f"Potential duplicate draft detected. Updating existing: {recent_draft}",
                    "Duplicate Draft Prevention"
                )
                # Update existing instead of creating new
                return update_draft_request(recent_draft, data, current_step, total_steps)

        frappe.logger().info(f"Creating new draft for user: {frappe.session.user}")

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
        # Get the last draft number for this year - using parameterized query to prevent SQL injection
        last_draft = frappe.db.sql("""
            SELECT request_number
            FROM `tabRequest`
            WHERE request_number LIKE %(pattern)s
            ORDER BY creation DESC
            LIMIT 1
        """, {"pattern": f"DRAFT-{year}-%"}, as_dict=True)

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
            "requester": frappe.session.user,  # The user who created it (may be agent)
            "requester_name": applicant_name,  # The actual applicant (client or self)
            "requester_email": applicant_email,  # The actual applicant email
            "requester_phone": data.get("requester_phone"),
            "requester_type": data.get("requester_type"),
            "acting_on_behalf": acting_on_behalf,  # Track if agent workflow
            "workflow_state": "Draft",
            "priority": data.get("priority", "Standard"),

            # Owner Details (when applicant is not the owner)
            "applicant_is_not_owner": cint(data.get("applicant_is_not_owner", 0)),
            "owner_name": data.get("owner_name"),
            "owner_email": data.get("owner_email"),
            "owner_phone": data.get("owner_phone"),
            "owner_address": data.get("owner_address"),

            # Invoice Fields
            "invoice_to": data.get("invoice_to"),
            "invoice_name": data.get("invoice_name"),
            "invoice_email": data.get("invoice_email"),
            "invoice_address": data.get("invoice_address"),
            "purchase_order_number": data.get("purchase_order_number"),

            # Delivery & Deposit Fields
            "delivery_preference": data.get("delivery_preference"),
            "transfer_deposit_required": cint(data.get("transfer_deposit_required", 0)),
            "transfer_deposit_consent_number": data.get("transfer_deposit_consent_number"),

            # Certificate of Title
            "certificate_of_title_document": data.get("certificate_of_title_document"),

            # Draft metadata - store in draft_full_data JSON
            "draft_full_data": full_data_json
        })

        # Add additional fields based on request type
        if data.get("building_value"):
            request_doc.building_value = data.get("building_value")

        # Save as draft (docstatus = 0)
        # Ignore mandatory field validation for drafts
        # Allow guest users to create draft requests
        request_doc.flags.ignore_permissions = True
        request_doc.flags.ignore_mandatory = True
        request_doc.flags.ignore_validate = True
        request_doc.insert(ignore_mandatory=True, ignore_permissions=True)

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

        # Save draft step information for resume functionality
        if current_step is not None:
            request_doc.db_set("draft_current_step", current_step, update_modified=False)
        if total_steps is not None:
            request_doc.db_set("draft_total_steps", total_steps, update_modified=False)

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

    Args:
        request_id: ID of the draft request to update
        data: Dictionary containing updated request data
        current_step: Current step in the form (1-indexed)
        total_steps: Total number of steps in the form

    Returns:
        dict: Updated request details
    """
    try:
        # Parse data if it's a JSON string
        if isinstance(data, str):
            import json
            data = json.loads(data)

        # Extract draft metadata
        current_step = current_step or data.pop("current_step", None)
        total_steps = total_steps or data.pop("total_steps", None)

        # Get the request document
        request_doc = frappe.get_doc("Request", request_id)

        # Validate user has permission to update (allow Guest for draft requests)
        if request_doc.requester != frappe.session.user and frappe.session.user != "Guest":
            frappe.throw(_("You don't have permission to update this request"))

        # Check if it's still a draft
        if request_doc.docstatus != 0:
            frappe.throw(_("Only draft requests can be updated"))

        # Serialize full form data to JSON
        import json
        full_data_json = json.dumps(data, default=str)

        # Computed properties that cannot be set directly (read-only)
        computed_properties = [
            "name", "creation", "modified", "owner",
            "requester_name", "requester_email", "requester_phone",  # Computed from User
            "computed_total_fees_excl_gst", "computed_gst_amount", "total_fees_incl_gst",  # Computed fees
        ]

        # Update fields
        for key, value in data.items():
            if hasattr(request_doc, key) and key not in computed_properties:
                try:
                    setattr(request_doc, key, value)
                except AttributeError:
                    # Skip properties without setters
                    pass

        # Update draft metadata - only store in draft_full_data JSON
        request_doc.draft_full_data = full_data_json

        # Check if application already exists and update it (prevent duplicates)
        if request_doc.application_doctype and request_doc.application_name:
            # Update existing application
            if request_doc.application_doctype == "SPISC Application":
                app_doc = frappe.get_doc("SPISC Application", request_doc.application_name)
                update_spisc_application(app_doc, data)
                app_doc.flags.ignore_mandatory = True
                app_doc.flags.ignore_permissions = True
                app_doc.flags.ignore_validate = True
                app_doc.save()
            elif request_doc.application_doctype == "Resource Consent Application":
                # Update Resource Consent Application with all field mappings
                update_rc_application(request_doc.application_name, data)
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

        # Save draft step information for resume functionality
        if current_step is not None:
            request_doc.db_set("draft_current_step", current_step, update_modified=False)
        if total_steps is not None:
            request_doc.db_set("draft_total_steps", total_steps, update_modified=False)

        request_doc.flags.ignore_mandatory = True
        request_doc.flags.ignore_permissions = True
        request_doc.flags.ignore_validate = True
        request_doc.flags.ignore_links = True
        request_doc.save()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Draft request updated successfully"),
            "request_id": request_doc.name,
            "request_number": request_doc.request_number
        }

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
            "workflow_state": request_doc.workflow_state
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
            "assigned_to": [assigned_to],
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
def get_request_type_config(request_type_code=None):
    """
    Get detailed configuration for a specific request type including steps and fields

    Args:
        request_type_code: The type_code or name of the Request Type

    Returns:
        dict: Complete request type configuration with steps, fields, and metadata
    """
    try:
        # Validate required parameter
        if not request_type_code:
            frappe.throw("Request type code is required")

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

        # Get council email (single-tenant)
        council_doc = frappe.get_single("Council")
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
                "doctype": "Project Task",
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
                "assigned_by": frappe.session.user,
                "assigned_to": assignee,
                "request": request_id
            })
            task_doc.insert(ignore_permissions=True)

            frappe.logger().info(f"Created Project Task {task_doc.name} for message on {request_id}")

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

        # Add workflow_state filter if provided (status parameter maps to workflow_state)
        if status:
            filters["workflow_state"] = status

        requests = frappe.get_all(
            "Request",
            filters=filters,
            fields=[
                "name", "request_number", "request_type", "workflow_state",
                "requester",  # Get requester user ID, computed fields fetched separately
                "brief_description", "creation", "modified"
            ],
            order_by="modified desc"
        )

        # Add computed fields for each request
        for req in requests:
            if req.get("requester"):
                user_info = frappe.db.get_value(
                    "User", req["requester"],
                    ["full_name", "email", "phone"], as_dict=True
                )
                if user_info:
                    req["requester_name"] = user_info.get("full_name")
                    req["requester_email"] = user_info.get("email")
                    req["requester_phone"] = user_info.get("phone")

        return requests

    except Exception as e:
        frappe.log_error(f"Get User Requests Error: {str(e)}", "Request API Error")
        frappe.throw(_("Failed to get user requests: {0}").format(str(e)))


@frappe.whitelist()
def get_request_summary_data(request_id):
    """
    Universal API to get summary data for any request type
    Used by the universal action bar and summary dashboard

    Args:
        request_id: Request ID

    Returns:
        dict: Summary metrics including tasks, meetings, communications, assessment status, and request type
    """
    try:
        # Get request details
        request_doc = frappe.get_doc("Request", request_id)
        request_type = request_doc.request_type

        # Get tasks count (all tasks)
        tasks_count = frappe.db.count("Project Task", {
            "request": request_id
        })

        # Get open tasks count
        open_tasks_count = frappe.db.count("Project Task", {
            "request": request_id,
            "status": ["in", ["Open", "In Progress", "Working"]]
        })

        # Get council meetings count
        meetings_count = frappe.db.count("Council Meeting", {
            "request": request_id
        })

        # Get communications count
        communications_count = frappe.db.count("Communication Log", {
            "request": request_id
        })

        # Get assessment project status if exists
        assessment_project = frappe.db.get_value("Assessment Project",
            {"request": request_id},
            ["name", "overall_status", "current_stage", "project_owner"],
            as_dict=True
        )

        if assessment_project:
            assessment_status = assessment_project.overall_status or "Not Started"
            current_stage = assessment_project.current_stage or "Not Started"
            assessment_project_name = assessment_project.name
            assessment_owner = assessment_project.project_owner
        else:
            assessment_status = "Not Created"
            current_stage = "N/A"
            assessment_project_name = None
            assessment_owner = None

        # Get application-specific data based on request type
        application_data = {}
        if request_type == "Social Pension for Indigent Senior Citizens (SPISC)":
            spisc_app = frappe.get_all("SPISC Application",
                filters={"request": request_id},
                fields=["eligibility_status", "age", "monthly_income"],
                limit=1
            )
            if spisc_app:
                application_data = {
                    "eligibility_status": spisc_app[0].eligibility_status or "Pending",
                    "age": spisc_app[0].age,
                    "monthly_income": spisc_app[0].monthly_income
                }

        elif request_type == "Resource Consent":
            rc_app = frappe.get_all("Resource Consent Application",
                filters={"request": request_id},
                fields=["statutory_clock_status", "days_elapsed", "notification_decision"],
                limit=1
            )
            if rc_app:
                application_data = {
                    "statutory_clock_status": rc_app[0].statutory_clock_status or "Running",
                    "days_elapsed": rc_app[0].days_elapsed or 0,
                    "notification_decision": rc_app[0].notification_decision
                }

        return {
            "success": True,
            "request_type": request_type,
            "tasks_count": tasks_count,
            "open_tasks_count": open_tasks_count,
            "meetings_count": meetings_count,
            "communications_count": communications_count,
            "assessment_status": assessment_status,
            "current_stage": current_stage,
            "assessment_project_name": assessment_project_name,
            "assessment_owner": assessment_owner,
            "requester_name": request_doc.requester_name,
            "workflow_state": request_doc.workflow_state,
            **application_data
        }

    except Exception as e:
        frappe.log_error(f"Get Request Summary Error: {str(e)}", "Request API Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def send_request_notification(request_id, subject, message, channel="Email"):
    """
    Send notification to requester for a request

    Args:
        request_id: Request ID
        subject: Notification subject
        message: Notification message
        channel: Communication channel (Email, SMS, Both)

    Returns:
        dict: Success status
    """
    try:
        request_doc = frappe.get_doc("Request", request_id)

        # Create Communication Log
        comm_log = frappe.get_doc({
            "doctype": "Communication Log",
            "request": request_id,
            "communication_type": "Outgoing",
            "subject": subject,
            "message": message,
            "channel": channel,
            "sent_by": frappe.session.user,
            "sent_to": request_doc.requester_email,
            "status": "Sent"
        })
        comm_log.insert(ignore_permissions=True)

        # Send email if channel includes Email
        if channel in ["Email", "Both"]:
            if request_doc.requester_email:
                frappe.sendmail(
                    recipients=[request_doc.requester_email],
                    subject=subject,
                    message=message,
                    reference_doctype="Request",
                    reference_name=request_id
                )

        # Send SMS if channel includes SMS
        if channel in ["SMS", "Both"]:
            # Get requester's mobile number from User document
            requester_mobile = frappe.db.get_value("User", request_doc.requester, "mobile_no")

            if requester_mobile:
                try:
                    # Use Frappe's built-in SMS functionality if configured
                    # Falls back gracefully if SMS settings are not configured
                    from frappe.core.doctype.sms_settings.sms_settings import send_sms

                    # Format message for SMS (remove HTML tags if any)
                    sms_text = frappe.utils.strip_html_tags(message)
                    # Limit SMS to 160 characters
                    if len(sms_text) > 160:
                        sms_text = sms_text[:157] + "..."

                    send_sms(
                        receiver_list=[requester_mobile],
                        msg=sms_text,
                        sender_name="CouncilsOnline"
                    )

                    # Update communication log status
                    comm_log.db_set("sms_status", "Sent")

                except Exception as sms_error:
                    # Log SMS error but don't fail the entire notification
                    frappe.log_error(
                        f"SMS sending failed for {requester_mobile}: {str(sms_error)}",
                        "SMS Notification Error"
                    )
                    comm_log.db_set("sms_status", "Failed")
                    comm_log.db_set("sms_error", str(sms_error))
            else:
                # No mobile number available
                frappe.log_error(
                    f"No mobile number found for user {request_doc.requester}",
                    "SMS Notification Error"
                )
                comm_log.db_set("sms_status", "No Mobile Number")

        frappe.db.commit()

        return {
            "success": True,
            "message": "Notification sent successfully"
        }

    except Exception as e:
        frappe.log_error(f"Send Notification Error: {str(e)}", "Request API Error")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def add_internal_note(request_id, note, visibility="Internal Only"):
    """
    Add internal note to request

    Args:
        request_id: Request ID
        note: Note content
        visibility: Note visibility (Internal Only, Share with Team)

    Returns:
        dict: Success status
    """
    try:
        # Create Communication Log for internal note
        comm_log = frappe.get_doc({
            "doctype": "Communication Log",
            "request": request_id,
            "communication_type": "Internal Note",
            "subject": f"Internal Note - {frappe.utils.now()}",
            "message": note,
            "channel": "Internal",
            "sent_by": frappe.session.user,
            "visibility": visibility,
            "status": "Logged"
        })
        comm_log.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": "Internal note added successfully"
        }

    except Exception as e:
        frappe.log_error(f"Add Internal Note Error: {str(e)}", "Request API Error")
        return {
            "success": False,
            "error": str(e)
        }
