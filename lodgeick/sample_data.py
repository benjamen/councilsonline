#!/usr/bin/env python3
"""
Create sample data for Lodgeick
Run this with: bench --site lodgeick.localhost execute lodgeick.sample_data.create_all
"""

import frappe
from frappe.utils import nowdate

def create_request_types():
    """Create sample Request Types"""
    request_types = [
        {
            "type_name": "Land Use Consent",
            "type_code": "RC-LU",
            "category": "Resource Consent",
            "description": "<p>Consent for land use activities that are not permitted under the District Plan.</p>",
            "processing_sla_days": 20,
            "base_fee": 350,
            "fee_calculation_method": "Deposit",
            "is_active": 1,
            "icon": "home"
        },
        {
            "type_name": "Subdivision Consent",
            "type_code": "RC-SD",
            "category": "Resource Consent",
            "description": "<p>Consent to subdivide land into multiple lots.</p>",
            "processing_sla_days": 20,
            "base_fee": 500,
            "fee_calculation_method": "Deposit",
            "is_active": 1,
            "icon": "grid"
        },
        {
            "type_name": "Building Consent - New Dwelling",
            "type_code": "BC-ND",
            "category": "Building Consent",
            "description": "<p>Consent for construction of a new residential dwelling.</p>",
            "processing_sla_days": 20,
            "base_fee": 400,
            "fee_calculation_method": "Value-Based",
            "is_active": 1,
            "icon": "home"
        },
        {
            "type_name": "Building Consent - Alteration",
            "type_code": "BC-ALT",
            "category": "Building Consent",
            "description": "<p>Consent for alterations to an existing building.</p>",
            "processing_sla_days": 20,
            "base_fee": 250,
            "fee_calculation_method": "Fixed",
            "is_active": 1,
            "icon": "tool"
        },
        {
            "type_name": "Building Consent - Addition",
            "type_code": "BC-ADD",
            "category": "Building Consent",
            "description": "<p>Consent for additions to an existing building (e.g., extension, deck, garage).</p>",
            "processing_sla_days": 20,
            "base_fee": 300,
            "fee_calculation_method": "Fixed",
            "is_active": 1,
            "icon": "plus"
        }
    ]

    print("\n📋 Creating Request Types...")
    for rt_data in request_types:
        if not frappe.db.exists("Request Type", rt_data["type_name"]):
            rt = frappe.get_doc({
                "doctype": "Request Type",
                **rt_data
            })
            rt.insert()
            print(f"  ✓ Created: {rt.type_name} ({rt.type_code})")
        else:
            print(f"  ⊙ Exists: {rt_data['type_name']}")

    frappe.db.commit()
    print("✅ Request Types created!\n")


def create_properties():
    """Create sample properties"""
    properties = [
        {
            "street_address": "123 Main Street",
            "suburb": "Naenae",
            "city": "Lower Hutt",
            "postcode": "5011",
            "legal_description": "Lot 5 DP 12345",
            "certificate_of_title": "WN123/456",
            "site_area": 650,
            "zoning": "Medium Density Residential",
            "frontage": 20,
            "site_shape": "Regular",
            "topography": "Flat",
            "ownership_type": "Freehold",
            "owner_name": "John Smith",
            "owner_email": "john.smith@example.com",
            "owner_phone": "021 123 4567",
            "latitude": -41.2165,
            "longitude": 174.9170
        },
        {
            "street_address": "456 Valley Road",
            "suburb": "Woburn",
            "city": "Lower Hutt",
            "postcode": "5010",
            "legal_description": "Lot 12 DP 67890",
            "certificate_of_title": "WN456/789",
            "site_area": 1200,
            "zoning": "Large Lot Residential",
            "frontage": 30,
            "site_shape": "Irregular",
            "topography": "Gentle Slope",
            "ownership_type": "Freehold",
            "owner_name": "Jane Doe",
            "owner_email": "jane.doe@example.com",
            "owner_phone": "021 987 6543",
            "latitude": -41.2089,
            "longitude": 174.9213
        },
        {
            "street_address": "789 Hill Street",
            "suburb": "Petone",
            "city": "Lower Hutt",
            "postcode": "5012",
            "legal_description": "Lot 3 DP 11223",
            "certificate_of_title": "WN789/012",
            "site_area": 450,
            "zoning": "High Density Residential",
            "frontage": 15,
            "site_shape": "Corner",
            "topography": "Flat",
            "ownership_type": "Freehold",
            "owner_name": "Bob Johnson",
            "owner_email": "bob.johnson@example.com",
            "owner_phone": "021 555 1234",
            "latitude": -41.2274,
            "longitude": 174.8721
        },
        {
            "street_address": "321 Park Avenue",
            "suburb": "Eastbourne",
            "city": "Lower Hutt",
            "postcode": "5013",
            "legal_description": "Lot 18 DP 33445",
            "certificate_of_title": "WN321/543",
            "site_area": 2500,
            "zoning": "Large Lot Residential",
            "frontage": 40,
            "site_shape": "Regular",
            "topography": "Steep Slope",
            "ownership_type": "Freehold",
            "owner_name": "Alice Brown",
            "owner_email": "alice.brown@example.com",
            "owner_phone": "021 777 8888",
            "heritage_status": "Listed - Category 2",
            "latitude": -41.2891,
            "longitude": 174.9032
        }
    ]

    print("🏠 Creating Properties...")
    created_properties = []
    for prop_data in properties:
        prop = frappe.get_doc({
            "doctype": "Property",
            **prop_data
        })
        prop.insert()
        created_properties.append(prop.name)
        print(f"  ✓ Created: {prop.street_address} ({prop.name})")

    frappe.db.commit()
    print("✅ Properties created!\n")
    return created_properties


def create_organization():
    """Create sample organization"""
    if not frappe.db.exists("Organization", "Urban Planning Consultants Ltd"):
        org = frappe.get_doc({
            "doctype": "Organization",
            "organization_name": "Urban Planning Consultants Ltd",
            "organization_type": "Planning Firm",
            "business_number": "1234567",
            "website": "https://urbanplanning.co.nz",
            "phone": "04 123 4567",
            "email": "info@urbanplanning.co.nz",
            "physical_address": "Level 3, 100 The Terrace, Wellington",
            "postal_address": "PO Box 1234, Wellington 6140",
            "shared_workspace_enabled": 1,
            "is_active": 1
        })
        org.insert()
        frappe.db.commit()
        print("🏢 Created Organization: Urban Planning Consultants Ltd\n")
    else:
        print("🏢 Organization already exists\n")


def create_all():
    """Main function to create all sample data"""
    print("\n" + "="*60)
    print("  LODGEICK SAMPLE DATA CREATION")
    print("="*60 + "\n")

    try:
        # Create Request Types
        create_request_types()

        # Create Properties
        properties = create_properties()

        # Create Organization
        create_organization()

        print("\n" + "="*60)
        print("  ✅ SAMPLE DATA CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nCreated:")
        print(f"  • 5 Request Types")
        print(f"  • {len(properties)} Properties")
        print(f"  • 1 Organization")
        print(f"\nProperty IDs created: {', '.join(properties)}")
        print("\nYou can now create test Requests using these properties!")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()
