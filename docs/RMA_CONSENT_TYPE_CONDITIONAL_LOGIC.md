# RMA Consent-Type-Specific Conditional Logic Implementation

**Version:** 1.0
**Date:** 2025-11-30
**Status:** ✅ Complete
**Commits:** [64413a1](https://github.com/benjamen/lodgeick/commit/64413a1), [4cbedb5](https://github.com/benjamen/lodgeick/commit/4cbedb5)

## Overview

This document describes the implementation of consent-type-specific conditional logic in the Resource Consent application form, ensuring compliance with RMA (Resource Management Act 1991) statutory requirements.

The system now intelligently shows/hides fields and enforces validation rules based on which consent types are selected (Land Use, Subdivision, Water Permit, Discharge Permit, Coastal Permit).

## Problem Statement

Previously, all Resource Consent applications used the same form regardless of consent type, showing unnecessary fields and not enforcing consent-type-specific RMA requirements:

- **s.123 RMA**: Water Permits, Discharge Permits, and Coastal Permits have max 35-year duration; Land Use and Subdivision can be unlimited
- **s.221 RMA**: Subdivision consents may require consent notices on title
- **s.106 RMA**: Land Use and Subdivision consents must be refused if natural hazards would cause material damage
- **s.87AAB RMA**: Fast-track processing available for Controlled activities (except Subdivision)

## Solution Architecture

### Frontend Implementation (Commit 64413a1)

#### 1. New Step: Step 7B - Consent Details
**Location:** [frontend/src/components/request-steps/Step7BConsentDetails.vue](../frontend/src/components/request-steps/Step7BConsentDetails.vue)

A dedicated step for consent-type-specific administrative details:

- **Per-Consent-Type Duration Fields**
  - Dynamically creates duration input for each selected consent type
  - Land Use/Subdivision: Unlimited checkbox available
  - Water/Discharge/Coastal Permits: Max 35 years enforced
  - Uses reactive data management to sync with parent form

- **Lapsing Period** (s.125 RMA)
  - Default: 5 years
  - 10 years for renewable energy
  - 3 years for aquaculture (Coastal Permit)

- **Consent Notice** (s.221 RMA - Subdivision only)
  - Appears only when Subdivision selected
  - Checkbox + conditional text field
  - Required if checked

- **Coastal Occupation Charge** (Coastal Permit only)
  - Acknowledgment checkbox
  - Appears only when Coastal Permit selected

- **Fast-Track Processing** (s.87AAB RMA)
  - User-selectable checkbox
  - Eligibility calculated: Controlled activity AND NOT Subdivision
  - Council can enable/disable via Request Type configuration

**Key Technical Features:**
```javascript
// Duration data management per consent type
const durationData = reactive({})

const getDurationData = (consentType) => {
  if (!durationData[consentType]) {
    const existing = props.modelValue.consent_type_durations?.find(
      d => d.consent_type === consentType
    )
    if (existing) {
      durationData[consentType] = { ...existing }
    } else {
      durationData[consentType] = {
        consent_type: consentType,
        duration_years: 10,
        duration_unlimited: false
      }
    }
  }
  return durationData[consentType]
}

// Sync to parent when changed
watch(durationData, () => {
  const durations = Object.values(durationData)
  emit('update:modelValue', {
    ...props.modelValue,
    consent_type_durations: durations
  })
}, { deep: true })
```

#### 2. Enhanced Step 10 (formerly Step 11) - NES & Hazards
**Location:** [frontend/src/components/request-steps/Step10NESHazards.vue](../frontend/src/components/request-steps/Step10NESHazards.vue)

**Conditional s.106 RMA Warning:**
- Prominent amber warning box appears for Land Use/Subdivision
- Outlines mandatory refusal grounds under s.106
- Emphasizes critical nature of hazards assessment

**"No Hazards" Confirmation:**
- For LUC/SC with no hazards identified
- Requires explicit confirmation checkbox
- Prevents accidental oversight of hazards consideration
- Clears hazards array when confirmed

```javascript
const requiresHazardsAssessment = computed(() => {
  return hasConsentType('Land Use') || hasConsentType('Subdivision')
})

// Clear hazards if user explicitly confirms none
watch(() => localData.value.no_natural_hazards_confirmed, (newVal) => {
  if (newVal && requiresHazardsAssessment.value) {
    const updatedData = { ...props.modelValue }
    updatedData.natural_hazards = []
    updatedData.no_natural_hazards_confirmed = true
    emit('update:modelValue', updatedData)
  }
})
```

#### 3. Updated NewRequest.vue
**Location:** [frontend/src/pages/NewRequest.vue](../frontend/src/pages/NewRequest.vue)

**Consent Type Computed Properties:**
```javascript
const hasConsentType = (type) => {
  return formData.value.consent_types?.some(ct => ct.consent_type === type) || false
}

const isLandUse = computed(() => hasConsentType('Land Use'))
const isSubdivision = computed(() => hasConsentType('Subdivision'))
const isWaterPermit = computed(() => hasConsentType('Water Permit'))
const isDischargePermit = computed(() => hasConsentType('Discharge Permit'))
const isCoastalPermit = computed(() => hasConsentType('Coastal Permit'))

const requiresNaturalHazardsAssessment = computed(() => {
  return isLandUse.value || isSubdivision.value
})

const eligibleForFastTrack = computed(() => {
  const isControlled = formData.value.activity_status === 'Controlled'
  const notSubdivision = !isSubdivision.value
  return isControlled && notSubdivision && isResourceConsent.value
})
```

**Step Renumbering:**
All Resource Consent steps after Step 7 incremented by 1:
- Step 7: Consent Type (unchanged)
- **Step 8: Consent Details (NEW)**
- Step 9: Proposal Details (was Step 8)
- Step 10: Site & Environment (was Step 9)
- Step 11: NES & Hazards (was Step 10)
- Step 12: AEE (was Step 11)
- Step 13: Plan Assessment (was Step 12)
- Step 14: Affected Parties (was Step 13)
- Step 15: Specialist Reports (was Step 14)
- Step 16: Proposed Conditions (was Step 15)
- Step 17: Declarations (was Step 16)
- Step 18: Review (was Step 17)

#### 4. Updated useFormValidation.js
**Location:** [frontend/src/composables/useFormValidation.js](../frontend/src/composables/useFormValidation.js)

**Step 8 Validation (Consent Details):**
```javascript
if (step === 8 && isResourceConsent.value) {
  // Duration validation - each consent type must have duration specified
  const consentTypes = formData.value.consent_types || []
  const hasDurations = consentTypes.every(ct => {
    const durationData = formData.value.consent_type_durations?.find(
      d => d.consent_type === ct.consent_type
    )
    if (!durationData) return false
    return durationData.duration_unlimited ||
           (durationData.duration_years && durationData.duration_years > 0)
  })

  // Consent notice validation (Subdivision only)
  const consentNoticeValid = !hasSubdivision(formData.value) ||
    !formData.value.consent_notice_required ||
    !!formData.value.consent_notice_details?.trim()

  return hasDurations && consentNoticeValid
}
```

**Step 11 Validation (NES & Hazards - LUC/SC):**
```javascript
if (step === 11 && isResourceConsent.value) {
  const requiresHazards = formData.value.consent_types?.some(ct =>
    ct.consent_type === 'Land Use' || ct.consent_type === 'Subdivision'
  )

  if (requiresHazards) {
    // Either have hazards identified OR explicitly confirm no hazards
    const hasHazards = formData.value.natural_hazards &&
                       formData.value.natural_hazards.length > 0
    const confirmedNoHazards = formData.value.no_natural_hazards_confirmed

    if (!hasHazards && !confirmedNoHazards) {
      return false // Must either identify hazards or confirm there are none
    }
  }

  return true // Optional for other consent types
}
```

**Submit Validation:**
```javascript
const canSubmit = computed(() => {
  if (isResourceConsent.value) {
    // Duration validation - per consent type
    const hasDurations = consentTypes.every(ct => {
      const durationData = formData.value.consent_type_durations?.find(
        d => d.consent_type === ct.consent_type
      )
      if (!durationData) return false
      return durationData.duration_unlimited ||
             (durationData.duration_years && durationData.duration_years > 0)
    })

    // Natural hazards validation for LUC/SC
    const requiresHazards = formData.value.consent_types?.some(ct =>
      ct.consent_type === 'Land Use' || ct.consent_type === 'Subdivision'
    )
    const hazardsValid = !requiresHazards ||
      (formData.value.natural_hazards && formData.value.natural_hazards.length > 0) ||
      formData.value.no_natural_hazards_confirmed

    return hasCouncil && hasRequestType && hasApplicantDetails &&
      hasPropertyAddress && hasDeliveryPreference && hasInvoiceTo &&
      hasConsentTypes && hasDurations && hazardsValid &&
      hasBriefDescription && hasDetailedDescription &&
      hasSiteDescription && hasCurrentUse && hasAEE && hasDeclarations
  }
})
```

### Backend Implementation (Commit 4cbedb5)

#### 1. New Child Doctype: Request Consent Type Duration
**Location:** [lodgeick/lodgeick/doctype/request_consent_type_duration/](../lodgeick/lodgeick/doctype/request_consent_type_duration/)

**Fields:**
- `consent_type` (Select) - Land Use, Subdivision, Water Permit, Discharge Permit, Coastal Permit
- `duration_years` (Int) - Requested duration in years
- `duration_unlimited` (Check) - Only for Land Use/Subdivision

**Validation Logic:**
```python
class RequestConsentTypeDuration(Document):
    def validate(self):
        """Validate duration based on consent type and RMA requirements."""
        max_duration_types = ["Discharge Permit", "Water Permit", "Coastal Permit"]

        if self.consent_type in max_duration_types:
            if self.duration_unlimited:
                frappe.throw(
                    f"{self.consent_type} cannot have unlimited duration. "
                    f"Maximum is 35 years per s.123 RMA."
                )
            if self.duration_years and self.duration_years > 35:
                frappe.throw(
                    f"{self.consent_type} duration cannot exceed 35 years per s.123 RMA."
                )

        # Ensure either duration_years or duration_unlimited is set
        if not self.duration_unlimited and not self.duration_years:
            frappe.throw(
                f"Please specify either a duration in years or select unlimited duration "
                f"for {self.consent_type}."
            )
```

#### 2. Resource Consent Application Updates
**Location:** [lodgeick/lodgeick/doctype/resource_consent_application/resource_consent_application.json](../lodgeick/lodgeick/doctype/resource_consent_application/resource_consent_application.json)

**New Section: "Consent Details (s.123, s.221 RMA)"**

Added 8 new fields:

| Field | Type | RMA Reference | Description |
|-------|------|--------------|-------------|
| `consent_type_durations` | Table | s.123 | Per-consent-type duration requests |
| `lapsing_period_years` | Int (default: 5) | s.125 | Time before consent lapses |
| `consent_notice_required` | Check | s.221 | Subdivision - title notice required |
| `consent_notice_details` | Text | s.221 | Matters for consent notice |
| `coastal_occupation_charge_acknowledged` | Check | - | CP - charge acknowledgment |
| `request_fast_track` | Check | s.87AAB | Fast-track processing request |
| `no_natural_hazards_confirmed` | Check | s.106 | LUC/SC - no hazards confirmation |
| `nes_items` | Table | - | Applicant NES assessments |

All fields include appropriate `depends_on`, `description`, and default values.

#### 3. Request Type Updates
**Location:** [lodgeick/lodgeick/doctype/request_type/request_type.json](../lodgeick/lodgeick/doctype/request_type/request_type.json)

**New Field:**
- `fast_track_available` (Check) - Enables councils to control fast-track processing availability per request type (Resource Consent only)

## RMA Statutory Requirements Matrix

| Requirement | Consent Types | Field | Validation |
|-------------|--------------|-------|------------|
| **s.123 Duration Limits** | WP, DP, CP | `duration_years` | Max 35 years |
| **s.123 Unlimited Duration** | LUC, SC | `duration_unlimited` | Allowed |
| **s.125 Lapsing Period** | All | `lapsing_period_years` | Default 5 years |
| **s.221 Consent Notice** | SC only | `consent_notice_required`<br>`consent_notice_details` | Required if checked |
| **s.106 Natural Hazards** | LUC, SC | `natural_hazards`<br>`no_natural_hazards_confirmed` | Must identify OR confirm none |
| **s.87AAB Fast-Track** | All except SC | `request_fast_track` | Controlled activities only |
| **Coastal Occupation Charge** | CP only | `coastal_occupation_charge_acknowledged` | Acknowledgment |

## Testing Scenarios

### 1. Single Consent Type - Land Use
- ✅ LUC duration field allows unlimited
- ✅ Natural hazards section shows s.106 critical warning
- ✅ Cannot proceed from Step 11 without hazards OR "no hazards" confirmation
- ✅ No consent notice field
- ✅ No coastal charge field
- ✅ Fast-track checkbox available if Controlled

### 2. Single Consent Type - Subdivision
- ✅ SC duration field allows unlimited
- ✅ Consent notice field appears and is required when checked
- ✅ Natural hazards section shows s.106 critical warning
- ✅ Cannot proceed from Step 11 without hazards OR "no hazards" confirmation
- ✅ Fast-track NOT available (even if Controlled)

### 3. Single Consent Type - Water Permit
- ✅ WP duration max 35 years, no unlimited checkbox
- ✅ No consent notice field
- ✅ Natural hazards section has standard messaging only
- ✅ Can proceed from Step 11 without hazards
- ✅ Fast-track checkbox available if Controlled

### 4. Single Consent Type - Coastal Permit
- ✅ CP duration max 35 years
- ✅ Coastal occupation charge acknowledgment appears
- ✅ Lapsing period shows 3-year option for aquaculture
- ✅ Fast-track checkbox available if Controlled

### 5. Multiple Consent Types - LUC + SC
- ✅ Two duration fields appear (one for LUC, one for SC)
- ✅ Both can be set to unlimited independently
- ✅ Consent notice field appears (SC requirement)
- ✅ Natural hazards section shows s.106 warning
- ✅ Cannot proceed without hazards OR confirmation
- ✅ Fast-track NOT available (SC blocks it)

### 6. Multiple Consent Types - LUC + WP
- ✅ Two duration fields appear
- ✅ LUC can be unlimited, WP max 35 years
- ✅ Natural hazards section shows s.106 warning (due to LUC)
- ✅ Cannot proceed without hazards OR confirmation
- ✅ Fast-track checkbox available if Controlled

### 7. Multiple Consent Types - SC + CP
- ✅ Two duration fields appear
- ✅ SC can be unlimited, CP max 35 years
- ✅ Consent notice field appears
- ✅ Coastal occupation charge appears
- ✅ Natural hazards section shows s.106 warning (due to SC)
- ✅ Fast-track NOT available (SC blocks it)

## Files Modified

### Frontend
1. [frontend/src/components/request-steps/Step7BConsentDetails.vue](../frontend/src/components/request-steps/Step7BConsentDetails.vue) - **NEW**
2. [frontend/src/components/request-steps/Step10NESHazards.vue](../frontend/src/components/request-steps/Step10NESHazards.vue)
3. [frontend/src/pages/NewRequest.vue](../frontend/src/pages/NewRequest.vue)
4. [frontend/src/composables/useFormValidation.js](../frontend/src/composables/useFormValidation.js)

### Backend
1. [lodgeick/lodgeick/doctype/request_consent_type_duration/](../lodgeick/lodgeick/doctype/request_consent_type_duration/) - **NEW**
   - `__init__.py`
   - `request_consent_type_duration.json`
   - `request_consent_type_duration.py`
2. [lodgeick/lodgeick/doctype/resource_consent_application/resource_consent_application.json](../lodgeick/lodgeick/doctype/resource_consent_application/resource_consent_application.json)
3. [lodgeick/lodgeick/doctype/request_type/request_type.json](../lodgeick/lodgeick/doctype/request_type/request_type.json)

## Database Migration

Migration completed successfully via `bench migrate` with no errors.

## Future Enhancements

### Step Merging for Better UX
As noted in planning, future work will merge steps to reduce perceived form length:
- Merge Step 7 (Consent Type) + Step 8 (Consent Details) into single accordion/tabbed interface
- Consider merging Step 11 (NES & Hazards) + Step 12 (AEE) for LUC/SC applications
- Implement progressive disclosure patterns

### Council Configuration
- Allow councils to customize which fields are required per consent type
- Enable council-specific help text and guidance
- Council-level NES and hazards templates

## Related Documentation

- [RMA 1991 - Resource Management Act](https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM230265.html)
- [s.87AAB Fast-Track Processing](https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM2421544.html)
- [s.104 Matters for Consideration](https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM231940.html)
- [s.106 Refusal Grounds - Hazards](https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM231970.html)
- [s.123 Duration of Consent](https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM232528.html)
- [s.125 Lapsing of Consent](https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM232534.html)
- [s.221 Consent Notices](https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM237637.html)

## Version History

| Version | Date | Changes | Commits |
|---------|------|---------|---------|
| 1.0 | 2025-11-30 | Initial implementation | 64413a1, 4cbedb5 |
