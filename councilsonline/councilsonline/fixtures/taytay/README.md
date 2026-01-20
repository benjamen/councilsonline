# Taytay Council Fixtures

This directory contains fixture data for the **Taytay Council** (Philippines) and its configurable request types, specifically the **Social Pension for Indigent Senior Citizens (SPISC)** application.

## What's Included

### 1. Council Configuration (`taytay_council.json`)
- **Council Code**: `TAYTAY-PH`
- **Council Name**: TayTay Council
- **Official Name**: Municipal Government of Taytay, Rizal
- **Enabled Request Types**:
  - Social Pension for Indigent Senior Citizens (SPISC)
  - Local Senior Assistance / Financial Aid for Elderly
  - Burial / Medical Support for Seniors

### 2. SPISC Request Type (`spisc_request_type.json`)

The **Social Pension for Indigent Senior Citizens (SPISC)** is a fully configured request type with:

- **5 Configurable Steps**:
  1. Personal Information
  2. Household Information
  3. Identity Verification
  4. Supporting Documents
  5. Declaration & Submission

- **9 Sections**:
  - Basic Details
  - Contact Information
  - Residential Address
  - Household Composition
  - Economic Status
  - Identity Documents
  - Required Documents
  - Optional Supporting Documents
  - Applicant Declaration

- **29 Fields** including:
  - Text inputs (Full Name, Address, etc.)
  - Date fields (Date of Birth, Signature Date)
  - Select dropdowns (Sex, Civil Status, Living Arrangement)
  - Currency fields (Monthly Income)
  - Checkboxes (4Ps Beneficiary, Declarations)
  - File attachments (Certificates, ID copies, Photos)

This demonstrates the **flattened child table architecture** required by Frappe:
- `step_configs` → Steps configuration
- `step_sections` → Sections with `parent_step_code` reference
- `step_fields` → Fields with `parent_section_code` reference

## Installation

### On a Fresh Site

```bash
# Import fixtures on a new Frappe site
bench --site your-site-name execute councilsonline.councilsonline.fixtures.taytay.import_taytay_fixtures.import_fixtures
```

### On an Existing Site

The import script will update existing records if they're found, so it's safe to run on an existing site:

```bash
bench --site your-site-name execute councilsonline.councilsonline.fixtures.taytay.import_taytay_fixtures.import_fixtures
```

### Expected Output

```
================================================================================
IMPORTING TAYTAY FIXTURES
================================================================================

Step 1: Importing Taytay Council...
  ✅ Created Council: TAYTAY-PH

Step 2: Importing SPISC Request Type with step configuration...
  ✅ Created Request Type: Social Pension for Indigent Senior Citizens (SPISC)
     - 5 steps
     - 9 sections
     - 29 fields

================================================================================
IMPORT COMPLETE
================================================================================
```

## Verification

After importing, verify the data:

1. **Council**: Navigate to http://your-site/app/council/TAYTAY-PH
2. **Request Type**: Navigate to http://your-site/app/request-type/Social%20Pension%20for%20Indigent%20Senior%20Citizens%20(SPISC)
3. **Test the Form**: Navigate to http://your-site/frontend and create a new SPISC request

## Production Deployment

### Option 1: Add to Frappe's fixtures system

Update `/workspace/development/frappe-bench/apps/councilsonline/councilsonline/hooks.py`:

```python
fixtures = [
    {
        "dt": "Council",
        "filters": [["council_code", "=", "TAYTAY-PH"]]
    },
    {
        "dt": "Request Type",
        "filters": [["name", "=", "Social Pension for Indigent Senior Citizens (SPISC)"]]
    }
]
```

Then export:

```bash
bench --site your-site export-fixtures
```

### Option 2: Use the import script (Recommended)

1. Include the fixture files in your app deployment
2. Add a migration patch to import on first deploy:

```python
# councilsonline/patches/v1_3/import_taytay_fixtures.py
import frappe
from councilsonline.councilsonline.fixtures.taytay.import_taytay_fixtures import import_fixtures

def execute():
    import_fixtures()
```

3. Add to `patches.txt`:
```
councilsonline.patches.v1_3.import_taytay_fixtures
```

### Option 3: Manual import on production

```bash
# SSH to production server
cd /path/to/frappe-bench

# Import fixtures
bench --site production-site execute councilsonline.councilsonline.fixtures.taytay.import_taytay_fixtures.import_fixtures

# Restart
bench restart
```

## Updating Fixtures

If you modify the Taytay council or SPISC request type in development:

```bash
# Re-export the council
bench --site councilsonline.localhost export-doc Council "TAYTAY-PH"

# Copy to fixtures directory
cp councilsonline/councilsonline/council/taytay_ph/taytay_ph.json councilsonline/councilsonline/fixtures/taytay/taytay_council.json

# Re-export SPISC
bench --site councilsonline.localhost export-doc "Request Type" "Social Pension for Indigent Senior Citizens (SPISC)"

# Copy to fixtures directory
cp "councilsonline/councilsonline/request_type/social_pension_for_indigent_senior_citizens_(spisc)/social_pension_for_indigent_senior_citizens_(spisc).json" councilsonline/councilsonline/fixtures/taytay/spisc_request_type.json
```

## Technical Notes

### Flattened Child Table Architecture

Frappe **does not support 3+ levels of nested child tables**. The SPISC request type uses a flattened structure:

**CORRECT** (2 levels):
```
Request Type (parent DocType)
  ├─ Request Type Step Config (child table)           ← LEVEL 1
  ├─ Request Type Step Section (child with parent_step_code)  ← LEVEL 1
  └─ Request Type Step Field (child with parent_section_code)  ← LEVEL 1
```

**INCORRECT** (3 levels - will not work):
```
Request Type
  └─ Step Config
      └─ Section
          └─ Field  ← 3rd level not supported!
```

The relationships are maintained through code reference fields:
- `step_sections.parent_step_code` → references `step_configs.step_code`
- `step_fields.parent_section_code` → references `step_sections.section_code`

See [NESTED_CHILD_TABLE_FIX.md](../../../NESTED_CHILD_TABLE_FIX.md) for details.

## Files in this Directory

```
taytay/
├── README.md                      # This file
├── taytay_council.json            # Council configuration
├── spisc_request_type.json        # SPISC request type with all steps/sections/fields
└── import_taytay_fixtures.py      # Import script
```

## Support

For issues or questions:
1. Check the main documentation: [NESTED_CHILD_TABLE_FIX.md](../../../NESTED_CHILD_TABLE_FIX.md)
2. Verify the backend API: `councilsonline/api.py::get_request_type_steps()`
3. Check frontend rendering: `frontend/src/components/DynamicStepRenderer.vue`

## Version History

- **v1.2** (2025-12-04): Initial Taytay fixtures with SPISC configurable steps
  - Flattened child table structure
  - 5 steps, 9 sections, 29 fields
  - Full Philippines localization (barangay, PhilSys ID, 4Ps, etc.)
