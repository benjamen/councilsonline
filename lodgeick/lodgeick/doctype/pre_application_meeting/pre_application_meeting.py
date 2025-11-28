# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date


class PreApplicationMeeting(Document):
	def before_insert(self):
		"""Set default values before insert"""
		if not self.requested_by:
			self.requested_by = frappe.session.user

		if not self.requested_date:
			self.requested_date = now_datetime()

	def after_insert(self):
		"""Create linked Event after insert"""
		self.create_event()

	def on_update(self):
		"""Update linked Event when meeting is updated"""
		if self.event and (self.has_value_changed("scheduled_start") or
		                   self.has_value_changed("scheduled_end") or
		                   self.has_value_changed("meeting_location") or
		                   self.has_value_changed("google_meet_link")):
			self.update_event()

	def on_trash(self):
		"""Delete linked Event when meeting is deleted"""
		if self.event:
			try:
				frappe.delete_doc("Event", self.event, ignore_permissions=True)
			except Exception as e:
				frappe.log_error(f"Error deleting linked event: {str(e)}")

	def create_event(self):
		"""Create a linked Frappe Event for calendar integration"""
		try:
			# Get request details
			request_doc = frappe.get_doc("Request", self.request)

			# Create Event
			event = frappe.get_doc({
				"doctype": "Event",
				"subject": f"{self.meeting_type} - {request_doc.request_number}",
				"event_category": "Meeting",
				"event_type": "Public",
				"starts_on": self.scheduled_start or add_to_date(now_datetime(), days=3),
				"ends_on": self.scheduled_end or add_to_date(self.scheduled_start or now_datetime(), hours=1),
				"all_day": 0,
				"description": self.get_event_description(),
				"status": "Open",
				"send_reminder": 1
			})

			# Add participants
			if self.applicant_email:
				event.append("event_participants", {
					"reference_doctype": "Contact",
					"email": self.applicant_email
				})

			if self.council_planner:
				planner = frappe.get_doc("User", self.council_planner)
				event.append("event_participants", {
					"reference_doctype": "User",
					"email": planner.email
				})

			event.insert(ignore_permissions=True)

			# Link event back to this meeting
			self.db_set("event", event.name, update_modified=False)

			frappe.msgprint(f"Calendar event {event.name} created successfully")

		except Exception as e:
			frappe.log_error(f"Error creating event for meeting: {str(e)}", "Meeting Event Creation Error")

	def update_event(self):
		"""Update the linked Frappe Event when meeting details change"""
		if not self.event:
			return

		try:
			event = frappe.get_doc("Event", self.event)

			# Update event fields
			if self.scheduled_start:
				event.starts_on = self.scheduled_start

			if self.scheduled_end:
				event.ends_on = self.scheduled_end

			event.description = self.get_event_description()

			# Update Google Meet link if available
			if self.google_meet_link:
				event.google_meet_link = self.google_meet_link

			event.save(ignore_permissions=True)

		except Exception as e:
			frappe.log_error(f"Error updating event: {str(e)}", "Meeting Event Update Error")

	def get_event_description(self):
		"""Generate event description with meeting details"""
		request_doc = frappe.get_doc("Request", self.request)

		description = f"""
		<h3>{self.meeting_type}</h3>
		<p><strong>Request:</strong> {request_doc.request_number}</p>
		<p><strong>Request Type:</strong> {request_doc.request_type}</p>
		<p><strong>Property:</strong> {request_doc.property_address or 'N/A'}</p>
		<p><strong>Applicant:</strong> {self.applicant_name or 'N/A'}</p>
		"""

		if self.meeting_location:
			description += f"<p><strong>Location:</strong> {self.meeting_location}</p>"

		if self.meeting_room:
			description += f"<p><strong>Room:</strong> {self.meeting_room}</p>"

		if self.google_meet_link:
			description += f'<p><strong>Google Meet:</strong> <a href="{self.google_meet_link}" target="_blank">Join Meeting</a></p>'

		if self.meeting_purpose:
			description += f"<p><strong>Purpose:</strong> {self.meeting_purpose}</p>"

		if self.discussion_points:
			description += f"<div><strong>Discussion Points:</strong><br>{self.discussion_points}</div>"

		return description

	def schedule_meeting(self, scheduled_start, scheduled_end, meeting_location=None,
	                     meeting_format="In Person", meeting_room=None, google_meet_link=None,
	                     council_planner=None):
		"""
		Schedule the meeting with specific details

		Args:
			scheduled_start: Datetime for meeting start
			scheduled_end: Datetime for meeting end
			meeting_location: Physical location
			meeting_format: Format (In Person, Video Call, etc.)
			meeting_room: Room number/name
			google_meet_link: Google Meet URL
			council_planner: User assigned as council planner
		"""
		self.scheduled_start = scheduled_start
		self.scheduled_end = scheduled_end
		self.meeting_location = meeting_location
		self.meeting_format = meeting_format
		self.meeting_room = meeting_room
		self.google_meet_link = google_meet_link
		self.council_planner = council_planner
		self.scheduled_by = frappe.session.user
		self.scheduled_date = now_datetime()
		self.status = "Scheduled"

		self.save(ignore_permissions=True)

		# Send notification to applicant
		self.send_meeting_confirmation()

	def send_meeting_confirmation(self):
		"""Send email confirmation to applicant"""
		if not self.applicant_email:
			return

		try:
			request_doc = frappe.get_doc("Request", self.request)

			# Build meeting details
			meeting_details = f"""
			<p>Dear {self.applicant_name},</p>
			<p>Your {self.meeting_type} for application {request_doc.request_number} has been scheduled.</p>

			<h3>Meeting Details:</h3>
			<ul>
				<li><strong>Date & Time:</strong> {frappe.utils.format_datetime(self.scheduled_start, "dd MMM yyyy, hh:mm a")} - {frappe.utils.format_datetime(self.scheduled_end, "hh:mm a")}</li>
				<li><strong>Format:</strong> {self.meeting_format}</li>
			"""

			if self.meeting_location:
				meeting_details += f"<li><strong>Location:</strong> {self.meeting_location}</li>"

			if self.meeting_room:
				meeting_details += f"<li><strong>Room:</strong> {self.meeting_room}</li>"

			if self.google_meet_link:
				meeting_details += f'<li><strong>Google Meet:</strong> <a href="{self.google_meet_link}">Join Meeting</a></li>'

			if self.council_planner:
				planner = frappe.get_doc("User", self.council_planner)
				meeting_details += f"<li><strong>Council Planner:</strong> {planner.full_name}</li>"

			meeting_details += "</ul>"

			if self.meeting_purpose:
				meeting_details += f"<p><strong>Purpose:</strong> {self.meeting_purpose}</p>"

			meeting_details += f"""
			<p>Please confirm your attendance by replying to this email.</p>
			<p>Best regards,<br>{frappe.db.get_value("Council", self.council, "council_name")}</p>
			"""

			# Send email
			frappe.sendmail(
				recipients=[self.applicant_email],
				subject=f"{self.meeting_type} Scheduled - {request_doc.request_number}",
				message=meeting_details,
				reference_doctype=self.doctype,
				reference_name=self.name
			)

			# Add comment to request
			request_doc.add_comment(
				"Comment",
				f"{self.meeting_type} scheduled for {frappe.utils.format_datetime(self.scheduled_start, 'dd MMM yyyy, hh:mm a')}"
			)

		except Exception as e:
			frappe.log_error(f"Error sending meeting confirmation: {str(e)}", "Meeting Confirmation Error")

	def complete_meeting(self, meeting_notes=None, outcome_summary=None, follow_up_required=False, follow_up_actions=None):
		"""
		Mark meeting as completed with outcome

		Args:
			meeting_notes: Notes from the meeting
			outcome_summary: Summary of meeting outcome
			follow_up_required: Whether follow-up is needed
			follow_up_actions: Description of follow-up actions
		"""
		self.status = "Completed"
		self.meeting_notes = meeting_notes
		self.outcome_summary = outcome_summary
		self.follow_up_required = follow_up_required
		self.follow_up_actions = follow_up_actions

		self.save(ignore_permissions=True)

		# Update linked event status
		if self.event:
			event = frappe.get_doc("Event", self.event)
			event.status = "Closed"
			event.save(ignore_permissions=True)

		# Add comment to request
		request_doc = frappe.get_doc("Request", self.request)
		comment_text = f"{self.meeting_type} completed."
		if outcome_summary:
			comment_text += f" Outcome: {outcome_summary}"

		request_doc.add_comment("Comment", comment_text)


def get_permission_query_conditions(user):
	"""Return permission query conditions for Pre-Application Meeting"""
	if not user:
		user = frappe.session.user

	# System Manager sees all
	if "System Manager" in frappe.get_roles(user):
		return None

	# Users see meetings for their requests or where they are assigned
	return f"""(
		`tabPre-Application Meeting`.requested_by = '{user}'
		OR `tabPre-Application Meeting`.council_planner = '{user}'
		OR `tabPre-Application Meeting`.request IN (
			SELECT name FROM `tabRequest` WHERE owner = '{user}'
		)
	)"""


def has_permission(doc, ptype, user):
	"""Check if user has permission for specific Pre-Application Meeting"""
	if not user:
		user = frappe.session.user

	# System Manager has full access
	if "System Manager" in frappe.get_roles(user):
		return True

	# Owner of the request
	request_doc = frappe.get_doc("Request", doc.request)
	if request_doc.owner == user:
		return True

	# User who requested the meeting
	if doc.requested_by == user:
		return True

	# Assigned council planner
	if doc.council_planner == user:
		return True

	# Consent Planner role
	if "Consent Planner" in frappe.get_roles(user):
		return True

	return False
