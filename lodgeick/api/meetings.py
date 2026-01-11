# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Council Meeting Management API - Handles meeting booking, scheduling, rescheduling, and completion
"""

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, add_days, get_datetime, now_datetime, today
from datetime import datetime, timedelta, time as datetime_time
import json


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
    try:
        # Parse JSON if strings
        if isinstance(attendees, str):
            attendees = json.loads(attendees) if attendees else []
        if isinstance(preferred_time_slots, str):
            preferred_time_slots = json.loads(preferred_time_slots) if preferred_time_slots else []

        attendees = attendees or []
        preferred_time_slots = preferred_time_slots or []

        request_doc = None

        # Handle draft/standalone meetings (no request_id yet)
        if request_id and request_id != "draft":
            # Verify the request exists
            if not frappe.db.exists("Request", request_id):
                frappe.throw(_("Request not found"))

            # Get the request document
            request_doc = frappe.get_doc("Request", request_id)

            # Check if a meeting already exists for this request
            existing_meeting = frappe.db.get_value(
                "Council Meeting",
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

        # Create Pre-Application Meeting (single-tenant: no council field needed)
        meeting_doc = frappe.get_doc({
            "doctype": "Council Meeting",
            "request": request_id if (request_id and request_id != "draft") else None,
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
                "doctype": "Project Task",
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
                "assigned_by": frappe.session.user,
                "assigned_to": council_user,
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
        frappe.log_error(str(e), "Meeting Booking Error")
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
        meeting = frappe.get_doc("Council Meeting", meeting_id)

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
                "workflow_state": request_doc.workflow_state
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
            "Council Meeting",
            filters={"request": request_id},
            fields=[
                "name", "meeting_type", "status", "scheduled_start", "scheduled_end",
                "meeting_format", "meeting_location", "council_planner", "requested_date",
                "meeting_purpose", "event", "google_meet_link"
            ],
            order_by="requested_date desc"
        )

        # Enrich with event details and process preferred slots
        for meeting in meetings:
            if meeting.event:
                event = frappe.get_doc("Event", meeting.event)
                meeting.event_status = event.status
                meeting.event_subject = event.subject

            # Fetch preferred time slots from child table
            # Note: preferred_time_slots is a Table field, so we fetch it separately
            meeting.proposed_slots = frappe.get_all(
                "Meeting Preferred Time Slot",
                filters={"parent": meeting.name},
                fields=["preferred_start"],
                order_by="preferred_start asc"
            )
            # Extract just the datetime values
            if meeting.proposed_slots:
                meeting.proposed_slots = [slot.preferred_start for slot in meeting.proposed_slots]

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
        meeting = frappe.get_doc("Council Meeting", meeting_id)

        # Check permissions - only council staff can schedule
        if not (frappe.has_permission("Council Meeting", "write", meeting)
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
        meeting = frappe.get_doc("Council Meeting", meeting_id)

        # Check permissions
        if not (frappe.has_permission("Council Meeting", "write", meeting)
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
        meeting = frappe.get_doc("Council Meeting", meeting_id)

        # Check permissions
        if not (frappe.has_permission("Council Meeting", "write", meeting)
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
        meeting = frappe.get_doc("Council Meeting", meeting_id)

        # Check permissions - only council staff can complete
        if not (frappe.has_permission("Council Meeting", "write", meeting)
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
            "Council Meeting",
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
            meeting_doc = frappe.get_doc("Council Meeting", meeting.name)
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
def get_meeting_config(council_code, meeting_type="Council Meeting"):
	"""
	Get meeting configuration for a specific council and meeting type

	Args:
		council_code: Council code (e.g., 'TYT', 'AKL')
		meeting_type: Type of meeting (default: 'Council Meeting')

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
def get_available_meeting_slots(council_code, meeting_type="Council Meeting", start_date=None, end_date=None, duration_minutes=None):
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
