<template>
  <div class="space-y-6">
    <div v-for="field in visibleFields" :key="field.field_name" class="field-wrapper">
      <!-- Data / Text Input -->
      <div v-if="field.field_type === 'Data'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-1">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500">*</span>
        </label>
        <input
          :id="field.field_name"
          type="text"
          v-model="localData[field.field_name]"
          :required="field.is_required"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          :placeholder="field.field_label"
        />
      </div>

      <!-- Select Dropdown -->
      <div v-else-if="field.field_type === 'Select'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-1">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500">*</span>
        </label>
        <select
          :id="field.field_name"
          v-model="localData[field.field_name]"
          :required="field.is_required"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
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
      </div>

      <!-- Checkbox -->
      <div v-else-if="field.field_type === 'Check'" class="form-group">
        <div class="flex items-start">
          <div class="flex items-center h-5">
            <input
              :id="field.field_name"
              type="checkbox"
              v-model="localData[field.field_name]"
              :required="field.is_required"
              class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
            />
          </div>
          <div class="ml-3 text-sm">
            <label :for="field.field_name" class="font-medium text-gray-700">
              {{ field.field_label }}
              <span v-if="field.is_required" class="text-red-500">*</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Text / Textarea -->
      <div v-else-if="field.field_type === 'Text'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-1">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500">*</span>
        </label>
        <textarea
          :id="field.field_name"
          v-model="localData[field.field_name]"
          :required="field.is_required"
          rows="4"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          :placeholder="field.field_label"
        ></textarea>
      </div>

      <!-- Date -->
      <div v-else-if="field.field_type === 'Date'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-1">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500">*</span>
        </label>
        <input
          :id="field.field_name"
          type="date"
          v-model="localData[field.field_name]"
          :required="field.is_required"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <!-- Integer -->
      <div v-else-if="field.field_type === 'Int'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-1">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500">*</span>
        </label>
        <input
          :id="field.field_name"
          type="number"
          v-model.number="localData[field.field_name]"
          :required="field.is_required"
          step="1"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <!-- Float -->
      <div v-else-if="field.field_type === 'Float'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-1">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500">*</span>
        </label>
        <input
          :id="field.field_name"
          type="number"
          v-model.number="localData[field.field_name]"
          :required="field.is_required"
          step="0.01"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <!-- Currency -->
      <div v-else-if="field.field_type === 'Currency'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-1">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500">*</span>
        </label>
        <div class="mt-1 relative rounded-md shadow-sm">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span class="text-gray-500 sm:text-sm">₱</span>
          </div>
          <input
            :id="field.field_name"
            type="number"
            v-model.number="localData[field.field_name]"
            :required="field.is_required"
            step="0.01"
            class="block w-full pl-7 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>
      </div>

      <!-- Attach / File Upload -->
      <div v-else-if="field.field_type === 'Attach' || field.field_type === 'Attach Image'" class="form-group">
        <label :for="field.field_name" class="block text-sm font-medium text-gray-700 mb-1">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500">*</span>
        </label>
        <div class="mt-1">
          <input
            :id="field.field_name"
            type="file"
            :accept="field.field_type === 'Attach Image' ? 'image/*' : '*'"
            :required="field.is_required && !localData[field.field_name]"
            @change="handleFileUpload($event, field.field_name)"
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <div v-if="localData[field.field_name]" class="mt-2 text-sm text-gray-600">
            Current file: {{ localData[field.field_name] }}
          </div>
        </div>
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
    if (!field.depends_on) return true

    // TODO: Implement proper conditional logic evaluation
    // For now, show all fields
    return true
  })
})

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
</style>
