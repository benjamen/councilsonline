# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, add_days, getdate, date_diff, format_date
from datetime import datetime, timedelta


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
        # 1. Set default status if not set
        if not self.status:
            self.status = "Draft"

        # 2. Validate council and request type association (skip for drafts)
        if self.status != "Draft":
            self.validate_council_license()
            self.validate_request_type_for_council()

        # 3. Validate brief description length
        if self.brief_description and len(self.brief_description) > 200:
            frappe.throw("Brief description must be 200 characters or less")

        # 4. Set default payment status
        if not self.payment_status:
            self.payment_status = "Pending"

        # 5. Calculate target completion date
        if self.request_type and self.submitted_date and not self.target_completion_date:
            self.calculate_target_completion_date()

        # 6. Calculate total fees
        self.calculate_total_fees()

    def validate_council_license(self):
        """Validate that council is active and has valid license"""
        if not self.council:
            frappe.throw("Council is required")

        council = frappe.get_doc("Council", self.council)

        if not council.is_active:
            frappe.throw(f"Council '{council.council_name}' is not active")

        if not council.is_license_valid():
            frappe.throw(f"Council '{council.council_name}' license has expired")

        if not council.can_accept_requests():
            frappe.throw(f"Council '{council.council_name}' has reached its monthly request limit")

    def validate_request_type_for_council(self):
        """Validate that request type is enabled for selected council"""
        if not self.council or not self.request_type:
            return

        # Check if request type is enabled for this council
        enabled = frappe.db.get_value(
            "Council Request Type",
            {
                "parent": self.council,
                "request_type": self.request_type,
                "is_enabled": 1
            },
            "name"
        )

        if not enabled:
            council_name = frappe.db.get_value("Council", self.council, "council_name")
            request_type_name = frappe.db.get_value("Request Type", self.request_type, "type_name")
            frappe.throw(f"Request type '{request_type_name}' is not available for {council_name}")

    def before_submit(self):
        """Actions before document is submitted"""
        # Validate council and request type before submission
        self.validate_council_license()
        self.validate_request_type_for_council()

        # Set submitted date
        if not self.submitted_date:
            self.submitted_date = getdate()

        # Set status to Submitted
        self.status = "Submitted"

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
        # Track status changes
        if self.has_value_changed("status"):
            old_status = self.get_doc_before_save().status if self.get_doc_before_save() else None
            self.add_status_history(old_status, self.status, "Status updated")

        # Handle workflow state changes
        if self.has_value_changed("workflow_state"):
            old_state = self.get_doc_before_save().workflow_state if self.get_doc_before_save() else None
            self.handle_workflow_state_change(old_state, self.workflow_state)

        # If status changed to Acknowledged, set acknowledged date
        if self.status == "Acknowledged" and not self.acknowledged_date:
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
        """Queue acknowledgment email to be sent in background (non-blocking)"""
        if not self.requester_email:
            return

        # Enqueue email to background job - prevents blocking request processing
        frappe.enqueue(
            method="lodgeick.emails.send_acknowledgment",
            queue="short",
            timeout=300,
            is_async=True,
            request=self.name,
            recipient=self.requester_email
        )
        frappe.logger().info(f"Acknowledgment email queued for {self.name}")

    def handle_workflow_state_change(self, old_state, new_state):
        """Handle business logic for workflow state transitions"""

        # Add status history tracking
        self.add_status_history(old_state, new_state, "Workflow state changed")

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

            # Update status field for backward compatibility
            self.db_set("status", new_state, update_modified=False)
            self.status = new_state

            indicator = "green" if new_state.startswith("Approved") or new_state == "Completed" else "red"
            frappe.msgprint(
                f"Request {new_state.lower()}.",
                alert=True,
                indicator=indicator
            )

        # State: Withdrawn/Cancelled - Mark as closed
        elif new_state in ["Withdrawn", "Cancelled"]:
            # Update status field for backward compatibility
            self.db_set("status", new_state, update_modified=False)
            self.status = new_state

            frappe.msgprint(
                f"Request {new_state.lower()}.",
                alert=True,
                indicator="red"
            )

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


def is_public_holiday(date):
    """Check if a date is a public holiday"""
    # TODO: Implement proper holiday checking against Holiday List DocType
    # For now, return False (no holidays considered)
    return False


@frappe.whitelist()
def get_my_requests(status=None):
    """Get requests for current user"""
    user = frappe.session.user

    filters = {"requester": user}
    if status:
        filters["status"] = status

    # Use SQL JOIN to avoid N+1 query - fetch council name in single query
    requests = frappe.db.sql("""
        SELECT
            r.name, r.request_number, r.status,
            r.brief_description, r.submitted_date, r.target_completion_date,
            r.is_overdue, r.request_type, r.request_category, r.council, r.creation,
            c.council_name
        FROM `tabRequest` r
        LEFT JOIN `tabCouncil` c ON r.council = c.name
        WHERE {conditions}
        ORDER BY r.modified DESC
    """.format(conditions=get_filter_conditions(filters)), as_dict=True)

    return requests


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
            "status",
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
def get_all_requests_for_staff():
    """Get all requests for internal staff view"""
    requests = frappe.get_all(
        "Request",
        fields=[
            "name",
            "request_number",
            "request_type",
            "request_category",
            "brief_description",
            "council",
            "status",
            "submitted_date",
            "target_completion_date",
            "assigned_to",
            "priority",
            "owner",
            "creation",
            "modified"
        ],
        order_by="creation desc"
    )

    # Enrich with council name
    for req in requests:
        if req.get("council"):
            council_name = frappe.db.get_value("Council", req["council"], "council_name")
            req["council_name"] = council_name

    return requests
