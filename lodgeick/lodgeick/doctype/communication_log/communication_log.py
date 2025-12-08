# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, nowdate


class CommunicationLog(Document):
    def autoname(self):
        """Generate communication number"""
        # Get request short name for better identification
        request = frappe.db.get_value("Request", self.request, "request_number")
        if request:
            # Count existing communications for this request
            count = frappe.db.count("Communication Log", {"request": self.request})
            self.communication_number = f"COMM-{request}-{count + 1:04d}"
            self.name = self.communication_number

    def validate(self):
        """Validation before saving"""
        # Ensure parent Request exists
        if not frappe.db.exists("Request", self.request):
            frappe.throw("Parent Request does not exist")

        # Set sender/recipient based on direction if not set
        if not self.sender:
            if self.direction == "Outgoing":
                self.sender = frappe.db.get_value("User", frappe.session.user, "email")
            else:
                # Get applicant email from request
                self.sender = frappe.db.get_value("Request", self.request, "requester_email")

        if not self.recipient:
            if self.direction == "Incoming":
                self.recipient = frappe.db.get_value("User", frappe.session.user, "email")
            else:
                # Get applicant email from request
                self.recipient = frappe.db.get_value("Request", self.request, "requester_email")

    def after_insert(self):
        """Actions after inserting communication log"""
        # If this is an outgoing email, send it
        if self.communication_type == "Email" and self.direction == "Outgoing" and not self.is_internal:
            self.send_email()

    def send_email(self):
        """Send email communication"""
        if not self.recipient:
            frappe.msgprint("No recipient specified for email", indicator="orange")
            return

        try:
            frappe.sendmail(
                recipients=[self.recipient],
                subject=self.subject,
                message=self.content,
                reference_doctype=self.doctype,
                reference_name=self.name,
                delayed=False
            )

            self.email_status = "Sent"
            self.email_sent_at = now()
            self.db_set("email_status", "Sent", update_modified=False)
            self.db_set("email_sent_at", now(), update_modified=False)

            frappe.msgprint(f"Email sent to {self.recipient}", indicator="green")

        except Exception as e:
            self.email_status = "Failed"
            self.db_set("email_status", "Failed", update_modified=False)
            frappe.log_error(f"Failed to send communication email: {str(e)}")
            frappe.msgprint(f"Failed to send email: {str(e)}", indicator="red")


@frappe.whitelist()
def get_request_communications(request, include_internal=False):
    """Get all communications for a request"""
    filters = {"request": request}
    if not include_internal:
        filters["is_internal"] = 0

    communications = frappe.get_all(
        "Communication Log",
        filters=filters,
        fields=[
            "name",
            "communication_number",
            "communication_type",
            "direction",
            "subject",
            "content",
            "communication_date",
            "sender",
            "recipient",
            "is_internal",
            "requires_response",
            "response_due_date",
            "responded_at"
        ],
        order_by="communication_date desc"
    )
    return communications


@frappe.whitelist()
def create_communication_from_email(request, subject, content, sender_email, direction="Incoming"):
    """Create communication log from email"""
    comm = frappe.get_doc({
        "doctype": "Communication Log",
        "request": request,
        "communication_type": "Email",
        "communication_method": "Automatic",
        "direction": direction,
        "subject": subject,
        "content": content,
        "sender": sender_email if direction == "Incoming" else frappe.session.user,
        "recipient": frappe.session.user if direction == "Incoming" else sender_email,
        "communication_date": now(),
        "email_status": "Delivered"
    })
    comm.insert()

    return {
        "success": True,
        "communication_number": comm.communication_number,
        "name": comm.name
    }


@frappe.whitelist()
def send_notification_to_applicant(request, subject, message, communication_type="Email"):
    """Send a notification to the applicant"""
    request_doc = frappe.get_doc("Request", request)

    comm = frappe.get_doc({
        "doctype": "Communication Log",
        "request": request,
        "communication_type": communication_type,
        "communication_method": "Manual",
        "direction": "Outgoing",
        "subject": subject,
        "content": message,
        "sender": frappe.db.get_value("User", frappe.session.user, "email"),
        "recipient": request_doc.requester_email,
        "communication_date": now()
    })
    comm.insert()

    return {
        "success": True,
        "communication_number": comm.communication_number,
        "name": comm.name
    }


@frappe.whitelist()
def add_internal_note(request, subject, content):
    """Add an internal note to a request"""
    comm = frappe.get_doc({
        "doctype": "Communication Log",
        "request": request,
        "communication_type": "Internal Note",
        "direction": "Outgoing",
        "subject": subject,
        "content": content,
        "sender": frappe.db.get_value("User", frappe.session.user, "full_name"),
        "is_internal": 1,
        "communication_date": now()
    })
    comm.insert()

    return {
        "success": True,
        "communication_number": comm.communication_number,
        "name": comm.name
    }


@frappe.whitelist()
def mark_response_received(communication_name):
    """Mark a communication as responded"""
    comm = frappe.get_doc("Communication Log", communication_name)
    comm.responded_at = now()
    comm.save()

    return {"success": True, "message": "Response recorded"}
