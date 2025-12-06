# Unified Request Architecture Guide
## One Pattern for All Request Types (RC, SPISC, Future)

**Version:** 1.0
**Date:** 2025-12-06
**Status:** Production Ready

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [The Unified Pattern](#the-unified-pattern)
3. [Components](#components)
4. [Implementation Guide](#implementation-guide)
5. [Address Lookup System](#address-lookup-system)
6. [UI Components](#ui-components)
7. [Testing](#testing)
8. [Migration Notes](#migration-notes)

---

## Architecture Overview

Lodgeick uses a **unified architecture** for all request types with three core principles:

1. **Thin Request** (workflow tracking only)
2. **Application DocType** (domain-specific data)
3. **Polymorphic Linking** (flexible relationships)

This architecture works for:
- ✅ Resource Consent (complex, 1,200+ fields, child tables)
- ✅ SPISC (moderate, 50+ fields, flat data)
- ✅ Building Consent (future)
- ✅ Licenses, permits, complaints (future)

---

## The Unified Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ REQUEST (Thin - Workflow Only)                              │
├─────────────────────────────────────────────────────────────┤
│ • request_number, request_type, council, applicant         │
│ • status, workflow_state, submitted_date                   │
│ • property_address (display only - synced)                 │
│ • brief_description (display only - synced)                │
│ • assessment_project (FK → Assessment Project)             │
│ • application_doctype (polymorphic)                        │
│ • application_name (polymorphic)                           │
└─────────────────────────────────────────────────────────────┘
                        ↓ (one-to-one)
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION DOCTYPE (Thick - Domain Data)                   │
├─────────────────────────────────────────────────────────────┤
│ Resource Consent Application:                              │
│ • request (FK)                                             │
│ • consent_types (child table)                              │
│ • affected_parties (child table)                           │
│ • assessment_of_effects                                     │
│ • ... 1,200 RMA-specific fields                            │
│                                                             │
│ SPISC Application:                                          │
│ • request (FK)                                             │
│ • full_name, birth_date, age, civil_status                 │
│ • barangay, municipality, province                         │
│ • monthly_income, eligibility_status                       │
│ • ... 50+ SPISC-specific fields                            │
└─────────────────────────────────────────────────────────────┘
                        ↓ (on_update sync)
                Request.property_address ← Application
                Request.brief_description ← Application
```

---

## Components

### Backend Components

#### 1. Request DocType
**Location:** `lodgeick/doctype/request/request.json`

**Key Fields:**
```json
{
  "application_doctype": "Data",        // e.g., "SPISC Application"
  "application_name": "Dynamic Link",   // Links to the application
  "property_address": "Small Text",     // Display field (synced)
  "brief_description": "Small Text"     // Display field (synced)
}
```

#### 2. Application DocTypes

**SPISC Application:**
`lodgeick/doctype/spisc_application/`

**Business Logic:**
```python
class SPISCApplication(Document):
    def validate(self):
        self.calculate_age()
        self.check_eligibility_criteria()

    def on_update(self):
        """Sync display fields to parent Request"""
        if self.request:
            request = frappe.get_doc("Request", self.request)
            request.db_set("property_address", self.get_display_address())
            request.db_set("brief_description", self.get_display_description())
```

**Resource Consent Application:**
`lodgeick/doctype/resource_consent_application/`

*Already implemented with 1,200+ fields and 10 child tables.*

#### 3. API Endpoints

**Location:** `lodgeick/api.py`

```python
@frappe.whitelist()
def create_draft_request(data):
    """Creates Request and Application DocType"""
    # Create thin Request
    request = frappe.get_doc({...})

    # Create Application based on type
    if category == "Resource Consent":
        application = create_rc_application(request.name, data)
    elif "SPISC" in request_type:
        application = create_spisc_application(request.name, data)

    # Set polymorphic link
    request.db_set("application_doctype", application.doctype)
    request.db_set("application_name", application.name)
```

### Frontend Components

#### 1. Enhanced UI Components

**NZAddressInput.vue** - New Zealand address with city dropdown
**ConsentTypeSelector.vue** - Multi-select cards for consent types
**ActivityStatusSelector.vue** - RMA activity classification
**UniversalAddressLookup.vue** - Multi-country address lookup (NZ, AU, PH)

#### 2. Review Component

**EnhancedApplicationReview.vue** - Polymorphic review screen

```vue
<EnhancedApplicationReview
  :request-name="request.name"
  :application-doctype="request.application_doctype"
  :application-name="request.application_name"
/>
```

**Features:**
- Fetches Application data via polymorphic link
- Displays RC-specific sections (consent types, property, AEE)
- Displays SPISC-specific sections (personal info, economic status)
- Automatic detection based on application_doctype

---

## Implementation Guide

### Creating a New Request Type

#### Step 1: Create Application DocType

```bash
cd apps/lodgeick
bench new-doctype --app lodgeick
# Name: "{Type} Application"
# Module: Lodgeick
```

**Add fields:**
```json
{
  "fields": [
    {
      "fieldname": "request",
      "fieldtype": "Link",
      "options": "Request",
      "unique": 1,
      "reqd": 1
    },
    // ... your domain-specific fields
  ]
}
```

#### Step 2: Add Business Logic

```python
# {type}_application.py
class YourApplication(Document):
    def on_update(self):
        """Sync display fields to Request"""
        if self.request:
            request = frappe.get_doc("Request", self.request)
            request.db_set("property_address", self.your_address_field)
            request.db_set("brief_description", f"{self.name} - {self.type}")
```

#### Step 3: Configure Request Type

Create Request Type record with:
- `step_configs` - Wizard steps
- `step_sections` - Sections within steps
- `step_fields` - Individual fields

#### Step 4: Update API

Add to `api.py`:
```python
def create_your_application(request_name, data):
    app = frappe.get_doc({
        "doctype": "Your Application",
        "request": request_name,
        # Map form fields
    })
    app.insert(ignore_mandatory=True)
    return app

# Hook into create_draft_request()
if request_type == "Your Type":
    application = create_your_application(request.name, data)
```

---

## Address Lookup System

### Multi-Country Support

**Countries Supported:**
- 🇳🇿 **New Zealand** - LINZ Property API (active)
- 🇦🇺 **Australia** - Stub (ready for GNAF integration)
- 🇵🇭 **Philippines** - Stub (ready for Google Places/OSM)

### Backend API

```python
@frappe.whitelist(allow_guest=True)
def search_addresses_universal(query, country):
    """Universal address lookup for NZ, AU, PH"""
    if country == "NZ":
        return search_property_address(query)
    elif country == "AU":
        return search_australia_addresses(query)
    elif country == "PH":
        return search_philippines_addresses(query)
```

### Frontend Usage

```vue
<UniversalAddressLookup
  v-model="address"
  :country="'NZ'"
  :show-country-selector="true"
  @address-selected="handleAddressSelected"
/>
```

### Integration Options

**Australia:**
- data.gov.au GNAF (free, government)
- Google Places API
- Mapbox Geocoding API

**Philippines:**
- Google Places API
- Nominatim (OpenStreetMap - free)
- OneMap Philippines

---

## UI Components

### 1. NZAddressInput

**Purpose:** New Zealand-specific address input with validated cities

```vue
<NZAddressInput
  v-model="address"
  :required="true"
/>
```

**Features:**
- Green gradient header
- NZ cities dropdown (Lower Hutt, Wellington, etc.)
- 4-digit postcode validation
- Real-time validation feedback

### 2. ConsentTypeSelector

**Purpose:** Multi-select UI for RMA consent types

```vue
<ConsentTypeSelector
  v-model="selectedConsents"
  :required="true"
/>
```

**Consent Types:**
- Land Use Consent
- Subdivision Consent
- Discharge Permit
- Water Permit
- Coastal Permit

### 3. ActivityStatusSelector

**Purpose:** RMA activity classification selector

```vue
<ActivityStatusSelector
  v-model="activityStatus"
  :required="true"
/>
```

**Activity Levels:**
- Permitted (green)
- Controlled (blue)
- Restricted Discretionary (yellow)
- Discretionary (orange)
- Non-Complying (red)

---

## Testing

### Backend Testing

```python
# Test SPISC Application creation
def test_create_spisc_application():
    request = frappe.get_doc("Request", "REQ-001")

    data = {
        "full_name": "Juan Dela Cruz",
        "birth_date": "1960-01-01",
        "monthly_income": 5000
    }

    app = create_spisc_application(request.name, data)

    assert app.age >= 60
    assert request.application_doctype == "SPISC Application"
    assert request.application_name == app.name
```

### Frontend Testing

```javascript
// Test UniversalAddressLookup
describe('UniversalAddressLookup', () => {
  it('fetches NZ addresses', async () => {
    const wrapper = mount(UniversalAddressLookup, {
      props: { country: 'NZ' }
    })

    await wrapper.find('input').setValue('123 Main')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.searchResults).toHaveLength(5)
  })
})
```

---

## Migration Notes

### Migrating Existing SPISC Applications

Current SPISC applications store data in `Request.draft_full_data` (JSON). Options:

**Option 1: Dual Support** (Recommended)
- Old applications continue using JSON
- New applications use SPISC Application DocType
- No breaking changes

**Option 2: Data Migration**
```python
# Migration script
def migrate_spisc_to_doctype():
    requests = frappe.get_all("Request",
        filters={"request_type": "SPISC", "application_doctype": ["is", "not set"]})

    for req in requests:
        request = frappe.get_doc("Request", req.name)
        data = json.loads(request.draft_full_data)

        # Create SPISC Application
        app = create_spisc_application(request.name, data)

        # Update Request
        request.db_set("application_doctype", "SPISC Application")
        request.db_set("application_name", app.name)
```

### Migrating RC Applications

RC already uses Application DocType pattern. Just need to:
1. ✅ Add polymorphic links (already done)
2. ✅ Update `create_draft_request()` (already done)
3. ⏳ Add Request Type configuration (Phase 2 - optional)

---

## Best Practices

### ✅ DO

- Create separate Application DocTypes for each request type
- Use polymorphic linking (application_doctype + application_name)
- Sync display fields in `on_update()` method
- Store complex data in Application DocType (not JSON)
- Use DynamicStepRenderer for configurable UI

### ❌ DON'T

- Store domain data in Request.draft_full_data
- Add type-specific fields to Request DocType
- Use EAV (Entity-Attribute-Value) pattern
- Hardcode step components
- Skip display field synchronization

---

## Decision Tree

**Q: Does your request type need child tables?**
→ YES: Create Application DocType
→ NO: Continue...

**Q: Need complex querying/reporting?**
→ YES: Create Application DocType
→ NO: Continue...

**Q: Statutory/regulatory requirements?**
→ YES: Create Application DocType
→ NO: Continue...

**Q: More than 50 fields?**
→ YES: Create Application DocType
→ NO: Could use JSON but Application DocType recommended

---

## Support & Resources

**Documentation:**
- [Request Type Configuration Guide](docs/REQUEST_TYPE_CONFIG.md)
- [Assessment Project Guide](docs/ASSESSMENT_GUIDE.md)
- [Property API Documentation](property-api/README.md)

**Code Examples:**
- SPISC Application: `lodgeick/doctype/spisc_application/`
- RC Application: `lodgeick/doctype/resource_consent_application/`
- API Methods: `lodgeick/api.py:375-520`

**Key Files:**
- Backend: `lodgeick/api.py`, `lodgeick/doctype/request/request.json`
- Frontend: `frontend/src/components/EnhancedApplicationReview.vue`
- Components: `frontend/src/components/NZAddressInput.vue`, etc.

---

## Version History

**v1.0 (2025-12-06):**
- Initial unified architecture implementation
- SPISC Application DocType created
- Universal address lookup (NZ, AU, PH)
- Enhanced UI components
- Polymorphic linking system
- EnhancedApplicationReview component

---

**Questions?** Contact the development team or refer to the inline code documentation.
