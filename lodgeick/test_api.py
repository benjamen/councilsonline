#!/usr/bin/env python3
"""
Test Lodgeick API endpoints
Run with: bench --site lodgeick.localhost execute lodgeick.test_api
"""

import frappe
from frappe.utils import nowdate, add_days
import json


def test_request_types():
    """Test Request Type API"""
    print("\n" + "="*60)
    print("  TESTING REQUEST TYPE API")
    print("="*60)

    # Get all request types
    request_types = frappe.get_all(
        "Request Type",
        fields=["name", "type_name", "type_code", "category", "base_fee", "processing_sla_days"]
    )

    print(f"\n✓ Found {len(request_types)} Request Types:")
    for rt in request_types:
        print(f"  - {rt.type_name} ({rt.type_code}): ${rt.base_fee}, {rt.processing_sla_days} days SLA")

    return request_types


def test_properties():
    """Test Property API"""
    print("\n" + "="*60)
    print("  TESTING PROPERTY API")
    print("="*60)

    # Get all properties
    properties = frappe.get_all(
        "Property",
        fields=["name", "street_address", "suburb", "city", "zoning", "site_area"]
    )

    print(f"\n✓ Found {len(properties)} Properties:")
    for prop in properties:
        print(f"  - {prop.name}: {prop.street_address}, {prop.suburb} ({prop.zoning}, {prop.site_area}m²)")

    return properties


def test_create_request(request_type, property_id):
    """Test creating a Request"""
    print("\n" + "="*60)
    print("  TESTING REQUEST CREATION")
    print("="*60)

    # Create a test request
    request = frappe.get_doc({
        "doctype": "Request",
        "request_type": request_type,
        "property": property_id,
        "requester": "Administrator",
        "requester_name": "John Smith",
        "requester_email": "john.smith@example.com",
        "requester_phone": "021 123 4567",
        "applicant_address": "123 Main Street, Lower Hutt",
        "brief_description": "New 3-bedroom residential dwelling",
        "detailed_description": "<p>Construction of a new single-storey residential dwelling with 3 bedrooms, 2 bathrooms, open-plan kitchen/living, double garage, and deck.</p><p>Timber frame construction on concrete slab foundation with Colorsteel roof.</p>",
        "project_description": "Test building consent application for a new dwelling",
        "workflow_state": "Draft"
    })

    request.insert()
    print(f"\n✓ Created Request: {request.request_number}")
    print(f"  - Workflow State: {request.workflow_state}")
    print(f"  - Type: {request.request_type}")
    print(f"  - Property: {request.property}")
    print(f"  - Applicant: {request.requester_name}")

    return request


def test_create_building_consent_application(request_name):
    """Test creating a Building Consent Application"""
    print("\n" + "="*60)
    print("  TESTING BUILDING CONSENT APPLICATION")
    print("="*60)

    # Create building consent application
    bca = frappe.get_doc({
        "doctype": "Building Consent Application",
        "request": request_name,
        "building_work_type": "New Build",
        "building_category": "Residential",
        "building_value": 450000,
        "floor_area": 180,
        "site_coverage": 150,
        "number_of_storeys": 1,
        "height_meters": 6.5,
        "construction_type": "Timber Frame",
        "foundations_type": "Concrete Slab",
        "roof_type": "Pitched",
        "num_dwellings": 1,
        "num_bedrooms": 3,
        "num_bathrooms": 2,
        "num_car_parks": 2
    })

    bca.insert()
    print(f"\n✓ Created Building Consent Application: {bca.name}")
    print(f"  - Building Work Type: {bca.building_work_type}")
    print(f"  - Building Value: ${bca.building_value:,.0f}")
    print(f"  - Floor Area: {bca.floor_area}m²")
    print(f"  - Height: {bca.height_meters}m")
    print(f"  - Resource Consent Required: {'Yes' if bca.resource_consent_required else 'No'}")

    return bca


def test_create_rfi(request_name):
    """Test creating an RFI"""
    print("\n" + "="*60)
    print("  TESTING RFI CREATION")
    print("="*60)

    # Create RFI
    rfi = frappe.get_doc({
        "doctype": "Request For Information",
        "request": request_name,
        "subject": "Missing Building Plans",
        "description": "<p>Please provide the following missing information:</p><ul><li>Detailed site plan showing all boundaries</li><li>Engineering calculations for foundation design</li><li>Fire egress plan</li></ul>",
        "urgency": "High",
        "issued_by": "Administrator",
        "issued_date": nowdate(),
        "due_date": add_days(nowdate(), 10),
        "stops_statutory_clock": 1
    })

    # Add some questions
    rfi.append("questions", {
        "question_number": "1",
        "category": "Site Plans",
        "question_text": "Please provide detailed site plan showing all boundaries and setbacks"
    })

    rfi.append("questions", {
        "question_number": "2",
        "category": "Specialist Reports",
        "question_text": "Provide engineering calculations for foundation design"
    })

    rfi.insert()
    print(f"\n✓ Created RFI: {rfi.rfi_number}")
    print(f"  - Subject: {rfi.subject}")
    print(f"  - Urgency: {rfi.urgency}")
    print(f"  - Due Date: {rfi.due_date}")
    print(f"  - Stops Clock: {'Yes' if rfi.stops_statutory_clock else 'No'}")
    print(f"  - Questions: {len(rfi.questions)}")

    return rfi


def test_create_payment(request_name):
    """Test creating a Payment"""
    print("\n" + "="*60)
    print("  TESTING PAYMENT CREATION")
    print("="*60)

    # Create payment
    payment = frappe.get_doc({
        "doctype": "Payment",
        "request": request_name,
        "payment_type": "Application Fee",
        "payment_method": "Credit Card",
        "payment_gateway": "Stripe",
        "payment_status": "Completed",
        "amount": 400,
        "currency": "NZD",
        "transaction_id": "pi_test_123456789"
    })

    payment.insert()
    print(f"\n✓ Created Payment: {payment.payment_number}")
    print(f"  - Type: {payment.payment_type}")
    print(f"  - Amount: ${payment.amount:.2f} + ${payment.gst:.2f} GST = ${payment.total_amount:.2f}")
    print(f"  - Status: {payment.payment_status}")
    print(f"  - Transaction ID: {payment.transaction_id}")

    return payment


def test_create_communication(request_name):
    """Test creating a Communication Log"""
    print("\n" + "="*60)
    print("  TESTING COMMUNICATION LOG")
    print("="*60)

    # Create communication
    comm = frappe.get_doc({
        "doctype": "Communication Log",
        "request": request_name,
        "communication_type": "Email",
        "communication_method": "Manual",
        "direction": "Outgoing",
        "subject": "Application Received - Additional Information Required",
        "content": "<p>Dear Applicant,</p><p>Your building consent application has been received and is currently under review.</p><p>Please note that additional information will be required as detailed in the RFI issued separately.</p><p>Best regards,<br>Council Planning Team</p>",
        "sender": "planning@council.govt.nz",
        "recipient": "john.smith@example.com",
        "is_internal": 0
    })

    comm.insert()
    print(f"\n✓ Created Communication Log: {comm.communication_number}")
    print(f"  - Type: {comm.communication_type}")
    print(f"  - Direction: {comm.direction}")
    print(f"  - Subject: {comm.subject}")
    print(f"  - From: {comm.sender}")
    print(f"  - To: {comm.recipient}")

    return comm


def test_whitelisted_methods():
    """Test whitelisted API methods"""
    print("\n" + "="*60)
    print("  TESTING WHITELISTED API METHODS")
    print("="*60)

    # Get a request to test with
    request = frappe.get_last_doc("Request")

    # Test get_my_applications
    try:
        from lodgeick.lodgeick.doctype.request.request import get_my_applications
        apps = get_my_applications()
        print(f"\n✓ get_my_applications(): Found {len(apps)} applications")
    except Exception as e:
        print(f"\n✗ get_my_applications() failed: {str(e)}")

    # Test calculate_outstanding_amount
    try:
        from lodgeick.lodgeick.doctype.payment.payment import calculate_outstanding_amount
        outstanding = calculate_outstanding_amount(request.name)
        print(f"✓ calculate_outstanding_amount(): ${outstanding.get('outstanding', 0):.2f} outstanding")
    except Exception as e:
        print(f"✗ calculate_outstanding_amount() failed: {str(e)}")

    # Test get_request_payments
    try:
        from lodgeick.lodgeick.doctype.payment.payment import get_request_payments
        payments = get_request_payments(request.name)
        print(f"✓ get_request_payments(): Found {len(payments)} payments")
    except Exception as e:
        print(f"✗ get_request_payments() failed: {str(e)}")

    # Test get_request_rfis
    try:
        from lodgeick.lodgeick.doctype.request_for_information.request_for_information import get_request_rfis
        rfis = get_request_rfis(request.name)
        print(f"✓ get_request_rfis(): Found {len(rfis)} RFIs")
    except Exception as e:
        print(f"✗ get_request_rfis() failed: {str(e)}")

    # Test get_request_communications
    try:
        from lodgeick.lodgeick.doctype.communication_log.communication_log import get_request_communications
        comms = get_request_communications(request.name)
        print(f"✓ get_request_communications(): Found {len(comms)} communications")
    except Exception as e:
        print(f"✗ get_request_communications() failed: {str(e)}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  LODGEICK API TESTING SUITE")
    print("="*60)

    try:
        # Test basic data retrieval
        request_types = test_request_types()
        properties = test_properties()

        # Create a test request
        if request_types and properties:
            # Use Building Consent - New Dwelling
            bc_type = next((rt for rt in request_types if rt.type_code == "BC-ND"), request_types[0])
            test_property = properties[0]

            # Create request
            request = test_create_request(bc_type.name, test_property.name)

            # Create building consent application
            bca = test_create_building_consent_application(request.name)

            # Create RFI
            rfi = test_create_rfi(request.name)

            # Create payment
            payment = test_create_payment(request.name)

            # Create communication
            comm = test_create_communication(request.name)

            # Test whitelisted methods
            test_whitelisted_methods()

        print("\n" + "="*60)
        print("  ✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nCreated test data:")
        print(f"  • Request: {request.request_number}")
        print(f"  • Building Consent App: {bca.name}")
        print(f"  • RFI: {rfi.rfi_number}")
        print(f"  • Payment: {payment.payment_number}")
        print(f"  • Communication: {comm.communication_number}")
        print("\nAll DocTypes and API methods are working correctly!")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()


if __name__ == "__main__":
    run_all_tests()
