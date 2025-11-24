# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RequestType(Document):
    pass


@frappe.whitelist(allow_guest=True)
def get_active_request_types():
    """Get all active request types for public application form"""
    return frappe.get_all(
        "Request Type",
        filters={"is_active": 1},
        fields=[
            "name",
            "type_name",
            "type_code",
            "category",
            "description",
            "base_fee",
            "processing_sla_days",
            "fee_calculation_method"
        ],
        order_by="type_name asc"
    )
