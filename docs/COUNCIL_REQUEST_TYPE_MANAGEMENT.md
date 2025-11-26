# Council Request Type Management

## Overview
The Lodgeick system allows each council to manage their own request types with council-specific pricing, descriptions, and process documentation. This provides flexibility for councils to customize request types to their local requirements while maintaining a centralized request type catalog.

## Architecture

### Two-Tier System

**1. Base Request Types** (Global Catalog)
- Managed centrally in the `Request Type` DocType
- Defines standard request types (e.g., "Resource Consent", "Building Consent", "LIM Request")
- Contains default values for fees, SLA, descriptions
- Shared across all councils

**2. Council Request Types** (Council-Specific Configuration)
- Managed per-council in the `Council Request Type` child table
- Allows councils to override base values
- Each council can enable/disable specific request types
- Council-specific pricing, descriptions, and process documentation

## Data Model

### Council DocType
Location: `/workspace/development/frappe-bench/apps/lodgeick/lodgeick/lodgeick/doctype/council/council.json`

**Key Field:**
```json
{
  "fieldname": "enabled_request_types",
  "fieldtype": "Table",
  "label": "Enabled Request Types",
  "options": "Council Request Type"
}
```

### Council Request Type (Child Table)
Location: `/workspace/development/frappe-bench/apps/lodgeick/lodgeick/lodgeick/doctype/council_request_type/council_request_type.json`

**Fields:**

| Field Name | Type | Description | Usage |
|------------|------|-------------|-------|
| `request_type` | Link | Link to base Request Type | Required - which request type to enable |
| `is_enabled` | Check | Enable/disable for this council | Default: checked |
| `base_fee_override` | Currency | Council-specific fee | Optional - overrides base request type fee |
| `sla_days_override` | Int | Council-specific SLA days | Optional - overrides base request type SLA |
| `brief_description` | Small Text | Short description (50-100 words) | Shown to applicants on request type selection |
| `process_description` | Text Editor | HTML process description | Detailed council process, shown to applicants |
| `notes` | Small Text | Internal notes | Internal only - not shown to applicants |

### Updated Fields (Just Added)

**brief_description:**
- Type: Small Text
- Purpose: Short description shown to applicants when selecting request type
- Example: "Apply for consent to subdivide your property into multiple titles. Required for all subdivisions regardless of number of lots."
- Overrides: Base request type description if provided

**process_description:**
- Type: Text Editor (HTML)
- Purpose: Detailed HTML description of the council's specific process
- Content can include:
  - Step-by-step process
  - Required documents
  - Timeline expectations
  - Contact information
  - Links to forms and resources
- Example HTML:
  ```html
  <h3>Our Process</h3>
  <ol>
    <li>Submit application online</li>
    <li>We review within 5 working days</li>
    <li>Request for Information (if needed)</li>
    <li>Decision within 20 working days</li>
  </ol>
  <p>For more information, contact our planning team at <a href="mailto:planning@huttcity.govt.nz">planning@huttcity.govt.nz</a></p>
  ```

## API Integration

### New API Method
Location: `/workspace/development/frappe-bench/apps/lodgeick/lodgeick/api.py:1050-1107`

**Method:** `get_council_request_types(council_code)`

**Purpose:** Fetch all enabled request types for a council with council-specific overrides

**Request:**
```javascript
await call('lodgeick.api.get_council_request_types', {
  council_code: 'HCC'
})
```

**Response:**
```json
[
  {
    "name": "resource-consent",
    "request_type_name": "Resource Consent",
    "category": "Planning",
    "description": "Apply for consent to subdivide your property...",
    "base_fee": 350.00,
    "sla_days": 20,
    "process_description": "<h3>Our Process</h3><ol>...",
    "is_active": true,
    "requires_property": true,
    "requires_payment": true,
    "council_specific": {
      "brief_description": "Council-specific description...",
      "process_description": "<h3>...</h3>",
      "base_fee_override": 350.00,
      "sla_days_override": 20
    }
  }
]
```

**Data Priority:**
1. If council has `base_fee_override` → use it, else use base request type fee
2. If council has `sla_days_override` → use it, else use base request type SLA
3. If council has `brief_description` → use it, else use base request type description
4. If council has `process_description` → include it (empty string if not set)

## Usage Workflow

### 1. Admin Setup (per Council)

**Step 1:** Navigate to Council form (e.g., "Hutt City Council")

**Step 2:** Go to "Request Types" section

**Step 3:** Add request types to `enabled_request_types` table:
- Select Request Type from dropdown
- Check "Enabled" checkbox
- Optionally override base fee
- Optionally override SLA days
- Add brief description (recommended)
- Add process description with HTML (recommended)
- Add internal notes if needed

**Example Configuration:**

| Request Type | Enabled | Base Fee Override | SLA Override | Brief Description | Process Description |
|-------------|---------|-------------------|--------------|-------------------|---------------------|
| Resource Consent | ✓ | $350 | 20 days | "Apply for subdivision consent..." | `<h3>Our Process...</h3>` |
| Building Consent | ✓ | $250 | 15 days | "Apply for building work..." | `<h3>Steps...</h3>` |
| LIM Request | ✓ | $150 | 5 days | "Request property information..." | `<p>Turnaround...</p>` |

### 2. Frontend Integration

**Current Implementation:**
The frontend already loads request types per council. With the new API, it will automatically receive council-specific pricing and descriptions.

**Update Required:**
Update the frontend request type loading to use `get_council_request_types` instead of querying Request Type directly.

**Location to update:** `/workspace/development/frappe-bench/apps/lodgeick/frontend/src/pages/NewRequest.vue`

**Before:**
```javascript
const { data: requestTypes } = createListResource({
  doctype: 'Request Type',
  filters: { is_active: 1 }
})
```

**After:**
```javascript
const requestTypes = ref([])

watch(() => formData.value.council, async (councilCode) => {
  if (councilCode) {
    const types = await call('lodgeick.api.get_council_request_types', {
      council_code: councilCode
    })
    requestTypes.value = types
  }
})
```

### 3. Displaying Process Information

When a user selects a request type, show the council's process description:

```html
<div v-if="selectedRequestType?.process_description" class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
  <h3 class="font-semibold text-blue-900 mb-2">{{ selectedCouncil.council_name }} Process</h3>
  <div class="text-sm text-blue-800" v-html="selectedRequestType.process_description"></div>
</div>
```

## Benefits

### For Councils
✅ **Flexibility:** Each council can set their own fees and SLAs
✅ **Custom Messaging:** Provide council-specific guidance to applicants
✅ **Process Transparency:** Detailed HTML descriptions inform applicants
✅ **Easy Management:** Enable/disable request types per council
✅ **Internal Notes:** Document council-specific requirements

### For Applicants
✅ **Clear Pricing:** See exact fees upfront (council-specific)
✅ **Process Clarity:** Understand what to expect from their council
✅ **Accurate Timelines:** Council-specific SLAs shown
✅ **Better Guidance:** Council-specific descriptions help prepare applications

### For System
✅ **Centralized Catalog:** Maintain standard request types globally
✅ **Decentralized Customization:** Councils customize without changing core
✅ **Data Integrity:** Base request types remain consistent
✅ **Multi-Tenancy:** Perfect for SaaS multi-council deployment

## Example: Council Configuration

### Hutt City Council - Resource Consent

**Base Request Type:**
- Name: Resource Consent
- Base Fee: $300
- SLA Days: 20
- Description: "Apply for resource consent under the RMA"

**Council Override (HCC):**
- Enabled: ✓
- Base Fee Override: $350
- SLA Days Override: 20 days
- Brief Description:
  ```
  Apply for resource consent for activities requiring approval under the Lower Hutt District Plan.
  Typical processing time is 20 working days for non-notified applications.
  ```
- Process Description:
  ```html
  <h3>How to Apply</h3>
  <ol>
    <li><strong>Submit Online:</strong> Complete the application form with all required information</li>
    <li><strong>Initial Review:</strong> We'll acknowledge receipt within 2 working days and assign a planner</li>
    <li><strong>RFI (if needed):</strong> We may request additional information - the clock stops during this time</li>
    <li><strong>Decision:</strong> Non-notified applications decided within 20 working days</li>
  </ol>

  <h4>What You Need</h4>
  <ul>
    <li>Site plans and drawings</li>
    <li>Assessment of Environmental Effects (AEE)</li>
    <li>Written approvals from affected parties (if applicable)</li>
  </ul>

  <h4>Questions?</h4>
  <p>Contact our planning team: <a href="mailto:planning@huttcity.govt.nz">planning@huttcity.govt.nz</a> or call 04 570 6666</p>
  ```
- Internal Notes:
  ```
  Requires planning officer review. Assign to planning team.
  Check for pre-app meetings first.
  ```

## Migration Notes

### Existing Data
- Existing councils may not have `brief_description` or `process_description` populated
- System will fall back to base Request Type description
- Councils should be notified to update their configurations

### Recommended Rollout
1. ✅ Update Council Request Type DocType schema (DONE)
2. ✅ Add API method `get_council_request_types` (DONE)
3. 🔄 Update frontend to use new API (PENDING)
4. 🔄 Update UI to display process descriptions (PENDING)
5. 🔄 Train council admins on how to configure (PENDING)
6. 🔄 Migrate existing council data (PENDING)

## Testing

### Test Scenarios

**1. Council with Overrides:**
- Create council "Test Council"
- Add Resource Consent with fee override $400
- Add brief description
- Add process description with HTML
- API should return $400 fee and custom descriptions

**2. Council without Overrides:**
- Create council "Basic Council"
- Add Resource Consent without overrides
- API should return base $300 fee and base description

**3. Mixed Configuration:**
- Add multiple request types to one council
- Some with overrides, some without
- Verify correct pricing and descriptions per type

**4. Disabled Request Type:**
- Uncheck "Enabled" on a council request type
- API should not return that type for the council

**5. HTML Rendering:**
- Add process description with HTML tags
- Verify HTML renders correctly in frontend
- Check for XSS protection (v-html is used)

## Security Considerations

### HTML in Process Description
- Uses `v-html` directive in Vue
- Trust only council admin input
- Councils have their own admin access
- Sanitization not needed as councils are trusted entities
- Monitor for script injection attempts

### Data Access
- API method requires authentication
- Returns only active councils
- Returns only enabled request types
- Councils can only see their own data in UI

## Future Enhancements

1. **Templating System:** Pre-built templates for common process descriptions
2. **Rich Media:** Support for images, videos in process descriptions
3. **Multi-language:** Translate descriptions per council's locale
4. **Version Control:** Track changes to council configurations over time
5. **Approval Workflow:** Require approval for fee changes
6. **Analytics:** Track which descriptions lead to better application quality

## Summary

The council request type management system is **fully implemented** at the backend level. The architecture supports:

✅ Council-specific pricing (base_fee_override)
✅ Council-specific SLAs (sla_days_override)
✅ Council-specific brief descriptions
✅ Council-specific process descriptions (HTML)
✅ Internal notes for council staff
✅ Enable/disable per council
✅ API method to fetch council-specific data

**Next Steps:** Update frontend to consume the new API and display council-specific process descriptions to applicants.
