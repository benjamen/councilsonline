# Frontend Implementation Guide: HCC Form Parity Features

## Overview
This document provides detailed instructions for implementing the new form fields in NewRequest.vue to match the backend schema changes completed in commit `900d360`.

## Backend Schema Completed ✓

### Request Doctype - New Fields Added:
1. **Owner Details Section** (conditional - shown if "I am not the property owner")
   - `applicant_is_not_owner` (checkbox)
   - `owner_name` (required if checked)
   - `owner_email`
   - `owner_phone`
   - `owner_address`

2. **Certificate of Title Document**
   - `certificate_of_title_document` (file upload - optional)

3. **Statutory Declarations** (all required checkboxes)
   - `declaration_rma_compliance`
   - `declaration_public_information`
   - `declaration_authorized`

4. **Invoicing Details**
   - `invoice_to` (dropdown: Applicant/Agent/Owner/Other)
   - `invoice_name` (required if "Other")
   - `invoice_email` (required if "Other")
   - `invoice_address`
   - `purchase_order_number`

### Resource Consent Application Doctype - New Fields Added:
1. **Transfer Deposit Section** (conditional)
   - `transfer_deposit_required` (checkbox)
   - `transfer_deposit_consent_number` (required if checked)

2. **AEE Document Upload**
   - `aee_document` (file upload - optional alternative to text fields)

3. **Structured AEE Fields**
   - `aee_activity_description`
   - `aee_existing_environment`
   - `aee_part2_assessment`

## Frontend Implementation Tasks

### File: `/workspace/development/frappe-bench/apps/lodgeick/frontend/src/pages/NewRequest.vue`

### Task 1: Add to formData Initialization (around line 3936)

```javascript
const formData = ref({
  // ... existing fields ...

  // NEW: Owner/Occupier fields
  applicant_is_not_owner: false,
  owner_name: '',
  owner_email: '',
  owner_phone: '',
  owner_address: '',

  // NEW: Certificate of Title document
  certificate_of_title_document: null,

  // NEW: Statutory declarations
  declaration_rma_compliance: false,
  declaration_public_information: false,
  declaration_authorized: false,

  // NEW: Invoicing details
  invoice_to: 'Applicant',
  invoice_name: '',
  invoice_email: '',
  invoice_address: '',
  purchase_order_number: '',

  // NEW: RC-specific fields
  transfer_deposit_required: false,
  transfer_deposit_consent_number: '',
  aee_document: null,
  aee_activity_description: '',
  aee_existing_environment: '',
  aee_part2_assessment: '',
})
```

### Task 2: Add Owner Details Section to Step 4 (after line 326)

Insert after the Applicant Contact Information section:

```vue
<!-- Property Owner Details (Conditional) -->
<div class="mt-6 border-t border-gray-200 pt-6">
  <div class="flex items-start mb-4">
    <input
      type="checkbox"
      v-model="formData.applicant_is_not_owner"
      class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
    />
    <label class="ml-3 text-sm font-medium text-gray-700">
      I am not the property owner
    </label>
  </div>

  <div v-if="formData.applicant_is_not_owner" class="space-y-4 pl-7">
    <p class="text-xs text-gray-600 mb-4">
      Under Section 88 of the RMA, you must provide the property owner's contact details.
    </p>

    <div class="grid md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Owner Name *</label>
        <input
          v-model="formData.owner_name"
          type="text"
          placeholder="Property owner's full name"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          :required="formData.applicant_is_not_owner"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Owner Email</label>
        <input
          v-model="formData.owner_email"
          type="email"
          placeholder="owner@example.com"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
    </div>

    <div class="grid md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Owner Phone</label>
        <input
          v-model="formData.owner_phone"
          type="tel"
          placeholder="021 123 4567"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Owner Address</label>
        <textarea
          v-model="formData.owner_address"
          rows="3"
          placeholder="Owner's postal address"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        ></textarea>
      </div>
    </div>
  </div>
</div>
```

### Task 3: Add CT Document Upload to Property Section (around line 400-450)

Find the property legal details section and add after Certificate of Title reference field:

```vue
<div>
  <label class="block text-sm font-medium text-gray-700 mb-2">
    Upload Certificate of Title (Optional)
  </label>
  <input
    type="file"
    @change="handleCTUpload"
    accept=".pdf,.jpg,.jpeg,.png"
    class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
  />
  <p v-if="formData.certificate_of_title_document" class="text-xs text-green-600 mt-1">
    ✓ Document uploaded
  </p>
  <p class="mt-1 text-xs text-gray-500">Upload a copy of the Certificate of Title if available</p>
</div>
```

### Task 4: Add File Upload Handler (in script section around line 5100)

```javascript
const handleCTUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const base64 = await fileToBase64(file)
    formData.value.certificate_of_title_document = {
      filename: file.name,
      filedata: base64,
      is_private: 0
    }
    console.log('[NewRequest] CT document uploaded:', file.name)
  } catch (error) {
    console.error('[NewRequest] Error uploading CT document:', error)
    alert('Failed to upload document. Please try again.')
  }
}

const handleAEEUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const base64 = await fileToBase64(file)
    formData.value.aee_document = {
      filename: file.name,
      filedata: base64,
      is_private: 0
    }
    console.log('[NewRequest] AEE document uploaded:', file.name)
  } catch (error) {
    console.error('[NewRequest] Error uploading AEE document:', error)
    alert('Failed to upload document. Please try again.')
  }
}
```

### Task 5: Add Transfer Deposit Section to RC Details (Step 5, around line 550)

Add near the top of the RC details step, after consent types:

```vue
<!-- Transfer Deposit from Existing Consent -->
<div class="border-t border-gray-200 pt-6 mt-6">
  <div class="flex items-start mb-4">
    <input
      type="checkbox"
      v-model="formData.transfer_deposit_required"
      class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
    />
    <label class="ml-3 text-sm font-medium text-gray-700">
      Transfer deposit from existing consent
    </label>
  </div>

  <div v-if="formData.transfer_deposit_required" class="pl-7">
    <label class="block text-sm font-medium text-gray-700 mb-2">
      Existing Consent Number *
    </label>
    <input
      v-model="formData.transfer_deposit_consent_number"
      type="text"
      placeholder="e.g., RC123456"
      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      :required="formData.transfer_deposit_required"
    />
    <p class="mt-1 text-xs text-gray-500">
      Enter the consent number from which the deposit should be transferred
    </p>
  </div>
</div>
```

### Task 6: Replace AEE Textarea with Structured Fields + Upload (around line 1200-1300)

Replace the existing single `assessment_of_effects` textarea with:

```vue
<!-- Assessment of Environmental Effects (AEE) -->
<div class="border-t border-gray-200 pt-6 mt-6">
  <h3 class="text-sm font-semibold text-gray-900 mb-2">
    Assessment of Environmental Effects (AEE) *
  </h3>
  <p class="text-xs text-gray-500 mb-4">
    Complete the structured fields below OR upload a completed AEE document (Schedule 4 RMA)
  </p>

  <!-- AEE Document Upload Option -->
  <div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
    <label class="block text-sm font-medium text-gray-700 mb-2">
      Upload Completed AEE Document (Optional)
    </label>
    <input
      type="file"
      @change="handleAEEUpload"
      accept=".pdf,.doc,.docx"
      class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
    />
    <p v-if="formData.aee_document" class="text-xs text-green-600 mt-1">
      ✓ AEE document uploaded
    </p>
    <p class="mt-1 text-xs text-gray-600">
      If you upload a document, you can skip the fields below or use them for AI-assisted completion
    </p>
  </div>

  <!-- Structured AEE Fields -->
  <div class="space-y-4">
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        1. Description of the Activity and its Purpose
      </label>
      <textarea
        v-model="formData.aee_activity_description"
        rows="4"
        placeholder="Describe what you are proposing to do and why..."
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      ></textarea>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        2. Description of the Existing Environment
      </label>
      <textarea
        v-model="formData.aee_existing_environment"
        rows="4"
        placeholder="Describe the current state of the site and surrounding area..."
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      ></textarea>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        3. Assessment Against Part 2 of the RMA (Sustainable Management)
      </label>
      <textarea
        v-model="formData.aee_part2_assessment"
        rows="4"
        placeholder="Assess how the proposal aligns with sustainable management principles..."
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      ></textarea>
    </div>

    <!-- Keep existing effects fields below -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        4. Effects on People (Amenity, Privacy, Noise, etc.)
      </label>
      <textarea
        v-model="formData.effects_on_people"
        rows="4"
        placeholder="Describe potential effects on neighbouring properties and the community..."
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      ></textarea>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        5. Physical Effects (Land, Water, Air)
      </label>
      <textarea
        v-model="formData.physical_effects"
        rows="4"
        placeholder="Describe effects on land stability, water quality, stormwater, air quality..."
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      ></textarea>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        6. Ecosystem and Biodiversity Effects
      </label>
      <textarea
        v-model="formData.ecosystem_effects"
        rows="4"
        placeholder="Describe effects on vegetation, wildlife, ecosystems..."
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      ></textarea>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        7. Cultural and Heritage Effects
      </label>
      <textarea
        v-model="formData.cultural_effects"
        rows="4"
        placeholder="Describe effects on cultural sites, heritage buildings, sites of significance to Māori..."
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      ></textarea>
    </div>
  </div>
</div>
```

### Task 7: Add Invoicing Section to Review Step (Step 6, around line 900)

Add before the summary section in the review step:

```vue
<!-- Invoicing Details -->
<div class="border-t border-gray-200 pt-6 mt-6">
  <h3 class="text-sm font-semibold text-gray-900 mb-4">Invoicing Details</h3>

  <div class="grid md:grid-cols-2 gap-4">
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Send Invoice To</label>
      <select
        v-model="formData.invoice_to"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="Applicant">Applicant</option>
        <option value="Agent/Consultant" v-if="formData.acting_on_behalf">Agent/Consultant</option>
        <option value="Property Owner" v-if="formData.applicant_is_not_owner">Property Owner</option>
        <option value="Other">Other</option>
      </select>
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Purchase Order Number</label>
      <input
        v-model="formData.purchase_order_number"
        type="text"
        placeholder="Optional PO number"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
    </div>
  </div>

  <div v-if="formData.invoice_to === 'Other'" class="grid md:grid-cols-2 gap-4 mt-4">
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Invoice Recipient Name *</label>
      <input
        v-model="formData.invoice_name"
        type="text"
        placeholder="Full name"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        :required="formData.invoice_to === 'Other'"
      />
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Invoice Email *</label>
      <input
        v-model="formData.invoice_email"
        type="email"
        placeholder="email@example.com"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        :required="formData.invoice_to === 'Other'"
      />
    </div>
  </div>

  <div v-if="formData.invoice_to === 'Other'" class="mt-4">
    <label class="block text-sm font-medium text-gray-700 mb-2">Invoice Address</label>
    <textarea
      v-model="formData.invoice_address"
      rows="3"
      placeholder="Postal address for invoicing"
      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
    ></textarea>
  </div>
</div>
```

### Task 8: Replace Single Terms Checkbox with Three Statutory Declarations

Find the current "terms and conditions" checkbox (around line 2100) and replace with:

```vue
<!-- Statutory Declarations -->
<div class="border-t border-gray-200 pt-6 mt-6">
  <h3 class="text-sm font-semibold text-gray-900 mb-4">Statutory Declarations *</h3>
  <p class="text-xs text-gray-600 mb-4">
    All declarations are required under the Resource Management Act 1991
  </p>

  <div class="space-y-3">
    <div class="flex items-start">
      <input
        type="checkbox"
        v-model="formData.declaration_rma_compliance"
        class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        required
      />
      <label class="ml-3 text-sm text-gray-700">
        I confirm this application contains all information required under Section 88 of the Resource Management Act 1991
      </label>
    </div>

    <div class="flex items-start">
      <input
        type="checkbox"
        v-model="formData.declaration_public_information"
        class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        required
      />
      <label class="ml-3 text-sm text-gray-700">
        I understand this information will be publicly available (unless marked as confidential under Section 42 RMA)
      </label>
    </div>

    <div class="flex items-start">
      <input
        type="checkbox"
        v-model="formData.declaration_authorized"
        class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        required
      />
      <label class="ml-3 text-sm text-gray-700">
        I am authorized to submit this application on behalf of the applicant{{ formData.applicant_is_not_owner ? ' and have informed the property owner' : '' }}
      </label>
    </div>
  </div>
</div>
```

### Task 9: Update Validation Logic (canProceed function, around line 4480)

Update Step 4 validation to check owner details if applicant_is_not_owner is checked:

```javascript
case 4:
  // Step 4: Property - Require either property link OR property_address, plus applicant fields
  const hasProperty = formData.value.property || formData.value.property_address
  const hasApplicantInfo = formData.value.applicant_phone && formData.value.applicant_type && formData.value.applicant_name && formData.value.applicant_email

  // NEW: Check owner details if checkbox is checked
  const hasOwnerInfo = !formData.value.applicant_is_not_owner || (
    formData.value.owner_name && formData.value.owner_name.trim().length > 0
  )

  return !!(hasProperty && hasApplicantInfo && hasOwnerInfo)
```

Update Step 6 (Review/Submit) validation to require all three declarations:

```javascript
case 6:
  // Step 6: Review & Submit - require all declarations
  return !!(
    formData.value.declaration_rma_compliance &&
    formData.value.declaration_public_information &&
    formData.value.declaration_authorized
  )
```

### Task 10: Update API Submission (submitRequest function, around line 5000)

Ensure all new fields are included in the API submission. The submit function should already handle all formData fields, but verify these specific new fields are mapped correctly:

```javascript
// In the API call payload, ensure these mappings exist:
resource_consent_application: {
  // ... existing fields ...
  transfer_deposit_required: formData.value.transfer_deposit_required ? 1 : 0,
  transfer_deposit_consent_number: formData.value.transfer_deposit_consent_number || null,
  aee_document: formData.value.aee_document,
  aee_activity_description: formData.value.aee_activity_description || null,
  aee_existing_environment: formData.value.aee_existing_environment || null,
  aee_part2_assessment: formData.value.aee_part2_assessment || null,
},

request: {
  // ... existing fields ...
  applicant_is_not_owner: formData.value.applicant_is_not_owner ? 1 : 0,
  owner_name: formData.value.owner_name || null,
  owner_email: formData.value.owner_email || null,
  owner_phone: formData.value.owner_phone || null,
  owner_address: formData.value.owner_address || null,
  certificate_of_title_document: formData.value.certificate_of_title_document,
  declaration_rma_compliance: formData.value.declaration_rma_compliance ? 1 : 0,
  declaration_public_information: formData.value.declaration_public_information ? 1 : 0,
  declaration_authorized: formData.value.declaration_authorized ? 1 : 0,
  invoice_to: formData.value.invoice_to || 'Applicant',
  invoice_name: formData.value.invoice_name || null,
  invoice_email: formData.value.invoice_email || null,
  invoice_address: formData.value.invoice_address || null,
  purchase_order_number: formData.value.purchase_order_number || null,
}
```

## Testing Checklist

After implementation, test the following:

### Owner Details
- [ ] Checkbox "I am not the property owner" shows/hides owner fields
- [ ] Owner name is required when checkbox is checked
- [ ] Validation prevents proceeding without owner name
- [ ] Owner details are saved to backend

### Certificate of Title Upload
- [ ] File upload accepts PDF, JPG, PNG
- [ ] Upload success message displays
- [ ] Uploaded file is included in submission

### Transfer Deposit
- [ ] Checkbox shows/hides consent number field (RC only)
- [ ] Consent number is required when checkbox is checked
- [ ] Field value is saved to Resource Consent Application

### AEE Improvements
- [ ] Document upload option works
- [ ] Structured fields (7 questions) display correctly
- [ ] Can submit with document upload OR text fields OR both
- [ ] All fields save to backend

### Invoicing
- [ ] Dropdown shows correct options based on form state
- [ ] "Other" option shows additional name/email fields
- [ ] Name and email are required when "Other" is selected
- [ ] Invoice recipient is saved correctly

### Statutory Declarations
- [ ] All three checkboxes display correctly
- [ ] All three are required to proceed
- [ ] Declaration text is clear and accurate
- [ ] Third declaration changes text if owner checkbox is checked

### End-to-End
- [ ] Can complete entire form with all new fields
- [ ] Validation works at each step
- [ ] Submission succeeds
- [ ] All data appears in backend Request and RC Application records
- [ ] File uploads are attached correctly

## Build and Deploy

After completing implementation:

```bash
cd /workspace/development/frappe-bench/apps/lodgeick/frontend
yarn build

cd /workspace/development/frappe-bench
git add .
git commit -m "feat: Add HCC form parity fields to applicant form

Frontend implementation of comprehensive form fields:
- Owner/occupier details (conditional Section 88 compliance)
- Certificate of Title document upload
- Statutory declarations (3 explicit checkboxes)
- Invoicing details with flexible recipient selection
- Transfer deposit section for RC applications
- Structured AEE fields + document upload option

Matches backend schema changes from commit 900d360.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Notes

- File size: NewRequest.vue is currently 252KB (5000+ lines)
- Consider refactoring into separate components in future:
  - `NewRequestBase.vue` - Steps 1-4 (common)
  - `ResourceConsentForm.vue` - Step 5 (RC-specific)
  - `ReviewSubmit.vue` - Step 6 (review)
- This would improve maintainability and match backend architecture
- Current approach: Add all fields to existing file, refactor later

## Architecture Future Consideration

The user has indicated interest in component separation. After this implementation is tested and working, consider creating a separate task for:

1. Extract common steps (1-4) to `NewRequestBase.vue`
2. Extract RC-specific step (5) to `ResourceConsentForm.vue`
3. Extract review/submit (6) to `ReviewSubmit.vue`
4. Create composables for shared state/logic
5. Update routing to support component-based flow

This separation would:
- Match backend architecture (Request + RC Application)
- Improve code maintainability
- Enable easier addition of other request types (Building Consent, etc.)
- Reduce file size from 252KB to manageable chunks
