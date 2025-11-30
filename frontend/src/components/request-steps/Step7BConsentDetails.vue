<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Consent Details</h2>
    <p class="text-gray-600 mb-8">Additional details specific to your consent type(s)</p>

    <div class="space-y-6">
      <!-- Duration - Per Consent Type -->
      <div>
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Requested Duration</h3>
        <p class="text-sm text-gray-600 mb-4">
          Specify the duration for each consent type selected
        </p>
        <div class="space-y-4">
          <div
            v-for="ct in props.modelValue.consent_types"
            :key="ct.consent_type"
            class="border border-gray-200 rounded-lg p-4 bg-gray-50"
          >
            <label class="block text-sm font-medium text-gray-700 mb-2">
              {{ ct.consent_type }} Duration
            </label>
            <div class="flex gap-4 items-center">
              <div class="flex-1">
                <input
                  v-model.number="getDurationData(ct.consent_type).duration_years"
                  type="number"
                  :min="1"
                  :max="getMaxDuration(ct.consent_type)"
                  placeholder="e.g., 10"
                  :disabled="getDurationData(ct.consent_type).duration_unlimited"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <span class="text-gray-600">years</span>
              <label v-if="canBeUnlimited(ct.consent_type)" class="flex items-center gap-2">
                <input
                  v-model="getDurationData(ct.consent_type).duration_unlimited"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="text-sm">Unlimited</span>
              </label>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              {{ getDurationHelpText(ct.consent_type) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Lapsing Period -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Lapsing Period
        </label>
        <select
          v-model.number="localData.lapsing_period_years"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option :value="5">5 years (standard)</option>
          <option :value="10">10 years (renewable energy)</option>
          <option v-if="isCoastalPermit" :value="3">3 years (aquaculture)</option>
        </select>
        <p class="mt-1 text-xs text-gray-500">
          Time period before consent lapses if not given effect to (s.125 RMA)
        </p>
      </div>

      <!-- Consent Notice - Subdivision only -->
      <div v-if="isSubdivision" class="border-t border-gray-200 pt-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Consent Notice (s.221 RMA)</h3>
        <p class="text-sm text-gray-600 mb-4">
          For subdivision consents, indicate whether a consent notice should be placed on the record of title
        </p>
        <div class="space-y-3">
          <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
            :class="localData.consent_notice_required ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
          >
            <input
              v-model="localData.consent_notice_required"
              type="checkbox"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">Consent notice required</span>
              <p class="text-xs text-gray-600 mt-1">
                Check if ongoing conditions need to be recorded on the certificate of title
              </p>
            </div>
          </label>

          <div v-if="localData.consent_notice_required" class="pl-7">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Consent Notice Details *
            </label>
            <textarea
              v-model="localData.consent_notice_details"
              rows="4"
              placeholder="Describe the matters to be included in the consent notice..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :required="localData.consent_notice_required"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Coastal Occupation Charge - Coastal Permit only -->
      <div v-if="isCoastalPermit" class="border-t border-gray-200 pt-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Coastal Occupation Charge</h3>
        <p class="text-sm text-gray-600 mb-4">
          For occupation of the coastal marine area, councils may impose a coastal occupation charge
        </p>
        <div class="space-y-3">
          <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
            :class="localData.coastal_occupation_charge_acknowledged ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
          >
            <input
              v-model="localData.coastal_occupation_charge_acknowledged"
              type="checkbox"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">I acknowledge that a coastal occupation charge may apply</span>
              <p class="text-xs text-gray-600 mt-1">
                The council will determine the applicable charge based on the nature and extent of occupation
              </p>
            </div>
          </label>
        </div>
      </div>

      <!-- Financial Contribution - All types -->
      <div class="border-t border-gray-200 pt-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Financial Contribution (s.108(2)(a) RMA)</h3>
        <p class="text-sm text-gray-600 mb-4">
          Council may impose financial contributions as a condition of consent
        </p>
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h5 class="font-semibold text-blue-900 text-sm">Information Only</h5>
              <p class="text-blue-800 text-sm mt-1">
                Financial contributions are determined by council policy and will be advised during processing if applicable. No action required at this stage.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Fast-Track Processing - User Selectable -->
      <div v-if="fastTrackAvailable" class="border-t border-gray-200 pt-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Fast-Track Processing (s.87AAB RMA)</h3>
        <p class="text-sm text-gray-600 mb-4">
          Controlled activities may be eligible for fast-track processing with reduced timeframes
        </p>

        <div v-if="eligibleForFastTrack" class="space-y-3">
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h5 class="font-semibold text-green-900 text-sm">Eligible for Fast-Track</h5>
                <p class="text-green-800 text-sm mt-1">
                  Based on your consent type and activity status (Controlled), this application is eligible for fast-track processing.
                </p>
              </div>
            </div>
          </div>

          <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
            :class="localData.request_fast_track ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
          >
            <input
              v-model="localData.request_fast_track"
              type="checkbox"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">Request fast-track processing</span>
              <p class="text-xs text-gray-600 mt-1">
                I would like this application to be processed under fast-track provisions (subject to council availability)
              </p>
            </div>
          </label>
        </div>

        <div v-else class="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p class="text-sm text-gray-600">
            Fast-track processing is only available for Controlled activities (excluding Subdivision consents).
            Your current selections do not qualify for fast-track.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch, computed, reactive } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

// Consent type checks
const hasConsentType = (type) => {
  return props.modelValue.consent_types?.some(ct => ct.consent_type === type) || false
}

const isSubdivision = computed(() => hasConsentType('Subdivision'))
const isCoastalPermit = computed(() => hasConsentType('Coastal Permit'))
const isLandUse = computed(() => hasConsentType('Land Use'))
const isWaterPermit = computed(() => hasConsentType('Water Permit'))
const isDischargePermit = computed(() => hasConsentType('Discharge Permit'))

// Duration helpers - per consent type
const canBeUnlimited = (consentType) => {
  return consentType === 'Land Use' || consentType === 'Subdivision'
}

const getMaxDuration = (consentType) => {
  return canBeUnlimited(consentType) ? 999 : 35
}

const getDurationHelpText = (consentType) => {
  if (canBeUnlimited(consentType)) {
    return 'Land Use and Subdivision consents can be granted for unlimited duration (s.123 RMA)'
  }
  return 'Water Permits, Discharge Permits, and Coastal Permits have a maximum duration of 35 years (s.123 RMA)'
}

// Duration data management - store per consent type
const durationData = reactive({})

const getDurationData = (consentType) => {
  if (!durationData[consentType]) {
    // Check if data exists in modelValue
    const existing = props.modelValue.consent_type_durations?.find(d => d.consent_type === consentType)
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

// Watch duration data and sync to modelValue
watch(durationData, () => {
  const durations = Object.values(durationData)
  emit('update:modelValue', {
    ...props.modelValue,
    consent_type_durations: durations
  })
}, { deep: true })

// Fast-track eligibility and availability
const eligibleForFastTrack = computed(() => {
  const isControlled = props.modelValue.activity_status === 'Controlled'
  const notSubdivision = !isSubdivision.value
  return isControlled && notSubdivision
})

// Check if council has fast-track enabled (will be passed from parent)
const fastTrackAvailable = computed(() => {
  // This will check against council's request type configuration
  // For now, assume available if the feature exists
  return true
})

// Local data
const localData = ref({
  lapsing_period_years: props.modelValue.lapsing_period_years || 5,
  consent_notice_required: props.modelValue.consent_notice_required || false,
  consent_notice_details: props.modelValue.consent_notice_details || '',
  coastal_occupation_charge_acknowledged: props.modelValue.coastal_occupation_charge_acknowledged || false,
  request_fast_track: props.modelValue.request_fast_track || false
})

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  localData.value.lapsing_period_years = newVal.lapsing_period_years || 5
  localData.value.consent_notice_required = newVal.consent_notice_required || false
  localData.value.consent_notice_details = newVal.consent_notice_details || ''
  localData.value.coastal_occupation_charge_acknowledged = newVal.coastal_occupation_charge_acknowledged || false
  localData.value.request_fast_track = newVal.request_fast_track || false
}, { deep: true })

// Watch local changes and emit
watch(localData, (newVal) => {
  emit('update:modelValue', {
    ...props.modelValue,
    lapsing_period_years: newVal.lapsing_period_years,
    consent_notice_required: newVal.consent_notice_required,
    consent_notice_details: newVal.consent_notice_details,
    coastal_occupation_charge_acknowledged: newVal.coastal_occupation_charge_acknowledged,
    request_fast_track: newVal.request_fast_track
  })
}, { deep: true })
</script>
