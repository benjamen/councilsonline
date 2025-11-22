# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ResourceConsentApplication(Document):
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
        from lodgeick.lodgeick.doctype.request.request import calculate_working_days_between

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
