<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Affected Parties</h2>
    <p class="text-gray-600 mb-8">Identify parties potentially affected by your proposal and any written approvals obtained</p>

    <div class="space-y-6">
      <!-- Affected Parties Note -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">About Affected Parties</h5>
            <p class="text-blue-800 text-sm mt-1">
              List all parties (neighbors, landowners, infrastructure providers, etc.) who may be affected by your proposal.
              If you have obtained written approvals, upload them as supporting documents.
            </p>
          </div>
        </div>
      </div>

      <!-- Affected Parties List -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Identified Affected Parties</h3>
        </div>

        <div class="p-6">
          <p class="text-sm text-gray-600 mb-4">
            This functionality uses the Affected Parties section you may have already filled in earlier.
            Use the main form's affected parties section to manage this list.
          </p>

          <div v-if="modelValue.affected_parties && modelValue.affected_parties.length > 0" class="space-y-3">
            <div
              v-for="(party, index) in modelValue.affected_parties"
              :key="index"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50"
            >
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <span class="text-sm text-gray-500">Name:</span>
                  <p class="font-medium">{{ party.party_name || 'Not specified' }}</p>
                </div>
                <div>
                  <span class="text-sm text-gray-500">Relationship:</span>
                  <p class="font-medium">{{ party.relationship || 'Not specified' }}</p>
                </div>
                <div>
                  <span class="text-sm text-gray-500">Address:</span>
                  <p class="font-medium">{{ party.address || 'Not specified' }}</p>
                </div>
                <div>
                  <span class="text-sm text-gray-500">Written Approval:</span>
                  <p class="font-medium">
                    <span v-if="party.written_approval" class="text-green-600">✓ Obtained</span>
                    <span v-else class="text-gray-500">Not obtained</span>
                  </p>
                </div>
              </div>
              <div v-if="party.effects" class="mt-3">
                <span class="text-sm text-gray-500">Effects:</span>
                <p class="text-sm mt-1">{{ party.effects }}</p>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p class="mt-2 text-sm text-gray-500">No affected parties identified yet</p>
            <p class="text-sm text-gray-500">Add affected parties in the Delivery & Payment step (Step 6)</p>
          </div>
        </div>
      </div>

      <!-- Written Approvals Section -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Written Approvals Summary</h3>
        </div>

        <div class="p-6">
          <div v-if="writtenApprovals.length > 0">
            <p class="text-sm text-gray-600 mb-4">
              You have obtained written approvals from {{ writtenApprovals.length }} affected {{ writtenApprovals.length === 1 ? 'party' : 'parties' }}.
            </p>
            <div class="space-y-2">
              <div
                v-for="party in writtenApprovals"
                :key="party.party_name"
                class="flex items-center text-sm"
              >
                <svg class="w-4 h-4 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>{{ party.party_name }} ({{ party.relationship }})</span>
              </div>
            </div>
            <div class="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p class="text-sm text-green-800">
                Remember to upload written approval documents in the supporting documents section.
              </p>
            </div>
          </div>

          <div v-else>
            <p class="text-sm text-gray-600">
              No written approvals have been obtained yet. If you obtain written approvals from affected parties,
              this can reduce notification requirements and processing timeframes.
            </p>
          </div>
        </div>
      </div>

      <!-- Consultation Notes -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Consultation Summary</h3>
        </div>

        <div class="p-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Describe any consultation you have undertaken with affected parties
          </label>
          <textarea
            v-model="localData.aee_consultation_summary"
            rows="6"
            placeholder="Describe who you consulted with, when, how, and the outcomes of consultation. Include any mitigation measures agreed to address concerns..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
          <p class="text-sm text-gray-500 mt-2">
            Documenting consultation efforts can demonstrate good faith engagement and help the council understand community views.
          </p>
        </div>
      </div>

      <!-- Guidance -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Affected Parties Guidance</h5>
            <ul class="text-yellow-800 text-sm mt-2 space-y-1 list-disc list-inside">
              <li>Consider immediate neighbors, landowners with shared boundaries</li>
              <li>Infrastructure providers (e.g., power, water, telecommunications)</li>
              <li>Parties with interests over the land (e.g., easements, covenants)</li>
              <li>Anyone who may experience effects from your proposal</li>
              <li>Written approvals can help reduce notification and costs</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

// Create local copy of data
const localData = ref({
  aee_consultation_summary: props.modelValue.aee_consultation_summary || ''
})

// Computed property for parties with written approvals
const writtenApprovals = computed(() => {
  if (!props.modelValue.affected_parties) return []
  return props.modelValue.affected_parties.filter(party => party.written_approval === true)
})

// Watch for external changes
watch(() => props.modelValue.aee_consultation_summary, (newVal) => {
  if (newVal !== localData.value.aee_consultation_summary) {
    localData.value.aee_consultation_summary = newVal || ''
  }
})

// Watch local changes and emit
watch(localData, (newVal) => {
  emit('update:modelValue', {
    ...props.modelValue,
    aee_consultation_summary: newVal.aee_consultation_summary
  })
}, { deep: true })
</script>
