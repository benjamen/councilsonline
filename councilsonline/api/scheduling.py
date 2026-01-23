# Copyright (c) 2026, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Generic Scheduling API - Reusable appointment scheduling for any team/department
"""

import frappe
from frappe import _
from frappe.utils import cint, getdate, now_datetime, get_datetime
from datetime import datetime, timedelta, time as datetime_time
import json


@frappe.whitelist()
def get_team_config(team_code):
	"""
	Get scheduling configuration for a specific team

	Args:
		team_code: Team code (e.g., 'PAYMENTS', 'MEETINGS')

	Returns:
		dict: Team configuration including duration, locations, etc.
	"""
	try:
		team = frappe.get_doc("Council Team", team_code)

		if not team:
			frappe.throw(_("Team not found"))

		if not team.is_active:
			frappe.throw(_("This team is not currently accepting appointments"))

		if not team.enable_scheduling:
			frappe.throw(_("Scheduling is not enabled for this team"))

		# Parse available durations
		available_durations = [int(d.strip()) for d in (team.available_appointment_durations or "30").split(",")]

		config = {
			"team_code": team.team_code,
			"team_name": team.team_name,
			"duration_minutes": cint(team.default_appointment_duration or 30),
			"available_durations": available_durations,
			"buffer_time": cint(team.appointment_buffer_time or 15),
			"advance_booking_days": cint(team.advance_booking_days or 30),
			"min_notice_hours": cint(team.min_notice_hours or 24),
			"max_daily_appointments": cint(team.max_daily_appointments or 20),
			"default_location": team.default_location,
			"locations": team.get_locations_list()
		}

		return {
			"success": True,
			"config": config
		}

	except Exception as e:
		frappe.log_error(f"Get Team Config Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def get_available_slots(team_code, start_date=None, end_date=None, duration_minutes=None, appointment_type=None):
	"""
	Get available appointment time slots for a team based on business hours and existing bookings

	Args:
		team_code: Team code
		start_date: Start date for availability check (YYYY-MM-DD)
		end_date: End date for availability check (YYYY-MM-DD)
		duration_minutes: Override duration in minutes (optional)
		appointment_type: Type of appointment for filtering (optional)

	Returns:
		dict: Available time slots grouped by date
	"""
	try:
		team = frappe.get_doc("Council Team", team_code)

		if not team:
			frappe.throw(_("Team not found"))

		if not team.is_active or not team.enable_scheduling:
			return {
				"success": False,
				"error": "Scheduling is not available for this team"
			}

		# Parse dates with minimum notice
		min_notice = timedelta(hours=cint(team.min_notice_hours or 24))
		earliest_booking = datetime.now() + min_notice

		if not start_date:
			start_date = earliest_booking.date()
		else:
			start_date = getdate(start_date)
			if datetime.combine(start_date, datetime_time(0, 0)) < earliest_booking:
				start_date = earliest_booking.date()

		advance_days = cint(team.advance_booking_days or 30)
		max_date = datetime.now().date() + timedelta(days=advance_days)

		if not end_date:
			end_date = min(start_date + timedelta(days=14), max_date)
		else:
			end_date = getdate(end_date)
			if end_date > max_date:
				end_date = max_date

		# Get configuration
		appointment_duration = cint(duration_minutes or team.default_appointment_duration or 30)
		buffer_time = cint(team.appointment_buffer_time or 15)
		max_daily = cint(team.max_daily_appointments or 20)

		# Get business hours
		business_hours = team.get_business_hours_dict()
		if not business_hours:
			# Default business hours (Monday-Friday, 9 AM - 5 PM)
			default_hours = {
				"start_time": datetime_time(9, 0),
				"end_time": datetime_time(17, 0)
			}
			for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
				business_hours[day] = default_hours

		# Get all booked appointments in the date range
		booked_appointments = frappe.get_all(
			"Scheduled Appointment",
			filters={
				"team": team_code,
				"scheduled_date": ["between", [start_date, end_date]],
				"status": ["in", ["Scheduled", "Confirmed"]]
			},
			fields=["scheduled_start", "scheduled_end", "scheduled_date"]
		)

		# Convert booked appointments to list of datetime ranges
		booked_slots = []
		daily_counts = {}
		for appt in booked_appointments:
			booked_slots.append({
				"start": get_datetime(appt.scheduled_start),
				"end": get_datetime(appt.scheduled_end)
			})
			date_str = str(appt.scheduled_date)
			daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

		# Generate available slots
		available_slots = []
		slots_by_date = {}
		current_date = start_date

		while current_date <= end_date:
			day_name = current_date.strftime("%A")
			date_str = current_date.isoformat()

			# Check if team is open on this day
			if day_name not in business_hours:
				current_date += timedelta(days=1)
				continue

			# Check max daily appointments
			if daily_counts.get(date_str, 0) >= max_daily:
				current_date += timedelta(days=1)
				continue

			day_hours = business_hours[day_name]
			day_start = datetime.combine(current_date, day_hours["start_time"])
			day_end = datetime.combine(current_date, day_hours["end_time"])

			# Skip slots in the past
			if day_start < earliest_booking:
				day_start = earliest_booking
				# Round up to next slot boundary
				minutes = day_start.minute
				if minutes % 15 != 0:
					day_start = day_start.replace(minute=(minutes // 15 + 1) * 15 % 60)
					if (minutes // 15 + 1) * 15 >= 60:
						day_start += timedelta(hours=1)

			day_slots = []
			current_slot_start = day_start

			while current_slot_start + timedelta(minutes=appointment_duration) <= day_end:
				current_slot_end = current_slot_start + timedelta(minutes=appointment_duration)

				# Check if this slot conflicts with any booked appointment
				is_available = True
				for booked in booked_slots:
					# Check for overlap (including buffer)
					buffer_start = booked["start"] - timedelta(minutes=buffer_time)
					buffer_end = booked["end"] + timedelta(minutes=buffer_time)
					if (current_slot_start < buffer_end and current_slot_end > buffer_start):
						is_available = False
						break

				# Add slot if available
				if is_available:
					slot = {
						"start": current_slot_start.isoformat(),
						"end": current_slot_end.isoformat(),
						"start_display": current_slot_start.strftime("%I:%M %p"),
						"end_display": current_slot_end.strftime("%I:%M %p"),
						"date": date_str,
						"day": day_name,
						"duration_minutes": appointment_duration
					}
					available_slots.append(slot)
					day_slots.append(slot)

				# Move to next slot
				current_slot_start += timedelta(minutes=appointment_duration + buffer_time)

			if day_slots:
				slots_by_date[date_str] = {
					"date": date_str,
					"day": day_name,
					"date_display": current_date.strftime("%A, %B %d, %Y"),
					"slots": day_slots
				}

			current_date += timedelta(days=1)

		return {
			"success": True,
			"slots": available_slots,
			"slots_by_date": slots_by_date,
			"total_slots": len(available_slots),
			"config": {
				"team_code": team_code,
				"team_name": team.team_name,
				"duration_minutes": appointment_duration,
				"buffer_time": buffer_time,
				"start_date": start_date.isoformat(),
				"end_date": end_date.isoformat(),
				"locations": team.get_locations_list()
			}
		}

	except Exception as e:
		frappe.log_error(f"Get Available Slots Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def book_appointment(team_code, scheduled_start, scheduled_end, appointment_type,
					 location=None, purpose=None, contact_name=None, contact_email=None,
					 contact_phone=None, reference_doctype=None, reference_name=None,
					 request_id=None, council_code=None):
	"""
	Book an appointment slot

	Args:
		team_code: Team code
		scheduled_start: Start datetime (ISO format)
		scheduled_end: End datetime (ISO format)
		appointment_type: Type of appointment (e.g., "Pickup", "Consultation")
		location: Location for the appointment
		purpose: Purpose/notes for the appointment
		contact_name: Contact name
		contact_email: Contact email
		contact_phone: Contact phone
		reference_doctype: Reference document type (optional)
		reference_name: Reference document name (optional)
		request_id: Associated Request ID (optional)
		council_code: Council code (optional)

	Returns:
		dict: Appointment details
	"""
	try:
		# Verify team exists and scheduling is enabled
		team = frappe.get_doc("Council Team", team_code)

		if not team or not team.is_active or not team.enable_scheduling:
			frappe.throw(_("Scheduling is not available for this team"))

		# Parse datetimes
		start_dt = get_datetime(scheduled_start)
		end_dt = get_datetime(scheduled_end)

		# Validate minimum notice period
		min_notice = timedelta(hours=cint(team.min_notice_hours or 24))
		if start_dt < datetime.now() + min_notice:
			frappe.throw(_("Appointments must be booked at least {0} hours in advance").format(
				team.min_notice_hours or 24
			))

		# Use database lock to prevent race conditions
		# Lock the team row while we check and create the appointment
		frappe.db.sql(
			"SELECT name FROM `tabCouncil Team` WHERE name = %s FOR UPDATE",
			(team_code,)
		)

		# Validate the slot is still available (with overlap check)
		overlapping = frappe.db.sql("""
			SELECT name FROM `tabScheduled Appointment`
			WHERE team = %s
			AND status IN ('Scheduled', 'Confirmed')
			AND (
				(scheduled_start <= %s AND scheduled_end > %s)
				OR (scheduled_start < %s AND scheduled_end >= %s)
				OR (scheduled_start >= %s AND scheduled_end <= %s)
			)
		""", (team_code, scheduled_start, scheduled_start, scheduled_end, scheduled_end,
			  scheduled_start, scheduled_end))

		if overlapping:
			frappe.throw(_("This time slot is no longer available. Please select another slot."))

		# Get council if provided
		council = None
		if council_code:
			council = frappe.db.get_value("Council", {"council_code": council_code}, "name")

		# Create appointment
		appointment = frappe.get_doc({
			"doctype": "Scheduled Appointment",
			"appointment_type": appointment_type,
			"team": team_code,
			"status": "Scheduled",
			"scheduled_start": scheduled_start,
			"scheduled_end": scheduled_end,
			"scheduled_date": start_dt.date(),
			"location": location or team.default_location,
			"purpose": purpose,
			"contact_name": contact_name,
			"contact_email": contact_email,
			"contact_phone": contact_phone,
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"request": request_id,
			"council": council,
			"booked_by": frappe.session.user,
			"booked_at": now_datetime()
		})

		appointment.insert(ignore_permissions=True)

		# Auto-confirm if team has auto_confirm_appointments enabled
		if team.auto_confirm_appointments:
			appointment.status = "Confirmed"
			appointment.confirmed_at = now_datetime()
			appointment.save(ignore_permissions=True)

		frappe.db.commit()

		return {
			"success": True,
			"appointment_id": appointment.name,
			"appointment_type": appointment_type,
			"scheduled_start": appointment.scheduled_start,
			"scheduled_end": appointment.scheduled_end,
			"location": appointment.location,
			"status": appointment.status,
			"message": _("Appointment {0} for {1}").format(
				"confirmed" if team.auto_confirm_appointments else "booked successfully",
				start_dt.strftime("%A, %B %d at %I:%M %p")
			)
		}

	except Exception as e:
		frappe.log_error(f"Book Appointment Error: {str(e)}")
		frappe.throw(_("Failed to book appointment: {0}").format(str(e)))


@frappe.whitelist()
def cancel_appointment(appointment_id, reason=None):
	"""
	Cancel an appointment

	Args:
		appointment_id: Appointment ID
		reason: Cancellation reason

	Returns:
		dict: Cancellation confirmation
	"""
	try:
		appointment = frappe.get_doc("Scheduled Appointment", appointment_id)

		# Verify user can cancel
		if appointment.booked_by != frappe.session.user and "System Manager" not in frappe.get_roles():
			frappe.throw(_("You can only cancel your own appointments"))

		if appointment.status in ["Completed", "Cancelled"]:
			frappe.throw(_("Cannot cancel an appointment that is already {0}").format(appointment.status.lower()))

		appointment.cancel(reason)

		return {
			"success": True,
			"appointment_id": appointment.name,
			"status": appointment.status,
			"message": _("Appointment cancelled successfully")
		}

	except Exception as e:
		frappe.log_error(f"Cancel Appointment Error: {str(e)}")
		frappe.throw(_("Failed to cancel appointment: {0}").format(str(e)))


@frappe.whitelist()
def get_appointment(appointment_id):
	"""
	Get appointment details

	Args:
		appointment_id: Appointment ID

	Returns:
		dict: Appointment details
	"""
	try:
		appointment = frappe.get_doc("Scheduled Appointment", appointment_id)

		# Get team name
		team_name = frappe.db.get_value("Council Team", appointment.team, "team_name")

		return {
			"success": True,
			"appointment": {
				"name": appointment.name,
				"appointment_type": appointment.appointment_type,
				"team": appointment.team,
				"team_name": team_name,
				"status": appointment.status,
				"scheduled_date": appointment.scheduled_date,
				"scheduled_start": appointment.scheduled_start,
				"scheduled_end": appointment.scheduled_end,
				"duration_minutes": appointment.duration_minutes,
				"location": appointment.location,
				"purpose": appointment.purpose,
				"contact_name": appointment.contact_name,
				"contact_email": appointment.contact_email,
				"contact_phone": appointment.contact_phone,
				"reference_doctype": appointment.reference_doctype,
				"reference_name": appointment.reference_name,
				"request": appointment.request,
				"request_number": appointment.request_number,
				"booked_by": appointment.booked_by,
				"booked_at": appointment.booked_at
			}
		}

	except Exception as e:
		frappe.log_error(f"Get Appointment Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def get_user_appointments(team_code=None, status=None, from_date=None, to_date=None):
	"""
	Get appointments for the current user

	Args:
		team_code: Filter by team (optional)
		status: Filter by status (optional)
		from_date: Filter from date (optional)
		to_date: Filter to date (optional)

	Returns:
		list: User's appointments
	"""
	try:
		filters = {
			"booked_by": frappe.session.user
		}

		if team_code:
			filters["team"] = team_code
		if status:
			filters["status"] = status
		if from_date:
			filters["scheduled_date"] = [">=", from_date]
		if to_date:
			if "scheduled_date" in filters:
				filters["scheduled_date"] = ["between", [from_date, to_date]]
			else:
				filters["scheduled_date"] = ["<=", to_date]

		appointments = frappe.get_all(
			"Scheduled Appointment",
			filters=filters,
			fields=[
				"name", "appointment_type", "team", "status",
				"scheduled_date", "scheduled_start", "scheduled_end",
				"location", "request", "request_number"
			],
			order_by="scheduled_start desc"
		)

		# Add team names
		for appt in appointments:
			appt.team_name = frappe.db.get_value("Council Team", appt.team, "team_name")

		return {
			"success": True,
			"appointments": appointments
		}

	except Exception as e:
		frappe.log_error(f"Get User Appointments Error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}
