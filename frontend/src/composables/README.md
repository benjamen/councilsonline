# CouncilsOnline Composables

Reusable Vue 3 composition functions for common form patterns in the CouncilsOnline application.

## Overview

These composables extract common logic from the monolithic `NewRequest.vue` component to improve:
- **Reusability** - Use the same logic across multiple components
- **Testability** - Test logic in isolation from UI
- **Maintainability** - Smaller, focused functions are easier to understand
- **Type Safety** - Full TypeScript support with proper types

## Available Composables

### 1. useFileUpload

Handles file uploads with validation (size, type) and error handling.

**Use cases:** Certificate of Title uploads, AEE documents, specialist reports, any file attachment

```typescript
import { useFileUpload, FILE_UPLOAD_PRESETS } from '@/composables'

// Example: Certificate of Title upload
const ctUpload = useFileUpload({
  ...FILE_UPLOAD_PRESETS.PDF_IMAGES_10MB,
  onFileSelect: (file) => {
    formData.value.certificate_of_title_document = file
  }
})

// In template:
<input
  type="file"
  @change="ctUpload.handleUpload"
  accept=".pdf,.jpg,.png"
/>
<p v-if="ctUpload.hasFile">✓ {{ ctUpload.fileName }} ({{ ctUpload.fileSize }})</p>
<p v-if="ctUpload.error" class="error">{{ ctUpload.error }}</p>
```

**Features:**
- File size validation
- MIME type validation
- Formatted file size display
- Custom error messages
- Preset configurations for common scenarios

**Presets:**
- `PDF_10MB` - PDF only, max 10MB
- `DOCUMENTS_20MB` - PDF and Word, max 20MB
- `PDF_IMAGES_10MB` - PDF and images, max 10MB
- `IMAGES_5MB` - Images only, max 5MB

### 2. useArrayField

Manages array-based form fields (add, remove, edit operations).

**Use cases:** Affected parties, HAIL activities, specialist reports, proposed conditions

```typescript
import { useArrayField } from '@/composables'

const affectedParties = useArrayField({
  initialValue: () => ({
    party_name: '',
    party_address: '',
    party_relationship: '',
    effects_description: '',
    mitigation_offered: false
  }),
  onAdd: (party) => {
    console.log('Added affected party:', party)
  },
  onRemove: (index, party) => {
    console.log('Removed party at index:', index)
  }
})

// In template:
<button @click="affectedParties.add()">Add Party</button>

<div v-for="(party, index) in affectedParties.items.value" :key="index">
  <h4>{{ party.party_name }}</h4>
  <button @click="affectedParties.remove(index)">Remove</button>
  <button @click="affectedParties.edit(index)">Edit</button>
</div>

<p v-if="affectedParties.isEmpty">No parties added yet</p>
<p>Total: {{ affectedParties.count }}</p>
```

**Features:**
- CRUD operations (add, remove, edit, save)
- Edit state management
- Validation support
- Item counting helpers
- Modal integration (via `useArrayFieldWithModal`)

**With Modal Support:**

```typescript
import { useArrayFieldWithModal } from '@/composables'

const hailActivities = useArrayFieldWithModal({
  initialValue: () => ({
    activity_description: '',
    hail_category: '',
    proposed_activities: []
  }),
  addModalTitle: 'Add HAIL Activity',
  editModalTitle: 'Edit HAIL Activity'
})

// In template:
<button @click="hailActivities.openAddModal()">Add Activity</button>

<Modal v-model="hailActivities.showModal" :title="hailActivities.modalTitle">
  <!-- Form fields here -->
  <button @click="hailActivities.closeModal()">Cancel</button>
  <button @click="hailActivities.save(editingItem)">Save</button>
</Modal>
```

### 3. useFormValidation

Provides form validation with error tracking and common validation rules.

**Use cases:** Step validation, field-level validation, conditional validation

```typescript
import { useFormValidation, ValidationRules } from '@/composables'

const { validate, errors, isValid, getError, setError } = useFormValidation()

// Define validation rules
const ownerDetailsRules = {
  owner_name: ValidationRules.when(
    () => formData.value.applicant_is_not_owner,
    ValidationRules.all(
      ValidationRules.required('Owner name is required'),
      ValidationRules.minLength(2, 'Name must be at least 2 characters')
    )
  ),
  owner_email: ValidationRules.when(
    () => formData.value.applicant_is_not_owner,
    ValidationRules.all(
      ValidationRules.required('Owner email is required'),
      ValidationRules.email()
    )
  ),
  owner_phone: ValidationRules.when(
    () => formData.value.applicant_is_not_owner,
    ValidationRules.all(
      ValidationRules.required('Owner phone is required'),
      ValidationRules.phone()
    )
  )
}

// Validate
const canProceed = async () => {
  const valid = await validate(formData.value, ownerDetailsRules)
  if (!valid) {
    console.log('Validation errors:', errors.value)
  }
  return valid
}

// In template:
<input v-model="formData.owner_name" :class="{ error: getError('owner_name') }" />
<p v-if="getError('owner_name')" class="error-message">{{ getError('owner_name') }}</p>
```

**Built-in Validation Rules:**
- `required(message?)` - Field must have a value
- `email(message?)` - Valid email format
- `phone(message?)` - Valid phone number (NZ format)
- `minLength(min, message?)` - Minimum character length
- `maxLength(max, message?)` - Maximum character length
- `pattern(regex, message?)` - Match regex pattern
- `url(message?)` - Valid URL format
- `numeric(message?)` - Must be a number
- `min(min, message?)` - Minimum numeric value
- `max(max, message?)` - Maximum numeric value
- `oneOf(values[], message?)` - Must be one of specified values
- `when(condition, rule)` - Conditional validation
- `all(...rules)` - Combine multiple rules

## Usage Examples

### Example 1: Owner Details Section with Validation

```typescript
// In component setup
import { useFormValidation, ValidationRules } from '@/composables'

const { validate, errors, getError } = useFormValidation()

const ownerRules = {
  owner_name: ValidationRules.when(
    () => formData.value.applicant_is_not_owner,
    ValidationRules.required('Owner name is required when applicant is not the owner')
  ),
  owner_email: ValidationRules.when(
    () => formData.value.applicant_is_not_owner,
    ValidationRules.all(
      ValidationRules.required(),
      ValidationRules.email()
    )
  )
}

const validateOwnerDetails = async () => {
  return await validate(formData.value, ownerRules)
}
```

### Example 2: File Upload with Custom Error Messages

```typescript
import { useFileUpload } from '@/composables'

const aeeUpload = useFileUpload({
  maxSize: 20 * 1024 * 1024, // 20MB
  allowedTypes: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  errorMessages: {
    fileSize: 'AEE documents must be less than 20MB',
    fileType: 'Only PDF and Word documents are allowed for AEE reports'
  },
  onFileSelect: (file) => {
    formData.value.aee_document = file
    // Optional: Upload immediately
    uploadAEEDocument(file)
  },
  onFileRemove: () => {
    formData.value.aee_document = null
  }
})
```

### Example 3: HAIL Activities with Modal

```typescript
import { useArrayFieldWithModal } from '@/composables'

const hailActivities = useArrayFieldWithModal({
  initialValue: () => ({
    activity_description: '',
    hail_category: '',
    currently_undertaken: false,
    previously_undertaken: false,
    likely_undertaken: false,
    preliminary_investigation_done: false,
    proposed_activities: [],
    notes: ''
  }),
  items: formData.value.hail_activities, // Link to form data
  addModalTitle: 'Add HAIL Activity',
  editModalTitle: 'Edit HAIL Activity',
  validate: (activity) => {
    if (!activity.activity_description) {
      return 'Activity description is required'
    }
    if (!activity.hail_category) {
      return 'HAIL category is required'
    }
    return null
  },
  onAdd: (activity) => {
    formData.value.hail_activities.push(activity)
  },
  onUpdate: (index, activity) => {
    formData.value.hail_activities[index] = activity
  },
  onRemove: (index) => {
    formData.value.hail_activities.splice(index, 1)
  }
})
```

## Migration Guide

### Before (inline logic in NewRequest.vue):

```typescript
// Scattered throughout 5,700+ line file
const handleCTUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 10 * 1024 * 1024) {
    alert('File size must be less than 10MB')
    event.target.value = ''
    return
  }

  const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
  if (!allowedTypes.includes(file.type)) {
    alert('Only PDF and image files are allowed')
    event.target.value = ''
    return
  }

  formData.value.certificate_of_title_document = file
  event.target.value = ''
}

const handleAEEUpload = (event) => {
  // Similar logic duplicated...
}
```

### After (using composables):

```typescript
import { useFileUpload, FILE_UPLOAD_PRESETS } from '@/composables'

// Certificate of Title
const ctUpload = useFileUpload({
  ...FILE_UPLOAD_PRESETS.PDF_IMAGES_10MB,
  onFileSelect: (file) => formData.value.certificate_of_title_document = file
})

// AEE Document
const aeeUpload = useFileUpload({
  ...FILE_UPLOAD_PRESETS.DOCUMENTS_20MB,
  onFileSelect: (file) => formData.value.aee_document = file
})

// In template - just use handleUpload!
<input type="file" @change="ctUpload.handleUpload" />
<input type="file" @change="aeeUpload.handleUpload" />
```

**Benefits:**
- ✅ Reduced code duplication
- ✅ Consistent error handling
- ✅ Reusable across components
- ✅ Easier to test
- ✅ Easier to maintain

## Testing

All composables are designed to be unit tested in isolation:

```typescript
import { describe, it, expect } from 'vitest'
import { useFileUpload } from '@/composables'

describe('useFileUpload', () => {
  it('should validate file size', () => {
    const { handleUpload, error } = useFileUpload({
      maxSize: 1024, // 1KB
      allowedTypes: ['application/pdf']
    })

    const mockFile = new File(['x'.repeat(2000)], 'test.pdf', { type: 'application/pdf' })
    const mockEvent = { target: { files: [mockFile], value: '' } }

    handleUpload(mockEvent)

    expect(error.value).toContain('File size')
  })
})
```

## Best Practices

1. **Always use presets when available** - They provide consistent validation
2. **Provide meaningful error messages** - Help users understand what went wrong
3. **Use conditional validation** - Only validate fields when relevant
4. **Combine validation rules** - Use `ValidationRules.all()` for complex validation
5. **Link to formData** - Keep composables synchronized with form state

## Future Enhancements

Planned composables for future development:
- `useStepNavigation` - Multi-step form navigation with history
- `useFormPersistence` - Auto-save drafts to localStorage
- `useAsyncValidation` - Server-side validation support
- `useDependentFields` - Manage field dependencies and cascading updates

---

**Version:** 1.0
**Last Updated:** 2025-11-28
**Author:** Claude Code
