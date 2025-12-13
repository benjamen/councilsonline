<template>
  <div class="space-y-4">
    <!-- Property Selector Header -->
    <div class="flex items-center justify-between mb-4">
      <label class="block text-sm font-medium text-gray-700">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>
      <button
        v-if="userProperties.length > 0"
        @click="showPropertySelector = !showPropertySelector"
        type="button"
        class="text-sm text-blue-600 hover:text-blue-700 font-medium"
      >
        {{ showPropertySelector ? 'Enter manually' : 'Select from my properties' }}
      </button>
    </div>

    <!-- Property Selector Dropdown (if user has properties) -->
    <div v-if="showPropertySelector && userProperties.length > 0" class="space-y-3">
      <select
        v-model="selectedPropertyId"
        @change="onPropertySelected"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">Select a property</option>
        <option
          v-for="property in userProperties"
          :key="property.name"
          :value="property.name"
        >
          {{ formatPropertyOption(property) }}
        </option>
        <option value="__new__">+ Add New Property</option>
      </select>

      <!-- Selected Property Display -->
      <div v-if="selectedProperty && selectedPropertyId !== '__new__'" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start justify-between">
          <div class="flex-1 space-y-1">
            <p class="text-sm font-medium text-gray-900">{{ selectedProperty.property_name || 'Property' }}</p>
            <p class="text-sm text-gray-700">{{ formatPropertyAddress(selectedProperty) }}</p>
            <p v-if="selectedProperty.legal_description" class="text-xs text-gray-600">{{ selectedProperty.legal_description }}</p>
          </div>
          <div class="flex space-x-2">
            <button
              @click="editProperty"
              type="button"
              class="text-sm text-blue-600 hover:text-blue-700"
              title="Edit property"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              @click="deleteProperty"
              type="button"
              class="text-sm text-red-600 hover:text-red-700"
              title="Remove property"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Manual Address Input or New Property Form -->
    <div v-if="!showPropertySelector || selectedPropertyId === '__new__' || userProperties.length === 0">
      <PhilippinesAddressInput
        :modelValue="localAddress"
        @update:modelValue="onAddressChange"
        :required="required"
      />
    </div>

    <!-- Add to My Properties Checkbox (when entering manually) -->
    <div v-if="(!showPropertySelector || selectedPropertyId === '__new__') && !selectedPropertyId" class="flex items-center space-x-2">
      <input
        v-model="saveToProfile"
        type="checkbox"
        id="save-property"
        class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
      />
      <label for="save-property" class="text-sm text-gray-700">
        Save this property to my profile for future use
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import PhilippinesAddressInput from './PhilippinesAddressInput.vue'
import { useUserProfile } from '../composables/useUserProfile'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  label: {
    type: String,
    default: 'Residential Address'
  },
  required: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const { userProfile, loadUserProfile, getAllProperties, defaultProperty } = useUserProfile()

// State
const showPropertySelector = ref(false)
const selectedPropertyId = ref('')
const saveToProfile = ref(false)
const localAddress = ref(props.modelValue || {})

// Computed
const userProperties = computed(() => getAllProperties.value || [])

const selectedProperty = computed(() => {
  if (!selectedPropertyId.value || selectedPropertyId.value === '__new__') return null
  return userProperties.value.find(p => p.name === selectedPropertyId.value)
})

// Methods
function formatPropertyOption(property) {
  const parts = []
  if (property.property_name) parts.push(property.property_name)
  if (property.street) parts.push(property.street)
  if (property.suburb) parts.push(property.suburb)
  if (property.city) parts.push(property.city)
  return parts.join(', ') || 'Unnamed Property'
}

function formatPropertyAddress(property) {
  const parts = []
  if (property.street) parts.push(property.street)
  if (property.barangay) parts.push(`Brgy. ${property.barangay}`)
  if (property.municipality) parts.push(property.municipality)
  if (property.province) parts.push(property.province)
  if (property.zip_code || property.postcode) parts.push(property.zip_code || property.postcode)
  return parts.join(', ')
}

function onPropertySelected() {
  if (selectedPropertyId.value === '__new__') {
    // Reset to manual entry mode
    localAddress.value = {}
    showPropertySelector.value = false
    return
  }

  if (selectedProperty.value) {
    // Map property to address format
    localAddress.value = {
      full_address: formatPropertyAddress(selectedProperty.value),
      address_line: selectedProperty.value.street || '',
      barangay: selectedProperty.value.barangay || '',
      municipality: selectedProperty.value.municipality || selectedProperty.value.city || '',
      province: selectedProperty.value.province || '',
      zip_code: selectedProperty.value.zip_code || selectedProperty.value.postcode || ''
    }

    emit('update:modelValue', localAddress.value)
  }
}

function onAddressChange(newAddress) {
  localAddress.value = newAddress
  emit('update:modelValue', newAddress)
}

function editProperty() {
  // Switch to manual mode with current property data
  showPropertySelector.value = false
  // Keep the current localAddress values for editing
}

function deleteProperty() {
  if (confirm('Are you sure you want to remove this property from selection?')) {
    selectedPropertyId.value = ''
    localAddress.value = {}
    emit('update:modelValue', {})
  }
}

// Initialize
onMounted(async () => {
  await loadUserProfile()

  // Auto-select default property if no value provided
  if (!props.modelValue || Object.keys(props.modelValue).length === 0) {
    if (defaultProperty.value) {
      selectedPropertyId.value = defaultProperty.value.name
      onPropertySelected()
    }
  }

  // Show property selector by default if user has properties
  if (userProperties.value.length > 0) {
    showPropertySelector.value = true
  }
})

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  if (newVal && Object.keys(newVal).length > 0) {
    localAddress.value = newVal
  }
}, { deep: true })
</script>
