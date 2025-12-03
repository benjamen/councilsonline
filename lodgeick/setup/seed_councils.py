#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""Seed sample councils for testing multi-council tenancy"""

import frappe
from frappe.utils import nowdate, add_months


def seed_sample_councils():
    """Create sample councils with request types"""

    councils_data = [
        {
            "council_code": "AKL",
            "council_name": "Auckland Council",
            "official_name": "Auckland Council",
            "contact_email": "consents@aucklandcouncil.govt.nz",
            "contact_phone": "09 301 0101",
            "website": "https://www.aucklandcouncil.govt.nz",
            "address_line_1": "135 Albert Street",
            "city": "Auckland",
            "postal_code": "1010",
            "timezone": "Pacific/Auckland",
            "primary_color": "#00AEEF",
            "secondary_color": "#002E5D",
            "is_active": 1,
            "license_start_date": nowdate(),
            "license_expiry_date": add_months(nowdate(), 12),
            "max_requests_per_month": 1000,
            "subscription_tier": "Enterprise",
            "default_sla_days": 20
        },
        {
            "council_code": "CHC",
            "council_name": "Christchurch City Council",
            "official_name": "Christchurch City Council",
            "contact_email": "consents@ccc.govt.nz",
            "contact_phone": "03 941 8999",
            "website": "https://ccc.govt.nz",
            "address_line_1": "53 Hereford Street",
            "city": "Christchurch",
            "postal_code": "8011",
            "timezone": "Pacific/Auckland",
            "primary_color": "#E4002B",
            "secondary_color": "#003366",
            "is_active": 1,
            "license_start_date": nowdate(),
            "license_expiry_date": add_months(nowdate(), 12),
            "max_requests_per_month": 750,
            "subscription_tier": "Premium",
            "default_sla_days": 20
        }
    ]

    # Get all request types
    request_types = frappe.get_all("Request Type", fields=["name", "type_name"])

    for council_data in councils_data:
        # Check if council already exists
        if frappe.db.exists("Council", {"council_code": council_data["council_code"]}):
            print(f"Council {council_data['council_code']} already exists, skipping...")
            continue

        # Create council
        council = frappe.get_doc({
            "doctype": "Council",
            **council_data
        })

        # Add all request types as enabled
        for request_type in request_types:
            council.append("enabled_request_types", {
                "request_type": request_type.name,
                "is_enabled": 1
            })

        council.flags.ignore_permissions = True
        council.insert()
        print(f"Created council: {council.council_name} ({council.council_code})")

    frappe.db.commit()
    print("Sample councils seeded successfully!")


if __name__ == "__main__":
    frappe.init(site="lodgeick.localhost")
    frappe.connect()
    seed_sample_councils()
