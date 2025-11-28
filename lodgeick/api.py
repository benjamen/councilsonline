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
def book_council_meeting(request_id, meeting_type="Pre-Application Meeting", meeting_purpose=None):
    """
    Book a council meeting for a request and create a Pre-Application Meeting record with Event

    Args:
        request_id: The Request document ID
        meeting_type: Type of meeting (default: Pre-Application Meeting)
        meeting_purpose: Purpose/reason for the meeting

    Returns:
        dict: Success message with meeting details
    """
    try:
        # Verify the request exists
        if not frappe.db.exists("Request", request_id):
            frappe.throw(_("Request not found"))

        # Get the request document
        request_doc = frappe.get_doc("Request", request_id)

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

        # Create Pre-Application Meeting
        meeting_doc = frappe.get_doc({
            "doctype": "Pre-Application Meeting",
            "request": request_id,
            "meeting_type": meeting_type,
            "status": "Requested",
            "meeting_purpose": meeting_purpose or f"Discuss {request_doc.request_type} application",
            "requested_by": frappe.session.user,
            "requested_date": frappe.utils.now_datetime()
        })

        meeting_doc.insert(ignore_permissions=True)

        # Add a comment to the request about the meeting booking
        request_doc.add_comment(
            "Comment",
            f"{meeting_type} requested. Meeting record {meeting_doc.name} created. A council planner will contact you within 2 business days to schedule."
        )

        # Create a notification task for council team (optional - using WB Task)
        try:
            council_user = "Administrator"  # Or get from council configuration
            task_doc = frappe.get_doc({
                "doctype": "WB Task",
                "title": f"Schedule {meeting_type} - {request_doc.request_number}",
                "description": f"""
                    <p><strong>Meeting Request:</strong> {meeting_doc.name}</p>
                    <p><strong>Request Number:</strong> {request_doc.request_number}</p>
                    <p><strong>Request Type:</strong> {request_doc.request_type}</p>
                    <p><strong>Applicant:</strong> {request_doc.applicant_name or 'N/A'} ({request_doc.applicant_email})</p>
                    <p><strong>Property:</strong> {request_doc.property_address or 'N/A'}</p>
                    <p><strong>Purpose:</strong> {meeting_purpose or 'N/A'}</p>
                    <br>
                    <p>Please schedule this meeting with the applicant within 2 business days.</p>
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
                "applicant_name": meeting.applicant_name,
                "applicant_email": meeting.applicant_email,
                "applicant_phone": meeting.applicant_phone,
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
        if meeting.applicant_email:
            request_doc = frappe.get_doc("Request", meeting.request)
            frappe.sendmail(
                recipients=[meeting.applicant_email],
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
        if meeting.applicant_email:
            request_doc = frappe.get_doc("Request", meeting.request)
            frappe.sendmail(
                recipients=[meeting.applicant_email],
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
                "meeting_format", "meeting_location", "applicant_name", "council_planner",
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


@frappe.whitelist()
def get_user_company_account():
	"""
	Get company account details for current user
	Returns company info + user's role in company

	Returns:
		dict: Company account details or None
	"""
	user = frappe.get_doc("User", frappe.session.user)

	if not user.company_account:
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
		user.company_account = None
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
