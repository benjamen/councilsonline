<template>
  <div class="selectable-item-picker">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center p-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">Loading {{ label }}...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-4 bg-red-50 border border-red-200 rounded-md">
      <p class="text-red-800">{{ error }}</p>
      <button @click="loadItems" class="mt-2 text-sm text-red-600 hover:text-red-800 underline">
        Try again
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="p-8 text-center text-gray-500">
      <p>No {{ label }} found</p>
    </div>

    <!-- Items Grid/List -->
    <div v-else>
      <!-- Search/Filter (optional) -->
      <div v-if="searchable" class="mb-4">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="`Search ${label}...`"
          class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <!-- Grid Layout (default) -->
      <div
        v-if="layout === 'grid'"
        class="grid gap-4"
        :class="gridClass"
      >
        <div
          v-for="item in filteredItems"
          :key="item.name"
          @click="selectItem(item)"
          class="cursor-pointer border rounded-lg p-4 transition-all hover:shadow-md"
          :class="[
            isSelected(item) ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' : 'border-gray-200 hover:border-blue-300',
            itemClass
          ]"
        >
          <slot name="item" :item="item">
            <!-- Default item rendering -->
            <div class="font-medium text-gray-900">
              {{ item[displayField] }}
            </div>
            <div v-if="descriptionField" class="text-sm text-gray-500 mt-1">
              {{ item[descriptionField] }}
            </div>
          </slot>
        </div>
      </div>

      <!-- List Layout -->
      <div
        v-else-if="layout === 'list'"
        class="space-y-2"
      >
        <div
          v-for="item in filteredItems"
          :key="item.name"
          @click="selectItem(item)"
          class="cursor-pointer border rounded-md p-3 transition-all hover:shadow-sm flex items-center justify-between"
          :class="[
            isSelected(item) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300',
            itemClass
          ]"
        >
          <slot name="item" :item="item">
            <!-- Default item rendering -->
            <div>
              <div class="font-medium text-gray-900">
                {{ item[displayField] }}
              </div>
              <div v-if="descriptionField" class="text-sm text-gray-500">
                {{ item[descriptionField] }}
              </div>
            </div>
          </slot>
          <div v-if="isSelected(item)" class="text-blue-600">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Dropdown Layout -->
      <div v-else-if="layout === 'dropdown'">
        <select
          :value="modelValue?.name || ''"
          @change="handleDropdownChange"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select {{ label }}</option>
          <option
            v-for="item in filteredItems"
            :key="item.name"
            :value="item.name"
          >
            {{ item[displayField] }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { AppApiClient } from '../api/AppApiClient.js'

const props = defineProps({
  /** Frappe app name (e.g., 'platform_core', 'social_services') */
  appName: {
    type: String,
    required: true
  },
  /** DocType name (e.g., 'Council', 'Household Record') */
  doctype: {
    type: String,
    required: true
  },
  /** Field to display as the item title */
  displayField: {
    type: String,
    default: 'name'
  },
  /** Field to display as the item description (optional) */
  descriptionField: {
    type: String,
    default: null
  },
  /** Field to use for filtering (e.g., 'is_active') */
  filterField: {
    type: String,
    default: null
  },
  /** Value to filter by (e.g., 1 for active items) */
  filterValue: {
    type: [String, Number, Boolean],
    default: 1
  },
  /** Additional filters object */
  filters: {
    type: Object,
    default: () => ({})
  },
  /** Fields to fetch from the server */
  fields: {
    type: Array,
    default: () => ['name']
  },
  /** Layout type: 'grid', 'list', or 'dropdown' */
  layout: {
    type: String,
    default: 'grid',
    validator: (value) => ['grid', 'list', 'dropdown'].includes(value)
  },
  /** Grid columns (CSS class for grid layout) */
  gridClass: {
    type: String,
    default: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
  },
  /** Custom CSS class for items */
  itemClass: {
    type: String,
    default: ''
  },
  /** Enable search/filter input */
  searchable: {
    type: Boolean,
    default: false
  },
  /** Label for the items (e.g., 'Councils', 'Households') */
  label: {
    type: String,
    default: 'items'
  },
  /** Currently selected item (v-model) */
  modelValue: {
    type: Object,
    default: null
  },
  /** Order by clause */
  orderBy: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'select', 'load'])

const items = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

/**
 * Compute the filters to send to the API
 */
const computedFilters = computed(() => {
  const baseFilters = { ...props.filters }

  if (props.filterField && props.filterValue !== undefined) {
    baseFilters[props.filterField] = props.filterValue
  }

  return baseFilters
})

/**
 * Compute the fields to fetch
 */
const computedFields = computed(() => {
  const fieldSet = new Set(['name', props.displayField])

  if (props.descriptionField) {
    fieldSet.add(props.descriptionField)
  }

  props.fields.forEach(f => fieldSet.add(f))

  return Array.from(fieldSet)
})

/**
 * Filter items based on search query
 */
const filteredItems = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return items.value
  }

  const query = searchQuery.value.toLowerCase()
  return items.value.filter(item => {
    const displayValue = (item[props.displayField] || '').toLowerCase()
    const descValue = props.descriptionField
      ? (item[props.descriptionField] || '').toLowerCase()
      : ''

    return displayValue.includes(query) || descValue.includes(query)
  })
})

/**
 * Check if an item is selected
 */
const isSelected = (item) => {
  return props.modelValue?.name === item.name
}

/**
 * Load items from the server
 */
const loadItems = async () => {
  loading.value = true
  error.value = null

  try {
    const api = new AppApiClient(props.appName)

    const options = {}
    if (props.orderBy) {
      options.order_by = props.orderBy
    }

    items.value = await api.getList(
      props.doctype,
      computedFilters.value,
      computedFields.value,
      options
    )

    emit('load', items.value)
  } catch (err) {
    error.value = err.message || `Failed to load ${props.label}`
    console.error(`Error loading ${props.doctype}:`, err)
  } finally {
    loading.value = false
  }
}

/**
 * Handle item selection
 */
const selectItem = (item) => {
  emit('update:modelValue', item)
  emit('select', item)
}

/**
 * Handle dropdown change
 */
const handleDropdownChange = (event) => {
  const name = event.target.value
  if (!name) {
    emit('update:modelValue', null)
    emit('select', null)
    return
  }

  const item = items.value.find(i => i.name === name)
  if (item) {
    selectItem(item)
  }
}

// Load items on mount
onMounted(() => {
  loadItems()
})

// Expose methods for parent components
defineExpose({
  loadItems,
  items
})
</script>

<style scoped>
.selectable-item-picker {
  @apply w-full;
}
</style>
