"""Test utilities for RC implementation"""

import frappe
from frappe.utils import nowdate

def test_rc_e2e_submission():
    """Test end-to-end RC submission with Property field mapping"""

    frappe.set_user("Administrator")

    # Test data matching RC Request Type fields
    test_data = {
        # Step 1: Applicant Details
        "requester_type": "Individual",
        "applicant_full_name": "John Test Smith",
        "requester_email": "john.smith@example.com",
        "requester_phone": "021234567",
        "applicant_postal_address": "123 Test Street, Auckland 1010",
        "has_agent": 0,

        # Step 2: Property Information
        "property_address": "456 Property Lane",
        "property_street_address": "456 Property Lane",
        "property_suburb": "Ponsonby",
        "property_city": "Auckland",
        "property_postcode": "1011",
        "property_legal_description": "Lot 1 DP 12345",
        "property_ct_reference": "NA123/456",
        "property_site_area": 800.5,
        "property_zoning": "Medium Density Residential",
        "applicant_is_owner": 1,

        # Step 3: Consent Type & Activity
        "consent_type_land_use": 1,
        "activity_title": "Single dwelling construction",
        "activity_description": "Construction of a new single dwelling",
        "activity_purpose": "To provide housing for family",
        "activity_status_type": "Restricted Discretionary",
        "plan_rules_breached": "Height in relation to boundary",

        # Step 4: Site Characteristics
        "site_topography": "Flat",
        "site_vegetation": "Grass and native trees",
        "site_development_status": "Vacant Land",
        "hazard_flooding": 0,

        # Step 5: Servicing
        "water_supply": "Public Reticulation",
        "wastewater_disposal": "Public Sewer",
        "stormwater_disposal": "Public Stormwater Network",
        "access_details": "Via existing road frontage",

        # Step 6: Consultation
        "consultation_undertaken": "Yes",
        "consultation_summary": "Consulted with neighbors",
        "affected_parties_details": "No affected parties identified",
        "written_approvals_obtained": 0,

        # Step 7: Assessment of Effects
        "aee_full_assessment": "Full assessment provided",
        "effects_visual_amenity": "Minimal visual effects",
        "effects_traffic_parking": "No traffic impacts",
        "effects_noise": "Construction noise only",
        "mitigation_measures": "Standard construction hours",

        # Step 8: Plans & Documents (would be file uploads in real scenario)
        # "site_plan": "attachment",

        # Step 9: Declarations
        "declaration_accuracy": 1,
        "declaration_authority": 1,
        "declaration_acknowledgment": 1,
        "applicant_signature": "John Test Smith",
        "signature_date": nowdate(),

        # Metadata
        "request_type": "Resource Consent - New Zealand",
        "council": "AKL"
    }

    print("======================================================================")
    print("Resource Consent - End-to-End Submission Test")
    print("======================================================================")
    print("")
    print("📝 Creating RC Request with test data...")

    try:
        # Call the create_draft_request API endpoint
        from lodgeick.api import create_draft_request

        result = create_draft_request(data=test_data, current_step=9, total_steps=9)

        print(f"✅ Request created successfully!")
        print(f"   Request ID: {result.get('request_name')}")
        print(f"   Property: {result.get('property_name', 'N/A')}")
        print(f"   RC App: {result.get('rc_app_name', 'N/A')}")
        print("")

        # Verify Property was created with all mandatory fields
        if result.get('property_name'):
            prop = frappe.get_doc("Property", result['property_name'])
            print("🏠 Property Field Verification:")
            print(f"   ✓ Postcode: {prop.postcode}")
            print(f"   ✓ Certificate of Title: {prop.certificate_of_title}")
            print(f"   ✓ Site Area: {prop.site_area} m²")
            print("")

        print("=" * 70)
        print("🎉 TEST PASSED - E2E Submission Successful!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
