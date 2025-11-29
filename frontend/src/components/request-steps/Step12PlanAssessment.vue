<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Plan Assessment</h2>
    <p class="text-gray-600 mb-8">Identify relevant district/regional plan rules and assess compliance</p>

    <div class="space-y-6">
      <!-- Plan Rules Section -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-900">District/Regional Plan Rules</h3>
            <button
              @click="addPlanRule"
              type="button"
              class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Add Plan Rule
            </button>
          </div>
        </div>

        <div class="p-6">
          <div v-if="localData.plan_rules && localData.plan_rules.length > 0" class="space-y-4">
            <div
              v-for="(rule, index) in localData.plan_rules"
              :key="index"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50"
            >
              <div class="flex justify-between items-start mb-4">
                <h4 class="font-medium text-gray-900">Plan Rule {{ index + 1 }}</h4>
                <button
                  @click="removePlanRule(index)"
                  type="button"
                  class="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Remove
                </button>
              </div>

              <div class="grid md:grid-cols-2 gap-4">
                <!-- Plan Type -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Plan Type <span class="text-red-500">*</span>
                  </label>
                  <select
                    v-model="rule.plan_type"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select plan type...</option>
                    <option value="District Plan">District Plan</option>
                    <option value="Regional Plan">Regional Plan</option>
                    <option value="Proposed Plan">Proposed Plan</option>
                    <option value="Plan Change">Plan Change</option>
                    <option value="National Policy Statement">National Policy Statement</option>
                    <option value="National Environmental Standard">National Environmental Standard</option>
                  </select>
                </div>

                <!-- Rule Reference -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Rule Reference <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="rule.rule_reference"
                    type="text"
                    required
                    placeholder="e.g., Rule 14.2.3.1"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <!-- Rule Description -->
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Rule Description <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="rule.description"
                  required
                  rows="3"
                  placeholder="Describe what the rule requires or controls..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>

              <!-- Compliance Status -->
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Compliance Status <span class="text-red-500">*</span>
                </label>
                <div class="flex gap-4">
                  <label class="flex items-center">
                    <input
                      type="radio"
                      :value="true"
                      v-model="rule.compliant"
                      class="mr-2"
                    />
                    <span class="text-sm">Complies</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      type="radio"
                      :value="false"
                      v-model="rule.compliant"
                      class="mr-2"
                    />
                    <span class="text-sm">Does Not Comply</span>
                  </label>
                </div>
              </div>

              <!-- Assessment Notes -->
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Assessment Notes
                </label>
                <textarea
                  v-model="rule.notes"
                  rows="3"
                  placeholder="Explain how your proposal complies or why consent is required..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="mt-2 text-sm text-gray-500">No plan rules added yet</p>
            <p class="text-sm text-gray-500">Click "Add Plan Rule" to identify relevant planning rules</p>
          </div>
        </div>
      </div>

      <!-- Help Text -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">Planning Assessment Guidance</h5>
            <ul class="text-blue-800 text-sm mt-2 space-y-1 list-disc list-inside">
              <li>Identify all relevant district and regional plan rules that apply to your proposal</li>
              <li>Check zone rules, overlays, designations, and any relevant standards</li>
              <li>Assess whether your proposal complies with permitted activity standards</li>
              <li>If non-compliant, explain why consent is required and the nature of the breach</li>
              <li>Consider relevant objectives, policies, and assessment criteria</li>
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
  plan_rules: props.modelValue.plan_rules || []
})

// Watch for external changes
watch(() => props.modelValue.plan_rules, (newVal) => {
  if (newVal !== localData.value.plan_rules) {
    localData.value.plan_rules = newVal || []
  }
}, { deep: true })

// Watch local changes and emit
watch(localData, (newVal) => {
  emit('update:modelValue', {
    ...props.modelValue,
    plan_rules: newVal.plan_rules
  })
}, { deep: true })

const addPlanRule = () => {
  localData.value.plan_rules.push({
    plan_type: '',
    rule_reference: '',
    description: '',
    compliant: null,
    notes: ''
  })
}

const removePlanRule = (index) => {
  localData.value.plan_rules.splice(index, 1)
}
</script>
