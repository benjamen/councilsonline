#!/usr/bin/env python3
"""
Create SPISC test data in various workflow states
Run with: bench --site councilsonline.localhost execute councilsonline.councilsonline.fixtures.spisc_test_data.create_test_applications
"""

import frappe
from frappe.utils import getdate, add_days, now_datetime
from datetime import datetime


def create_test_applications():
    """Create SPISC applications in different workflow states for testing"""

    print("\n" + "="*80)
    print("CREATING SPISC TEST DATA")
    print("="*80 + "\n")

    # Get or create TAYTAY-PH council
    council = frappe.db.get_value('Council', {'name': 'TAYTAY-PH'}, 'name')
    if not council:
        print("⚠ Council TAYTAY-PH not found, using default")
        council = frappe.db.get_value('Council', {}, 'name')

    # Get SPISC request type
    request_type = frappe.db.get_value(
        'Request Type',
        {'name': ['like', '%SPISC%']},
        'name'
    )
    if not request_type:
        print("⚠ SPISC request type not found")
        return

    print(f"Using Request Type: {request_type}")
    print(f"Using Council: {council}\n")

    # Test data for applications
    test_applicants = [
        {
            "applicant_name": "Maria Santos Cruz",
            "birth_date": "1960-01-15",
            "email": "maria.cruz@test.ph",
            "phone": "+639171234501",
            "workflow_state": "Submitted",
            "address_line": "123 Rizal Street",
            "barangay": "San Juan",
            "sex": "Female",
            "civil_status": "Widowed"
        },
        {
            "applicant_name": "Juan dela Rosa",
            "birth_date": "1958-05-20",
            "email": "juan.delarosa@test.ph",
            "phone": "+639171234502",
            "workflow_state": "Acknowledged",
            "address_line": "456 Bonifacio Avenue",
            "barangay": "Dolores",
            "sex": "Male",
            "civil_status": "Married"
        },
        {
            "applicant_name": "Luisa Fernandez Reyes",
            "birth_date": "1962-03-10",
            "email": "luisa.reyes@test.ph",
            "phone": "+639171234503",
            "workflow_state": "Processing",
            "address_line": "789 Mabini Street",
            "barangay": "Muzon",
            "sex": "Female",
            "civil_status": "Single"
        },
        {
            "applicant_name": "Pedro Garcia Santos",
            "birth_date": "1959-11-30",
            "email": "pedro.santos@test.ph",
            "phone": "+639171234504",
            "workflow_state": "Processing",
            "address_line": "321 Luna Avenue",
            "barangay": "San Isidro",
            "sex": "Male",
            "civil_status": "Widowed"
        }
    ]

    created_count = 0

    for applicant_data in test_applicants:
        try:
            applicant_name = applicant_data["applicant_name"]
            workflow_state = applicant_data["workflow_state"]

            # Check if already exists
            existing = frappe.db.exists(
                'Request',
                {
                    'requester_name': applicant_name,
                    'request_type': request_type
                }
            )

            if existing:
                print(f"✓ Application for {applicant_name} already exists ({existing})")
                continue

            # Create Request
            request = frappe.get_doc({
                'doctype': 'Request',
                'request_type': request_type,
                'council': council,
                'requester': 'test.applicant@test.ph',  # Required field
                'requester_name': applicant_data["applicant_name"],
                'requester_email': applicant_data["email"],
                'requester_phone': applicant_data["phone"],
                'brief_description': f"Social Pension application for {applicant_data['applicant_name']}",  # Required field
                'submitted_date': now_datetime(),
                'workflow_state': 'Draft',
                'status': 'Draft'
            })
            request.insert(ignore_permissions=True)
            frappe.db.commit()

            # Create SPISC Application
            spisc_app = frappe.get_doc({
                'doctype': 'SPISC Application',
                'request': request.name,

                # Personal Information
                'birth_date': getdate(applicant_data["birth_date"]),
                'sex': applicant_data["sex"],
                'civil_status': applicant_data["civil_status"],

                # Address
                'address_line': applicant_data["address_line"],
                'barangay': applicant_data["barangay"],
                'municipality': 'Taytay',
                'province': 'Rizal',

                # Household
                'household_size': 2,
                'living_arrangement': 'Living with children',

                # Economic
                'monthly_income': 3000.00,
                'income_source': 'Family support',
                'is_4ps_beneficiary': 0,

                # Identity
                'philsys_id': f'1234-5678-{created_count + 1:04d}',

                # Required documents (dummy paths)
                'barangay_cert_indigency': '/files/test_cert.pdf',
                'birth_certificate': '/files/test_birth.pdf',
                'valid_id_copy': '/files/test_id.pdf',
                'recent_photo': '/files/test_photo.jpg',

                # Declarations
                'declaration_truth': 1,
                'declaration_consent': 1,
                'signature': '/files/test_signature.png',
                'signature_date': getdate(),

                # Eligibility (for backend testing)
                'eligibility_status': 'Pending'
            })
            spisc_app.insert(ignore_permissions=True)
            frappe.db.commit()

            # Progress workflow to target state
            if workflow_state != 'Draft':
                # Submit
                request.workflow_state = 'Submitted'
                request.save(ignore_permissions=True)
                frappe.db.commit()

            if workflow_state == 'Acknowledged':
                # Acknowledge
                request.workflow_state = 'Acknowledged'
                request.acknowledged_date = now_datetime()
                request.save(ignore_permissions=True)
                frappe.db.commit()

                # Trigger assessment project creation
                try:
                    request.auto_create_assessment_project()
                    print(f"  ✓ Assessment project created for {applicant_name}")
                except Exception as e:
                    print(f"  ⚠ Assessment project creation failed: {str(e)}")

            if workflow_state == 'Processing':
                # Acknowledge first
                request.workflow_state = 'Acknowledged'
                request.acknowledged_date = now_datetime()
                request.save(ignore_permissions=True)
                frappe.db.commit()

                # Try to create assessment project
                try:
                    request.auto_create_assessment_project()
                except:
                    pass

                # Then move to Processing
                request.workflow_state = 'Processing'
                request.save(ignore_permissions=True)
                frappe.db.commit()

            print(f"✓ Created SPISC application: {request.name} - {applicant_name} ({workflow_state})")
            created_count += 1

        except Exception as e:
            print(f"✗ Error creating application for {applicant_data['applicant_name']}: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n✓ Created {created_count} new SPISC test applications")
    print("="*80 + "\n")

    return created_count


if __name__ == "__main__":
    create_test_applications()
