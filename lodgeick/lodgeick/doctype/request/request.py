# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, add_days, getdate


class Request(Document):
    def autoname(self):
        """Generate request number based on type and year"""
        # For draft requests without request_type, use generic DRAFT prefix
        if not self.request_type:
            from frappe.model.naming import make_autoname
            self.name = make_autoname("DRAFT-.YYYY.-.#####")
            self.request_number = self.name
            return

        # Get prefix from request type
        request_type_doc = frappe.get_doc("Request Type", self.request_type)
        prefix = request_type_doc.type_code or "REQ"

        # Format: RC-2025-001, BC-2025-001, REQ-2025-001, etc.
        from frappe.model.naming import make_autoname
        self.name = make_autoname(f"{prefix}-.YYYY.-.###")
        self.request_number = self.name

    def validate(self):
        """Validation before saving"""
        # 1. Set default workflow_state if not set
        if not self.workflow_state:
            self.workflow_state = "Draft"

        # 2. Validate brief description length
        if self.brief_description and len(self.brief_description) > 200:
            frappe.throw("Brief description must be 200 characters or less")

        # 3. Set default payment status
        if not self.payment_status:
            self.payment_status = "Pending"

        # 4. Calculate target completion date
        if self.request_type and self.submitted_date and not self.target_completion_date:
            self.calculate_target_completion_date()

        # 6. Calculate total fees
        self.calculate_total_fees()

    def before_submit(self):
        """Actions before document is submitted"""
        # Set submitted date
        if not self.submitted_date:
            self.submitted_date = getdate()

        # Set workflow_state to Submitted
        if not self.workflow_state or self.workflow_state == "Draft":
            self.workflow_state = "Submitted"

    def on_submit(self):
        """Actions when document is submitted"""
        # Add to status history
        self.add_status_history("Draft", "Submitted", "Request submitted by applicant")

        # Send acknowledgment email
        self.send_acknowledgment_email()

        # Create timeline entry
        self.add_comment("Label", "Request Submitted")

    def on_update_after_submit(self):
        """Actions after document is updated post-submission"""
        # Handle workflow state changes
        if self.has_value_changed("workflow_state"):
            old_state = self.get_doc_before_save().workflow_state if self.get_doc_before_save() else None
            self.handle_workflow_state_change(old_state, self.workflow_state)

            # Add to status history
            self.add_status_history(old_state, self.workflow_state, "Workflow state changed")

            # Emit real-time notification for workflow state change
            self.emit_realtime_update("workflow_state_changed", {
                "old_state": old_state,
                "new_state": self.workflow_state,
                "request_number": self.name
            })

        # If workflow_state changed to Acknowledged, set acknowledged date
        if self.workflow_state == "Acknowledged" and not self.acknowledged_date:
            self.acknowledged_date = getdate()
            self.calculate_target_completion_date()

            # Auto-create assessment project if enabled
            self.auto_create_assessment_project()

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

    def calculate_total_fees(self):
        """Calculate total fees from fee line items and set computed fields"""
        # Calculate subtotal from fees
        total = 0
        if self.fees:
            for fee in self.fees:
                total += fee.total or 0

        # Set the computed values (these will also be available as properties)
        self._total_fees_excl_gst = total
        self._gst_amount = total * 0.15  # 15% GST
        self._total_fees_incl_gst = total + self._gst_amount

        # Also set the actual fields for now (backward compatibility)
        self.total_fees_excl_gst = total
        self.gst_amount = total * 0.15
        self.total_fees_incl_gst = total + self.gst_amount

    @property
    def computed_total_fees_excl_gst(self):
        """Computed property for total fees excluding GST"""
        if hasattr(self, '_total_fees_excl_gst'):
            return self._total_fees_excl_gst

        total = 0
        if self.fees:
            for fee in self.fees:
                total += fee.total or 0
        return total

    @property
    def computed_gst_amount(self):
        """Computed property for GST amount"""
        if hasattr(self, '_gst_amount'):
            return self._gst_amount
        return self.computed_total_fees_excl_gst * 0.15

    @property
    def computed_total_fees_incl_gst(self):
        """Computed property for total fees including GST"""
        if hasattr(self, '_total_fees_incl_gst'):
            return self._total_fees_incl_gst
        return self.computed_total_fees_excl_gst + self.computed_gst_amount

    @property
    def requester_name(self):
        """Get requester name from User document"""
        if self.requester:
            return frappe.db.get_value("User", self.requester, "full_name")
        return None

    @property
    def requester_email(self):
        """Get requester email from User document"""
        if self.requester:
            return frappe.db.get_value("User", self.requester, "email")
        return None

    @property
    def agent_name(self):
        """Get agent name from User document"""
        if self.agent:
            return frappe.db.get_value("User", self.agent, "full_name")
        return None

    @property
    def agent_email(self):
        """Get agent email from User document"""
        if self.agent:
            return frappe.db.get_value("User", self.agent, "email")
        return None

    @property
    def is_overdue(self):
        """Calculate if request is overdue based on target completion date"""
        if not self.target_completion_date:
            return False
        return getdate() > getdate(self.target_completion_date)

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
        """Queue acknowledgment email to be sent in background (non-blocking)"""
        # Get requester email from User document
        requester_email = frappe.db.get_value("User", self.requester, "email") if self.requester else None
        if not requester_email:
            return

        # Enqueue email to background job - prevents blocking request processing
        frappe.enqueue(
            method="lodgeick.emails.send_acknowledgment",
            queue="short",
            timeout=300,
            is_async=True,
            request=self.name,
            recipient=requester_email
        )
        frappe.logger().info(f"Acknowledgment email queued for {self.name}")

    def handle_workflow_state_change(self, old_state, new_state):
        """Handle business logic for workflow state transitions"""

        # State: Acknowledged - Create assessment project
        if new_state == "Acknowledged":
            # Set acknowledged date on Request
            if not self.acknowledged_date:
                ack_date = getdate()
                self.db_set("acknowledged_date", ack_date, update_modified=False)
                self.acknowledged_date = ack_date
                self.calculate_target_completion_date()
                if self.target_completion_date:
                    self.db_set("target_completion_date", self.target_completion_date, update_modified=False)

            # Auto-create assessment project
            self.auto_create_assessment_project()

            frappe.msgprint(
                f"Request acknowledged. Assessment project will be created.",
                alert=True,
                indicator="green"
            )

        # States: Approved/Approved with Conditions/Declined/Completed - Set completion date
        elif new_state in ["Approved", "Approved with Conditions", "Declined", "Completed"]:
            if not self.actual_completion_date:
                completion_date = getdate()
                self.db_set("actual_completion_date", completion_date, update_modified=False)
                self.actual_completion_date = completion_date

            indicator = "green" if new_state.startswith("Approved") or new_state == "Completed" else "red"
            frappe.msgprint(
                f"Request {new_state.lower()}.",
                alert=True,
                indicator=indicator
            )

        # State: Withdrawn/Cancelled - Mark as closed
        elif new_state in ["Withdrawn", "Cancelled"]:
            frappe.msgprint(
                f"Request {new_state.lower()}.",
                alert=True,
                indicator="red"
            )

    def emit_realtime_update(self, event_type, data):
        """Emit real-time update via socket.io to all users watching this request"""
        try:
            # Publish to request-specific channel
            frappe.publish_realtime(
                event=f"request_update:{self.name}",
                message={
                    "event_type": event_type,
                    "data": data,
                    "timestamp": now()
                },
                doctype="Request",
                docname=self.name
            )

            # Also publish to requester's personal channel
            if self.requester:
                frappe.publish_realtime(
                    event="request_update",
                    message={
                        "event_type": event_type,
                        "request": self.name,
                        "data": data,
                        "timestamp": now()
                    },
                    user=self.requester
                )
        except Exception as e:
            # Don't fail the transaction if real-time notification fails
            frappe.log_error(f"Failed to emit real-time update for {self.name}: {str(e)}")

    def auto_create_assessment_project(self):
        """Auto-create assessment project when request is acknowledged"""
        # Check if assessment project already exists
        if self.assessment_project:
            return

        # Check if request type has default assessment template
        request_type_doc = frappe.get_doc("Request Type", self.request_type)

        # Try to find a suitable assessment template
        template = None
        if hasattr(request_type_doc, 'default_assessment_template') and request_type_doc.default_assessment_template:
            template = request_type_doc.default_assessment_template
        else:
            # Find first active template for this request type
            templates = frappe.get_all(
                "Assessment Template",
                filters={
                    "request_type": self.request_type,
                    "is_active": 1
                },
                limit=1
            )
            if templates:
                template = templates[0].name

        if not template:
            # No template found, skip auto-creation
            frappe.msgprint(f"No assessment template found for {self.request_type}. Assessment project not created.", alert=True)
            return

        # Create assessment project
        try:
            assessment_project = frappe.get_doc({
                "doctype": "Assessment Project",
                "request": self.name,
                "assessment_template": template,
                "project_owner": self.assigned_to or frappe.session.user,
                "statutory_clock_days": request_type_doc.processing_sla_days or 20,
                "overall_status": "In Progress"
            })
            assessment_project.insert()

            # Create stages from template
            assessment_project.create_stages_from_template()

            # Auto-create tasks from task templates
            tasks_created = assessment_project.create_tasks_from_template()

            assessment_project.save()

            # Link back to request
            self.db_set("assessment_project", assessment_project.name, update_modified=False)

            frappe.msgprint(
                f"✅ Assessment Project {assessment_project.name} created with {tasks_created} tasks",
                alert=True,
                indicator="green",
                title="Project Plan Created"
            )

        except Exception as e:
            frappe.log_error(f"Failed to auto-create assessment project: {str(e)}")
            frappe.msgprint(f"Failed to create assessment project: {str(e)}", alert=True, indicator="red")


def add_working_days(start_date, days):
    """Add working days to a date (excluding weekends and public holidays)"""
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


def is_public_holiday(date, holiday_list=None):
    """
    Check if a date is a public holiday

    Args:
        date: Date to check (datetime.date or string)
        holiday_list: Optional holiday list name. If not provided, uses default.

    Returns:
        bool: True if date is a public holiday
    """
    try:
        from frappe.utils import getdate

        # Convert string to date if needed
        check_date = getdate(date)

        # Get holiday list name
        if not holiday_list:
            # Try to get default holiday list from Lodgeick settings or use NZ default
            holiday_list = frappe.db.get_single_value("System Settings", "default_holiday_list")

            if not holiday_list:
                # Look for NZ public holidays list
                holiday_list = frappe.db.get_value(
                    "Holiday List",
                    {"country": "New Zealand"},
                    "name"
                )

        if not holiday_list:
            # No holiday list configured, assume no holidays
            return False

        # Check if date exists in Holiday List
        holiday = frappe.db.exists(
            "Holiday",
            {
                "parent": holiday_list,
                "holiday_date": check_date
            }
        )

        return bool(holiday)

    except Exception as e:
        # Log error but don't fail - assume not a holiday
        frappe.log_error(f"Holiday check error: {str(e)}", "Holiday Check Error")
        return False


@frappe.whitelist()
def get_my_requests(workflow_state=None, page=1, page_size=20):
    """
    Get requests for current user with pagination support

    Args:
        workflow_state: Filter by workflow state (optional)
        page: Page number (1-indexed, default: 1)
        page_size: Items per page (default: 20, max: 100)

    Returns:
        dict: {
            "data": [...],
            "total": int,
            "page": int,
            "page_size": int,
            "total_pages": int
        }
    """
    user = frappe.session.user

    # Validate and sanitize pagination params
    page = max(1, int(page))
    page_size = min(100, max(1, int(page_size)))  # Max 100 items per page
    offset = (page - 1) * page_size

    filters = {"requester": user}
    if workflow_state:
        filters["workflow_state"] = workflow_state

    conditions = get_filter_conditions(filters)

    # Get total count
    total = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabRequest` r
        WHERE {conditions}
    """.format(conditions=conditions))[0][0]

    # Use SQL JOIN to avoid N+1 query - fetch council name in single query
    requests = frappe.db.sql("""
        SELECT
            r.name, r.request_number, r.workflow_state,
            r.brief_description, r.submitted_date, r.target_completion_date,
            r.is_overdue, r.request_type, r.request_category, r.council, r.creation,
            c.council_name
        FROM `tabRequest` r
        LEFT JOIN `tabCouncil` c ON r.council = c.name
        WHERE {conditions}
        ORDER BY r.modified DESC
        LIMIT {page_size} OFFSET {offset}
    """.format(
        conditions=conditions,
        page_size=page_size,
        offset=offset
    ), as_dict=True)

    return {
        "data": requests,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size  # Ceiling division
    }


def get_filter_conditions(filters):
    """Build WHERE conditions from filters dict"""
    if not filters:
        return "1=1"

    conditions = []
    for key, value in filters.items():
        if isinstance(value, list):
            # Handle IN clause
            values = ', '.join([frappe.db.escape(v) for v in value])
            conditions.append(f"r.{key} IN ({values})")
        else:
            # Handle equality
            conditions.append(f"r.{key} = {frappe.db.escape(value)}")

    return " AND ".join(conditions) if conditions else "1=1"


@frappe.whitelist()
def get_my_applications():
    """Get applications for current user (Dashboard view)"""
    user = frappe.session.user

    requests = frappe.get_all(
        "Request",
        filters={"requester": user},
        fields=[
            "name",
            "request_number",
            "request_type",
            "workflow_state",
            "council",
            "property_address",
            "brief_description",
            "creation",
            "submitted_date",
            "statutory_clock_started",
            "working_days_elapsed"
        ],
        order_by="modified desc"
    )

    # Enrich with council name
    for req in requests:
        if req.get("council"):
            council_name = frappe.db.get_value("Council", req["council"], "council_name")
            req["council_name"] = council_name

    return requests


@frappe.whitelist()
def submit_request(request_id):
    """Submit a request (move from Draft to Submitted)"""
    doc = frappe.get_doc("Request", request_id)

    # Validate user has permission
    if doc.requester != frappe.session.user:
        frappe.throw("You don't have permission to submit this request")

    # Check if already submitted
    if doc.docstatus == 1:
        frappe.throw("Request is already submitted")

    # Submit
    doc.submit()

    return {
        "success": True,
        "message": "Request submitted successfully",
        "request_number": doc.request_number
    }


@frappe.whitelist()
def calculate_fees(request_type, building_value=None):
    """Calculate estimated fees for a request"""
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


@frappe.whitelist()
def get_all_requests_for_staff(page=1, page_size=20, workflow_state=None, council=None):
    """
    Get all requests for internal staff view with pagination

    Args:
        page: Page number (1-indexed, default: 1)
        page_size: Items per page (default: 20, max: 100)
        workflow_state: Filter by workflow state (optional)
        council: Filter by council (optional)

    Returns:
        dict: Paginated results with metadata
    """
    # Validate and sanitize pagination params
    page = max(1, int(page))
    page_size = min(100, max(1, int(page_size)))
    offset = (page - 1) * page_size

    # Build filters
    filters = {}
    if workflow_state:
        filters["workflow_state"] = workflow_state
    if council:
        filters["council"] = council

    # Get total count
    total = frappe.db.count("Request", filters=filters)

    # Use SQL JOIN to avoid N+1 query
    where_clause = "1=1"
    if workflow_state:
        where_clause += f" AND r.workflow_state = {frappe.db.escape(workflow_state)}"
    if council:
        where_clause += f" AND r.council = {frappe.db.escape(council)}"

    requests = frappe.db.sql(f"""
        SELECT
            r.name, r.request_number, r.request_type,
            r.brief_description, r.council, r.workflow_state, r.submitted_date,
            r.target_completion_date, r.assigned_to,
            r.owner, r.creation, r.modified,
            c.council_name
        FROM `tabRequest` r
        LEFT JOIN `tabCouncil` c ON r.council = c.name
        WHERE {where_clause}
        ORDER BY r.creation DESC
        LIMIT {page_size} OFFSET {offset}
    """, as_dict=True)

    return {
        "data": requests,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@frappe.whitelist()
def generate_invoice_pdf(request_name):
    """
    Generate invoice PDF for a request using Frappe's Print Format

    Args:
        request_name: Name of the Request document

    Returns:
        dict: Contains PDF file info or error
    """
    try:
        request = frappe.get_doc("Request", request_name)

        # Generate PDF using the Invoice print format
        pdf = frappe.get_print(
            "Request",
            request_name,
            print_format="Invoice",
            as_pdf=True
        )

        # Save PDF as File attachment
        file_name = f"Invoice_{request_name}.pdf"
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "attached_to_doctype": "Request",
            "attached_to_name": request_name,
            "content": pdf,
            "is_private": 1
        })
        file_doc.save(ignore_permissions=True)

        return {
            "success": True,
            "file_url": file_doc.file_url,
            "file_name": file_name
        }

    except Exception as e:
        frappe.log_error(f"Error generating invoice PDF: {str(e)}", "Invoice PDF Generation")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def email_invoice(request_name, recipient_email=None):
    """
    Email invoice PDF to applicant or specified recipient

    Args:
        request_name: Name of the Request document
        recipient_email: Optional email override (default: applicant email)

    Returns:
        dict: Success status
    """
    try:
        request = frappe.get_doc("Request", request_name)
        council = frappe.get_doc("Council", request.council)

        # Determine recipient
        if not recipient_email:
            recipient_email = request.applicant_email or frappe.db.get_value("User", request.requester, "email")

        if not recipient_email:
            return {
                "success": False,
                "error": "No recipient email found"
            }

        # Generate PDF
        pdf_result = generate_invoice_pdf(request_name)
        if not pdf_result.get("success"):
            return pdf_result

        # Email subject and message
        subject = f"Invoice for {request.request_type} Application - {request.name}"

        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
            <h2>Invoice for Your Application</h2>

            <p>Dear {request.applicant_name or 'Applicant'},</p>

            <p>Please find attached the invoice for your {request.request_type} application.</p>

            <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Request Number:</strong> {request.name}</p>
                <p style="margin: 5px 0;"><strong>Total Amount:</strong> ${request.total_fees_incl_gst or 0:.2f} (incl GST)</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> {request.payment_status or 'Pending'}</p>
            </div>

            <p>Payment can be made via:</p>
            <ul>
                <li>Online at our portal</li>
                <li>Bank transfer (reference: {request.name})</li>
                <li>In person at {council.council_name}</li>
            </ul>

            <p style="margin-top: 20px;">If you have any questions, please contact us at {council.contact_email}</p>

            <p style="margin-top: 30px; font-size: 12px; color: #666;">
                This is an automated message from {council.council_name}
            </p>
        </div>
        """

        # Send email with PDF attachment
        frappe.sendmail(
            recipients=[recipient_email],
            subject=subject,
            message=message,
            attachments=[{
                "fname": pdf_result["file_name"],
                "fcontent": frappe.get_doc("File", {"file_url": pdf_result["file_url"]}).get_content()
            }],
            reference_doctype="Request",
            reference_name=request_name
        )

        # Log in request
        request.add_comment("Comment", f"Invoice emailed to {recipient_email}")

        return {
            "success": True,
            "message": f"Invoice emailed to {recipient_email}"
        }

    except Exception as e:
        frappe.log_error(f"Error emailing invoice: {str(e)}", "Invoice Email")
        return {
            "success": False,
            "error": str(e)
        }
