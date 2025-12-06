# @lodgeick/ui

Shared UI library for Lodgeick multi-app architecture. This package provides reusable components, composables, and utilities that work across all domain apps (platform_core, lodgement_requests, resource_consents, social_services, etc.).

## Architecture

The UI library enables **70% code reuse** across domain-specific apps by providing:

- **Configuration-driven components** - Generic components that adapt to different DocTypes and apps
- **Unified API client** - Consistent way to call APIs across different apps
- **Store factories** - Generate Pinia stores from configuration instead of writing repetitive code
- **Shared composables** - Common form validation, file upload, and navigation logic

## Installation

The UI library is installed as a local workspace package:

```bash
cd frontend
npm install
```

The package.json includes: `"@lodgeick/ui": "file:../ui-library"`

## Components

### DynamicFieldRenderer

Renders form fields dynamically based on Frappe field configuration.

```vue
<template>
  <DynamicFieldRenderer
    :fields="stepFields"
    v-model="formData"
  />
</template>

<script setup>
import { DynamicFieldRenderer } from '@lodgeick/ui'
import { ref } from 'vue'

const formData = ref({})
const stepFields = ref([...]) // From get_request_type_steps API
</script>
```

### SelectableItemPicker

Generic selector component - replaces all hardcoded selectors (CouncilSelector, etc.).

**Grid Layout (Default)**:
```vue
<template>
  <SelectableItemPicker
    app-name="platform_core"
    doctype="Council"
    display-field="council_name"
    description-field="council_region"
    filter-field="is_active"
    :filter-value="1"
    layout="grid"
    grid-class="grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
    label="Councils"
    v-model="selectedCouncil"
    @select="handleCouncilSelect"
  />
</template>

<script setup>
import { SelectableItemPicker } from '@lodgeick/ui'
import { ref } from 'vue'

const selectedCouncil = ref(null)

const handleCouncilSelect = (council) => {
  console.log('Selected:', council.council_name)
}
</script>
```

**List Layout**:
```vue
<SelectableItemPicker
  app-name="social_services"
  doctype="Household Record"
  display-field="head_of_household_name"
  description-field="barangay"
  layout="list"
  label="Households"
  searchable
  v-model="selectedHousehold"
/>
```

**Dropdown Layout**:
```vue
<SelectableItemPicker
  app-name="platform_core"
  doctype="Council"
  display-field="council_name"
  layout="dropdown"
  label="Council"
  v-model="selectedCouncil"
/>
```

**Custom Item Rendering** (using slots):
```vue
<SelectableItemPicker
  app-name="platform_core"
  doctype="Council"
  display-field="council_name"
  v-model="selectedCouncil"
>
  <template #item="{ item }">
    <div class="flex items-center gap-3">
      <img :src="item.logo" class="w-12 h-12 rounded-full" />
      <div>
        <div class="font-bold" :style="{ color: item.primary_color }">
          {{ item.council_name }}
        </div>
        <div class="text-sm text-gray-500">{{ item.council_region }}</div>
      </div>
    </div>
  </template>
</SelectableItemPicker>
```

## API Client

### AppApiClient

Unified API client for calling different Frappe apps without hardcoding app names.

```javascript
import { AppApiClient } from '@lodgeick/ui'

// Resource Consents app
const rcApi = new AppApiClient('resource_consents')
const rcApplication = await rcApi.get('Resource Consent Application', 'RC-2025-001')

// Social Services app
const ssApi = new AppApiClient('social_services')
const households = await ssApi.getList('Household Record', { is_active: 1 }, [
  'name',
  'head_of_household_name',
  'barangay'
])

// Platform Core app
const coreApi = new AppApiClient('platform_core')
const councils = await coreApi.getList('Council', { is_active: 1 })

// Call custom API methods
const lodgementApi = new AppApiClient('lodgement_requests')
const steps = await lodgementApi.call('get_request_type_steps', {
  request_type: 'SPISC',
  council_code: 'PH-TAY'
})
```

**Available Methods**:

- `call(method, args)` - Call whitelisted API method
- `getList(doctype, filters, fields, options)` - Get list of documents
- `get(doctype, name)` - Get single document
- `save(doctype, data)` - Save document (create/update)
- `insert(doctype, data)` - Insert new document
- `delete(doctype, name)` - Delete document
- `getCount(doctype, filters)` - Get count of matching documents
- `db(query)` - Run database query

## Store Factories

### createEntityStore

Generate Pinia stores from configuration instead of writing repetitive code.

**Creating a Store**:

```javascript
// In resource_consents app - stores/council.js
import { createEntityStore } from '@lodgeick/ui'

export const useCouncilStore = createEntityStore('council', {
  appName: 'platform_core',
  doctype: 'Council',
  filters: { is_active: 1 },
  fields: ['name', 'council_name', 'primary_color', 'logo', 'council_region'],
  displayField: 'council_name',
  orderBy: 'council_name asc'
})
```

```javascript
// In social_services app - stores/household.js
import { createEntityStore } from '@lodgeick/ui'

export const useHouseholdStore = createEntityStore('household', {
  appName: 'social_services',
  doctype: 'Household Record',
  filters: { is_active: 1 },
  fields: ['name', 'head_of_household_name', 'barangay', 'member_count'],
  displayField: 'head_of_household_name'
})
```

**Using a Store**:

```vue
<script setup>
import { useCouncilStore } from '@/stores/council'
import { onMounted } from 'vue'

const councilStore = useCouncilStore()

onMounted(async () => {
  await councilStore.loadItems()
})

// Select a council
const selectCouncil = (council) => {
  councilStore.selectItem(council)
}

// Access selected council
console.log(councilStore.selectedDisplay) // "Auckland Council"
console.log(councilStore.selectedName) // "COUNCIL-001"

// Filter items
await councilStore.updateFilters({ council_region: 'North Island' })

// Reload
await councilStore.reload()

// Save an item
await councilStore.saveItem({
  name: 'COUNCIL-001',
  council_name: 'Updated Name'
})

// Delete an item
await councilStore.deleteItem('COUNCIL-001')

// Get count
const count = await councilStore.getCount()
</script>
```

**Available Store State**:
- `items` - Array of loaded items
- `selected` - Currently selected item
- `loading` - Loading state
- `error` - Error message
- `currentFilters` - Active filters

**Available Store Getters**:
- `selectedDisplay` - Display value of selected item
- `selectedName` - Name of selected item
- `hasItems` - Boolean if items exist
- `itemCount` - Count of items
- `findByName(name)` - Find item by name
- `findBy(field, value)` - Find item by field

**Available Store Actions**:
- `loadItems(additionalFilters)` - Load items from server
- `reload()` - Reload with current filters
- `selectItem(item)` - Select an item
- `selectByName(name)` - Select by name
- `clearSelection()` - Clear selection
- `updateFilters(newFilters)` - Update filters and reload
- `resetFilters()` - Reset to default filters
- `fetchItem(name)` - Get single item from server
- `saveItem(data)` - Save item
- `deleteItem(name)` - Delete item
- `getCount()` - Get count from server

## Composables

### useFileUpload

Handle file uploads with progress tracking and validation.

```vue
<script setup>
import { useFileUpload } from '@lodgeick/ui'

const { uploadFile, uploading, progress, error } = useFileUpload()

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  const url = await uploadFile(file, {
    maxSize: 10 * 1024 * 1024, // 10MB
    allowedTypes: ['image/jpeg', 'image/png', 'application/pdf']
  })

  console.log('Uploaded file URL:', url)
}
</script>
```

### useFormValidation

Form validation with error tracking.

```vue
<script setup>
import { useFormValidation } from '@lodgeick/ui'

const { validateField, errors, clearErrors } = useFormValidation()

const email = ref('')

const onEmailBlur = () => {
  validateField('email', email.value, {
    required: true,
    type: 'email'
  })
}
</script>

<template>
  <input
    v-model="email"
    @blur="onEmailBlur"
    :class="{ 'border-red-500': errors.email }"
  />
  <span class="text-red-500 text-sm">{{ errors.email }}</span>
</template>
```

### useArrayField

Manage array fields (child tables) with add/remove/reorder.

```vue
<script setup>
import { useArrayField } from '@lodgeick/ui'

const { items, addItem, removeItem, moveUp, moveDown } = useArrayField([])

const addMember = () => {
  addItem({
    member_name: '',
    relationship: '',
    age: null
  })
}
</script>
```

### useStepNavigation

Multi-step form navigation.

```vue
<script setup>
import { useStepNavigation } from '@lodgeick/ui'

const { currentStep, totalSteps, goToNextStep, goToPreviousStep, canGoNext, canGoBack } = useStepNavigation(10)

// Navigate
if (canGoNext.value) {
  goToNextStep()
}
</script>
```

## Migration Examples

### Before: Hardcoded Council Selector

```vue
<!-- OLD: CouncilSelector.vue - hardcoded to Council DocType -->
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div
      v-for="council in councils"
      :key="council.name"
      @click="select(council)"
      class="border rounded-lg p-4 cursor-pointer"
      :class="selected?.name === council.name ? 'border-blue-500 bg-blue-50' : ''"
    >
      {{ council.council_name }}
    </div>
  </div>
</template>

<script setup>
import { createResource } from 'frappe-ui'

const councils = createResource({
  url: 'lodgeick.api.get_active_councils', // HARDCODED APP NAME
  method: 'GET'
})
</script>
```

### After: Generic Selector

```vue
<!-- NEW: Using SelectableItemPicker -->
<template>
  <SelectableItemPicker
    app-name="platform_core"
    doctype="Council"
    display-field="council_name"
    filter-field="is_active"
    label="Councils"
    v-model="selectedCouncil"
  />
</template>

<script setup>
import { SelectableItemPicker } from '@lodgeick/ui'
import { ref } from 'vue'

const selectedCouncil = ref(null)
</script>
```

### Before: Domain-Specific Store

```javascript
// OLD: Repetitive store code for each entity
import { defineStore } from 'pinia'

export const useCouncilStore = defineStore('council', {
  state: () => ({
    councils: [],
    selected: null,
    loading: false
  }),
  actions: {
    async loadCouncils() {
      this.loading = true
      const response = await frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Council',
          filters: { is_active: 1 },
          fields: ['name', 'council_name']
        }
      })
      this.councils = response.message
      this.loading = false
    }
  }
})
```

### After: Configuration-Driven Store

```javascript
// NEW: Single line to create store
import { createEntityStore } from '@lodgeick/ui'

export const useCouncilStore = createEntityStore('council', {
  appName: 'platform_core',
  doctype: 'Council',
  filters: { is_active: 1 },
  fields: ['name', 'council_name'],
  displayField: 'council_name'
})
```

## Benefits

1. **70% Code Reuse**: Components, composables, and utilities are shared across all apps
2. **Faster Development**: New apps can be created quickly using existing components
3. **Consistency**: All apps have the same UI patterns and behaviors
4. **Maintainability**: Bug fixes and improvements benefit all apps
5. **Flexibility**: Configuration-driven approach adapts to different domains (RC, social services, etc.)
6. **Type Safety**: TypeScript support for better developer experience
7. **No Hardcoding**: App names, DocTypes, and field names are all configurable

## Future Enhancements

- Add more generic components (ConfigurableMultiStepForm, DynamicDetailView)
- Create region-specific validators (NZ, Philippines)
- Add app configuration system (AppConfig interface)
- Create storybook documentation for components
- Add unit tests for all components and utilities
