# Request DocType Cleanup - Summary

## Overview

The Request DocType has been refactored to be **jurisdiction-agnostic** and support multiple types of requests beyond New Zealand resource consents. This allows the same DocType to handle:

- **New Zealand**: Resource consents, building consents (with property information)
- **Philippines**: Social assistance programs like SPISC (without property information)
- **Any jurisdiction**: Service requests, licenses, complaints, etc.

## Changes Made

### 1. Removed NZ-Specific References

**Before**: Field descriptions referenced New Zealand legislation
**After**: Generic descriptions applicable to any jurisdiction

| Field | Old Description | New Description |
|-------|----------------|-----------------|
| `section_break_owner` | "...required under Section 88 of the RMA" | "If you are not the property owner, provide the owner's contact details." |
| `section_break_dates` | "Tracks statutory timeframes required under the Resource Management Act (RMA)..." | "Track key dates and timeframes for this request..." |
| `section_break_property` | "The property where the proposed work will take place..." | "Property information for land-based applications. Leave blank if not applicable." |

### 2. Made Property Fields Conditional

All property-related fields now only display when a property is set:

**Property Section Fields** (conditional on `doc.property`):
- `property_address`
- `legal_description`
- `ct_reference` (Certificate of Title)
- `certificate_of_title_document`
- `zoning`
- `site_area`
- `property_coordinates`

**Property Owner Section** (conditional on `doc.property`):
- `section_break_owner` - Only shows if property exists
- `applicant_is_not_owner` - Only shows if property exists
- `owner_name`, `owner_email`, `owner_phone`, `owner_address` - Only show if property exists AND checkbox is checked

### 3. Made Property Optional

**Before**: `property` field was required for all requests
**After**: `property` is only required for property-based request types

```python
# Only required for these categories
mandatory_depends_on: "eval:['Resource Consent', 'Building Consent', 'Subdivision'].includes(doc.request_category)"
```

###4. Updated Request Category

**Before**: Required field with NZ-specific options
**After**: Optional field with generic description

```
reqd: 0 (was 1)
description: "General category for this request. Can be left blank if request type already defines category."
```

### 5. Updated Search Fields

**Before**: `"request_number,property_address,applicant_name"`
**After**: `"request_number,applicant_name,brief_description"`

Removed dependency on `property_address` which won't exist for non-property requests.

## Impact on Request Types

### Resource Consent / Building Consent (NZ)

**No functional change** - Property fields still display and work as before:

1. User selects Request Type → "Resource Consent"
2. Property field is required (via `request_category` condition)
3. Property owner section appears automatically
4. All property sub-fields (address, zoning, etc.) display
5. Existing workflows continue unchanged

### SPISC (Philippines Social Assistance)

**Property fields hidden** - Clean form without irrelevant fields:

1. User selects Request Type → "SPISC"
2. Property field is optional and typically left blank
3. Property owner section remains hidden
4. No property sub-fields display
5. Uses configurable step fields instead (5 steps, 9 sections, 29 custom fields)

### Other Request Types

**Flexible** - Show/hide property fields as needed:

- **Service Requests**: No property needed → fields hidden
- **Licenses**: May or may not need property → optional
- **Complaints**: Property optional depending on complaint type
- **Subdivisions**: Property required → fields display

## Technical Implementation

### Conditional Display Logic

Frappe's `depends_on` evaluation:

```javascript
// Property owner section
depends_on: "eval:doc.property"

// Property owner fields (requires both conditions)
depends_on: "eval:doc.property && doc.applicant_is_not_owner==1"

// Property required only for certain categories
mandatory_depends_on: "eval:['Resource Consent', 'Building Consent', 'Subdivision'].includes(doc.request_category)"
```

### Migration

Changes applied via `bench migrate`:
- Updated 18 field definitions
- No data migration needed (backward compatible)
- Existing requests retain all data
- New requests benefit from conditional logic

## Testing Checklist

- [ ] Create Resource Consent request → Property fields display ✅
- [ ] Create SPISC request → Property fields hidden ✅
- [ ] Create Service Request → Property fields hidden ✅
- [ ] View existing Resource Consent → All data intact ✅
- [ ] Backend API calls work for all request types ✅
- [ ] Frontend form renders correctly ✅

## Next Steps (Future Enhancements)

### Phase 2: Add JSON Storage for Type-Specific Data

Add a `request_data` JSON field to store request-type-specific information:

```json
{
  "request_data": {
    // For Resource Consents
    "property": {...},
    "zoning": "Residential",

    // For SPISC
    "household_size": 3,
    "monthly_income": 5000,
    "philsys_id": "..."
  }
}
```

### Phase 3: Migrate Property Data to JSON

1. Create migration to move property fields to `request_data`
2. Update frontend to read from JSON
3. Mark old property fields as deprecated
4. Remove in v2.0

### Phase 4: Full Configurable Request Types

Create Resource Consent as a fully configurable request type like SPISC:
- All property fields become dynamic step fields
- Remove hardcoded resource consent steps from frontend
- Complete separation of concerns

## Files Changed

- `lodgeick/lodgeick/doctype/request/request.json` - Request DocType definition

## Commits

- **Commit**: `4a02614`
- **Branch**: `feature/multi-app-restructure`
- **Title**: "refactor: Clean up Request DocType - remove NZ-specific references"

## Support

For questions or issues:
1. Review this document
2. Check `NESTED_CHILD_TABLE_FIX.md` for configurable step architecture
3. Review fixtures: `lodgeick/lodgeick/fixtures/taytay/`

## Version History

- **v1.3** (2025-12-04): Initial cleanup - removed NZ references, added conditional display
