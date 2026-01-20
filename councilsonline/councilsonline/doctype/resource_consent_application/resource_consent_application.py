# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from councilsonline.utils.application_sync import sync_to_request


class ResourceConsentApplication(Document):
    def before_insert(self):
        """Actions before first insert"""
        # Auto-populate conditions from Request Type templates
        if self.request and not self.conditions:
            self.apply_condition_templates()

    def validate(self):
        """Validation before saving"""
        # Ensure parent Request exists
        if not frappe.db.exists("Request", self.request):
            frappe.throw("Parent Request does not exist")

        # AEE minimum word count for discretionary activities
        if self.activity_status in ["Discretionary", "Non-Complying"]:
            if self.assessment_of_effects:
                word_count = len(self.assessment_of_effects.split())
                if word_count < 500:
                    frappe.msgprint(
                        f"Warning: AEE should be at least 500 words for {self.activity_status} activities. Current: {word_count} words",
                        indicator="orange"
                    )

        # Count written approvals
        if self.affected_parties:
            self.written_approvals_obtained = len([
                p for p in self.affected_parties if p.approval_obtained
            ])

            # Check notification logic
            if self.notification_level == "Non-Notified":
                total_affected = len(self.affected_parties)
                if self.written_approvals_obtained < total_affected:
                    frappe.msgprint(
                        f"Warning: Non-notified but only {self.written_approvals_obtained}/{total_affected} affected parties have given approval",
                        indicator="orange"
                    )

        # Calculate statutory clock metrics
        if self.statutory_clock_started:
            self.calculate_working_days()

    def on_update(self):
        """Sync display fields to parent Request using standardized utility"""
        sync_to_request(self)

    def on_submit(self):
        """Actions on submit"""
        # Update parent Request
        request = frappe.get_doc("Request", self.request)
        if request.docstatus == 0:
            request.submit()

    def calculate_working_days(self):
        """Calculate working days elapsed excluding weekends and holidays"""
        if not self.statutory_clock_started:
            return

        from frappe.utils import now_datetime
        from councilsonline.councilsonline.doctype.request.request import calculate_working_days_between

        end_date = self.statutory_clock_stopped or now_datetime()
        self.working_days_elapsed = calculate_working_days_between(
            self.statutory_clock_started,
            end_date
        )

        # Get SLA from parent request
        request = frappe.get_doc("Request", self.request)
        if request.request_type:
            request_type_doc = frappe.get_doc("Request Type", request.request_type)
            sla_days = request_type_doc.processing_sla_days or 20

            self.working_days_remaining = max(0, sla_days - self.working_days_elapsed)

    def start_statutory_clock(self):
        """Start the RMA statutory clock"""
        from frappe.utils import now_datetime
        if not self.statutory_clock_started:
            self.statutory_clock_started = now_datetime()
            self.statutory_clock_stopped = None
            self.save(ignore_permissions=True)

    def stop_statutory_clock(self):
        """Stop the RMA statutory clock"""
        from frappe.utils import now_datetime
        if self.statutory_clock_started and not self.statutory_clock_stopped:
            self.statutory_clock_stopped = now_datetime()
            self.save(ignore_permissions=True)

    def restart_statutory_clock(self):
        """Restart the RMA statutory clock after RFI"""
        if self.statutory_clock_stopped:
            self.statutory_clock_stopped = None
            self.save(ignore_permissions=True)

    def apply_condition_templates(self):
        """
        Apply condition templates from the Request Type to this Resource Consent Application.
        This method is called automatically on document creation (before_insert).
        Can also be called manually via a button to refresh conditions.
        """
        if not self.request:
            return

        # Get the parent Request
        request = frappe.get_doc("Request", self.request)
        if not request.request_type:
            return

        # Get the Request Type with its condition templates
        request_type = frappe.get_doc("Request Type", request.request_type)

        if not request_type.condition_templates:
            return

        # Counter for auto-numbering conditions
        condition_number = 1

        # Apply each template that has auto_apply enabled
        for template_link in request_type.condition_templates:
            if not template_link.auto_apply:
                continue

            # Get the condition template
            template = frappe.get_doc("Consent Condition Template", template_link.condition_template)

            if not template.is_active:
                continue

            # Use the template's instantiate method to create condition data
            condition_data = template.instantiate_for_request(
                request_doc=request,
                condition_number=template_link.default_condition_number or str(condition_number)
            )

            # Append to conditions child table
            self.append("conditions", condition_data)

            condition_number += 1

        frappe.msgprint(
            f"Applied {len(self.conditions)} condition template(s) from Request Type: {request_type.type_name}",
            indicator="green",
            alert=True
        )


@frappe.whitelist()
def refresh_condition_templates(resource_consent_name):
    """
    API method to refresh condition templates for an existing Resource Consent Application.
    This clears existing conditions and reapplies templates.
    """
    doc = frappe.get_doc("Resource Consent Application", resource_consent_name)

    # Clear existing conditions
    doc.conditions = []

    # Reapply templates
    doc.apply_condition_templates()

    # Save the document
    doc.save()

    frappe.msgprint(
        f"Conditions refreshed. {len(doc.conditions)} template(s) applied.",
        indicator="green"
    )

    return doc
