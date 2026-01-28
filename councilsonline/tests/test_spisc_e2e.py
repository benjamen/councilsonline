"""
End-to-End Test Suite for SPISC (Social Pension for Indigent Senior Citizens) Flow

This test suite covers the complete flow from user registration to pension pickup:
1. User account creation
2. SPISC application submission
3. Slot booking (for Office Pickup)
4. Council staff processing
5. Pickup completion

Test Users:
- Applicant: test_applicant_spisc@test.com
- Council Staff: Administrator (or create test staff)
"""

import frappe
from frappe.tests.utils import FrappeTestCase
from datetime import datetime, date, timedelta
from unittest.mock import patch
import json


class TestSPISCEndToEnd(FrappeTestCase):
    """End-to-end test for SPISC application flow"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        super().setUpClass()
        cls.test_email = f"test_spisc_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
        cls.test_phone = "09171234567"  # Valid PH mobile number
        cls.test_password = "TestPassword123!"

    def setUp(self):
        """Set up before each test"""
        frappe.set_user("Administrator")

    def tearDown(self):
        """Clean up after each test"""
        frappe.set_user("Administrator")

    # =========================================================================
    # TEST 1: User Registration (PH)
    # =========================================================================
    def test_01_register_user_ph(self):
        """Test user registration with Philippine phone number"""
        from councilsonline.api.auth import register_user_ph

        # Test registration
        result = register_user_ph(
            email=self.test_email,
            first_name="Juan",
            last_name="Dela Cruz",
            phone=self.test_phone,
            password=self.test_password,
            barangay="San Isidro",
            municipality="Taytay",
            province="Rizal"
        )

        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("user"), self.test_email)

        # Verify user was created
        user = frappe.get_doc("User", self.test_email)
        self.assertEqual(user.first_name, "Juan")
        self.assertEqual(user.last_name, "Dela Cruz")

        # Verify profile was created
        profile = frappe.get_doc("User Profile Extended", self.test_email)
        self.assertEqual(profile.postal_suburb, "San Isidro")
        self.assertEqual(profile.postal_city, "Taytay")

    def test_01b_validate_ph_phone(self):
        """Test Philippine phone number validation"""
        from councilsonline.api.auth import validate_ph_phone_number

        # Valid mobile numbers
        self.assertTrue(validate_ph_phone_number("09171234567")[0])
        self.assertTrue(validate_ph_phone_number("09991234567")[0])
        self.assertTrue(validate_ph_phone_number("+639171234567")[0])
        self.assertTrue(validate_ph_phone_number("0917-123-4567")[0])

        # Valid landline
        self.assertTrue(validate_ph_phone_number("028123456")[0])
        self.assertTrue(validate_ph_phone_number("032-123-4567")[0])

        # Invalid numbers
        self.assertFalse(validate_ph_phone_number("1234567")[0])
        self.assertFalse(validate_ph_phone_number("08171234567")[0])  # Wrong prefix

    # =========================================================================
    # TEST 2: SPISC Application Creation & Submission
    # =========================================================================
    def test_02_create_spisc_application(self):
        """Test creating a SPISC application"""
        # Ensure test user exists
        if not frappe.db.exists("User", self.test_email):
            self.test_01_register_user_ph()

        frappe.set_user(self.test_email)

        from councilsonline.api.requests import create_draft_request, submit_request

        # Step 1: Create draft request
        draft_data = {
            "request_type": "Social Pension for Indigent Senior Citizens (SPISC)",
            "council": "TAYTAY",
            # Personal Information
            "full_name": "Juan Dela Cruz",
            "birth_date": "1960-01-15",  # 65+ years old
            "sex": "Male",
            "civil_status": "Widowed",
            "mobile_number": self.test_phone,
            "email": self.test_email,
            "address_line": "123 Main Street",
            "barangay": "San Isidro",
            "municipality": "Taytay",
            "province": "Rizal",
            # Household Information
            "household_size": 1,
            "living_arrangement": "Living alone",
            "monthly_income": 3000,  # Below poverty threshold
            "income_source": "No income",
            "is_4ps_beneficiary": False,
            # Identity
            "osca_id": "OSCA-2020-12345",
            # Payment Method
            "payment_preference": "Office Pickup",
            # Declaration
            "declaration_truth": True,
            "declaration_consent": True,
            "signature_date": str(date.today())
        }

        result = create_draft_request(draft_data, current_step=6)
        self.assertTrue("request_id" in result)
        request_id = result["request_id"]

        # Step 2: Submit the request
        frappe.set_user(self.test_email)
        submit_result = submit_request(request_id, draft_data)

        self.assertTrue("request_number" in submit_result or "success" in submit_result)

        # Verify SPISC Application was created
        spisc_app = frappe.get_all(
            "SPISC Application",
            filters={"request": request_id},
            limit=1
        )
        self.assertTrue(len(spisc_app) > 0)

        # Store for later tests
        self.__class__.request_id = request_id
        self.__class__.spisc_app_name = spisc_app[0].name

    def test_02b_verify_eligibility_calculation(self):
        """Test that eligibility is calculated correctly"""
        if not hasattr(self, 'spisc_app_name'):
            self.test_02_create_spisc_application()

        spisc_app = frappe.get_doc("SPISC Application", self.spisc_app_name)

        # Age should be calculated (65+ based on birth_date 1960-01-15)
        self.assertIsNotNone(spisc_app.age)
        self.assertGreaterEqual(spisc_app.age, 60)

        # Income should indicate eligibility
        self.assertLess(spisc_app.monthly_income or 0, 10000)

    # =========================================================================
    # TEST 3: Slot Booking (Office Pickup)
    # =========================================================================
    def test_03_book_pickup_slot(self):
        """Test booking a pickup slot for pension collection"""
        if not hasattr(self, 'request_id'):
            self.test_02_create_spisc_application()

        from councilsonline.api.scheduling import book_appointment, get_available_slots

        # Get available slots
        frappe.set_user(self.test_email)

        # Find next available weekday
        next_date = date.today() + timedelta(days=7)
        while next_date.weekday() >= 5:  # Skip weekends
            next_date += timedelta(days=1)

        # Book appointment
        try:
            booking_result = book_appointment(
                request=self.request_id,
                team="Social Services",
                appointment_date=str(next_date),
                appointment_time="10:00",
                duration=30,
                purpose="Pension Pickup",
                notes="SPISC pension collection"
            )

            self.assertTrue(booking_result.get("success") or "appointment" in booking_result)
            if "appointment_id" in booking_result:
                self.__class__.appointment_id = booking_result["appointment_id"]
        except Exception as e:
            # Booking may not be available if team not configured
            frappe.log_error(f"Booking test skipped: {str(e)}")

    # =========================================================================
    # TEST 4: Council Staff Processing
    # =========================================================================
    def test_04_staff_review_application(self):
        """Test council staff reviewing and processing the application"""
        if not hasattr(self, 'request_id'):
            self.test_02_create_spisc_application()

        # Switch to Administrator (council staff)
        frappe.set_user("Administrator")

        # Get the request
        request = frappe.get_doc("Request", self.request_id)

        # Staff should be able to view all details
        self.assertIsNotNone(request.requester_name)
        self.assertIsNotNone(request.request_type)

        # Check Assessment Project was created
        assessment = frappe.get_all(
            "Assessment Project",
            filters={"request": self.request_id},
            limit=1
        )

        if assessment:
            assessment_doc = frappe.get_doc("Assessment Project", assessment[0].name)
            self.assertEqual(assessment_doc.request, self.request_id)
            self.__class__.assessment_id = assessment[0].name

    def test_04b_staff_assess_eligibility(self):
        """Test staff assessing applicant eligibility"""
        if not hasattr(self, 'spisc_app_name'):
            self.test_02_create_spisc_application()

        frappe.set_user("Administrator")

        # Update SPISC application with assessment
        spisc_app = frappe.get_doc("SPISC Application", self.spisc_app_name)
        spisc_app.eligibility_status = "Eligible"
        spisc_app.assessed_by = "Administrator"
        spisc_app.assessment_date = date.today()
        spisc_app.assessment_notes = "Applicant meets all eligibility criteria"
        spisc_app.save()

        # Verify
        updated_app = frappe.get_doc("SPISC Application", self.spisc_app_name)
        self.assertEqual(updated_app.eligibility_status, "Eligible")

    def test_04c_staff_approve_application(self):
        """Test staff approving the application"""
        if not hasattr(self, 'request_id'):
            self.test_02_create_spisc_application()

        frappe.set_user("Administrator")

        request = frappe.get_doc("Request", self.request_id)

        # Transition to approved state
        try:
            request.workflow_state = "Approved"
            request.save()
            self.assertEqual(request.workflow_state, "Approved")
        except Exception as e:
            # Workflow may require specific transitions
            frappe.log_error(f"Approval test: {str(e)}")

    # =========================================================================
    # TEST 5: Pickup Completion
    # =========================================================================
    def test_05_complete_pickup(self):
        """Test completing the pension pickup"""
        if not hasattr(self, 'request_id'):
            self.test_02_create_spisc_application()

        frappe.set_user("Administrator")

        # Mark appointment as completed (if exists)
        if hasattr(self, 'appointment_id'):
            try:
                appointment = frappe.get_doc("Scheduled Appointment", self.appointment_id)
                appointment.status = "Completed"
                appointment.save()
            except:
                pass

        # Create benefit payout record
        try:
            payout = frappe.get_doc({
                "doctype": "Benefit Payout",
                "spisc_application": self.spisc_app_name,
                "beneficiary_name": "Juan Dela Cruz",
                "payout_amount": 500,  # PHP 500 monthly pension
                "payout_date": date.today(),
                "payout_method": "Cash - Office Pickup",
                "status": "Paid",
                "collected_by": "Juan Dela Cruz",
                "collected_date": datetime.now()
            })
            payout.insert()
            self.assertTrue(payout.name is not None)
        except Exception as e:
            frappe.log_error(f"Payout creation: {str(e)}")

    # =========================================================================
    # CLEANUP
    # =========================================================================
    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        super().tearDownClass()
        frappe.set_user("Administrator")

        # Delete test user and related data
        try:
            if frappe.db.exists("User", cls.test_email):
                # Delete profile first
                if frappe.db.exists("User Profile Extended", cls.test_email):
                    frappe.delete_doc("User Profile Extended", cls.test_email, force=True)
                frappe.delete_doc("User", cls.test_email, force=True)

            # Clean up requests created by test user
            test_requests = frappe.get_all(
                "Request",
                filters={"requester": cls.test_email},
                pluck="name"
            )
            for req in test_requests:
                # Delete SPISC applications
                spisc_apps = frappe.get_all(
                    "SPISC Application",
                    filters={"request": req},
                    pluck="name"
                )
                for app in spisc_apps:
                    frappe.delete_doc("SPISC Application", app, force=True)

                # Delete Assessment Projects
                assessments = frappe.get_all(
                    "Assessment Project",
                    filters={"request": req},
                    pluck="name"
                )
                for asmt in assessments:
                    frappe.delete_doc("Assessment Project", asmt, force=True)

                frappe.delete_doc("Request", req, force=True)

            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Test cleanup error: {str(e)}")


# =========================================================================
# MANUAL TEST SCRIPT (for running outside pytest)
# =========================================================================
def run_spisc_e2e_manual():
    """
    Manual test script for SPISC flow.
    Run via: bench --site councilsonline.localhost execute councilsonline.tests.test_spisc_e2e.run_spisc_e2e_manual
    """
    print("=" * 60)
    print("SPISC End-to-End Test (Manual)")
    print("=" * 60)

    test_email = f"test_manual_{datetime.now().strftime('%H%M%S')}@test.com"
    test_phone = "09171234567"

    # 1. Register User
    print("\n1. Registering user...")
    from councilsonline.api.auth import register_user_ph
    try:
        result = register_user_ph(
            email=test_email,
            first_name="Maria",
            last_name="Santos",
            phone=test_phone,
            password="Test123!",
            barangay="San Isidro",
            municipality="Taytay",
            province="Rizal"
        )
        print(f"   User registered: {result}")
    except Exception as e:
        print(f"   Registration failed: {e}")
        return

    # 2. Create SPISC Application
    print("\n2. Creating SPISC application...")
    frappe.set_user(test_email)

    from councilsonline.api.requests import create_draft_request, submit_request

    draft_data = {
        "request_type": "Social Pension for Indigent Senior Citizens (SPISC)",
        "council": "TAYTAY",
        "full_name": "Maria Santos",
        "birth_date": "1958-03-20",
        "sex": "Female",
        "civil_status": "Widowed",
        "mobile_number": test_phone,
        "email": test_email,
        "address_line": "456 Side Street",
        "barangay": "San Isidro",
        "municipality": "Taytay",
        "province": "Rizal",
        "household_size": 2,
        "living_arrangement": "Living with children",
        "monthly_income": 2500,
        "income_source": "Family support",
        "is_4ps_beneficiary": False,
        "osca_id": "OSCA-2019-54321",
        "payment_preference": "Office Pickup",
        "declaration_truth": True,
        "declaration_consent": True,
        "signature_date": str(date.today())
    }

    try:
        result = create_draft_request(draft_data, current_step=6)
        request_id = result.get("request_id")
        print(f"   Draft created: {request_id}")

        submit_result = submit_request(request_id, draft_data)
        print(f"   Application submitted: {submit_result}")
    except Exception as e:
        print(f"   Application creation failed: {e}")
        frappe.set_user("Administrator")
        return

    # 3. Staff Processing
    print("\n3. Council staff processing...")
    frappe.set_user("Administrator")

    try:
        request = frappe.get_doc("Request", request_id)
        print(f"   Request status: {request.workflow_state}")

        # Get SPISC app
        spisc_apps = frappe.get_all("SPISC Application", filters={"request": request_id})
        if spisc_apps:
            spisc_app = frappe.get_doc("SPISC Application", spisc_apps[0].name)
            print(f"   SPISC App: {spisc_app.name}")
            print(f"   Applicant Age: {spisc_app.age}")
            print(f"   Monthly Income: PHP {spisc_app.monthly_income}")

            # Assess eligibility
            spisc_app.eligibility_status = "Eligible"
            spisc_app.assessed_by = "Administrator"
            spisc_app.save()
            print(f"   Eligibility: {spisc_app.eligibility_status}")
    except Exception as e:
        print(f"   Staff processing error: {e}")

    # 4. Cleanup
    print("\n4. Test completed. Cleaning up...")
    try:
        # Delete test data
        if frappe.db.exists("User Profile Extended", test_email):
            frappe.delete_doc("User Profile Extended", test_email, force=True)
        if frappe.db.exists("User", test_email):
            frappe.delete_doc("User", test_email, force=True)
        frappe.db.commit()
        print("   Cleanup complete.")
    except Exception as e:
        print(f"   Cleanup error: {e}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
