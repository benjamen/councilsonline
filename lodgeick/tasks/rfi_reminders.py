# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_days, date_diff
from lodgeick.emails import send_email


def send_rfi_due_date_reminders():
	"""
	Scheduled task to send reminders for upcoming RFI due dates
	Runs daily to check:
	- RFIs due in 3 days (first reminder)
	- RFIs due in 1 day (final reminder)
	- Overdue RFIs (escalation)
	"""
	today = getdate()

	# Find all pending RFIs
	pending_rfis = frappe.get_all(
		"Request for Information",
		filters={
			"docstatus": 1,  # Submitted
			"response_received": 0,  # Not yet responded
			"due_date": ["is", "set"]
		},
		fields=["name", "request", "due_date", "issued_date", "information_required"]
	)

	for rfi in pending_rfis:
		days_until_due = date_diff(rfi.due_date, today)

		# Send reminder based on days remaining
		if days_until_due == 3:
			send_rfi_reminder(rfi, reminder_type="3_day_reminder")
		elif days_until_due == 1:
			send_rfi_reminder(rfi, reminder_type="final_reminder")
		elif days_until_due < 0:
			# Overdue
			send_rfi_reminder(rfi, reminder_type="overdue", days_overdue=abs(days_until_due))


def send_rfi_reminder(rfi_data, reminder_type="reminder", days_overdue=0):
	"""
	Send RFI reminder email to applicant

	Args:
		rfi_data: Dict containing RFI details
		reminder_type: Type of reminder (3_day_reminder, final_reminder, overdue)
		days_overdue: Number of days overdue (for overdue reminders)
	"""
	try:
		# Get full RFI document
		rfi = frappe.get_doc("Request for Information", rfi_data.name)

		# Get parent request
		request = frappe.get_doc("Request", rfi.request)

		# Determine email subject and urgency
		if reminder_type == "overdue":
			subject = f"URGENT: Overdue Response Required - RFI {rfi.name}"
			urgency = "OVERDUE"
			urgency_message = f"This RFI is now {days_overdue} day(s) overdue. Please respond immediately to avoid delays in processing your application."
		elif reminder_type == "final_reminder":
			subject = f"Final Reminder: RFI Response Due Tomorrow - {rfi.name}"
			urgency = "URGENT"
			urgency_message = "This RFI response is due tomorrow. Please submit your response as soon as possible."
		else:
			subject = f"Reminder: RFI Response Due in 3 Days - {rfi.name}"
			urgency = "REMINDER"
			urgency_message = "This RFI response is due in 3 days. Please prepare your response."

		# Email content
		message = f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<div style="background-color: {'#dc3545' if reminder_type == 'overdue' else '#ffc107'};
						color: {'white' if reminder_type == 'overdue' else '#000'};
						padding: 15px;
						border-radius: 5px 5px 0 0;">
				<h2 style="margin: 0;">⏰ {urgency}: Request for Information</h2>
			</div>

			<div style="padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
				<p>Dear {request.applicant_name or 'Applicant'},</p>

				<p style="font-weight: bold; color: {'#dc3545' if reminder_type == 'overdue' else '#856404'};">
					{urgency_message}
				</p>

				<div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
					<p style="margin: 5px 0;"><strong>Request Number:</strong> {request.name}</p>
					<p style="margin: 5px 0;"><strong>RFI Number:</strong> {rfi.name}</p>
					<p style="margin: 5px 0;"><strong>Issued Date:</strong> {frappe.utils.format_date(rfi.issued_date)}</p>
					<p style="margin: 5px 0;"><strong>Due Date:</strong> {frappe.utils.format_date(rfi.due_date)}</p>
					{f'<p style="margin: 5px 0; color: #dc3545;"><strong>Days Overdue:</strong> {days_overdue}</p>' if days_overdue > 0 else ''}
				</div>

				<h3>Information Required:</h3>
				<div style="background-color: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
					{rfi.information_required}
				</div>

				<div style="margin-top: 20px; padding: 15px; background-color: #e7f3ff; border-radius: 5px;">
					<p style="margin: 0;"><strong>⚠️ Important:</strong></p>
					<p style="margin: 5px 0;">
						The statutory clock for your application is paused while we await your response.
						Delays in responding will extend the processing time for your application.
					</p>
				</div>

				<div style="margin-top: 30px; text-align: center;">
					<a href="{frappe.utils.get_url()}/app/request/{request.name}"
					   style="display: inline-block;
							  padding: 12px 30px;
							  background-color: #007bff;
							  color: white;
							  text-decoration: none;
							  border-radius: 5px;
							  font-weight: bold;">
						Respond to RFI
					</a>
				</div>

				<p style="margin-top: 30px; font-size: 12px; color: #666;">
					If you have any questions or need an extension, please contact us immediately.
				</p>
			</div>
		</div>
		"""

		# Get recipient email
		recipient_email = request.applicant_email or request.requester

		if not recipient_email:
			frappe.log_error(
				f"No email address found for RFI {rfi.name}",
				"RFI Reminder Failed"
			)
			return

		# Send email
		send_email(
			recipients=[recipient_email],
			subject=subject,
			message=message,
			reference_doctype="Request for Information",
			reference_name=rfi.name
		)

		# Log the reminder
		rfi.add_comment(
			"Comment",
			f"{urgency} email sent to {recipient_email}"
		)

		frappe.logger().info(f"RFI reminder sent: {rfi.name} ({reminder_type})")

	except Exception as e:
		frappe.log_error(
			f"Error sending RFI reminder for {rfi_data.name}: {str(e)}",
			"RFI Reminder Error"
		)


def escalate_overdue_rfis():
	"""
	Escalate RFIs that are overdue by more than 7 days
	Sends notification to council manager
	"""
	today = getdate()
	escalation_threshold = add_days(today, -7)

	overdue_rfis = frappe.get_all(
		"Request for Information",
		filters={
			"docstatus": 1,
			"response_received": 0,
			"due_date": ["<", escalation_threshold]
		},
		fields=["name", "request", "due_date", "issued_date"]
	)

	for rfi_data in overdue_rfis:
		try:
			rfi = frappe.get_doc("Request for Information", rfi_data.name)
			request = frappe.get_doc("Request", rfi.request)
			council = frappe.get_doc("Council", request.council)

			days_overdue = abs(date_diff(rfi_data.due_date, today))

			# Send escalation email to council contact
			subject = f"⚠️ ESCALATION: RFI Overdue by {days_overdue} Days - {rfi.name}"

			message = f"""
			<p>Dear Council Manager,</p>

			<p>The following Request for Information has been overdue for {days_overdue} days:</p>

			<ul>
				<li><strong>Request:</strong> {request.name}</li>
				<li><strong>RFI Number:</strong> {rfi.name}</li>
				<li><strong>Applicant:</strong> {request.applicant_name}</li>
				<li><strong>Due Date:</strong> {frappe.utils.format_date(rfi.due_date)}</li>
				<li><strong>Days Overdue:</strong> {days_overdue}</li>
			</ul>

			<p>Please follow up with the applicant or consider appropriate action.</p>

			<p><a href="{frappe.utils.get_url()}/app/request/{request.name}">View Request</a></p>
			"""

			send_email(
				recipients=[council.contact_email],
				subject=subject,
				message=message,
				reference_doctype="Request for Information",
				reference_name=rfi.name
			)

			# Log escalation
			rfi.add_comment("Comment", f"Escalated to council manager (overdue by {days_overdue} days)")

			frappe.logger().info(f"RFI escalated: {rfi.name} ({days_overdue} days overdue)")

		except Exception as e:
			frappe.log_error(
				f"Error escalating RFI {rfi_data.name}: {str(e)}",
				"RFI Escalation Error"
			)
