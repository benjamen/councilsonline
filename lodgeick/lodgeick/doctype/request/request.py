# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, add_days, getdate, date_diff
from datetime import datetime, timedelta


class Request(Document):
    def autoname(self):
        """Generate request number based on type and year"""
        if not self.request_type:
            frappe.throw("Request Type is required")

        # Get prefix from request type
        request_type_doc = frappe.get_doc("Request Type", self.request_type)
        prefix = request_type_doc.type_code or "REQ"

        # Format: RC-2025-001, BC-2025-001, etc.
        from frappe.model.naming import make_autoname
        self.name = make_autoname(f"{prefix}-.YYYY.-.###")
        self.request_number = self.name

    def validate(self):
        """Validation before saving"""
        # 1. Validate brief description length
        if self.brief_description and len(self.brief_description) > 200:
            frappe.throw("Brief description must be 200 characters or less")

        # 2. Set default status if not set
        if not self.status:
            self.status = "Draft"

        # 3. Set default payment status
        if not self.payment_status:
            self.payment_status = "Pending"

        # 4. Calculate target completion date
        if self.request_type and self.submitted_date and not self.target_completion_date:
            self.calculate_target_completion_date()

        # 5. Calculate working days
        if self.statutory_clock_started:
            self.calculate_working_days()

        # 6. Calculate total fees
        self.calculate_total_fees()

    def before_submit(self):
        """Actions before document is submitted"""
        # Set submitted date
        if not self.submitted_date:
            self.submitted_date = getdate()

        # Set status to Submitted
        self.status = "Submitted"

    def on_submit(self):
        """Actions when document is submitted"""
        # Add to status history
        self.add_status_history("Draft", "Submitted", "Application submitted by applicant")

        # Send acknowledgment email
        self.send_acknowledgment_email()

        # Create timeline entry
        self.add_comment("Label", "Application Submitted")

    def on_update_after_submit(self):
        """Actions after document is updated post-submission"""
        # Track status changes
        if self.has_value_changed("status"):
            old_status = self.get_doc_before_save().status if self.get_doc_before_save() else None
            self.add_status_history(old_status, self.status, "Status updated")

        # If status changed to Acknowledged, start statutory clock
        if self.status == "Acknowledged" and not self.statutory_clock_started:
            self.statutory_clock_started = now()
            self.acknowledged_date = getdate()
            self.calculate_target_completion_date()

    def calculate_target_completion_date(self):
        """Calculate target completion date based on SLA"""
        if not self.request_type or not self.submitted_date:
            return

        # Get SLA from request type
        request_type_doc = frappe.get_doc("Request Type", self.request_type)
        sla_days = request_type_doc.processing_sla_days or 20

        # Calculate target date (adding working days)
        start_date = getdate(self.acknowledged_date or self.submitted_date)
        self.target_completion_date = add_working_days(start_date, sla_days)

    def calculate_working_days(self):
        """Calculate working days elapsed excluding weekends and holidays"""
        if not self.statutory_clock_started:
            return

        end_date = self.statutory_clock_stopped or now()
        self.working_days_elapsed = calculate_working_days_between(
            self.statutory_clock_started,
            end_date
        )

        # Get SLA from request type
        if self.request_type:
            request_type_doc = frappe.get_doc("Request Type", self.request_type)
            sla_days = request_type_doc.processing_sla_days or 20

            self.working_days_remaining = max(0, sla_days - self.working_days_elapsed)
            self.is_overdue = 1 if self.working_days_elapsed > sla_days else 0

    def calculate_total_fees(self):
        """Calculate total fees from fee line items"""
        total = 0
        if self.fees:
            for fee in self.fees:
                total += fee.total or 0

        self.total_fees_excl_gst = total
        self.gst_amount = total * 0.15  # 15% GST
        self.total_fees_incl_gst = total + self.gst_amount

    def add_status_history(self, from_status, to_status, reason=None):
        """Add entry to status history"""
        self.append("status_history", {
            "from_status": from_status,
            "to_status": to_status,
            "changed_by": frappe.session.user,
            "changed_on": now(),
            "reason": reason
        })

    def send_acknowledgment_email(self):
        """Send acknowledgment email to applicant"""
        if not self.applicant_email:
            return

        subject = f"Your application {self.request_number} has been received"
        message = f"""
        <p>Hi {self.applicant_name},</p>

        <p>Thank you for submitting your application for {self.brief_description} at {self.property_address}.</p>

        <p><strong>Application Details:</strong></p>
        <ul>
            <li>Application Number: {self.request_number}</li>
            <li>Submitted: {frappe.format_date(self.submitted_date)}</li>
            <li>Type: {self.request_type}</li>
        </ul>

        <p>We will review your application and notify you once it has been accepted for processing.</p>

        <p>You can track your application status at any time through the portal.</p>

        <p>Kind regards,<br>
        Council Consents Team</p>
        """

        try:
            frappe.sendmail(
                recipients=[self.applicant_email],
                subject=subject,
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name
            )
        except Exception as e:
            frappe.log_error(f"Failed to send acknowledgment email: {str(e)}")


def add_working_days(start_date, days):
    """Add working days to a date (excluding weekends and NZ public holidays)"""
    current_date = getdate(start_date)
    working_days_added = 0

    while working_days_added < days:
        current_date = add_days(current_date, 1)

        # Skip weekends
        if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            continue

        # Skip public holidays
        if is_public_holiday(current_date):
            continue

        working_days_added += 1

    return current_date


def calculate_working_days_between(start_date, end_date):
    """Calculate working days between two dates (excluding weekends and holidays)"""
    start = getdate(start_date)
    end = getdate(end_date)

    if start > end:
        return 0

    working_days = 0
    current_date = start

    while current_date <= end:
        # Skip weekends
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            # Skip public holidays
            if not is_public_holiday(current_date):
                working_days += 1

        current_date = add_days(current_date, 1)

    return working_days


def is_public_holiday(date):
    """Check if a date is a NZ public holiday"""
    # TODO: This should check against a Holiday List doctype
    # For now, return False (no holidays)
    # In production, check Frappe's Holiday List

    from frappe.utils import get_holidays

    try:
        holidays = get_holidays("New Zealand")
        return date in holidays
    except:
        # If Holiday List not found, return False
        return False


@frappe.whitelist()
def get_my_applications(status=None):
    """Get applications for current user"""
    user = frappe.session.user

    filters = {"applicant": user}
    if status:
        filters["status"] = status

    applications = frappe.get_all(
        "Request",
        filters=filters,
        fields=[
            "name", "request_number", "status", "property_address",
            "brief_description", "submitted_date", "target_completion_date",
            "working_days_remaining", "is_overdue", "request_type"
        ],
        order_by="modified desc"
    )

    return applications


@frappe.whitelist()
def submit_application(request_id):
    """Submit an application (move from Draft to Submitted)"""
    doc = frappe.get_doc("Request", request_id)

    # Validate user has permission
    if doc.applicant != frappe.session.user:
        frappe.throw("You don't have permission to submit this application")

    # Check if already submitted
    if doc.docstatus == 1:
        frappe.throw("Application is already submitted")

    # Submit
    doc.submit()

    return {
        "success": True,
        "message": "Application submitted successfully",
        "request_number": doc.request_number
    }


@frappe.whitelist()
def calculate_fees(request_type, building_value=None):
    """Calculate estimated fees for an application"""
    request_type_doc = frappe.get_doc("Request Type", request_type)

    fees = []
    total = 0

    # Base fee
    if request_type_doc.base_fee:
        fees.append({
            "type": "Application Fee",
            "amount": request_type_doc.base_fee
        })
        total += request_type_doc.base_fee

    # Value-based fee
    if request_type_doc.fee_calculation_method == "Value-Based" and building_value:
        building_value = float(building_value)
        fee = building_value * 0.002  # 0.2% example
        fees.append({
            "type": "Processing Fee",
            "amount": fee
        })
        total += fee

    # Deposit
    if request_type_doc.fee_calculation_method == "Deposit":
        deposit = 1500  # Example
        fees.append({
            "type": "Processing Deposit",
            "amount": deposit
        })
        total += deposit

    # Hourly estimate
    if request_type_doc.fee_calculation_method == "Hourly":
        estimated_hours = 10  # Example
        hourly_rate = request_type_doc.hourly_rate or 150
        fee = estimated_hours * hourly_rate
        fees.append({
            "type": "Processing Fee (estimated)",
            "amount": fee
        })
        total += fee

    gst = total * 0.15
    total_incl_gst = total + gst

    return {
        "fees": fees,
        "subtotal": total,
        "gst": gst,
        "total": total_incl_gst
    }
