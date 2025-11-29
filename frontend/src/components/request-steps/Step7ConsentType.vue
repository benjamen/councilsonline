<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Consent Type & Activity Status</h2>
    <p class="text-gray-600 mb-8">Select the types of consent you're applying for and the activity status</p>

    <div class="space-y-6">
      <!-- Card-Based Consent Type Selector -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-4">
          Consent Types Required * <span class="text-xs text-gray-500">(Select all that apply)</span>
        </label>
        <div class="grid md:grid-cols-2 gap-4">
          <div
            v-for="consentType in availableConsentTypes"
            :key="consentType.value"
            @click="toggleConsentType(consentType.value)"
            class="border-2 rounded-lg p-4 cursor-pointer transition-all hover:shadow-md"
            :class="isConsentTypeSelected(consentType.value) ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
          >
            <div class="flex items-start">
              <input
                type="checkbox"
                :checked="isConsentTypeSelected(consentType.value)"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded pointer-events-none"
                readonly
              />
              <div class="ml-3 flex-1">
                <h3 class="text-base font-semibold text-gray-900">{{ consentType.label }}</h3>
                <p class="text-sm text-gray-600 mt-1">{{ consentType.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Status -->
      <div class="border-t border-gray-200 pt-6">
        <label class="block text-sm font-medium text-gray-700 mb-3">
          Activity Status Under District/Regional Plan *
        </label>
        <div class="space-y-2">
          <label
            v-for="status in activityStatuses"
            :key="status.value"
            class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-all hover:bg-gray-50"
            :class="localData.activity_status === status.value ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
          >
            <input
              type="radio"
              v-model="localData.activity_status"
              :value="status.value"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">{{ status.label }}</span>
              <p class="text-xs text-gray-600 mt-1">{{ status.description }}</p>
            </div>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

// Available consent types
const availableConsentTypes = [
  {
    value: 'Land Use',
    label: 'Land Use',
    description: 'For buildings, structures, and use of land'
  },
  {
    value: 'Subdivision',
    label: 'Subdivision',
    description: 'For dividing land into separate lots or titles'
  },
  {
    value: 'Discharge Permit',
    label: 'Discharge Permit',
    description: 'For discharges to land, water, or air'
  },
  {
    value: 'Water Permit',
    label: 'Water Permit',
    description: 'For taking, using, damming, or diverting water'
  },
  {
    value: 'Coastal Permit',
    label: 'Coastal Permit',
    description: 'For activities in the coastal marine area'
  }
]

// Activity statuses
const activityStatuses = [
  {
    value: 'Permitted',
    label: 'Permitted Activity',
    description: 'Complies with all permitted activity standards'
  },
  {
    value: 'Controlled',
    label: 'Controlled Activity',
    description: 'Council must grant consent, can impose conditions'
  },
  {
    value: 'Restricted Discretionary',
    label: 'Restricted Discretionary Activity',
    description: "Council's discretion limited to specified matters"
  },
  {
    value: 'Discretionary',
    label: 'Discretionary Activity',
    description: 'Council has full discretion to grant or decline'
  },
  {
    value: 'Non-Complying',
    label: 'Non-Complying Activity',
    description: 'Does not comply with plan, requires special consideration'
  }
]

// Local data
const localData = ref({
  consent_types: props.modelValue.consent_types || [],
  activity_status: props.modelValue.activity_status || ''
})

// Watch for external changes
watch(() => [props.modelValue.consent_types, props.modelValue.activity_status], ([newConsentTypes, newActivityStatus]) => {
  localData.value.consent_types = newConsentTypes || []
  localData.value.activity_status = newActivityStatus || ''
}, { deep: true })

// Watch local changes and emit
watch(localData, (newVal) => {
  emit('update:modelValue', {
    ...props.modelValue,
    consent_types: newVal.consent_types,
    activity_status: newVal.activity_status
  })
}, { deep: true })

// Toggle consent type selection
const toggleConsentType = (consentType) => {
  const index = localData.value.consent_types.findIndex(ct => ct.consent_type === consentType)
  if (index > -1) {
    localData.value.consent_types.splice(index, 1)
  } else {
    localData.value.consent_types.push({ consent_type: consentType })
  }
}

// Check if consent type is selected
const isConsentTypeSelected = (consentType) => {
  return localData.value.consent_types.some(ct => ct.consent_type === consentType)
}
</script>
