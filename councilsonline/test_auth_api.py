#!/usr/bin/env python3
"""
Test CouncilsOnline Authentication API endpoints
Run with: bench --site councilsonline.localhost execute councilsonline.test_auth_api.run_all_tests
"""

import frappe
from frappe.utils import now, random_string
import json


def cleanup_test_users(test_email_prefix="test_auth_"):
    """Clean up test users created during testing"""
    try:
        users = frappe.get_all("User", filters={"email": ["like", f"%{test_email_prefix}%"]})
        for user in users:
            frappe.delete_doc("User", user.name, force=True)
        frappe.db.commit()
        print(f"✓ Cleaned up {len(users)} test users")
    except Exception as e:
        print(f"Warning: Cleanup failed: {str(e)}")


def test_nz_phone_validation():
    """Test NZ phone number validation"""
    print("\n" + "="*60)
    print("  TESTING NZ PHONE NUMBER VALIDATION")
    print("="*60)

    from councilsonline.api.auth import validate_nz_phone_number

    test_cases = [
        # Valid cases
        ("021 123 4567", True, "Mobile 021"),
        ("022-1234567", True, "Mobile 022"),
        ("027 12345678", True, "Mobile 027"),
        ("028 1234567", True, "Mobile 028"),
        ("029 12345678", True, "Mobile 029"),
        ("03 123 4567", True, "Auckland landline"),
        ("04-123-4567", True, "Wellington landline"),
        ("09 123 4567", True, "Auckland landline"),
        ("+64 21 123 4567", True, "International mobile"),
        ("0064 21 123 4567", True, "International format"),

        # Invalid cases
        ("020 123 4567", False, "Invalid mobile prefix"),
        ("01 123 4567", False, "Invalid landline prefix"),
        ("123456", False, "Too short"),
        ("12345678901234", False, "Too long"),
        ("abc123def", False, "Non-numeric"),
        ("", False, "Empty string"),
    ]

    passed = 0
    failed = 0

    for phone, expected_valid, description in test_cases:
        is_valid, error = validate_nz_phone_number(phone)
        if is_valid == expected_valid:
            status = "✓"
            passed += 1
        else:
            status = "✗"
            failed += 1

        print(f"  {status} {description:30s} | {phone:20s} | {'Valid' if is_valid else f'Invalid: {error}'}")

    print(f"\n  Passed: {passed}/{len(test_cases)}, Failed: {failed}/{len(test_cases)}")
    return failed == 0


def test_register_requester_individual():
    """Test registering an individual requester"""
    print("\n" + "="*60)
    print("  TESTING INDIVIDUAL REQUESTER REGISTRATION")
    print("="*60)

    from councilsonline.api.auth import register_user

    test_email = f"test_auth_{random_string(8)}@example.com"

    try:
        result = register_user(
            email=test_email,
            first_name="John",
            last_name="Smith",
            phone="021 123 4567",
            password="TestPassword123!",
            user_role="requester",
            applicant_type="Individual",
            property_street="123 Main Street",
            property_suburb="Lower Hutt",
            property_city="Wellington",
            property_postcode="5010"
        )

        print(f"  ✓ User registered: {test_email}")
        print(f"  ✓ Success: {result.get('success')}")
        print(f"  ✓ Message: {result.get('message')}")

        # Verify user was created
        user = frappe.get_doc("User", test_email)
        print(f"  ✓ User found in database: {user.full_name}")
        print(f"  ✓ User type: {user.user_type}")

        # Check roles
        roles = [r.role for r in user.roles]
        print(f"  ✓ Roles assigned: {', '.join(roles)}")
        assert "Applicant" in roles, "Applicant role should be assigned"

        # Verify User Profile Extended
        profile = frappe.get_doc("User Profile Extended", {"user": test_email})
        print(f"  ✓ User Profile Extended created")
        print(f"  ✓ Profile role: {profile.user_role}")
        print(f"  ✓ Properties count: {len(profile.properties)}")

        # Verify property was added
        if profile.properties:
            prop = profile.properties[0]
            print(f"  ✓ Default property: {prop.street}, {prop.suburb}")

        return True

    except Exception as e:
        print(f"  ✗ Registration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_register_requester_company():
    """Test registering a company requester"""
    print("\n" + "="*60)
    print("  TESTING COMPANY REQUESTER REGISTRATION")
    print("="*60)

    from councilsonline.api.auth import register_user

    test_email = f"test_auth_{random_string(8)}@example.com"

    try:
        result = register_user(
            email=test_email,
            first_name="Jane",
            last_name="Doe",
            phone="04 123 4567",
            password="TestPassword123!",
            user_role="requester",
            applicant_type="Company",
            organization_name="Acme Construction Ltd",
            company_number="1234567"
        )

        print(f"  ✓ Company user registered: {test_email}")
        print(f"  ✓ Success: {result.get('success')}")

        # Verify user
        user = frappe.get_doc("User", test_email)
        print(f"  ✓ User: {user.full_name}")

        # Verify Organization was created
        if user.organization:
            org = frappe.get_doc("Organization", user.organization)
            print(f"  ✓ Organization created: {org.organization_name}")
            print(f"  ✓ Organization type: {org.organization_type}")
            print(f"  ✓ Company number: {org.company_number}")
        else:
            print(f"  ✗ Organization not linked to user")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Registration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_register_agent():
    """Test registering an agent"""
    print("\n" + "="*60)
    print("  TESTING AGENT REGISTRATION")
    print("="*60)

    from councilsonline.api.auth import register_agent

    test_email = f"test_auth_{random_string(8)}@example.com"

    try:
        result = register_agent(
            email=test_email,
            first_name="Bob",
            last_name="Builder",
            phone="027 123 4567",
            password="TestPassword123!",
            user_role="agent",
            agent_type="Sole Trader",
            business_street="456 Business Ave",
            business_suburb="Auckland Central",
            business_city="Auckland",
            business_postcode="1010"
        )

        print(f"  ✓ Agent registered: {test_email}")
        print(f"  ✓ Success: {result.get('success')}")

        # Verify user
        user = frappe.get_doc("User", test_email)
        print(f"  ✓ User: {user.full_name}")

        # Check roles - agents should have both Agent and Applicant
        roles = [r.role for r in user.roles]
        print(f"  ✓ Roles assigned: {', '.join(roles)}")
        assert "Agent" in roles, "Agent role should be assigned"
        assert "Applicant" in roles, "Applicant role should also be assigned"

        # Verify User Profile Extended with Agent role
        profile = frappe.get_doc("User Profile Extended", {"user": test_email})
        print(f"  ✓ Profile created with role: {profile.user_role}")
        assert profile.user_role == "Agent", "Profile should have Agent role"
        print(f"  ✓ Business type: {profile.business_type}")

        return True

    except Exception as e:
        print(f"  ✗ Agent registration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_register_agent_company():
    """Test registering an agent with company"""
    print("\n" + "="*60)
    print("  TESTING AGENT COMPANY REGISTRATION")
    print("="*60)

    from councilsonline.api.auth import register_agent

    test_email = f"test_auth_{random_string(8)}@example.com"

    try:
        result = register_agent(
            email=test_email,
            first_name="Sarah",
            last_name="Consultant",
            phone="022 987 6543",
            password="TestPassword123!",
            user_role="agent",
            agent_type="Company",
            company_name="Planning Consultants Ltd",
            company_number="9876543",
            nzbn="1234567890123",  # 13 digits
            business_street="789 Corporate Drive",
            business_suburb="Wellington CBD",
            business_city="Wellington",
            business_postcode="6011"
        )

        print(f"  ✓ Agent company registered: {test_email}")

        # Verify user
        user = frappe.get_doc("User", test_email)

        # Verify Organization
        if user.organization:
            org = frappe.get_doc("Organization", user.organization)
            print(f"  ✓ Agent organization: {org.organization_name}")
            print(f"  ✓ Organization type: {org.organization_type}")
            print(f"  ✓ Company number: {org.company_number}")
        else:
            print(f"  ✗ Organization not created")
            return False

        # Verify profile
        profile = frappe.get_doc("User Profile Extended", {"user": test_email})
        print(f"  ✓ Company name in profile: {profile.company_name}")
        print(f"  ✓ Business type: {profile.business_type}")

        return True

    except Exception as e:
        print(f"  ✗ Agent company registration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_duplicate_email():
    """Test that duplicate emails are rejected"""
    print("\n" + "="*60)
    print("  TESTING DUPLICATE EMAIL REJECTION")
    print("="*60)

    from councilsonline.api.auth import register_user

    test_email = f"test_auth_{random_string(8)}@example.com"

    try:
        # Register first user
        result1 = register_user(
            email=test_email,
            first_name="First",
            last_name="User",
            phone="021 111 1111",
            password="TestPassword123!"
        )
        print(f"  ✓ First registration successful")

        # Try to register with same email
        try:
            result2 = register_user(
                email=test_email,
                first_name="Second",
                last_name="User",
                phone="021 222 2222",
                password="TestPassword456!"
            )
            print(f"  ✗ Second registration should have failed but didn't!")
            return False
        except frappe.exceptions.ValidationError as e:
            print(f"  ✓ Duplicate email correctly rejected: {str(e)}")
            return True

    except Exception as e:
        print(f"  ✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_phone():
    """Test that invalid phone numbers are rejected"""
    print("\n" + "="*60)
    print("  TESTING INVALID PHONE NUMBER REJECTION")
    print("="*60)

    from councilsonline.api.auth import register_user

    test_email = f"test_auth_{random_string(8)}@example.com"

    invalid_phones = [
        ("123", "Too short"),
        ("abc123def", "Non-numeric"),
        ("020 123 4567", "Invalid mobile prefix"),
    ]

    passed = 0
    for phone, description in invalid_phones:
        try:
            register_user(
                email=f"test_{random_string(6)}@example.com",
                first_name="Test",
                last_name="User",
                phone=phone,
                password="TestPassword123!"
            )
            print(f"  ✗ {description}: Should have been rejected but wasn't")
        except frappe.exceptions.ValidationError:
            print(f"  ✓ {description}: Correctly rejected")
            passed += 1

    return passed == len(invalid_phones)


def test_invalid_nzbn():
    """Test that invalid NZBN is rejected"""
    print("\n" + "="*60)
    print("  TESTING INVALID NZBN REJECTION")
    print("="*60)

    from councilsonline.api.auth import register_agent

    try:
        register_agent(
            email=f"test_{random_string(8)}@example.com",
            first_name="Test",
            last_name="Agent",
            phone="021 123 4567",
            password="TestPassword123!",
            agent_type="Company",
            company_name="Test Company",
            nzbn="12345"  # Invalid - not 13 digits
        )
        print(f"  ✗ Invalid NZBN should have been rejected")
        return False
    except frappe.exceptions.ValidationError as e:
        print(f"  ✓ Invalid NZBN correctly rejected: {str(e)}")
        return True


def test_rate_limit():
    """Test rate limiting on registration"""
    print("\n" + "="*60)
    print("  TESTING RATE LIMITING (3 per 5 minutes)")
    print("="*60)

    from councilsonline.api.auth import register_user

    print("  Note: This test registers 3 users to test rate limiting")
    print("  The 4th registration should be blocked by rate limit")

    try:
        # Register 3 users (should succeed)
        for i in range(3):
            email = f"test_ratelimit_{random_string(8)}@example.com"
            register_user(
                email=email,
                first_name=f"User{i+1}",
                last_name="Test",
                phone=f"021 {100+i:03d} 4567",
                password="TestPassword123!"
            )
            print(f"  ✓ Registration {i+1}/3 successful")

        # 4th registration should fail due to rate limit
        try:
            email = f"test_ratelimit_{random_string(8)}@example.com"
            register_user(
                email=email,
                first_name="User4",
                last_name="Test",
                phone="021 999 4567",
                password="TestPassword123!"
            )
            print(f"  ✗ 4th registration should have been rate limited but wasn't")
            return False
        except Exception as e:
            if "rate limit" in str(e).lower():
                print(f"  ✓ Rate limit correctly enforced: {str(e)}")
                return True
            else:
                print(f"  ? 4th registration failed, but not due to rate limit: {str(e)}")
                return False

    except Exception as e:
        print(f"  ✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_user_profile_api():
    """Test user profile retrieval and update APIs"""
    print("\n" + "="*60)
    print("  TESTING USER PROFILE API")
    print("="*60)

    from councilsonline.api.auth import register_user, get_user_profile, update_user_profile

    test_email = f"test_auth_{random_string(8)}@example.com"

    try:
        # Register user
        register_user(
            email=test_email,
            first_name="Profile",
            last_name="Test",
            phone="021 123 4567",
            password="TestPassword123!"
        )
        print(f"  ✓ User registered")

        # Get profile
        frappe.set_user(test_email)  # Simulate logged-in user
        profile = get_user_profile()
        print(f"  ✓ Profile retrieved: {profile.get('full_name')}")
        print(f"  ✓ Email: {profile.get('email')}")
        print(f"  ✓ Account type: {profile.get('account_type')}")

        # Update profile
        update_result = update_user_profile(
            bio="Test bio for testing",
            location="Wellington, NZ"
        )
        print(f"  ✓ Profile updated: {update_result.get('message')}")

        # Verify update
        updated_profile = get_user_profile()
        assert updated_profile.get('bio') == "Test bio for testing"
        assert updated_profile.get('location') == "Wellington, NZ"
        print(f"  ✓ Bio: {updated_profile.get('bio')}")
        print(f"  ✓ Location: {updated_profile.get('location')}")

        frappe.set_user("Administrator")  # Reset to admin
        return True

    except Exception as e:
        frappe.set_user("Administrator")  # Reset to admin
        print(f"  ✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all authentication tests"""
    print("\n" + "="*60)
    print("  COUNCILSONLINE AUTHENTICATION API TEST SUITE")
    print("="*60)
    print(f"  Site: {frappe.local.site}")
    print(f"  Test started: {now()}")
    print("="*60)

    # Clean up any existing test users first
    cleanup_test_users()

    tests = [
        ("NZ Phone Validation", test_nz_phone_validation),
        ("Register Individual Requester", test_register_requester_individual),
        ("Register Company Requester", test_register_requester_company),
        ("Register Agent (Sole Trader)", test_register_agent),
        ("Register Agent Company", test_register_agent_company),
        ("Duplicate Email Rejection", test_duplicate_email),
        ("Invalid Phone Rejection", test_invalid_phone),
        ("Invalid NZBN Rejection", test_invalid_nzbn),
        ("Rate Limiting", test_rate_limit),
        ("User Profile API", test_user_profile_api),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            frappe.db.commit()  # Commit after each test
        except Exception as e:
            print(f"\n✗ {test_name} CRASHED: {str(e)}")
            results.append((test_name, False))
            frappe.db.rollback()

    # Print summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8s} | {test_name}")

    print("="*60)
    print(f"  Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("="*60)

    if failed == 0:
        print("  ✅ ALL TESTS PASSED!")
    else:
        print(f"  ⚠️  {failed} TEST(S) FAILED")

    print(f"\n  Test completed: {now()}")
    print("\n  Cleaning up test users...")
    cleanup_test_users()

    return failed == 0


if __name__ == "__main__":
    run_all_tests()
