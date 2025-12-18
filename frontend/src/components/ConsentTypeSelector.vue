<template>
  <div class="space-y-4">
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-blue-900">Type of Consent Required</h3>
          <p class="text-xs text-blue-700 mt-0.5">Select all consent types that apply to your application</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <!-- Land Use Consent -->
      <div
        @click="toggleConsent('Land Use Consent')"
        class="cursor-pointer rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="isSelected('Land Use Consent')
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
          : 'border-gray-300 bg-white hover:border-blue-300'"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div class="h-5 w-5 rounded flex items-center justify-center"
              :class="isSelected('Land Use Consent') ? 'bg-blue-500' : 'bg-gray-300'">
              <svg v-if="isSelected('Land Use Consent')" class="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M3.707 5.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 00-1.414-1.414L5 6.586 3.707 5.293z"/>
              </svg>
            </div>
          </div>
          <div class="ml-3 flex-1">
            <h4 class="text-sm font-semibold" :class="isSelected('Land Use Consent') ? 'text-blue-900' : 'text-gray-900'">
              Land Use Consent
            </h4>
            <p class="text-xs text-gray-600 mt-1">
              Building, alterations, or activities that don't comply with district plan rules
            </p>
          </div>
        </div>
      </div>

      <!-- Subdivision Consent -->
      <div
        @click="toggleConsent('Subdivision Consent')"
        class="cursor-pointer rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="isSelected('Subdivision Consent')
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
          : 'border-gray-300 bg-white hover:border-blue-300'"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div class="h-5 w-5 rounded flex items-center justify-center"
              :class="isSelected('Subdivision Consent') ? 'bg-blue-500' : 'bg-gray-300'">
              <svg v-if="isSelected('Subdivision Consent')" class="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M3.707 5.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 00-1.414-1.414L5 6.586 3.707 5.293z"/>
              </svg>
            </div>
          </div>
          <div class="ml-3 flex-1">
            <h4 class="text-sm font-semibold" :class="isSelected('Subdivision Consent') ? 'text-blue-900' : 'text-gray-900'">
              Subdivision Consent
            </h4>
            <p class="text-xs text-gray-600 mt-1">
              Dividing land into separate titles or creating new lots
            </p>
          </div>
        </div>
      </div>

      <!-- Discharge Permit -->
      <div
        @click="toggleConsent('Discharge Permit')"
        class="cursor-pointer rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="isSelected('Discharge Permit')
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
          : 'border-gray-300 bg-white hover:border-blue-300'"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div class="h-5 w-5 rounded flex items-center justify-center"
              :class="isSelected('Discharge Permit') ? 'bg-blue-500' : 'bg-gray-300'">
              <svg v-if="isSelected('Discharge Permit')" class="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M3.707 5.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 00-1.414-1.414L5 6.586 3.707 5.293z"/>
              </svg>
            </div>
          </div>
          <div class="ml-3 flex-1">
            <h4 class="text-sm font-semibold" :class="isSelected('Discharge Permit') ? 'text-blue-900' : 'text-gray-900'">
              Discharge Permit
            </h4>
            <p class="text-xs text-gray-600 mt-1">
              Discharging contaminants to land, air, or water
            </p>
          </div>
        </div>
      </div>

      <!-- Water Permit -->
      <div
        @click="toggleConsent('Water Permit')"
        class="cursor-pointer rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="isSelected('Water Permit')
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
          : 'border-gray-300 bg-white hover:border-blue-300'"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div class="h-5 w-5 rounded flex items-center justify-center"
              :class="isSelected('Water Permit') ? 'bg-blue-500' : 'bg-gray-300'">
              <svg v-if="isSelected('Water Permit')" class="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M3.707 5.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 00-1.414-1.414L5 6.586 3.707 5.293z"/>
              </svg>
            </div>
          </div>
          <div class="ml-3 flex-1">
            <h4 class="text-sm font-semibold" :class="isSelected('Water Permit') ? 'text-blue-900' : 'text-gray-900'">
              Water Permit
            </h4>
            <p class="text-xs text-gray-600 mt-1">
              Taking, using, damming, or diverting water
            </p>
          </div>
        </div>
      </div>

      <!-- Coastal Permit -->
      <div
        @click="toggleConsent('Coastal Permit')"
        class="cursor-pointer rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="isSelected('Coastal Permit')
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
          : 'border-gray-300 bg-white hover:border-blue-300'"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div class="h-5 w-5 rounded flex items-center justify-center"
              :class="isSelected('Coastal Permit') ? 'bg-blue-500' : 'bg-gray-300'">
              <svg v-if="isSelected('Coastal Permit')" class="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 12 12">
                <path d="M3.707 5.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 00-1.414-1.414L5 6.586 3.707 5.293z"/>
              </svg>
            </div>
          </div>
          <div class="ml-3 flex-1">
            <h4 class="text-sm font-semibold" :class="isSelected('Coastal Permit') ? 'text-blue-900' : 'text-gray-900'">
              Coastal Permit
            </h4>
            <p class="text-xs text-gray-600 mt-1">
              Activities in the coastal marine area
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Count -->
    <div v-if="selectedConsents.length > 0" class="bg-blue-50 border border-blue-200 rounded-lg p-3">
      <p class="text-sm text-blue-900">
        <span class="font-semibold">{{ selectedConsents.length }}</span>
        {{ selectedConsents.length === 1 ? 'consent type' : 'consent types' }} selected
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Array,
		default: () => [],
	},
	required: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["update:modelValue"])

const selectedConsents = ref([])

onMounted(() => {
	if (props.modelValue && Array.isArray(props.modelValue)) {
		selectedConsents.value = [...props.modelValue]
	}
})

watch(
	() => props.modelValue,
	(newVal) => {
		if (newVal && Array.isArray(newVal)) {
			selectedConsents.value = [...newVal]
		}
	},
	{ deep: true },
)

function isSelected(consentType) {
	return selectedConsents.value.includes(consentType)
}

function toggleConsent(consentType) {
	const index = selectedConsents.value.indexOf(consentType)
	if (index > -1) {
		selectedConsents.value.splice(index, 1)
	} else {
		selectedConsents.value.push(consentType)
	}
	emit("update:modelValue", selectedConsents.value)
}
</script>
