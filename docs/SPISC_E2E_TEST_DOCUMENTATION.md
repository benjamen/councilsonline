# SPISC End-to-End Test Documentation

## Overview

This document describes the complete end-to-end testing process for the Social Pension for Indigent Senior Citizens (SPISC) application flow in CouncilsOnline.

**Version:** 1.0
**Last Updated:** January 2026
**Author:** Claude AI

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Test Flow Overview](#test-flow-overview)
3. [User Perspective Tests](#user-perspective-tests)
4. [Council Staff Perspective Tests](#council-staff-perspective-tests)
5. [API Endpoints](#api-endpoints)
6. [Running Tests](#running-tests)
7. [Test Data](#test-data)

---

## System Requirements

### Prerequisites
- Bench running with `councilsonline.localhost` site
- Redis and MariaDB services running
- SPISC request type installed (via `ph_social_services` config pack)

### Start Services
```bash
cd /workspace/development/frappe-bench
bench start
```

---

## Test Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SPISC APPLICATION FLOW                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  USER PERSPECTIVE                     COUNCIL STAFF PERSPECTIVE          │
│  ────────────────                     ─────────────────────────          │
│                                                                          │
│  1. Create Account ─────────────────────────────────────────────────────│
│     └─ register_user_ph()                                               │
│                                                                          │
│  2. Start SPISC Application ────────────────────────────────────────────│
│     └─ Select "SPISC" request type                                      │
│     └─ create_draft_request()                                           │
│                                                                          │
│  3. Complete Wizard Steps ──────────────────────────────────────────────│
│     ├─ Step 1: Personal Information                                     │
│     ├─ Step 2: Household Information                                    │
│     ├─ Step 3: Identity Verification                                    │
│     ├─ Step 4: Supporting Documents                                     │
│     ├─ Step 5: Payment Method                                           │
│     └─ Step 6: Declaration & Review                                     │
│                                                                          │
│  4. Submit Application ─────────────────────────────────────────────────│
│     └─ submit_request()                         3. Receive Application  │
│                                                    └─ Dashboard shows   │
│                                                       new submission    │
│                                                                          │
│                                                 4. Review & Assess      │
│                                                    ├─ Verify documents  │
│                                                    ├─ Check eligibility │
│                                                    └─ Update SPISC app  │
│                                                                          │
│  5. Book Pickup Slot (if Office Pickup) ────────────────────────────────│
│     └─ book_appointment()                       5. Confirm Appointment  │
│                                                    └─ schedule_meeting()│
│                                                                          │
│  6. Collect Pension ────────────────────────────────────────────────────│
│     └─ Visit office                             6. Process Payout       │
│                                                    ├─ Verify identity   │
│                                                    ├─ Record payout     │
│                                                    └─ Complete pickup   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## User Perspective Tests

### Test 1: Create User Account

**Endpoint:** `POST /api/method/councilsonline.api.auth.register_user_ph`

**Test Data:**
```json
{
  "email": "test_user@test.com",
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "phone": "09171234567",
  "password": "SecurePass123!",
  "barangay": "San Isidro",
  "municipality": "Taytay",
  "province": "Rizal"
}
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Account created successfully. You can now log in.",
  "user": "test_user@test.com"
}
```

**Verification Steps:**
1. User document created in `tabUser`
2. User Profile Extended created with address details
3. User has "Applicant" role assigned

---

### Test 2: Create SPISC Application Draft

**Endpoint:** `POST /api/method/councilsonline.api.requests.create_draft_request`

**Prerequisites:**
- User logged in
- SPISC request type exists

**Test Data:**
```json
{
  "request_type": "Social Pension for Indigent Senior Citizens (SPISC)",
  "council": "TAYTAY",
  "full_name": "Juan Dela Cruz",
  "birth_date": "1960-01-15",
  "sex": "Male",
  "civil_status": "Widowed",
  "mobile_number": "09171234567",
  "email": "test_user@test.com",
  "address_line": "123 Main Street",
  "barangay": "San Isidro",
  "municipality": "Taytay",
  "province": "Rizal"
}
```

**Expected Result:**
```json
{
  "success": true,
  "request_id": "REQ-TAYTAY-2026-00001",
  "message": "Draft saved"
}
```

---

### Test 3: Complete Wizard - Personal Information

**Form Fields (Step 1):**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| full_name | Data | Yes | - |
| birth_date | Date | Yes | min_age:60 |
| sex | Select | Yes | Male/Female |
| civil_status | Select | Yes | Single/Married/Widowed/Separated |
| mobile_number | Data | Yes | PH phone format |
| email | Data | No | Email format |
| address_line | Data | Yes | - |
| barangay | Data | Yes | - |
| municipality | Data | Yes | Default: Taytay |
| province | Data | Yes | Default: Rizal |

---

### Test 4: Complete Wizard - Household Information

**Form Fields (Step 2):**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| household_size | Int | Yes | > 0 |
| living_arrangement | Select | Yes | Options: Living alone, Living with spouse, Living with children, Living with relatives, Other |
| monthly_income | Currency | Yes | PHP format |
| income_source | Select | Yes | Options: No income, Family support, Pension, Small business, Other |
| is_4ps_beneficiary | Check | No | - |

---

### Test 5: Complete Wizard - Identity Verification

**Form Fields (Step 3):**

| Field | Type | Required |
|-------|------|----------|
| philsys_id | Data | No |
| sss_number | Data | No |
| osca_id | Data | No |
| other_id | Data | No |

---

### Test 6: Complete Wizard - Supporting Documents

**Form Fields (Step 4):**

| Field | Type | Required |
|-------|------|----------|
| barangay_cert_indigency | Attach | Yes |
| birth_certificate | Attach | Yes |
| valid_id_copy | Attach | Yes |
| recent_photo | Attach Image | Yes |
| medical_certificate | Attach | No (if frail/sickly/disabled) |

---

### Test 7: Complete Wizard - Payment Method

**Form Fields (Step 5):**

| Field | Type | Required | Depends On |
|-------|------|----------|------------|
| payment_preference | Select | Yes | - |
| bank_name | Data | Conditional | payment_preference == "Bank Transfer" |
| bank_account_number | Data | Conditional | payment_preference == "Bank Transfer" |
| bank_account_holder | Data | Conditional | payment_preference == "Bank Transfer" |
| pickup_schedule | Pickup Schedule | Conditional | payment_preference == "Office Pickup" |

---

### Test 8: Review Step Verification

**Expected Display on Review:**

1. **Eligibility Summary** (SPISC-specific)
   - Age with eligibility indicator (60+)
   - Monthly income with eligibility indicator (below threshold)
   - Overall eligibility status

2. **Applicant Details**
   - Name, Email, Phone

3. **Personal Information Section**
   - All step 1 fields with values

4. **Household Information Section**
   - Household size, living arrangement, income details

5. **Identity Verification Section**
   - ID numbers (if provided)

6. **Uploaded Documents Summary**
   - Count of uploaded documents
   - Links to view each file

7. **Payment Method Section**
   - Selected preference
   - Bank details or pickup schedule

8. **Declaration Section**
   - Truth declaration status
   - Data privacy consent status
   - Signature date

---

### Test 9: Submit Application

**Endpoint:** `POST /api/method/councilsonline.api.requests.submit_request`

**Parameters:**
```json
{
  "request_id": "REQ-TAYTAY-2026-00001",
  "data": { /* all form data */ }
}
```

**Expected Result:**
```json
{
  "success": true,
  "request_number": "REQ-TAYTAY-2026-00001",
  "sla_info": {
    "target_date": "2026-02-27",
    "working_days": 30
  }
}
```

**Backend Actions:**
1. Request status changes to "Submitted"
2. SPISC Application record created
3. Assessment Project created (with tasks)
4. Email notification sent to council

---

### Test 10: Book Pickup Slot

**Endpoint:** `POST /api/method/councilsonline.api.scheduling.book_appointment`

**Parameters:**
```json
{
  "request": "REQ-TAYTAY-2026-00001",
  "team": "Social Services",
  "appointment_date": "2026-02-10",
  "appointment_time": "10:00",
  "duration": 30,
  "purpose": "Pension Pickup"
}
```

**Expected Result:**
```json
{
  "success": true,
  "appointment_id": "SCH-2026-00001",
  "scheduled_datetime": "2026-02-10 10:00:00"
}
```

---

## Council Staff Perspective Tests

### Test S1: View Submitted Applications

**Dashboard Access:**
- URL: `http://councilsonline.localhost/app/request`
- Filter: Status = "Submitted"

**Expected:**
- List of pending applications
- Application details viewable
- SPISC Application linked

---

### Test S2: Review Application Details

**Access:**
- Click on request to view details
- Navigate to linked SPISC Application

**Verification Points:**
1. All applicant information visible
2. Documents accessible
3. Age calculated correctly
4. Income recorded

---

### Test S3: Assess Eligibility

**SPISC Application Fields to Update:**

| Field | Action |
|-------|--------|
| eligibility_status | Set to "Eligible" or "Not Eligible" |
| assessed_by | Auto-set to current user |
| assessment_date | Auto-set to current date |
| assessment_notes | Add comments |

**Eligibility Criteria:**
- Age >= 60 years
- Monthly income below PHP 10,000 (poverty threshold)
- No SSS/GSIS pension
- Taytay resident for at least 6 months

---

### Test S4: Approve/Reject Application

**Workflow Transition:**
- From: "Under Review"
- To: "Approved" or "Rejected"

**Actions on Approval:**
1. Update request status
2. Generate approval letter
3. Notify applicant

---

### Test S5: Schedule/Confirm Pickup

**For Office Pickup:**
1. View Scheduled Appointment
2. Confirm or reschedule
3. Notify applicant

---

### Test S6: Process Payout

**Create Benefit Payout Record:**

```json
{
  "doctype": "Benefit Payout",
  "spisc_application": "SPISC-2026-00001",
  "beneficiary_name": "Juan Dela Cruz",
  "payout_amount": 500,
  "payout_date": "2026-02-10",
  "payout_method": "Cash - Office Pickup",
  "status": "Paid",
  "collected_by": "Juan Dela Cruz",
  "collected_date": "2026-02-10 10:30:00"
}
```

---

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/councilsonline.api.auth.register_user_ph` | POST | Register PH user |
| `/api/method/login` | POST | User login |

### Request Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/councilsonline.api.requests.create_draft_request` | POST | Create/update draft |
| `/api/method/councilsonline.api.requests.submit_request` | POST | Submit application |
| `/api/method/councilsonline.api.requests.get_request_type_config` | GET | Get form configuration |
| `/api/method/councilsonline.api.requests.get_user_requests` | GET | List user's requests |

### Scheduling
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/councilsonline.api.scheduling.get_available_slots` | GET | Get available slots |
| `/api/method/councilsonline.api.scheduling.book_appointment` | POST | Book appointment |

---

## Running Tests

### Automated Tests

```bash
# Run all SPISC E2E tests
cd /workspace/development/frappe-bench
bench --site councilsonline.localhost run-tests \
  --app councilsonline \
  --module councilsonline.tests.test_spisc_e2e

# Run specific test
bench --site councilsonline.localhost run-tests \
  --app councilsonline \
  --module councilsonline.tests.test_spisc_e2e \
  --test test_02_create_spisc_application
```

### Manual Test Script

```bash
# Run manual E2E test
bench --site councilsonline.localhost execute \
  councilsonline.tests.test_spisc_e2e.run_spisc_e2e_manual
```

### Browser Testing

1. Open `http://councilsonline.localhost/frontend`
2. Click "Register" and create account with PH phone
3. Login and navigate to "New Request"
4. Select "SPISC" application type
5. Complete all wizard steps
6. Review and submit

---

## Test Data

### Sample Senior Citizen Data

```json
{
  "applicants": [
    {
      "name": "Juan Dela Cruz",
      "birth_date": "1960-01-15",
      "age": 66,
      "sex": "Male",
      "civil_status": "Widowed",
      "phone": "09171234567",
      "barangay": "San Isidro",
      "income": 3000,
      "income_source": "No income",
      "expected_eligibility": "Eligible"
    },
    {
      "name": "Maria Santos",
      "birth_date": "1955-06-20",
      "age": 70,
      "sex": "Female",
      "civil_status": "Married",
      "phone": "09181234567",
      "barangay": "Santa Ana",
      "income": 5000,
      "income_source": "Family support",
      "expected_eligibility": "Eligible"
    },
    {
      "name": "Pedro Garcia",
      "birth_date": "1970-03-10",
      "age": 55,
      "sex": "Male",
      "civil_status": "Single",
      "phone": "09191234567",
      "barangay": "San Juan",
      "income": 15000,
      "income_source": "Small business",
      "expected_eligibility": "Not Eligible (under 60)"
    }
  ]
}
```

### Taytay Barangays (for address validation)

- Bagong Pag-asa
- Corazon de Jesus
- Dolores
- Floodway
- Muzon
- San Isidro
- San Juan
- Santa Ana
- Santo Domingo
- Santo Nino

---

## Review Step Improvements Made

The following improvements were made to the Review Step component:

1. **SPISC Eligibility Summary**
   - Visual indicators for age eligibility (60+)
   - Income eligibility check (below poverty threshold)
   - Overall eligibility status

2. **Comprehensive Data Display**
   - All wizard steps shown with data
   - Step completion indicators
   - Conditional sections (Bank vs Pickup)

3. **Document Summary**
   - Count of uploaded documents
   - View links for each file
   - Missing required documents warning

4. **Improved Validation**
   - Lists missing required fields
   - Highlights incomplete sections
   - Clear completion status

---

## Known Issues / Limitations

1. **Phone Validation**: Only PH (09xx) and NZ (02x) formats supported
2. **Document Upload**: Max file size 10MB
3. **Appointment Booking**: Requires Council Team with scheduling enabled
4. **Eligibility**: Final determination by council staff, not automatic

---

## Changelog

- **v1.0** (Jan 2026): Initial documentation
  - Added PH phone validation
  - Enhanced Review Step for SPISC
  - Created E2E test suite
