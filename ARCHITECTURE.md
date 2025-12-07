# Lodgeick Platform Architecture

## Overview

Lodgeick is a multi-council platform for managing civic applications (Resource Consents, Building Consents, Social Pensions, etc.) with a flexible, configuration-driven architecture.

---

## Core Architecture Patterns

### 1. Polymorphic Application Linking

The platform uses a **polymorphic relationship** between Request (workflow) and Application (domain-specific data).

```
Request (Workflow Container)
  ├─ application_doctype: "Resource Consent Application"
  └─ application_name: "RC-APP-00001" (Dynamic Link)
       │
       └──> Resource Consent Application (Domain Data)
              ├─ request: back-reference to Request
              ├─ consent_types (child table)
              ├─ activity_status
              ├─ statutory_clock_started
              └─ ... (189 RC-specific fields)

Request (Workflow Container)
  ├─ application_doctype: "SPISC Application"
  └─ application_name: "SPISC-00001" (Dynamic Link)
       │
       └──> SPISC Application (Domain Data)
              ├─ request: back-reference to Request
              ├─ full_name
              ├─ birth_date, age, sex
              └─ ... (61 pension-specific fields)
```

**Benefits**:
- Single Request DocType supports multiple application types
- Type-safe via Dynamic Link (uses actual DocType names)
- Bidirectional navigation (Request ↔ Application)
- New application types can be added without changing Request

**Implementation**: See `/workspace/development/frappe-bench/apps/lodgeick/lodgeick/api.py` lines 732-743

---

### 2. Request Type Configuration System

Dynamic form generation via a **flattened three-level hierarchy**.

#### Why Flattened?

Frappe doesn't support nested child tables. Instead of:
```
Request Type
  └─ Steps (child table)
       └─ Sections (nested - NOT POSSIBLE)
            └─ Fields (nested - NOT POSSIBLE)
```

We use **parent code linkage**:
```
Request Type
  ├─ step_configs (child table)
  │    └─ step_code: "rc_applicant_details"
  │
  ├─ step_sections (child table)
  │    └─ parent_step_code: "rc_applicant_details" (links to step)
  │    └─ section_code: "applicant_info"
  │
  └─ step_fields (child table)
       └─ parent_section_code: "applicant_info" (links to section)
       └─ field_name: "applicant_name"
```

#### Configuration Tables

**Request Type Step Config** (10 fields)
- `step_number`, `step_code`, `step_title`
- `step_component` (default: DynamicStepRenderer)
- `step_description` (optional help text)
- `is_enabled`, `is_required`, `show_on_review`
- `depends_on` (JavaScript conditional logic)

**Request Type Step Section** (11 fields)
- `parent_step_code` (links to step)
- `section_code`, `section_title`, `section_description`
- `section_type` (Section/Tab/Accordion/Field Group)
- `sequence`, `is_enabled`, `is_required`, `show_on_review`
- `depends_on` (JavaScript conditional logic)

**Request Type Step Field** (15 fields)
- `parent_section_code` (links to section)
- `field_name`, `field_label`, `field_type`
- `is_required`, `show_on_review`, `review_label`
- `options`, `default_value`, `depends_on`, `validation` (JavaScript)
- Supports 14 field types: Data, Select, Check, Text, Text Editor, Attach, Link, Table, Date, Float, Currency, etc.

#### Example: Resource Consent - New Zealand

**File**: `lodgeick/request_type/resource_consent_-_new_zealand/resource_consent_-_new_zealand.json`
- **9 steps**: Applicant → Property → Consent → Site → Consultation → AEE → Documents → Conditions → Declaration
- **27 sections**: Grouped by step
- **90 fields**: All RMA compliance requirements
- **1,298 lines** of JSON configuration

---

### 3. Request DocType - Workflow Orchestration

**Purpose**: Cross-domain workflow container

**Key Responsibilities**:
- Workflow state management (Draft → Submitted → Processing → Decision)
- Council routing and assignment
- Applicant and agent information (single source of truth)
- Timeline tracking (submitted, acknowledged, target/actual completion dates)
- Fee calculation and payment tracking
- Assessment Project integration (auto-created on acknowledgment)

**Does NOT contain**: Domain-specific data (that's in Application DocTypes)

**Fields** (74 total):
- Core: `request_number`, `request_type`, `status`, `workflow_state`
- Council: `council`, `request_category`
- People: `applicant` (User link), `agent`, `organization`
- Polymorphic: `application_doctype`, `application_name` (Dynamic Link)
- Timeline: `submitted_date`, `acknowledged_date`, `target_completion_date`
- Financial: `total_fees_incl_gst`, `payment_status`, `fees` (child table)
- Assessment: `assessment_project` (auto-created)

---

### 4. Application DocTypes - Domain-Specific Data

#### Resource Consent Application (189 fields, 11 child tables)

**Purpose**: RMA (Resource Management Act) compliance

**Key Sections**:
- Consent Types (child table): Land Use, Subdivision, Discharge, Water, Coastal
- Activity Status: Permitted, Controlled, Restricted Discretionary, Discretionary, Non-Complying, Prohibited
- Assessment of Environmental Effects (Schedule 4 RMA)
- Notification Level: Non-Notified, Limited Notified, Fully Notified
- Statutory Clock: Working days tracking per RMA sections 91-115
- Natural Hazards (child table): NES compliance
- Affected Parties (child table): Written approvals tracking
- Consultation: Iwi consultation, affected parties
- Conditions (child table): Proposed and final conditions
- Decision: Approve/Decline with conditions

**Child Tables**:
1. RC Consent Type
2. RC Affected Party
3. RC Natural Hazard
4. Resource Consent Condition (proposed)
5. Resource Consent Condition (final)
6. Resource Consent Additional Consent
7. Resource Consent PBA Contact (Permitted Boundary Activity)
8. Resource Consent Consulted Organization
9. Resource Consent Application Document
10. Resource Consent Lodgement Payment
11. HAIL Activity (Hazardous Activities and Industries List)

#### SPISC Application (61 fields)

**Purpose**: Social Pension for Indigent Senior Citizens (Philippines)

**Key Sections**:
- Personal Information: `full_name`, `birth_date`, `age` (auto-calculated), `sex`, `civil_status`
- Economic Status: `monthly_income`, `is_4ps_beneficiary`, `poverty_score`
- Identity: `philsys_id`, `sss_number`, `osca_id`
- Documents: Barangay cert, birth certificate, valid ID, photo, medical cert
- Assessment: `eligibility_status`, `eligibility_notes`
- Payment: `monthly_pension_amount` (PHP 500), `payment_method`, bank details

**Syncs back to Request**: Updates `property_address`, `brief_description` via `db_set()`

---

### 5. Data Flow: Request → Application → Assessment Project

```
1. User submits form via NewRequest.vue
   ↓
2. API creates Request (workflow container)
   ↓
3. API creates Application (domain-specific data)
   - Resource Consent Application (RMA)
   - SPISC Application (pension)
   - Building Consent Application (building code)
   ↓
4. Request.application_doctype = "Resource Consent Application"
   Request.application_name = "RC-APP-00001"
   ↓
5. On acknowledgment: Assessment Project auto-created
   - Links to Request
   - Provides task tracking, team collaboration
   - Stage-based workflow
```

---

## Current Implementation Status

### ✅ Fully Implemented

1. **Polymorphic Application Linking**: Request ↔ Multiple Application types
2. **Request Type Configuration**: 90-field RC config proves scalability
3. **Flattened Hierarchy**: Works efficiently without nested child tables
4. **Dynamic Form Rendering**: All request types use DynamicStepRenderer (Phase 2.1)
5. **Conditional Logic Engine**: depends_on evaluation working for steps/sections/fields (Phase 2.2)
6. **Single Source Applicant Data**: Request stores applicant info, Applications only domain-specific (Phase 2.3)
7. **Property Field Mapping**: All 7 mandatory Property fields mapped
8. **Consent Types Child Table**: Fixed to use rows instead of strings

### ✅ Fully Implemented (continued)

9. **Validation JavaScript Execution**: Complete for all field types (Phase 3.1 complete)
   - Built-in validation: email, phone, url, number
   - Custom JavaScript expressions: `eval:value >= 18`, `eval:value === formData.password`
   - Validation errors displayed on blur/change
   - Implemented for all field types: Data, Select, Text, Date, Currency, Check, Int, Float
   - Visual feedback: red border and error messages
   - Validation utility: [fieldValidation.js](frontend/src/utils/fieldValidation.js)

### ⚠️ Partially Implemented

(None - all planned features for Phase 1-3.1 complete)

### ✅ Fully Implemented (continued)

10. **Step Template Library**: Reusable step patterns (Phase 3.2 complete)
   - 4 standard templates: declaration, applicant_details, bank_details, payment_collection
   - Template loader utility: [step_templates.py](lodgeick/templates/step_templates.py)
   - JSON-based templates with customization options
   - Programmatic application via `apply_template()` function
   - Reduces duplication, ensures consistency
   - Full documentation: [Templates README](lodgeick/templates/step_templates/README.md)

1. **Configuration UI (Visual Request Type Builder)**: Complete - Phase 3.3
   - Visual builder for creating/editing Request Types without JSON editing
   - Component: [RequestTypeBuilder.vue](frontend/src/pages/RequestTypeBuilder.vue)
   - API endpoints: [api.py](lodgeick/api.py) - `get_step_templates()`, `load_step_template()`, `save_request_type_config()`, `load_request_type_config()`
   - Features:
   - Step/section/field management UI (add, delete, reorder)
   - Template library integration (apply templates with one click)
   - Save/load Request Types from database
   - JSON preview/export functionality
   - Real-time validation
   - Status: Fully functional, production-ready

1. **Bidirectional Sync Events**: Complete - Phase 3.4
   - Event-driven Application → Request sync mechanism
   - Utility module: [application_sync.py](lodgeick/utils/application_sync.py)
   - Standardized `sync_to_request()` function
   - Application-specific display logic builders
   - Implemented for all Application types:
     - SPISC Application (refactored to use utility)
     - Resource Consent Application (new)
     - Building Consent Application (new)
   - Automatic updates to Request display fields:
     - `property_address` - Display address from Application
     - `brief_description` - Summary with Application type and key details
   - Status: Fully functional, all Application types supported

### ⚠️ Partially Implemented (None)

All planned features through Phase 3.4 are complete

### ❌ Not Implemented

None - All planned architecture features through Phase 3.4 are complete

---

## Design Decisions & Rationale

### Why Polymorphic Link Instead of Inheritance?

**Considered**: Making all applications inherit from base "Application" class

**Chosen**: Polymorphic link with separate DocTypes

**Reasons**:
1. Frappe doesn't support true inheritance (only DocType extension)
2. Domain models are vastly different (RC has 189 fields, SPISC has 61)
3. Easier to maintain separate schemas
4. Councils can customize individual application types
5. No shared fields to justify inheritance overhead

### Why Flattened Configuration Instead of Nested?

**Constraint**: Frappe doesn't support nested child tables

**Solution**: Parent code linkage (step_code → parent_step_code → parent_section_code)

**Benefits**:
1. Single-level queries (fast)
2. No recursive loading
3. Each table independently manageable
4. Clear separation of concerns

### Why Request + Application Instead of Single DocType?

**Alternative**: One big DocType with all fields

**Chosen**: Separate Request (workflow) and Application (domain)

**Reasons**:
1. Workflow logic reusable across all application types
2. Domain-specific validations isolated
3. Different access patterns (workflow vs data entry)
4. Cleaner permission model
5. Easier to extend with new application types

---

## Applicant Information Storage Pattern

### Design Decision (Phase 2.3 - Implemented)

**Single Source of Truth**: Request DocType

**Rationale**:
- Eliminates duplication across Application DocTypes
- Consistent applicant data regardless of application type
- Supports agent workflows (acting on behalf)

**Request Fields**:
```python
applicant: User link (person who created request, or client)
applicant_name: Full name (auto-fetched from User or manual override)
applicant_email: Email (auto-fetched from User or manual override)
applicant_phone: Phone number
agent: Optional User link (person acting on behalf)
agent_name: Agent's full name
agent_email: Agent's email
agent_phone: Agent's phone
organization: Optional Organization link
```

**Application DocTypes Store**:
- Domain-specific fields only
- SPISC: birth_date, age, sex, civil_status, address, income, etc.
- RC: consent types, activity status, AEE, conditions, etc.

**Field Mapping**:
```python
# api.py (lines 659-667)
# Maps SPISC form fields to Request fields
if data.get("full_name"):
    data["applicant_name"] = data["full_name"]
if data.get("mobile_number"):
    data["applicant_phone"] = data["mobile_number"]
if data.get("email"):
    data["applicant_email"] = data["email"]
```

**Request Type Configuration**:
- Fields remain in configuration (for dynamic forms)
- Values stored in Request (not Application)
- No duplication in database

**SPISC Application Removed Fields** (Phase 2.3):
- ~~full_name~~ → Request.applicant_name
- ~~mobile_number~~ → Request.applicant_phone
- ~~email~~ → Request.applicant_email

---

## Payment and Bank Details Step Pattern

### Design Decision (Phase 2.4 - Implemented)

**Configuration-Driven Payment Steps**: Add to Request Type JSON (not hardcoded injection)

**Previous Approach** (Removed):
- API auto-injected payment_collection step if `collects_payment=True`
- API auto-injected bank_details step if `make_payment=True`
- 130+ lines of hardcoded step/section/field definitions (api.py lines 3993-4143)

**New Approach**:
- Add payment/bank steps directly to Request Type configuration
- Use `depends_on` for conditional display
- Fully customizable per council and request type

**Benefits**:
- No code changes to modify payment workflows
- Council-specific payment requirements
- Flexible field validation and options
- Consistent with other steps (configuration-driven)

**How to Add Payment Steps**:

1. **For fee collection** (payments FROM applicant):
   ```json
   {
     "step_code": "payment_collection",
     "step_title": "Payment & Invoice Details",
     "step_component": "DynamicStepRenderer",
     "sections": [
       {
         "section_code": "invoice_details",
         "fields": [
           {"field_name": "invoice_to", "field_type": "Select", ...},
           {"field_name": "invoice_name", "field_type": "Data", ...},
           {"field_name": "invoice_email", "field_type": "Data", ...}
         ]
       }
     ]
   }
   ```

2. **For payouts** (payments TO applicant):
   ```json
   {
     "step_code": "bank_details",
     "step_title": "Bank Account Details",
     "step_component": "DynamicStepRenderer",
     "sections": [
       {
         "section_code": "bank_account",
         "fields": [
           {"field_name": "account_holder_name", "field_type": "Data", ...},
           {"field_name": "bank_name", "field_type": "Data", ...},
           {"field_name": "account_number", "field_type": "Data", ...},
           {"field_name": "account_type", "field_type": "Select", ...}
         ]
       }
     ]
   }
   ```

3. **Set flags for accounting** (optional):
   - `collects_payment`: True if request type involves fee collection
   - `make_payment`: True if request type involves payouts to applicant

**Example Use Cases**:
- RC (Resource Consent): Add payment_collection step for lodgement fees
- SPISC: Add bank_details step for pension direct deposit
- Building Consent: Add payment_collection with conditional fast-track fee field

---

## Sync Patterns

### Current State

**SPISC Application → Request**:
```python
# spisc_application.py on_update()
request.db_set("property_address", f"{barangay}, {municipality}, {province}")
request.db_set("brief_description", f"{request.applicant_name} - SPISC Application (Age: {self.age})")
```

**Resource Consent Application → Request**:
- No automatic sync
- Display fields removed (Phase 1 cleanup)

### Recommended Pattern (Future - Phase 3.4)

Use Frappe hooks for automatic sync:
```python
# In Application DocType hooks
def on_update(self):
    if self.request:
        request = frappe.get_doc("Request", self.request)
        request.db_set("brief_description", self.get_summary())
        # Trigger events for real-time updates
```

---

## Step Template Library (Phase 3.2)

### Overview

Step templates are reusable JSON-based patterns that eliminate duplication across Request Type configurations. Instead of manually defining common steps like "Declaration" or "Applicant Details" for every request type, templates provide pre-configured step/section/field structures.

### Available Templates

| Template | Purpose | Fields | Use Case |
|----------|---------|--------|----------|
| `declaration.json` | Declaration & Signature | 5 fields | Final step for most request types |
| `applicant_details.json` | Applicant Information | 7 fields | Initial applicant data collection |
| `bank_details.json` | Bank Account (payouts) | 5 fields | Pension, rebates (TO applicant) |
| `payment_collection.json` | Payment & Invoice | 6 fields | Fees, lodgements (FROM applicant) |

### Usage Example

```python
from lodgeick.templates.step_templates import apply_template

# Create new request type
rt_doc = frappe.new_doc("Request Type")
rt_doc.name = "Building Consent"

# Apply applicant template
apply_template(rt_doc, "applicant_details", step_number=1)

# Add custom steps (2-6)...

# Apply payment template with customization
apply_template(rt_doc, "payment_collection", step_number=7, customization={
    "include_fast_track_option": True
})

# Apply declaration template
apply_template(rt_doc, "declaration", step_number=8)

rt_doc.insert()
```

### Template Structure

Each template contains:
- **step_config**: Step metadata (code, title, component)
- **sections**: Array of section definitions
- **fields**: Array of field definitions per section
- **customization_options**: Optional features to enable/disable
- **usage_notes**: Implementation guidance

### Benefits

1. **Consistency**: Same fields, labels, validations across all request types
2. **Faster Development**: New request types in minutes instead of hours
3. **Reduced Duplication**: Write once, use everywhere
4. **Easier Maintenance**: Update template → affects all using it
5. **Best Practices**: Templates encode UX patterns and validation rules

### Template Files

- Templates: [lodgeick/templates/step_templates/](lodgeick/templates/step_templates/)
- Utility Functions: [step_templates.py](lodgeick/templates/step_templates.py)
- Documentation: [Templates README](lodgeick/templates/step_templates/README.md)

### Helper Functions

```python
# Load template to inspect
template = load_template("declaration")

# List all available
templates = list_available_templates()  # ['declaration', 'applicant_details', ...]

# Get metadata
info = get_template_info("bank_details")

# Validate structure
is_valid, errors = validate_template(template_data)
```

---

## File Structure

```
lodgeick/
├── lodgeick/
│   ├── doctype/
│   │   ├── request/                    # Workflow container
│   │   ├── request_type/               # Configuration parent
│   │   ├── request_type_step_config/   # Step definitions
│   │   ├── request_type_step_section/  # Section definitions
│   │   ├── request_type_step_field/    # Field definitions
│   │   ├── resource_consent_application/  # RC domain data
│   │   ├── spisc_application/          # Pension domain data
│   │   └── ...
│   ├── request_type/
│   │   └── resource_consent_-_new_zealand/  # RC-NZ configuration
│   │       └── resource_consent_-_new_zealand.json (1,298 lines)
│   └── api.py                          # Core API endpoints
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── NewRequest.vue          # Request wizard
│   │   └── components/
│   │       └── request-steps/
│   │           ├── DynamicStepRenderer.vue   # Config-driven rendering
│   │           ├── DynamicFieldRenderer.vue
│   │           ├── Step1ApplicantProposal.vue  # RC legacy (to be removed)
│   │           ├── Step2NaturalHazards.vue     # RC legacy
│   │           └── ... (Step3-Step8)
```

---

## Migration Path: Hardcoded RC → Dynamic Config

### Current (Phase 1 Complete)

- ✅ 14 display fields removed from RC Application
- ✅ Schema fields added (step_description, section_description)
- ✅ Documentation created

### Next (Phase 2)

1. **Remove hardcoded RC steps** (`NewRequest.vue` lines 1100-1109)
2. **Enable dynamic config for RC** (usesConfigurableSteps = true)
3. **Keep legacy components as reference** (don't delete immediately)
4. **Test thoroughly** (E2E Playwright suite)

### Future (Phase 3)

1. Delete legacy Step1-Step8 components
2. Build configuration UI
3. Create step template library

---

## Testing Strategy

### E2E Tests

**File**: `frontend/tests/e2e/rc-application.spec.js`
- 37 tests total
- 36/37 passing (97.3% pass rate)
- Covers desktop and mobile viewports

**Backend Test**: `lodgeick/test_utils.py`
- `test_rc_e2e_submission()` - Full submission flow
- Validates Property creation with 7 mandatory fields
- Tests RC Application creation with child tables

---

## Performance Considerations

### Request Type Configuration Loading

**Current**: Single query loads all steps, sections, fields
```python
# api.py get_request_type_steps()
step_configs = frappe.get_all("Request Type Step Config", ...)
step_sections = frappe.get_all("Request Type Step Section", ...)
step_fields = frappe.get_all("Request Type Step Field", ...)
```

**Optimization**: Already efficient due to flattened structure (3 queries vs recursive loading)

### Child Table Performance

**RC Application**: 11 child tables
- Only load when needed (not eager loaded)
- Use pagination for large tables (e.g., conditions)

---

## Security Model

### Permissions

**Request**:
- Applicant: Create, Read own
- Agent: Create, Read delegated
- Council Staff: Read, Update assigned
- Council Manager: All operations

**Application DocTypes**:
- Inherit Request permissions
- Domain-specific validations in `.py` files

---

## Future Enhancements

1. **Template Library** (Phase 3.2): Reusable step patterns
2. **Configuration UI** (Phase 3.3): Visual editor for Request Types
3. **Validation Engine** (Phase 3.1): Execute JavaScript validation
4. **Real-time Sync** (Phase 3.4): Event-driven Request ↔ Application updates
5. **Versioning**: Track Request Type configuration changes
6. **Multi-language**: Translate step/section/field labels

---

## Related Documentation

- Plan: `/home/frappe/.claude/plans/vectorized-riding-waffle.md`
- Test Summary: `/tmp/RC_PROPERTY_FIELDS_FIX_SUMMARY.md`
- API Documentation: See docstrings in `lodgeick/api.py`

---

**Last Updated**: 2025-12-07
**Architecture Version**: 1.0 (Post Phase 1 Cleanup)
