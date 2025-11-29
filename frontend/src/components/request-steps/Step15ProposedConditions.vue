<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Proposed Conditions</h2>
    <p class="text-gray-600 mb-8">Suggest conditions that could be imposed to address adverse effects</p>

    <div class="space-y-6">
      <!-- Info Box -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">About Proposed Conditions</h5>
            <p class="text-blue-800 text-sm mt-1">
              Proposing consent conditions demonstrates a proactive approach to managing effects.
              Conditions should be specific, measurable, achievable, and directly related to managing adverse effects.
            </p>
          </div>
        </div>
      </div>

      <!-- Proposed Conditions Section -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-900">Proposed Consent Conditions</h3>
            <button
              @click="addCondition"
              type="button"
              class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Add Condition
            </button>
          </div>
        </div>

        <div class="p-6">
          <div v-if="localData.proposed_conditions && localData.proposed_conditions.length > 0" class="space-y-4">
            <div
              v-for="(condition, index) in localData.proposed_conditions"
              :key="index"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50"
            >
              <div class="flex justify-between items-start mb-4">
                <h4 class="font-medium text-gray-900">Condition {{ index + 1 }}</h4>
                <button
                  @click="removeCondition(index)"
                  type="button"
                  class="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Remove
                </button>
              </div>

              <div class="grid md:grid-cols-2 gap-4 mb-4">
                <!-- Condition Category -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Condition Category
                  </label>
                  <select
                    v-model="condition.category"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select category...</option>
                    <option value="General">General</option>
                    <option value="Construction">Construction Management</option>
                    <option value="Operational">Operational</option>
                    <option value="Landscaping">Landscaping</option>
                    <option value="Servicing">Servicing & Infrastructure</option>
                    <option value="Traffic">Traffic & Parking</option>
                    <option value="Noise">Noise</option>
                    <option value="Stormwater">Stormwater</option>
                    <option value="Contamination">Contamination</option>
                    <option value="Heritage">Heritage</option>
                    <option value="Ecology">Ecology & Biodiversity</option>
                    <option value="Monitoring">Monitoring & Reporting</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <!-- Timing -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Timing
                  </label>
                  <select
                    v-model="condition.timing"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select timing...</option>
                    <option value="Prior to Commencement">Prior to Commencement</option>
                    <option value="During Construction">During Construction</option>
                    <option value="Prior to Occupation">Prior to Occupation</option>
                    <option value="Ongoing">Ongoing</option>
                    <option value="On Completion">On Completion</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <!-- Condition Text -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Condition Wording <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="condition.condition_text"
                  required
                  rows="4"
                  placeholder="Write the proposed condition in clear, enforceable language...

Example: 'All construction activities shall be limited to the hours of 7:00am to 7:00pm Monday to Saturday, with no work permitted on Sundays or public holidays.'"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>

              <!-- Rationale -->
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Rationale
                </label>
                <textarea
                  v-model="condition.rationale"
                  rows="3"
                  placeholder="Explain the purpose of this condition and how it addresses adverse effects..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            <p class="mt-2 text-sm text-gray-500">No conditions proposed yet</p>
            <p class="text-sm text-gray-500">Click "Add Condition" to propose consent conditions</p>
          </div>
        </div>
      </div>

      <!-- Example Conditions -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Example Condition Types</h3>
        </div>

        <div class="p-6 space-y-3">
          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Construction Hours</p>
            <p class="text-xs text-gray-600 mt-1">Limiting construction activities to specific hours to manage noise effects</p>
          </div>

          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Landscaping</p>
            <p class="text-xs text-gray-600 mt-1">Requiring planting to screen development or enhance visual amenity</p>
          </div>

          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Traffic Management</p>
            <p class="text-xs text-gray-600 mt-1">Requiring traffic management plans or parking arrangements</p>
          </div>

          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Stormwater</p>
            <p class="text-xs text-gray-600 mt-1">Requiring stormwater management devices or erosion control measures</p>
          </div>

          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Monitoring</p>
            <p class="text-xs text-gray-600 mt-1">Requiring monitoring and reporting of environmental effects</p>
          </div>
        </div>
      </div>

      <!-- Guidance -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Writing Good Conditions</h5>
            <ul class="text-yellow-800 text-sm mt-2 space-y-1 list-disc list-inside">
              <li><strong>Clear:</strong> Unambiguous and easy to understand</li>
              <li><strong>Enforceable:</strong> Able to be monitored and enforced by the council</li>
              <li><strong>Necessary:</strong> Directly related to managing an identified adverse effect</li>
              <li><strong>Reasonable:</strong> Practical and achievable to implement</li>
              <li><strong>Specific:</strong> Include measurable standards, timeframes, or thresholds</li>
              <li>Note: The council may modify, add, or remove conditions during processing</li>
            </ul>
          </div>
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

// Create local copy of data
const localData = ref({
  proposed_conditions: props.modelValue.proposed_conditions || []
})

// Watch for external changes
watch(() => props.modelValue.proposed_conditions, (newVal) => {
  if (newVal !== localData.value.proposed_conditions) {
    localData.value.proposed_conditions = newVal || []
  }
}, { deep: true })

// Watch local changes and emit
watch(localData, (newVal) => {
  emit('update:modelValue', {
    ...props.modelValue,
    proposed_conditions: newVal.proposed_conditions
  })
}, { deep: true })

const addCondition = () => {
  localData.value.proposed_conditions.push({
    category: '',
    timing: '',
    condition_text: '',
    rationale: ''
  })
}

const removeCondition = (index) => {
  localData.value.proposed_conditions.splice(index, 1)
}
</script>
