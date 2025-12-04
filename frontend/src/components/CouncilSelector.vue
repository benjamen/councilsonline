<template>
  <div class="council-selector">
    <!-- Label Section -->
    <div v-if="showLabel" class="mb-2">
      <label class="text-sm font-medium text-gray-700">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>
      <p v-if="description" class="text-xs text-gray-500 mt-1">
        {{ description }}
      </p>
    </div>

    <!-- Using the new SelectableItemPicker with custom slot for councils -->
    <SelectableItemPicker
      app-name="lodgeick"
      doctype="Council"
      display-field="council_name"
      filter-field="is_active"
      :filter-value="1"
      :fields="['name', 'council_code', 'council_name', 'logo', 'primary_color', 'website', 'contact_email']"
      :layout="displayMode === 'cards' ? 'grid' : 'dropdown'"
      grid-class="grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      label="Councils"
      :model-value="selectedCouncilObject"
      :searchable="displayMode === 'cards'"
      order-by="council_name asc"
      @update:model-value="handleCouncilSelect"
    >
      <!-- Custom card rendering for councils -->
      <template v-if="displayMode === 'cards'" #item="{ item }">
        <div class="flex items-start space-x-3">
          <!-- Logo or initials -->
          <div
            v-if="item.logo"
            class="w-12 h-12 flex-shrink-0 rounded overflow-hidden"
          >
            <img
              :src="item.logo"
              :alt="item.council_name"
              class="w-full h-full object-contain"
            />
          </div>
          <div
            v-else
            class="w-12 h-12 flex-shrink-0 rounded flex items-center justify-center text-white font-bold text-lg"
            :style="{ backgroundColor: item.primary_color || '#3B82F6' }"
          >
            {{ item.council_code }}
          </div>

          <!-- Council info -->
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold truncate text-gray-900">
              {{ item.council_name }}
            </h3>
            <p v-if="item.website" class="text-xs text-gray-500 truncate mt-1">
              {{ formatWebsite(item.website) }}
            </p>
          </div>
        </div>
      </template>
    </SelectableItemPicker>

    <!-- Clear button -->
    <div v-if="showClearButton && selectedCouncilCode" class="mt-2">
      <button
        @click="clearSelection"
        type="button"
        class="text-sm text-gray-600 hover:text-gray-800 underline"
      >
        Clear selection
      </button>
    </div>

    <!-- Selected info panel -->
    <div
      v-if="selectedCouncilCode && showSelectedInfo && selectedCouncilObject"
      class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200"
    >
      <div class="flex items-start space-x-3">
        <div
          class="w-10 h-10 flex-shrink-0 rounded flex items-center justify-center text-white font-bold"
          :style="{ backgroundColor: selectedCouncilObject.primary_color || '#3B82F6' }"
        >
          {{ selectedCouncilObject.council_code }}
        </div>
        <div class="flex-1">
          <h4 class="font-medium text-gray-900">
            {{ selectedCouncilObject.council_name }}
          </h4>
          <p v-if="selectedCouncilObject.contact_email" class="text-xs text-gray-600 mt-1">
            {{ selectedCouncilObject.contact_email }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * CouncilSelector_NEW.vue
 *
 * REFACTORED VERSION using @lodgeick/ui library
 *
 * This demonstrates the new pattern:
 * - Uses SelectableItemPicker (generic component) instead of hardcoded logic
 * - Works with any app (via app-name prop) - ready for platform_core
 * - No hardcoded API calls - uses AppApiClient under the hood
 * - Custom rendering via slots
 * - Much less code (90 lines vs 238 lines)
 *
 * Benefits:
 * - 60% less code
 * - Reusable pattern for other entities (Household, Request Type, etc.)
 * - Easy to adapt when Council moves to platform_core app
 * - Consistent with other selectors across the platform
 */

import { ref, computed, watch } from 'vue'
import { SelectableItemPicker } from '@lodgeick/ui'

const props = defineProps({
  modelValue: {
    type: String,
    default: null
  },
  label: {
    type: String,
    default: 'Select Council'
  },
  description: {
    type: String,
    default: ''
  },
  displayMode: {
    type: String,
    default: 'dropdown', // 'dropdown' or 'cards'
    validator: (value) => ['dropdown', 'cards'].includes(value)
  },
  required: {
    type: Boolean,
    default: false
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  showClearButton: {
    type: Boolean,
    default: false
  },
  showSelectedInfo: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedCouncilCode = ref(props.modelValue)
const selectedCouncilObject = ref(null)

const formatWebsite = (url) => {
  return url?.replace(/^https?:\/\/(www\.)?/, '') || ''
}

const handleCouncilSelect = (council) => {
  selectedCouncilObject.value = council
  selectedCouncilCode.value = council?.council_code || null
  emit('update:modelValue', selectedCouncilCode.value)
  emit('change', selectedCouncilCode.value)
}

const clearSelection = () => {
  selectedCouncilObject.value = null
  selectedCouncilCode.value = null
  emit('update:modelValue', null)
  emit('change', null)
}

watch(() => props.modelValue, (newValue) => {
  selectedCouncilCode.value = newValue
})
</script>

<style scoped>
.council-selector {
  @apply w-full;
}
</style>
