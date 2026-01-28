# SPISC Council Staff End-to-End Documentation

This document describes the complete council staff workflow for processing SPISC (Social Pension for Indigent Senior Citizens) applications from receipt to payout completion.

## Table of Contents

1. [Staff Login & Dashboard Access](#1-staff-login--dashboard-access)
2. [Request Management Dashboard](#2-request-management-dashboard)
3. [Viewing SPISC Applications](#3-viewing-spisc-applications)
4. [Eligibility Assessment Workflow](#4-eligibility-assessment-workflow)
5. [Appointment Scheduling (Council Side)](#5-appointment-scheduling-council-side)
6. [Payout Processing](#6-payout-processing)
7. [API Reference](#7-api-reference)

---

## 1. Staff Login & Dashboard Access

### 1.1 Staff User Requirements

Council staff must have:
- **User Type**: "System User" (not Website User)
- **Enabled**: Account must be active
- **Roles**: Appropriate roles for access (e.g., "Council Staff", "Social Services Officer")

### 1.2 Login Process

**URL**: `/login`

Staff login using Frappe's standard authentication:

```
Email: staff@council.ph
Password: ********
```

### 1.3 Accessing the Internal Dashboard

**URL**: `/frontend/internal`

The Internal Request Management dashboard (`InternalRequestManagement.vue`) provides:
- Request overview with stats
- Filtering and search capabilities
- Assignment functionality
- Task management

### 1.4 Dashboard Navigation Tabs

| Tab | Description |
|-----|-------------|
| **All Requests** | View and manage all submitted requests |
| **My Tasks** | Personal task queue and assignments |
| **GIS Maps** | External link to property GIS viewer |
| **District Plan** | External link to district plan viewer |
| **Analytics** | Performance metrics (coming soon) |

---

## 2. Request Management Dashboard

### 2.1 Statistics Overview

The dashboard displays key metrics:

| Metric | Description |
|--------|-------------|
| **Total Requests** | All requests in the system |
| **New/Unassigned** | Requests without assigned staff |
| **In Progress** | Requests under active review |
| **RFI Issued** | Requests awaiting more information |
| **Completed** | Approved, declined, or withdrawn requests |

### 2.2 Filtering Options

Staff can filter requests by:
- **Search**: Request number, address, applicant name
- **Council**: Filter by council (multi-tenant support)
- **Status**: Submitted, Under Review, RFI Issued, Approved, Declined
- **Assigned To**: All Staff, Unassigned, Assigned to Me
- **Request Type**: Building Consent, Resource Consent, LIM, SPISC, etc.

### 2.3 Request Table Columns

| Column | Description |
|--------|-------------|
| Request | Request number and type |
| Council | Associated council |
| Applicant | Name and email |
| Address | Property address (if applicable) |
| Status | Current workflow state |
| Assigned To | Staff member responsible |
| Days Elapsed | Working days since submission |
| Actions | Assign, View buttons |

---

## 3. Viewing SPISC Applications

### 3.1 Opening a Request

Click on any request row or the "View" button to open the request detail view.

**Route**: `/frontend/internal/request/:id`

### 3.2 SPISC Application Data

The SPISC Application DocType contains:

```python
# Key Fields
- request: Link to parent Request
- full_name: Applicant's full name
- birth_date: Date of birth
- age: Calculated age (auto-computed)
- sex: Male/Female
- civil_status: Single/Married/Widowed/Divorced

# Address Information
- address_line: Street address
- barangay: Barangay name
- municipality: Municipality
- province: Province

# Household & Income
- household_size: Number in household
- living_arrangement: Living situation
- monthly_income: Monthly income in PHP
- income_source: Source of income
- is_4ps_beneficiary: Boolean

# Identity & Documents
- osca_id: OSCA ID number
- valid_ids: Attached documents

# Payment Preference
- payment_preference: "Office Pickup" or "Bank Transfer"
- bank_name: (if bank transfer)
- bank_account_number: (if bank transfer)

# Eligibility Assessment
- eligibility_status: Pending/Eligible/Ineligible
- assessed_by: Staff who assessed
- assessment_date: Date of assessment
- assessment_notes: Assessment notes
```

### 3.3 Eligibility Criteria

The system automatically checks:

1. **Age Requirement**: Must be 60 years or older
   ```python
   # Backend validation in spisc_application.py
   def check_eligibility_criteria(self):
       if self.age and self.age < 60:
           frappe.throw(
               "Applicant must be 60 years or older to be eligible for SPISC",
               title="Age Requirement Not Met"
           )
   ```

2. **Income Threshold**: Monthly income below PHP 10,000
   ```python
   if self.monthly_income and self.monthly_income >= 10000:
       # Flag for manual review
   ```

3. **4Ps Non-Beneficiary**: Cannot be receiving 4Ps benefits
4. **Residency**: Must reside in the municipality

---

## 4. Eligibility Assessment Workflow

### 4.1 Assessment Project

When a SPISC application is submitted, an Assessment Project is automatically created:

```python
# API: councilsonline.api.assessments.create_assessment_project_for_request
def create_assessment_project_for_request(request, request_type):
    # Check if Assessment Project already exists
    existing = frappe.db.exists("Assessment Project", {"request": request})
    if existing:
        return frappe.get_doc("Assessment Project", existing)

    # Get Assessment Template for SPISC
    template = frappe.db.get_value("Assessment Template",
        {"request_type": request_type}, "name")

    # Create Assessment Project
    assessment_project = frappe.get_doc({
        "doctype": "Assessment Project",
        "request": request,
        "assessment_template": template,
        "status": "Not Started"
    })
    assessment_project.insert(ignore_permissions=True)
```

### 4.2 Assessment Stages

The Assessment Project progresses through stages:

| Stage | Description |
|-------|-------------|
| **Document Review** | Verify submitted documents |
| **Eligibility Check** | Validate age, income, residency |
| **KYC Verification** | Identity verification |
| **Home Visit** | (Optional) Site verification |
| **Final Approval** | Management sign-off |

### 4.3 Staff Assessment Actions

**Updating Eligibility Status:**

```python
# Staff updates SPISC Application
spisc_app = frappe.get_doc("SPISC Application", app_name)
spisc_app.eligibility_status = "Eligible"  # or "Ineligible"
spisc_app.assessed_by = frappe.session.user
spisc_app.assessment_date = frappe.utils.today()
spisc_app.assessment_notes = "Applicant meets all eligibility criteria"
spisc_app.save()
```

### 4.4 KYC Verification

The social services API provides KYC verification:

```python
# API: councilsonline.api.social_services.verify_kyc
@frappe.whitelist()
def verify_kyc(application_id, verification_result, notes=None):
    """
    Verify KYC submission

    Args:
        application_id: SPISC Application ID
        verification_result: "Approved" or "Rejected"
        notes: Verification notes
    """
```

### 4.5 Eligibility Engine

The system includes an eligibility calculation engine:

```python
# API: councilsonline.api.social_services.calculate_eligibility
@frappe.whitelist()
def calculate_eligibility(application_id):
    """
    Calculate eligibility based on configured rules

    Checks:
    - Age >= 60
    - Income < poverty threshold
    - Not 4Ps beneficiary
    - Residency requirements
    """
```

**Override Capability:**

```python
# API: councilsonline.api.social_services.override_eligibility
@frappe.whitelist()
def override_eligibility(application_id, new_status, reason, authorized_by):
    """
    Override calculated eligibility (requires authorization)
    """
```

---

## 5. Appointment Scheduling (Council Side)

### 5.1 Team Configuration

Council teams are configured for scheduling:

```python
# API: councilsonline.api.scheduling.get_team_config
{
    "team_code": "SOCIAL_SERVICES",
    "team_name": "Social Services",
    "duration_minutes": 30,
    "available_durations": [15, 30, 45, 60],
    "buffer_time": 15,
    "advance_booking_days": 30,
    "min_notice_hours": 24,
    "max_daily_appointments": 20,
    "default_location": "Municipal Hall",
    "locations": ["Municipal Hall", "Barangay Hall", "Satellite Office"]
}
```

### 5.2 Viewing Appointments

Staff can view booked appointments:

```python
# API: councilsonline.api.scheduling.get_available_slots
response = get_available_slots(
    team_code="SOCIAL_SERVICES",
    start_date="2026-02-01",
    end_date="2026-02-14",
    duration_minutes=30
)

# Returns:
{
    "success": True,
    "slots_by_date": {
        "2026-02-03": {
            "date": "2026-02-03",
            "day": "Tuesday",
            "slots": [
                {
                    "start": "2026-02-03T09:00:00",
                    "end": "2026-02-03T09:30:00",
                    "start_display": "09:00 AM",
                    "end_display": "09:30 AM"
                }
            ]
        }
    }
}
```

### 5.3 Appointment Management

**Viewing Appointment Details:**

```python
# API: councilsonline.api.scheduling.get_appointment
get_appointment(appointment_id="APT-2026-00001")
```

**Cancelling Appointments:**

```python
# API: councilsonline.api.scheduling.cancel_appointment
cancel_appointment(
    appointment_id="APT-2026-00001",
    reason="Beneficiary requested reschedule"
)
```

### 5.4 Completing Pickup Appointments

When beneficiary arrives for pickup:

```python
# Update appointment status
appointment = frappe.get_doc("Scheduled Appointment", appointment_id)
appointment.status = "Completed"
appointment.completed_at = frappe.utils.now_datetime()
appointment.completed_by = frappe.session.user
appointment.save()
```

---

## 6. Payout Processing

### 6.1 Payout Creation

When a SPISC beneficiary is approved and arrives for pickup:

```python
# API: councilsonline.api.payments.create_payout
@frappe.whitelist()
def create_payout(
    spisc_application,
    beneficiary_name,
    payout_amount,
    payout_method,
    period_start=None,
    period_end=None
):
    """
    Create a benefit payout record

    Args:
        spisc_application: SPISC Application ID
        beneficiary_name: Beneficiary's full name
        payout_amount: Amount in PHP (typically 500)
        payout_method: "Cash - Office Pickup" or "Bank Transfer"
    """
```

### 6.2 Payout Batch Processing

For bulk payouts:

```python
# API: councilsonline.api.payments.create_payout_batch
@frappe.whitelist()
def create_payout_batch(
    batch_name,
    payout_date,
    payout_method,
    beneficiary_list
):
    """
    Create a batch of payouts for multiple beneficiaries
    """
```

### 6.3 Bank File Generation

For bank transfers:

```python
# API: councilsonline.api.payments.generate_bank_file
@frappe.whitelist()
def generate_bank_file(batch_id, bank_format="PH_INSTAPAY"):
    """
    Generate bank payment file for batch transfer

    Supported formats:
    - PH_INSTAPAY: InstaPay format
    - PH_PESONET: PESONet format
    """
```

### 6.4 Payout Approval

```python
# API: councilsonline.api.payments.approve_payout_batch
@frappe.whitelist()
def approve_payout_batch(batch_id, approved_by, approval_notes=None):
    """
    Approve a payout batch for processing
    """
```

### 6.5 Recording Cash Pickup

When beneficiary collects cash:

```python
# Create payout record
payout = frappe.get_doc({
    "doctype": "Benefit Payout",
    "spisc_application": spisc_app_name,
    "beneficiary_name": "Juan Dela Cruz",
    "payout_amount": 500,  # PHP 500 monthly pension
    "payout_date": frappe.utils.today(),
    "payout_method": "Cash - Office Pickup",
    "status": "Paid",
    "collected_by": "Juan Dela Cruz",
    "collected_date": frappe.utils.now_datetime(),
    "disbursed_by": frappe.session.user
})
payout.insert()
```

---

## 7. API Reference

### 7.1 Council APIs

| Endpoint | Description |
|----------|-------------|
| `get_staff_users` | Get list of staff users with roles |
| `get_council_stats` | Get council statistics |
| `get_council_requests` | Get requests for specific council |

### 7.2 Request APIs

| Endpoint | Description |
|----------|-------------|
| `assign_request` | Assign request to staff member |
| `get_request_summary_data` | Get request summary metrics |
| `send_request_notification` | Send notification to applicant |
| `add_internal_note` | Add internal staff note |

### 7.3 Assessment APIs

| Endpoint | Description |
|----------|-------------|
| `create_assessment_project_for_request` | Create assessment project |
| `get_spisc_summary_data` | Get SPISC dashboard summary |
| `get_assessment_templates` | List assessment templates |
| `load_assessment_template` | Load specific template |

### 7.4 Scheduling APIs

| Endpoint | Description |
|----------|-------------|
| `get_team_config` | Get team scheduling config |
| `get_available_slots` | Get available time slots |
| `book_appointment` | Book an appointment |
| `cancel_appointment` | Cancel appointment |
| `get_appointment` | Get appointment details |
| `get_user_appointments` | Get user's appointments |

### 7.5 Payment APIs

| Endpoint | Description |
|----------|-------------|
| `create_payout` | Create single payout |
| `create_payout_batch` | Create batch payout |
| `generate_bank_file` | Generate bank transfer file |
| `approve_payout_batch` | Approve batch for processing |
| `add_to_masterlist` | Add beneficiary to masterlist |

### 7.6 Social Services APIs

| Endpoint | Description |
|----------|-------------|
| `submit_kyc_verification` | Submit KYC documents |
| `verify_kyc` | Verify KYC submission |
| `check_kyc_status` | Check KYC status |
| `calculate_eligibility` | Calculate eligibility |
| `override_eligibility` | Override eligibility decision |
| `run_fraud_check` | Run fraud detection |
| `check_duplicate_application` | Check for duplicates |
| `detect_identity_fraud` | Detect identity fraud |

---

## 8. Complete Staff Workflow Summary

### Step-by-Step Process

```
1. RECEIVE APPLICATION
   ├── Application appears in "All Requests" tab
   ├── Status: "Submitted"
   └── Unassigned

2. ASSIGN TO STAFF
   ├── Click "Assign" button
   ├── Select staff member
   └── Add assignment notes

3. INITIAL REVIEW
   ├── Open request detail view
   ├── Review submitted documents
   ├── Check completeness
   └── Request additional info if needed (RFI)

4. ELIGIBILITY ASSESSMENT
   ├── Verify age (60+)
   ├── Verify income (below threshold)
   ├── Check 4Ps status
   ├── Verify residency
   └── Update eligibility_status

5. KYC VERIFICATION
   ├── Verify identity documents
   ├── Cross-check with OSCA records
   └── Update KYC status

6. FINAL APPROVAL
   ├── Review assessment
   ├── Approve/Decline
   └── Update workflow state

7. SCHEDULE PICKUP (if Office Pickup)
   ├── View available slots
   ├── Confirm with beneficiary
   └── Book appointment

8. PROCESS PAYOUT
   ├── Create payout record
   ├── For cash: Record collection
   ├── For bank: Generate bank file
   └── Mark as Paid

9. COMPLETE
   ├── Update request status
   └── Archive/close case
```

---

## 9. Testing the Council Staff Workflow

### Running E2E Tests

```bash
# Run SPISC E2E tests
bench --site councilsonline.localhost run-tests \
  --app councilsonline \
  --module councilsonline.tests.test_spisc_e2e

# Run manual test script
bench --site councilsonline.localhost execute \
  councilsonline.tests.test_spisc_e2e.run_spisc_e2e_manual
```

### Test Data

See `councilsonline/tests/test_spisc_e2e.py` for:
- Test user creation
- SPISC application submission
- Staff processing simulation
- Payout completion

---

## 10. Related Documentation

- [SPISC User E2E Documentation](./SPISC_E2E_TEST_DOCUMENTATION.md) - Applicant-side workflow
- [Test Helpers](../frappe-bench/apps/councilsonline/councilsonline/tests/test_helpers.py) - Test utilities

---

*Last Updated: January 2026*
*Version: 1.0*
