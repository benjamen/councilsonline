# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, now


class RequestForInformation(Document):
    def autoname(self):
        """Generate RFI number"""
        # Get request short name for better identification
        request = frappe.db.get_value("Request", self.request, "request_number")
        if request:
            # Count existing RFIs for this request
            count = frappe.db.count("Request For Information", {"request": self.request})
            self.rfi_number = f"RFI-{request}-{count + 1:04d}"
            self.name = self.rfi_number

    def validate(self):
        """Validation before saving"""
        # Ensure parent Request exists
        if not frappe.db.exists("Request", self.request):
            frappe.throw("Parent Request does not exist")

        # Due date must be after issued date
        if self.due_date and self.issued_date:
            if self.due_date < self.issued_date:
                frappe.throw("Due date cannot be before issued date")

        # Set default due date if not provided (10 working days)
        if not self.due_date and self.issued_date:
            self.due_date = add_days(self.issued_date, 14)  # 10 working days ≈ 14 calendar days

        # Validate response fields
        if self.response_received:
            if not self.response_date:
                self.response_date = nowdate()
            if not self.responded_by:
                self.responded_by = frappe.session.user

    def before_submit(self):
        """Actions before submitting RFI"""
        if not self.issued_by:
            self.issued_by = frappe.session.user

        if not self.issued_date:
            self.issued_date = nowdate()

    def on_submit(self):
        """Actions when RFI is submitted"""
        # Stop statutory clock if required
        if self.stops_statutory_clock:
            self.stop_statutory_clock()

        # Send notification to applicant
        self.send_rfi_notification()

        # Update parent Request status
        self.update_request_status()

    def on_update_after_submit(self):
        """Actions when RFI is updated after submission"""
        # If response is received, restart statutory clock
        if self.response_received and not self.clock_restarted_date:
            self.restart_statutory_clock()

    def stop_statutory_clock(self):
        """Stop the statutory clock on parent Request"""
        request = frappe.get_doc("Request", self.request)
        if request.status not in ["Closed", "Withdrawn", "Declined"]:
            # Delegate to child DocType
            request.stop_statutory_clock()

            # Update parent status
            request.status = "RFI Issued"
            request.save(ignore_permissions=True)

            self.clock_stopped_date = now()
            frappe.db.set_value(
                "Request For Information",
                self.name,
                "clock_stopped_date",
                self.clock_stopped_date,
                update_modified=False
            )

            frappe.msgprint(
                f"Statutory clock stopped for Request {request.request_number}",
                indicator="orange",
                title="Clock Stopped"
            )

    def restart_statutory_clock(self):
        """Restart the statutory clock on parent Request"""
        request = frappe.get_doc("Request", self.request)
        if request.status == "RFI Issued":
            # Check if there are other outstanding RFIs
            outstanding_rfis = frappe.db.count(
                "Request For Information",
                {
                    "request": self.request,
                    "docstatus": 1,
                    "response_received": 0
                }
            )

            # Only restart if no other outstanding RFIs
            if outstanding_rfis == 0:
                # Delegate to child DocType
                request.restart_statutory_clock()

                # Update parent status
                request.status = "Under Review"
                request.save(ignore_permissions=True)

                self.clock_restarted_date = now()
                frappe.db.set_value(
                    "Request For Information",
                    self.name,
                    "clock_restarted_date",
                    self.clock_restarted_date,
                    update_modified=False
                )

                frappe.msgprint(
                    f"Statutory clock restarted for Request {request.request_number}",
                    indicator="green",
                    title="Clock Restarted"
                )

    def send_rfi_notification(self):
        """Send email notification to applicant"""
        request = frappe.get_doc("Request", self.request)
        if not request.requester_email:
            return

        message = f"""
        <h3>Request for Information Issued</h3>
        <p>Dear {request.requester_name},</p>
        <p>We require additional information to process your application <strong>{request.request_number}</strong>.</p>

        <h4>RFI Details:</h4>
        <ul>
            <li><strong>RFI Number:</strong> {self.rfi_number}</li>
            <li><strong>Subject:</strong> {self.subject}</li>
            <li><strong>Due Date:</strong> {frappe.utils.format_date(self.due_date)}</li>
            <li><strong>Urgency:</strong> {self.urgency}</li>
        </ul>

        <p>{self.description}</p>

        <p>Please provide the requested information by <strong>{frappe.utils.format_date(self.due_date)}</strong>.</p>

        <p>The statutory processing clock has been {"stopped" if self.stops_statutory_clock else "not stopped"} for this RFI.</p>

        <p>You can view and respond to this RFI by logging into the portal.</p>

        <p>Best regards,<br>
        {frappe.db.get_value("User", self.issued_by, "full_name")}</p>
        """

        try:
            frappe.sendmail(
                recipients=[request.requester_email],
                subject=f"RFI Issued for Application {request.request_number}",
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name
            )
        except Exception as e:
            frappe.log_error(f"Failed to send RFI notification: {str(e)}")

    def update_request_status(self):
        """Update parent Request status"""
        request = frappe.get_doc("Request", self.request)
        if request.status not in ["Closed", "Withdrawn", "Declined"]:
            request.status = "RFI Issued"
            request.save(ignore_permissions=True)


@frappe.whitelist()
def get_request_rfis(request):
    """Get all RFIs for a request"""
    rfis = frappe.get_all(
        "Request For Information",
        filters={"request": request},
        fields=[
            "name",
            "rfi_number",
            "subject",
            "issued_date",
            "due_date",
            "urgency",
            "response_received",
            "response_date",
            "stops_statutory_clock"
        ],
        order_by="issued_date desc"
    )
    return rfis


@frappe.whitelist()
def mark_response_received(rfi_name, response_notes=None):
    """Mark RFI response as received"""
    rfi = frappe.get_doc("Request For Information", rfi_name)
    rfi.response_received = 1
    rfi.response_date = nowdate()
    rfi.responded_by = frappe.session.user
    if response_notes:
        rfi.response_notes = response_notes
    rfi.save()

    return {"success": True, "message": "RFI response recorded successfully"}
