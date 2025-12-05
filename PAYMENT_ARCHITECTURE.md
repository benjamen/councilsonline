# Payment Architecture Documentation

## Overview

The Lodgeick system now supports **bidirectional payment workflows**:
1. **Council collects FROM applicant** (fees, invoices) - e.g., Resource Consent fees
2. **Council pays TO applicant** (grants, pensions, reimbursements) - e.g., SPISC pensions

## Architecture

### Configuration Fields (Request Type)

Two boolean fields control payment behavior:

| Field | Description | Effect |
|-------|-------------|--------|
| `collects_payment` | Council collects payment FROM applicant | Auto-injects "Payment & Invoice Details" step |
| `make_payment` | Council makes payment TO applicant | Auto-injects "Bank Account Details" step |

### Child Table Structure

#### Council Payment Account (Child of Council)

**Purpose**: Store council's bank accounts for receiving payments

**Fields**:
- `account_name` (Data, Required) - Friendly name (e.g., "Main Operating Account")
- `account_type` (Select, Required) - Bank Account, Credit Card, PayPal, Stripe, Other
- `is_default` (Check) - Default account for payment collection
- `bank_name` (Data) - Name of bank/financial institution
- `account_number` (Data) - Account number
- `routing_number` (Data) - Routing/BSB/sort code
- `swift_code` (Data) - International bank code
- `iban` (Data) - International Bank Account Number
- `billing_name` (Data) - Billing contact name
- `billing_email` (Data) - Email for payment confirmations
- `billing_phone` (Data) - Phone for billing inquiries
- `billing_address` (Small Text) - Billing correspondence address

**Use Cases**:
- Resource consent application fees
- Building permit fees
- Subdivision fees
- Development contributions

#### User Bank Account (Child of User via Custom Fields)

**Purpose**: Store applicant's bank accounts for receiving payments

**Fields**:
- `account_name` (Data, Required) - Friendly name (e.g., "Main Savings")
- `account_holder_name` (Data, Required) - Full name on account
- `bank_name` (Data, Required) - Name of bank
- `account_number` (Data, Required) - Account number
- `account_type` (Select, Required) - Savings, Checking, Current, Money Market, Other
- `is_default` (Check) - Default account for payments
- `routing_number` (Data) - Routing/BSB code
- `branch_code` (Data) - Bank branch code
- `swift_code` (Data) - International bank code

**Use Cases**:
- SPISC monthly PHP 500 pension deposits
- Grant disbursements
- Reimbursements
- Emergency assistance payments

### Request DocType References

The Request document includes link fields to reference selected payment accounts:

| Field | Links To | Visible When | Purpose |
|-------|----------|--------------|---------|
| `selected_payment_account` | Council Payment Account | `collects_payment = 1` | Council account to receive payment |
| `selected_bank_account` | User Bank Account | `make_payment = 1` | Applicant account to receive payment |

## Dynamic Step Injection

The backend API (`get_request_type_steps`) automatically injects payment steps based on Request Type configuration.

### Payment Collection Step (collects_payment = 1)

**Step Code**: `payment_collection`
**Title**: Payment & Invoice Details

**Fields**:
- `invoice_to` (Select, Required) - Applicant, Property Owner, Other
- `invoice_name` (Data, Required) - Name for invoice
- `invoice_email` (Data, Required) - Email for invoice (validated)

### Bank Details Step (make_payment = 1)

**Step Code**: `bank_details`
**Title**: Bank Account Details

**Fields**:
- `account_holder_name` (Data, Required) - Account holder name
- `bank_name` (Data, Required) - Bank name
- `account_number` (Data, Required) - Account number
- `routing_number` (Data) - Routing/branch number
- `account_type` (Select, Required) - Savings, Checking, Current

## Implementation Examples

### SPISC (Social Pension for Indigent Senior Citizens)

**Configuration**:
```json
{
  "name": "Social Pension for Indigent Senior Citizens (SPISC)",
  "category": "Social Assistance",
  "collects_payment": 0,  // No fees - social assistance program
  "make_payment": 1,      // Government pays PHP 500/month TO citizen
  "base_fee": 0.0,
  "processing_sla_days": 30
}
```

**Workflow**:
```
Step 1: Personal Information (configurable)
Step 2: Household Information (configurable)
Step 3: Identity Verification (configurable)
Step 4: Supporting Documents (configurable)
Step 5: Declaration & Submission (configurable)
Step 6: Bank Account Details (auto-injected ✨)
Step 7: Review & Submit
```

**User Experience**:
- Property Details section: ❌ Hidden (no property involved)
- Bank Account form: ✅ Displays for pension deposit info
- Captures: account holder name, bank name, account number, routing, account type

### Resource Consent

**Configuration**:
```json
{
  "name": "Resource Consent",
  "category": "Resource Consent",
  "collects_payment": 1,  // Council collects fees FROM applicant
  "make_payment": 0,      // No disbursement to applicant
  "base_fee": 500.0,
  "fee_calculation_method": "Fixed"
}
```

**Workflow**:
```
Steps 1-11: Resource Consent hardcoded steps
Step 12: Payment & Invoice Details (auto-injected ✨)
Step 13: Review & Submit
```

**User Experience**:
- Property Details section: ✅ Visible (always required for RC)
- Invoice form: ✅ Displays for fee payment
- Captures: invoice to, invoice name, invoice email

## Frontend Integration

### Conditional Property Display

The Review step ([Step17Review.vue:48](../frontend/src/components/request-steps/Step17Review.vue#L48)) conditionally shows the Property Details section:

```javascript
const hasPropertyDetails = computed(() => {
  // Always show for resource consent
  if (props.isResourceConsent) {
    return true
  }

  // Check if property data actually exists in the request
  return !!(props.modelValue.property || props.modelValue.property_address)
})
```

**Result**:
- SPISC: Property Details section hidden (no property involved)
- Resource Consent: Property Details section visible
- Other types: Shows only if property data exists

## Database Schema

### Council DocType
```
council
├── (existing fields...)
└── payment_accounts (Table → Council Payment Account)
```

### User DocType (via Custom Fields)
```
user
├── (core Frappe fields...)
├── bank_accounts_section (Section Break)
└── bank_accounts (Table → User Bank Account)
```

### Request DocType
```
request
├── (existing fields...)
├── section_break_fees
├── selected_payment_account (Link → Council Payment Account)
├── selected_bank_account (Link → User Bank Account)
└── (remaining fields...)
```

## API Reference

### get_request_type_steps(request_type, council_code)

**Location**: [lodgeick/api.py:3485](../lodgeick/api.py#L3485)

**Logic**:
1. Load configured steps from Request Type
2. If `rt_doc.collects_payment`:
   - Inject payment_collection step
3. If `rt_doc.make_payment`:
   - Inject bank_details step
4. Apply council-specific overrides (if provided)
5. Sort steps by step_number
6. Return steps configuration

**Example Response** (SPISC):
```json
{
  "uses_config": true,
  "steps": [
    {"step_number": 1, "step_code": "personal_info", "step_title": "Personal Information"},
    {"step_number": 2, "step_code": "household_info", "step_title": "Household Information"},
    {"step_number": 3, "step_code": "identity_verification", "step_title": "Identity Verification"},
    {"step_number": 4, "step_code": "supporting_documents", "step_title": "Supporting Documents"},
    {"step_number": 5, "step_code": "declaration", "step_title": "Declaration & Submission"},
    {
      "step_number": 6,
      "step_code": "bank_details",
      "step_title": "Bank Account Details",
      "sections": [
        {
          "section_code": "bank_account",
          "section_title": "Payment Recipient Details",
          "fields": [
            {"field_name": "account_holder_name", "field_type": "Data", "is_required": true},
            {"field_name": "bank_name", "field_type": "Data", "is_required": true},
            {"field_name": "account_number", "field_type": "Data", "is_required": true},
            {"field_name": "routing_number", "field_type": "Data", "is_required": false},
            {"field_name": "account_type", "field_type": "Select", "is_required": true}
          ]
        }
      ]
    }
  ]
}
```

## Testing Guide

### Test SPISC Workflow

1. **Navigate to frontend**: http://localhost:8090/frontend
2. **Select Council**: Taytay Council (TAYTAY-PH)
3. **Select Request Type**: Social Pension for Indigent Senior Citizens (SPISC)
4. **Complete Steps 1-5**:
   - Personal Information
   - Household Information
   - Identity Verification
   - Supporting Documents
   - Declaration & Submission
5. **Step 6: Bank Account Details** (should appear automatically)
   - Enter account holder name
   - Enter bank name
   - Enter account number
   - Enter routing number (optional)
   - Select account type
6. **Review & Submit**
   - Verify Property Details section is HIDDEN
   - Verify Bank Account Details are shown in review
   - Submit application

### Test Resource Consent Workflow

1. **Select Request Type**: Resource Consent
2. **Complete Steps 1-11** (existing RC steps)
3. **Step 12: Payment & Invoice Details** (should appear automatically)
   - Select invoice recipient (Applicant/Property Owner/Other)
   - Enter invoice name
   - Enter invoice email
4. **Review & Submit**
   - Verify Property Details section is VISIBLE
   - Verify Payment/Invoice details shown in review
   - Submit application

### Verify Data Storage

After submission, verify data is stored correctly:

**Council Payment Accounts**:
```python
council = frappe.get_doc("Council", "TAYTAY-PH")
print(council.payment_accounts)  # List of Council Payment Account rows
```

**User Bank Accounts**:
```python
user = frappe.get_doc("User", "user@example.com")
print(user.bank_accounts)  # List of User Bank Account rows
```

**Request References**:
```python
request = frappe.get_doc("Request", "REQ-0001")
print(request.selected_payment_account)  # Link to council account
print(request.selected_bank_account)     # Link to user account
```

## Migration

The payment architecture is applied via migration patch:

**Patch**: [lodgeick/patches/v1_3/add_payment_child_tables.py](../lodgeick/patches/v1_3/add_payment_child_tables.py)

**What it does**:
1. Creates Custom Field: `User-bank_accounts_section` (Section Break)
2. Creates Custom Field: `User-bank_accounts` (Table → User Bank Account)

**Run manually**:
```bash
bench --site lodgeick.localhost migrate
```

## Files Modified

### Backend
- [lodgeick/lodgeick/doctype/request_type/request_type.json](../lodgeick/lodgeick/doctype/request_type/request_type.json) - Added payment booleans
- [lodgeick/lodgeick/doctype/request/request.json](../lodgeick/lodgeick/doctype/request/request.json) - Added payment references
- [lodgeick/lodgeick/doctype/council/council.json](../lodgeick/lodgeick/doctype/council/council.json) - Added payment accounts child table
- [lodgeick/api.py](../lodgeick/api.py) - Payment step injection logic
- [lodgeick/lodgeick/doctype/council_payment_account/](../lodgeick/lodgeick/doctype/council_payment_account/) - New child table
- [lodgeick/lodgeick/doctype/user_bank_account/](../lodgeick/lodgeick/doctype/user_bank_account/) - New child table
- [lodgeick/patches/v1_3/add_payment_child_tables.py](../lodgeick/patches/v1_3/add_payment_child_tables.py) - Migration patch
- [lodgeick/patches.txt](../lodgeick/patches.txt) - Added patch reference

### Frontend
- [frontend/src/components/request-steps/Step17Review.vue](../frontend/src/components/request-steps/Step17Review.vue) - Conditional property display

### Fixtures
- [lodgeick/lodgeick/fixtures/taytay/spisc_request_type.json](../lodgeick/lodgeick/fixtures/taytay/spisc_request_type.json) - Set `make_payment = 1`

## Future Enhancements

### Phase 2: Payment Processing Integration
- Integrate with payment gateways (Stripe, PayPal)
- Automated invoice generation
- Payment status tracking
- Receipt generation

### Phase 3: Automated Disbursements
- Scheduled payment runs for SPISC pensions
- Batch payment processing
- Payment reconciliation
- Audit trail

### Phase 4: Multi-currency Support
- Support for different currencies per council
- Exchange rate management
- Multi-currency reporting

## Support

For questions or issues:
1. Review this document
2. Check [REQUEST_DOCTYPE_CLEANUP.md](./REQUEST_DOCTYPE_CLEANUP.md) for Request DocType refactor
3. Review SPISC fixture: [spisc_request_type.json](./lodgeick/lodgeick/fixtures/taytay/spisc_request_type.json)

## Version History

- **v1.3** (2025-12-05): Initial payment architecture implementation
  - Bidirectional payment support
  - Child table structure for council and user accounts
  - Dynamic step injection
  - Conditional property display
