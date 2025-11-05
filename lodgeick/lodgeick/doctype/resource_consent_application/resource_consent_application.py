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

    def on_submit(self):
        """Actions on submit"""
        # Update parent Request
        request = frappe.get_doc("Request", self.request)
        if request.docstatus == 0:
            request.submit()
