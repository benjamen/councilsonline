# Request Type Step Templates

This directory contains reusable step templates for Request Type configuration. Templates eliminate duplication and ensure consistency across different request types.

## Available Templates

### 1. `declaration.json`
**Standard declaration step with truth, consent, and signature fields**

- Declaration of information accuracy
- Authorization for verification
- Acknowledgment of false information consequences
- Electronic signature
- Date field

**Use Case**: Final step for most request types
**Customization Options**: Privacy consent, terms acceptance, witness fields

### 2. `applicant_details.json`
**Standard applicant information collection**

- Personal information (name, email, phone)
- Address fields (street, city, postal code, country)

**Use Case**: Initial step for applicant-submitted requests
**Customization Options**: Organization fields, agent fields, address format

### 3. `bank_details.json`
**Bank account information for payment processing (payouts TO applicant)**

- Account holder name
- Bank name
- Account number
- Account type
- Branch code (optional)

**Use Case**: Request types that make payments TO applicants (e.g., SPISC pensions, rebates)
**Customization Options**: SWIFT code, IBAN, country-specific fields

### 4. `payment_collection.json`
**Payment and invoice details (payments FROM applicant)**

- Invoice recipient details
- Billing address
- Payment method selection
- Purchase order number

**Use Case**: Request types that collect fees FROM applicants (e.g., Resource Consent lodgement fees)
**Customization Options**: Tax ID, fast-track option, payment methods

---

## Usage

### Method 1: Programmatic (Python)

```python
from councilsonline.templates.step_templates import load_template, apply_template

# Load a template to inspect it
template = load_template("declaration")

# Apply template to a Request Type
request_type = frappe.get_doc("Request Type", "My Request Type")
apply_template(request_type, "declaration", step_number=5)
request_type.save()
```

### Method 2: Programmatic with Customization

```python
# Apply with customization options
apply_template(
    request_type,
    "bank_details",
    customization={
        "include_swift_code": True,
        "include_iban": True
    },
    step_number=4
)
```

### Method 3: Manual JSON Copy

1. Open the template JSON file (e.g., `declaration.json`)
2. Copy the `step_config`, `sections`, and `fields`
3. Paste into your Request Type JSON configuration
4. Adjust `step_number` and `step_code` as needed

---

## Template Structure

Each template follows this structure:

```json
{
  "template_name": "unique_identifier",
  "template_title": "Human Readable Title",
  "description": "What this template provides",
  "version": "1.0",
  "step_config": {
    "step_code": "step_code_value",
    "step_title": "Step Title",
    "step_component": "DynamicStepRenderer",
    "is_enabled": 1,
    "is_required": 1,
    "show_on_review": 1
  },
  "sections": [
    {
      "section_code": "section_code_value",
      "section_title": "Section Title",
      "section_type": "Standard",
      "sequence": 1,
      "is_enabled": 1,
      "is_required": 1,
      "show_on_review": 1,
      "fields": [
        {
          "field_name": "field_name_value",
          "field_label": "Field Label",
          "field_type": "Data",
          "is_required": 1,
          "show_on_review": 1,
          "validation": "email"
        }
      ]
    }
  ],
  "customization_options": {
    "option_name": false
  },
  "usage_notes": "Additional guidance"
}
```

---

## Creating New Templates

To create a new template:

1. Create a new `.json` file in this directory
2. Follow the structure above
3. Include meaningful `customization_options`
4. Add clear `usage_notes`
5. Test the template with `validate_template()`:

```python
from councilsonline.templates.step_templates import validate_template
import json

with open('my_template.json') as f:
    template = json.load(f)

is_valid, errors = validate_template(template)
if not is_valid:
    print("Errors:", errors)
```

---

## Helper Functions

### `load_template(template_name)`
Load a template from JSON file

### `apply_template(request_type_doc, template_name, customization=None, step_number=None)`
Apply a template to a Request Type document

### `list_available_templates()`
Get list of all available template names

### `get_template_info(template_name)`
Get metadata about a template without loading full configuration

### `validate_template(template_data)`
Validate template structure

---

## Benefits

1. **Consistency**: Standard fields across all request types
2. **Reduced Duplication**: Write once, use everywhere
3. **Faster Development**: New request types can reuse proven patterns
4. **Easier Maintenance**: Update template once, affects all using it
5. **Best Practices**: Templates encode validation and UX patterns

---

## Examples

### Resource Consent with Templates

```python
rt_doc = frappe.new_doc("Request Type")
rt_doc.name = "Building Consent"
rt_doc.category = "Planning"

# Add standard applicant step
apply_template(rt_doc, "applicant_details", step_number=1)

# Add custom property/building steps (step 2-6)
# ... (custom configuration here)

# Add payment collection step
apply_template(rt_doc, "payment_collection", step_number=7, customization={
    "include_fast_track_option": True
})

# Add declaration step
apply_template(rt_doc, "declaration", step_number=8)

rt_doc.insert()
```

### SPISC with Templates

```python
rt_doc = frappe.new_doc("Request Type")
rt_doc.name = "Senior Citizen Pension"
rt_doc.category = "Social Assistance"

# Add applicant details
apply_template(rt_doc, "applicant_details", step_number=1)

# Add custom eligibility/household steps (step 2-4)
# ... (custom configuration here)

# Add bank details for pension payments
apply_template(rt_doc, "bank_details", step_number=5)

# Add declaration
apply_template(rt_doc, "declaration", step_number=6)

rt_doc.insert()
```

---

## Future Enhancements

Potential templates to add:

- `property_details` - Standard property information
- `document_upload` - File attachment step
- `agent_representation` - Agent acting on behalf
- `organization_details` - Company/organization information
- `emergency_contact` - Emergency contact details
- `identity_verification` - ID verification fields
- `terms_and_conditions` - T&C acceptance

---

**Version**: 1.0
**Last Updated**: 2025-12-07
**Phase**: 3.2 - Step Template Library
