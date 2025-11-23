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
    company_number=None
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

        # Set default roles based on account type
        if account_type == "ratepayer":
            user.append("roles", {"role": "Applicant"})
        elif account_type == "civilian":
            user.append("roles", {"role": "Applicant"})
        elif account_type == "supplier":
            user.append("roles", {"role": "Applicant"})
            user.append("roles", {"role": "Agent"})

        # Save user
        user.flags.ignore_permissions = True
        user.insert()

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
            "applicant": frappe.session.user,
            "applicant_name": frappe.get_value("User", frappe.session.user, "full_name"),
            "applicant_email": frappe.session.user,
            "applicant_phone": data.get("applicant_phone"),
            "applicant_type": data.get("applicant_type"),
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
