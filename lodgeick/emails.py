"""
Asynchronous Email Sending Module
Background jobs for sending emails to prevent blocking request processing
"""

import frappe
from frappe.utils import get_url


def send_email(recipients, subject, message, reference_doctype=None, reference_name=None, attachments=None, now=True):
	"""Generic email sending function

	Args:
		recipients: List of email addresses
		subject: Email subject
		message: Email message (HTML)
		reference_doctype: Optional DocType for reference
		reference_name: Optional document name for reference
		attachments: Optional list of attachments
		now: Send immediately (default True)
	"""
	try:
		frappe.sendmail(
			recipients=recipients,
			subject=subject,
			message=message,
			reference_doctype=reference_doctype,
			reference_name=reference_name,
			attachments=attachments,
			now=now
		)

		frappe.logger().info(f"Email sent: {subject} to {', '.join(recipients)}")

	except Exception as e:
		frappe.log_error(f"Failed to send email '{subject}': {str(e)}", "Email Error")
		# Don't raise - email failure shouldn't break the workflow


def send_acknowledgment(request, recipient):
	"""Send acknowledgment email in background

	Args:
		request: Request document name
		recipient: Email address of recipient
	"""
	try:
		request_doc = frappe.get_doc("Request", request)

		# Build email content
		subject = f"Acknowledgment: {request_doc.request_number}"

		message = f"""
		<p>Dear {request_doc.requester_name},</p>

		<p>Thank you for submitting your application.</p>

		<p><strong>Request Number:</strong> {request_doc.request_number}</p>
		<p><strong>Request Type:</strong> {request_doc.request_type}</p>
		<p><strong>Council:</strong> {request_doc.council}</p>
		<p><strong>Target Completion:</strong> {request_doc.target_completion_date}</p>

		<p>You can track the progress of your application at:</p>
		<p><a href="{get_url()}/app/request/{request_doc.name}">View Application</a></p>

		<p>Best regards,<br>{request_doc.council}</p>
		"""

		frappe.sendmail(
			recipients=[recipient],
			subject=subject,
			message=message,
			now=True
		)

		frappe.logger().info(f"Acknowledgment email sent for {request}")

	except Exception as e:
		frappe.log_error(f"Failed to send acknowledgment for {request}: {str(e)}", "Email Error")
		# Don't raise - email failure shouldn't break the workflow


def send_rfi_notification(rfi, recipient):
	"""Send RFI notification email in background

	Args:
		rfi: Request For Information document name
		recipient: Email address of applicant
	"""
	try:
		rfi_doc = frappe.get_doc("Request For Information", rfi)
		request_doc = frappe.get_doc("Request", rfi_doc.request)

		subject = f"Information Required: {rfi_doc.name}"

		message = f"""
		<p>Dear {request_doc.requester_name},</p>

		<p>We require additional information for your application:</p>

		<p><strong>Request Number:</strong> {request_doc.request_number}</p>
		<p><strong>RFI Number:</strong> {rfi_doc.name}</p>
		<p><strong>Due Date:</strong> {rfi_doc.due_date}</p>

		<p><strong>Information Required:</strong></p>
		<div>{rfi_doc.information_required}</div>

		<p>Please respond by {rfi_doc.due_date} to avoid delays in processing.</p>

		<p><a href="{get_url()}/app/request/{request_doc.name}">View Application & Respond</a></p>

		<p>Best regards,<br>{request_doc.council}</p>
		"""

		frappe.sendmail(
			recipients=[recipient],
			subject=subject,
			message=message,
			now=True
		)

		frappe.logger().info(f"RFI notification sent for {rfi}")

	except Exception as e:
		frappe.log_error(f"Failed to send RFI notification for {rfi}: {str(e)}", "Email Error")


def send_status_change_notification(request, old_status, new_status, recipient):
	"""Send status change notification email in background

	Args:
		request: Request document name
		old_status: Previous status
		new_status: Current status
		recipient: Email address of applicant
	"""
	try:
		request_doc = frappe.get_doc("Request", request)

		subject = f"Status Update: {request_doc.request_number} - {new_status}"

		message = f"""
		<p>Dear {request_doc.requester_name},</p>

		<p>The status of your application has been updated:</p>

		<p><strong>Request Number:</strong> {request_doc.request_number}</p>
		<p><strong>Previous Status:</strong> {old_status}</p>
		<p><strong>Current Status:</strong> {new_status}</p>

		<p><a href="{get_url()}/app/request/{request_doc.name}">View Application Details</a></p>

		<p>Best regards,<br>{request_doc.council}</p>
		"""

		frappe.sendmail(
			recipients=[recipient],
			subject=subject,
			message=message,
			now=True
		)

		frappe.logger().info(f"Status change email sent for {request}: {old_status} -> {new_status}")

	except Exception as e:
		frappe.log_error(f"Failed to send status change notification for {request}: {str(e)}", "Email Error")


def send_payment_confirmation(payment, recipient):
	"""Send payment confirmation email in background

	Args:
		payment: Payment document name
		recipient: Email address of payer
	"""
	try:
		payment_doc = frappe.get_doc("Payment", payment)
		request_doc = frappe.get_doc("Request", payment_doc.request)

		subject = f"Payment Confirmation: {payment_doc.payment_number}"

		message = f"""
		<p>Dear {request_doc.requester_name},</p>

		<p>We have received your payment:</p>

		<p><strong>Payment Number:</strong> {payment_doc.payment_number}</p>
		<p><strong>Request Number:</strong> {request_doc.request_number}</p>
		<p><strong>Amount:</strong> ${payment_doc.total_amount:.2f}</p>
		<p><strong>Payment Date:</strong> {payment_doc.payment_date}</p>

		<p>Thank you for your payment.</p>

		<p><a href="{get_url()}/app/request/{request_doc.name}">View Application</a></p>

		<p>Best regards,<br>{request_doc.council}</p>
		"""

		frappe.sendmail(
			recipients=[recipient],
			subject=subject,
			message=message,
			now=True
		)

		frappe.logger().info(f"Payment confirmation sent for {payment}")

	except Exception as e:
		frappe.log_error(f"Failed to send payment confirmation for {payment}: {str(e)}", "Email Error")
