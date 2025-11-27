# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint


@frappe.whitelist(allow_guest=True)
def register_user(
    email,
    first_name,
    last_name,
    phone,
    password,
    account_type="ratepayer",
    property_address=None,
    company_name=None,
    company_number=None,
    council_code=None
):
    """
    Register a new user for Lodgeick

    Args:
        email: User's email address
        first_name: First name
        last_name: Last name
        phone: Phone number
        password: Password
        account_type: Type of account (ratepayer, civilian, supplier)
        property_address: Property address (for ratepayers)
        company_name: Company name (for suppliers)
        company_number: Company registration number (for suppliers)
        council_code: Council code for default council (optional)

    Returns:
        dict: Success message and user info
    """

    # Validate required fields
    if not email or not first_name or not last_name or not password:
        frappe.throw(_("Email, first name, last name, and password are required"))

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

        # Set account type and default roles
        if account_type == "ratepayer":
            user.account_type = "Applicant"
            user.applicant_type = "Individual"
            user.append("roles", {"role": "Applicant"})
        elif account_type == "civilian":
            user.account_type = "Applicant"
            user.applicant_type = "Individual"
            user.append("roles", {"role": "Applicant"})
        elif account_type == "supplier":
            user.account_type = "Agent"
            user.applicant_type = "Company"
            user.append("roles", {"role": "Applicant"})
            user.append("roles", {"role": "Agent"})

        # Save user
        user.flags.ignore_permissions = True
        user.insert()

        # Set default council if provided
        if council_code:
            # Validate council exists and is active
            council = frappe.db.get_value(
                "Council",
                {"council_code": council_code, "is_active": 1},
                ["name", "council_name"],
                as_dict=True
            )
            if council:
                user.default_council = council.name
                user.save(ignore_permissions=True)

        # Create additional profile information if needed
        # You might want to create a custom doctype for extended user profile
        if property_address:
            # Store in user bio or custom field
            user.bio = f"Property: {property_address}"
            user.save(ignore_permissions=True)

        if company_name:
            # Create organization record
            org = frappe.get_doc({
                "doctype": "Organization",
                "organization_name": company_name,
                "organization_type": "Supplier",
                "contact_email": email,
                "contact_phone": phone,
                "company_number": company_number
            })
            org.flags.ignore_permissions = True
            org.insert()

            # Link user to organization (you might need to add a custom field)
            user.organization = org.name
            user.save(ignore_permissions=True)

        frappe.db.commit()

        return {
            "success": True,
            "message": _("User registered successfully. Please check your email to verify your account."),
            "user": email
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"User Registration Error: {str(e)}")
        frappe.throw(_("Registration failed. Please try again or contact support."))


@frappe.whitelist()
def create_draft_request(data):
    """
    Create a draft request that can be saved without submission

    Args:
        data: Dictionary containing request data

    Returns:
        dict: Created request details
    """
    try:
        # Parse data if it's a JSON string
        if isinstance(data, str):
            import json
            data = json.loads(data)

        # Get request type to determine category
        request_type = data.get("request_type")
        if not request_type:
            frappe.throw(_("Request Type is required"))

        # Get category from request type
        request_type_doc = frappe.get_doc("Request Type", request_type)
        category = request_type_doc.category or "Service Request"

        # If property_address is provided but no property link, create a property record
        property_link = data.get("property")
        if not property_link and data.get("property_address"):
            # Create a new property record
            property_doc = frappe.get_doc({
                "doctype": "Property",
                "street_address": data.get("property_address"),
                "legal_description": data.get("legal_description"),
                "zoning": data.get("zone")
            })
            property_doc.insert(ignore_permissions=True)
            property_link = property_doc.name

        # Determine applicant details based on whether acting on behalf
        acting_on_behalf = data.get("acting_on_behalf", False)

        if acting_on_behalf:
            # Agent workflow - use client details provided in the form
            applicant_name = data.get("applicant_name")
            applicant_email = data.get("applicant_email")
        else:
            # Self-application - use current user's details
            applicant_name = data.get("applicant_name") or frappe.get_value("User", frappe.session.user, "full_name")
            applicant_email = data.get("applicant_email") or frappe.session.user

        # Create request document
        request_doc = frappe.get_doc({
            "doctype": "Request",
            "request_type": request_type,
            "request_category": category,
            "brief_description": data.get("brief_description"),
            "detailed_description": data.get("detailed_description"),
            "property": property_link,  # Link to Property DocType
            "property_address": data.get("property_address"),
            "legal_description": data.get("legal_description"),
            "council": data.get("council"),  # Add council field
            "applicant": frappe.session.user,  # The user who created it (may be agent)
            "applicant_name": applicant_name,  # The actual applicant (client or self)
            "applicant_email": applicant_email,  # The actual applicant email
            "applicant_phone": data.get("applicant_phone"),
            "applicant_type": data.get("applicant_type"),
            "acting_on_behalf": acting_on_behalf,  # Track if agent workflow
            "status": "Draft",
            "priority": data.get("priority", "Standard")
        })

        # Add additional fields based on request type
        if data.get("building_value"):
            request_doc.building_value = data.get("building_value")

        # Save as draft (docstatus = 0)
        # Ignore mandatory field validation for drafts
        request_doc.flags.ignore_permissions = False
        request_doc.flags.ignore_mandatory = True
        request_doc.insert(ignore_mandatory=True)

        # If Resource Consent, create Resource Consent Application child document
        if category == "Resource Consent":
            rc_app = frappe.get_doc({
                "doctype": "Resource Consent Application",
                "request": request_doc.name,
                "consent_types": data.get("consent_types"),
                "activity_status": data.get("activity_status"),

                # Proposal Details
                "building_height": data.get("building_height"),
                "building_floor_area": data.get("building_floor_area"),
                "earthworks_volume": data.get("earthworks_volume"),
                "earthworks_vertical_alteration": data.get("earthworks_vertical_alteration"),
                "vehicle_movements_daily": data.get("vehicle_movements_daily"),
                "parking_spaces_provided": data.get("parking_spaces_provided"),
                "hours_of_operation": data.get("hours_of_operation"),
                "consent_term_requested": data.get("consent_term_requested"),

                # Site & Environment
                "site_topography": data.get("site_topography"),
                "existing_vegetation_description": data.get("existing_vegetation_description"),
                "watercourses_present": cint(data.get("watercourses_present")),
                "watercourse_description": data.get("watercourse_description"),
                "natural_hazards_identified": data.get("natural_hazards_identified"),
                "existing_infrastructure": data.get("existing_infrastructure"),
                "contamination_status_hail": data.get("contamination_status_hail"),

                # Assessment of Environmental Effects
                "assessment_of_effects": data.get("assessment_of_effects"),
                "effects_on_people": data.get("effects_on_people"),
                "physical_effects": data.get("physical_effects"),
                "earthworks_effects": data.get("earthworks_effects"),
                "discharge_contaminants_effects": data.get("discharge_contaminants_effects"),
                "ecosystem_effects": data.get("ecosystem_effects"),
                "hazard_risk_assessment": data.get("hazard_risk_assessment"),
                "cultural_effects": data.get("cultural_effects"),

                # Planning and Other
                "planning_assessment": data.get("planning_assessment"),
                "alternatives_considered": data.get("alternatives_considered"),
                "mitigation_proposed": data.get("mitigation_proposed"),
                "iwi_consultation_undertaken": cint(data.get("iwi_consultation_undertaken")),
                "iwi_consulted": data.get("iwi_consulted"),
                "proposed_conditions": data.get("proposed_conditions")
            })

            # Add affected parties (child table)
            if data.get("affected_parties"):
                for party in data.get("affected_parties"):
                    rc_app.append("affected_parties", {
                        "party_name": party.get("party_name"),
                        "address": party.get("address"),
                        "written_approval_obtained": cint(party.get("written_approval_obtained", 0))
                    })

            # Add specialist reports (child table)
            if data.get("specialist_reports"):
                for report in data.get("specialist_reports"):
                    rc_app.append("specialist_reports", {
                        "report_type": report.get("report_type"),
                        "specialist_name": report.get("specialist_name"),
                        "date_prepared": report.get("date_prepared")
                    })

            rc_app.flags.ignore_permissions = False
            rc_app.flags.ignore_mandatory = True
            rc_app.insert(ignore_mandatory=True)

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
def update_draft_request(request_id, data):
    """
    Update an existing draft request

    Args:
        request_id: ID of the request to update
        data: Dictionary containing updated request data

    Returns:
        dict: Success message
    """
    try:
        # Parse data if it's a JSON string
        if isinstance(data, str):
            import json
            data = json.loads(data)

        # Get the request document
        request_doc = frappe.get_doc("Request", request_id)

        # Validate user has permission to update
        if request_doc.applicant != frappe.session.user:
            frappe.throw(_("You don't have permission to update this request"))

        # Check if it's still a draft
        if request_doc.docstatus != 0:
            frappe.throw(_("Only draft requests can be updated"))

        # Update fields
        for key, value in data.items():
            if hasattr(request_doc, key) and key not in ["name", "creation", "modified", "owner"]:
                setattr(request_doc, key, value)

        request_doc.save()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Draft request updated successfully")
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Update Draft Request Error: {str(e)}")
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
def book_council_meeting(request_id, meeting_type="Pre-Application Meeting"):
    """
    Book a council meeting for a request and create a task for the council team

    Args:
        request_id: The Request document ID
        meeting_type: Type of meeting (default: Pre-Application Meeting)

    Returns:
        dict: Success message with task details
    """
    try:
        # Verify the request exists
        if not frappe.db.exists("Request", request_id):
            frappe.throw(_("Request not found"))

        # Get the request document
        request_doc = frappe.get_doc("Request", request_id)

        # Get a valid council staff user (Administrator or first system user)
        council_user = frappe.session.user
        if council_user == "Guest":
            # Fallback to Administrator if current user is Guest
            council_user = "Administrator"

        # Create a WB Task for the council team
        task_doc = frappe.get_doc({
            "doctype": "WB Task",
            "title": f"{meeting_type} - {request_doc.request_number}",
            "description": f"""
                <p><strong>Meeting Type:</strong> {meeting_type}</p>
                <p><strong>Request Number:</strong> {request_doc.request_number}</p>
                <p><strong>Request Type:</strong> {request_doc.request_type}</p>
                <p><strong>Applicant:</strong> {request_doc.applicant_name or 'N/A'}</p>
                <p><strong>Property:</strong> {request_doc.property_address or 'N/A'}</p>
                <p><strong>Brief Description:</strong> {request_doc.brief_description or 'N/A'}</p>
                <br>
                <p>The applicant has requested a {meeting_type.lower()}. Please contact them within 2 business days to schedule.</p>
            """,
            "status": "Open",
            "priority": "High",
            "task_type": "Manual",
            "due_date": frappe.utils.add_days(frappe.utils.today(), 2),
            "assign_from": council_user,
            "assign_to": council_user,
            "request": request_id
        })

        task_doc.insert(ignore_permissions=True)

        # Add a comment to the request about the meeting booking
        request_doc.add_comment(
            "Comment",
            f"{meeting_type} booking requested. Task {task_doc.name} created for council team."
        )

        frappe.db.commit()

        return {
            "success": True,
            "task_id": task_doc.name,
            "task_title": task_doc.title,
            "message": f"{meeting_type} booking request created successfully"
        }

    except Exception as e:
        frappe.log_error(f"Book Council Meeting Error: {str(e)}", "Meeting Booking Error")
        frappe.throw(_("Failed to book meeting: {0}").format(str(e)))


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
        order_by="council_name"
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


@frappe.whitelist()
def get_user_councils(user=None):
    """
    Get councils associated with current user

    Args:
        user: User email (optional, defaults to current user)

    Returns:
        dict: User's default council and associated councils
    """
    user = user or frappe.session.user

    # Get default council
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
                    "requires_property": request_type_doc.requires_property if hasattr(request_type_doc, 'requires_property') else True,
                    "requires_payment": request_type_doc.requires_payment if hasattr(request_type_doc, 'requires_payment') else True
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

    frappe.db.set_value("User", user, "default_council", council_code)
    frappe.db.commit()

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


# ============================================================================
# USER PROFILE & SETTINGS API ENDPOINTS
# ============================================================================

@frappe.whitelist()
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
        "applicant_type": user_doc.get("applicant_type") or "Individual",
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


@frappe.whitelist()
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


@frappe.whitelist()
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
                "request_type_name": request_type.request_type_name,
                "category": request_type.category,
                "description": council_rt.brief_description or request_type.description,
                "base_fee": council_rt.base_fee_override or request_type.base_fee,
                "sla_days": council_rt.sla_days_override or request_type.sla_days,
                "process_description": council_rt.process_description or "",
                "is_active": request_type.is_active,
                "requires_property": request_type.requires_property,
                "requires_payment": request_type.requires_payment,
                "council_specific": {
                    "brief_description": council_rt.brief_description,
                    "process_description": council_rt.process_description,
                    "base_fee_override": council_rt.base_fee_override,
                    "sla_days_override": council_rt.sla_days_override
                }
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
