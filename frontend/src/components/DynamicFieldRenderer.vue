<template>
  <div class="space-y-6">
    <div v-for="field in visibleFields" :key="field.field_name" class="field-wrapper">
      <!-- Philippines Address Input (special handling for address fields) -->
      <div v-if="isAddressField(field)" class="form-group">
        <PhilippinesAddressInput
          v-model="localData[field.field_name]"
          :required="field.is_required"
        />
      </div>

      <!-- Data / Text Input -->
      <div v-else-if="field.field_type === 'Data'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-2 flex items-center">
          <span>{{ field.field_label }}</span>
          <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
          <Tooltip v-if="field.help_text || field.description" :text="field.help_text || field.description" />
        </label>
        <div class="relative">
          <input
            :id="field.field_name"
            type="text"
            v-model="localData[field.field_name]"
            :required="field.is_required"
            class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            :class="{'border-blue-500 ring-2 ring-blue-100': localData[field.field_name]}"
            :placeholder="getPlaceholder(field)"
          />
          <div v-if="getFieldIcon(field)" class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <span v-html="getFieldIcon(field)" class="text-gray-400"></span>
          </div>
        </div>
        <p v-if="field.description" class="mt-1 text-xs text-gray-500">{{ field.description }}</p>
      </div>

      <!-- Select Dropdown -->
      <div v-else-if="field.field_type === 'Select'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-2 flex items-center">
          <span>{{ field.field_label }}</span>
          <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
          <Tooltip v-if="field.help_text || field.description" :text="field.help_text || field.description" />
        </label>
        <div class="relative">
          <select
            :id="field.field_name"
            v-model="localData[field.field_name]"
            :required="field.is_required"
            class="block w-full pl-4 pr-10 py-3 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 rounded-lg transition-all appearance-none bg-white"
            :class="{'border-blue-500 ring-2 ring-blue-100': localData[field.field_name]}"
          >
            <option value="">Select {{ field.field_label }}</option>
            <option
              v-for="option in getSelectOptions(field.options)"
              :key="option"
              :value="option"
            >
              {{ option }}
            </option>
          </select>
          <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
        <p v-if="field.description" class="mt-1 text-xs text-gray-500">{{ field.description }}</p>
      </div>

      <!-- Checkbox -->
      <div v-else-if="field.field_type === 'Check'" class="form-group">
        <div class="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
          <div class="flex items-center h-5">
            <input
              :id="field.field_name"
              type="checkbox"
              v-model="localData[field.field_name]"
              :required="field.is_required"
              class="focus:ring-blue-500 h-5 w-5 text-blue-600 border-gray-300 rounded cursor-pointer"
            />
          </div>
          <div class="ml-3 text-sm">
            <label :for="field.field_name" class="font-medium text-gray-700 cursor-pointer">
              {{ field.field_label }}
              <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
            </label>
            <p v-if="field.description" class="mt-1 text-xs text-gray-500">{{ field.description }}</p>
          </div>
        </div>
      </div>

      <!-- Text / Textarea -->
      <div v-else-if="field.field_type === 'Text'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-2">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
        </label>
        <textarea
          :id="field.field_name"
          v-model="localData[field.field_name]"
          :required="field.is_required"
          rows="4"
          class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-y"
          :class="{'border-blue-500 ring-2 ring-blue-100': localData[field.field_name]}"
          :placeholder="getPlaceholder(field)"
        ></textarea>
        <p v-if="field.description" class="mt-1 text-xs text-gray-500">{{ field.description }}</p>
      </div>

      <!-- Date -->
      <div v-else-if="field.field_type === 'Date'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-2 flex items-center">
          <span>{{ field.field_label }}</span>
          <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
          <Tooltip v-if="field.help_text || field.description" :text="field.help_text || field.description" />
        </label>
        <div class="relative">
          <input
            :id="field.field_name"
            type="date"
            v-model="localData[field.field_name]"
            :required="field.is_required"
            class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            :class="{'border-blue-500 ring-2 ring-blue-100': localData[field.field_name]}"
          />
          <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </div>
        </div>
        <p v-if="field.description" class="mt-1 text-xs text-gray-500">{{ field.description }}</p>
      </div>

      <!-- Integer -->
      <div v-else-if="field.field_type === 'Int'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-2 flex items-center">
          <span>{{ field.field_label }}</span>
          <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
          <Tooltip v-if="field.help_text || field.description" :text="field.help_text || field.description" />
        </label>
        <div class="relative">
          <input
            :id="field.field_name"
            type="number"
            v-model.number="localData[field.field_name]"
            :required="field.is_required"
            step="1"
            class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            :class="{'border-blue-500 ring-2 ring-blue-100': localData[field.field_name]}"
            :placeholder="getPlaceholder(field)"
          />
          <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/>
            </svg>
          </div>
        </div>
        <p v-if="field.description" class="mt-1 text-xs text-gray-500">{{ field.description }}</p>
      </div>

      <!-- Float -->
      <div v-else-if="field.field_type === 'Float'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-2">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
        </label>
        <div class="relative">
          <input
            :id="field.field_name"
            type="number"
            v-model.number="localData[field.field_name]"
            :required="field.is_required"
            step="0.01"
            class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            :class="{'border-blue-500 ring-2 ring-blue-100': localData[field.field_name]}"
            :placeholder="getPlaceholder(field)"
          />
          <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/>
            </svg>
          </div>
        </div>
        <p v-if="field.description" class="mt-1 text-xs text-gray-500">{{ field.description }}</p>
      </div>

      <!-- Currency -->
      <div v-else-if="field.field_type === 'Currency'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-2">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <span class="text-gray-500 text-base font-medium">₱</span>
          </div>
          <input
            :id="field.field_name"
            type="number"
            v-model.number="localData[field.field_name]"
            :required="field.is_required"
            step="0.01"
            class="block w-full pl-10 pr-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            :class="{'border-blue-500 ring-2 ring-blue-100': localData[field.field_name]}"
            placeholder="0.00"
          />
        </div>
        <p v-if="field.description" class="mt-1 text-xs text-gray-500">{{ field.description }}</p>
      </div>

      <!-- Attach / File Upload with Camera Support -->
      <div v-else-if="field.field_type === 'Attach' || field.field_type === 'Attach Image'" class="form-group">
        <CameraUpload
          :label="field.field_label"
          :required="field.is_required"
          :accept="field.field_type === 'Attach Image' ? 'image/*' : '*'"
          :multiple="false"
          v-model="localData[field.field_name]"
        />
      </div>

      <!-- Unsupported field type -->
      <div v-else class="form-group">
        <div class="text-sm text-gray-500 italic">
          Field type "{{ field.field_type }}" not yet supported for {{ field.field_label }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import CameraUpload from './CameraUpload.vue'
import PhilippinesAddressInput from './PhilippinesAddressInput.vue'
import Tooltip from './Tooltip.vue'
import { isFieldVisible } from '../utils/conditionalLogic'

const props = defineProps({
  fields: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Filter visible fields based on depends_on logic
const visibleFields = computed(() => {
  return props.fields.filter(field => {
    return isFieldVisible(field, localData.value)
  })
})

// Check if field is an address field
const isAddressField = (field) => {
  // Only trigger for the actual address collection section, not individual address parts
  // Check if this is part of an address section AND is the primary address field
  const parentSection = field.parent_section_code?.toLowerCase() || ''
  const addressSections = ['address', 'residential_address', 'permanent_address', 'property_address', 'current_address', 'home_address']

  // Only show Philippines/Address component for the main address field in an address section
  // This prevents duplication where both the section and individual fields trigger the component
  return addressSections.includes(parentSection) &&
         field.field_name === 'address_line' &&
         field.field_type === 'Data'
}

// Get placeholder text for field
const getPlaceholder = (field) => {
  if (field.placeholder) return field.placeholder

  // Generate smart placeholders based on field name/label
  const label = field.field_label?.toLowerCase() || ''

  if (label.includes('name')) return 'e.g., Juan Dela Cruz'
  if (label.includes('email')) return 'e.g., juan@example.com'
  if (label.includes('phone') || label.includes('mobile') || label.includes('contact')) {
    return 'e.g., 0917 123 4567'
  }
  if (label.includes('age')) return 'e.g., 25'
  if (label.includes('occupation')) return 'e.g., Teacher'
  if (label.includes('income') || label.includes('salary')) return 'e.g., 15000'

  return `Enter ${field.field_label}`
}

// Get icon for field based on type
const getFieldIcon = (field) => {
  const label = field.field_label?.toLowerCase() || ''

  if (label.includes('email')) {
    return '<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/></svg>'
  }
  if (label.includes('phone') || label.includes('mobile') || label.includes('contact')) {
    return '<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>'
  }
  if (label.includes('name')) {
    return '<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>'
  }

  return null
}

// Parse select options from newline-separated string
const getSelectOptions = (optionsString) => {
  if (!optionsString) return []
  return optionsString.split('\n').map(opt => opt.trim()).filter(Boolean)
}

// Handle file upload
const handleFileUpload = (event, fieldName) => {
  const file = event.target.files[0]
  if (file) {
    // TODO: Implement actual file upload to Frappe
    // For now, just store the filename
    localData.value[fieldName] = file.name
  }
}

// Set default values on mount
watch(() => props.fields, (fields) => {
  fields.forEach(field => {
    if (field.default_value && !localData.value[field.field_name]) {
      if (field.default_value === 'Today' && field.field_type === 'Date') {
        localData.value[field.field_name] = new Date().toISOString().split('T')[0]
      } else {
        localData.value[field.field_name] = field.default_value
      }
    }
  })
}, { immediate: true })
</script>

<style scoped>
.form-group {
  margin-bottom: 1.5rem;
}

input:focus, select:focus, textarea:focus {
  outline: none;
}

/* Remove default number input spinners for cleaner look */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

/* Ensure date input has proper cursor */
input[type="date"] {
  cursor: pointer;
}

/* Smooth transitions */
input, select, textarea {
  transition: all 0.2s ease-in-out;
}
</style>
