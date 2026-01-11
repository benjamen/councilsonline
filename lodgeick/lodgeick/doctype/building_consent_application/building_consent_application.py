# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from lodgeick.utils.application_sync import sync_to_request


class BuildingConsentApplication(Document):
    def validate(self):
        """Validation before saving"""
        # Ensure parent Request exists
        if not frappe.db.exists("Request", self.request):
            frappe.throw("Parent Request does not exist")

        # Check if resource consent required
        self.check_resource_consent_requirement()

        # If MultiProof or BuiltReady, set fast-track processing
        if self.multiproof_approval or self.builtready_approval:
            request = frappe.get_doc("Request", self.request)
            if request.request_type:
                request_type = frappe.get_doc("Request Type", request.request_type)
                # Fast track is 10 days instead of 20
                if request_type.processing_sla_days != 10:
                    frappe.msgprint(
                        "Fast-track processing (10 days) applies due to MultiProof/BuiltReady approval",
                        indicator="blue"
                    )

        # Building value must be reasonable
        if self.building_value and self.building_value <= 0:
            frappe.throw("Building value must be greater than 0")

    def check_resource_consent_requirement(self):
        """Check if building triggers resource consent"""
        # Get property details
        request = frappe.get_doc("Request", self.request)
        property_id = getattr(request, 'property', None) or request.get('property')
        if not property_id:
            return

        property_doc = frappe.get_doc("Property", property_id)

        # Example triggers for resource consent
        triggers = []

        # Height exceeds typical limit (example: 8m for residential)
        if self.height_meters and self.height_meters > 8:
            triggers.append(f"Building height {self.height_meters}m exceeds typical 8m limit")

        # Site coverage exceeds limit
        if property_doc.site_area and self.site_coverage:
            coverage_percent = (self.site_coverage / property_doc.site_area) * 100
            if coverage_percent > 50:  # Example limit
                triggers.append(f"Site coverage {coverage_percent:.1f}% exceeds 50% limit")

        # Setback checks would go here (need more property boundary data)

        if triggers:
            self.resource_consent_required = 1
            frappe.msgprint(
                f"Resource consent may be required:<br>{'<br>'.join(['• ' + t for t in triggers])}",
                indicator="orange",
                title="Resource Consent Check"
            )

    def on_update(self):
        """Sync display fields to parent Request using standardized utility"""
        sync_to_request(self)

    def on_submit(self):
        """Actions on submit"""
        # Update parent Request
        request = frappe.get_doc("Request", self.request)
        if request.docstatus == 0:
            request.submit()
