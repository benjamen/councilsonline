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
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">Identified Affected Parties</h3>
          <button
            @click="openAddModal"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Affected Party
          </button>
        </div>

        <div class="p-6">
          <div v-if="localData.affected_parties && localData.affected_parties.length > 0" class="space-y-3">
            <div
              v-for="(party, index) in localData.affected_parties"
              :key="index"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50"
            >
              <div class="flex items-start justify-between mb-3">
                <h4 class="font-semibold text-gray-900">{{ party.party_name || 'Unnamed Party' }}</h4>
                <div class="flex items-center gap-2">
                  <button
                    @click="openEditModal(index)"
                    type="button"
                    class="text-blue-600 hover:text-blue-800 p-1"
                    title="Edit"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="removeParty(index)"
                    type="button"
                    class="text-red-600 hover:text-red-800 p-1"
                    title="Remove"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <span class="text-sm text-gray-500">Relationship:</span>
                  <p class="font-medium">{{ party.relationship || 'Not specified' }}</p>
                </div>
                <div>
                  <span class="text-sm text-gray-500">Contact:</span>
                  <p class="font-medium">{{ party.contact_info || 'Not specified' }}</p>
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
            <p class="text-sm text-gray-500 mt-1">Click "Add Affected Party" to get started</p>
          </div>
        </div>
      </div>

      <!-- Add/Edit Modal -->
      <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
        <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingIndex !== null ? 'Edit' : 'Add' }} Affected Party
            </h3>
            <button
              @click="closeModal"
              type="button"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Party Name *</label>
              <input
                v-model="currentParty.party_name"
                type="text"
                placeholder="e.g., John Smith, ABC Infrastructure Ltd"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Relationship *</label>
              <select
                v-model="currentParty.relationship"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Select relationship</option>
                <option value="Adjacent neighbor">Adjacent neighbor</option>
                <option value="Nearby neighbor">Nearby neighbor</option>
                <option value="Property owner">Property owner</option>
                <option value="Leaseholder">Leaseholder</option>
                <option value="Easement holder">Easement holder</option>
                <option value="Infrastructure provider">Infrastructure provider</option>
                <option value="Iwi/Hapū">Iwi/Hapū</option>
                <option value="Community group">Community group</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Contact Information</label>
              <input
                v-model="currentParty.contact_info"
                type="text"
                placeholder="Email or phone number"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Address</label>
              <textarea
                v-model="currentParty.address"
                rows="2"
                placeholder="Physical or postal address"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Potential Effects</label>
              <textarea
                v-model="currentParty.effects"
                rows="3"
                placeholder="Describe how your proposal may affect this party (e.g., visual, noise, access, etc.)"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <div class="flex items-start">
              <input
                v-model="currentParty.written_approval"
                type="checkbox"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label class="ml-3 text-sm text-gray-700">
                <span class="font-medium">Written approval obtained</span>
                <p class="text-xs text-gray-500 mt-1">
                  Check this if you have obtained written approval from this party (upload approval document separately)
                </p>
              </label>
            </div>
          </div>

          <div class="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-end gap-3">
            <button
              @click="closeModal"
              type="button"
              class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="saveParty"
              type="button"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              :disabled="!currentParty.party_name || !currentParty.relationship"
            >
              {{ editingIndex !== null ? 'Update' : 'Add' }} Party
            </button>
          </div>
        </div>
      </div>

      <!-- Written Approvals Summary -->
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
import { computed, defineEmits, defineProps, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

// Create local copy of data
const localData = ref({
	affected_parties: props.modelValue.affected_parties || [],
	aee_consultation_summary: props.modelValue.aee_consultation_summary || "",
})

// Modal state
const showModal = ref(false)
const editingIndex = ref(null)
const currentParty = ref({
	party_name: "",
	relationship: "",
	contact_info: "",
	address: "",
	effects: "",
	written_approval: false,
})

// Computed property for parties with written approvals
const writtenApprovals = computed(() => {
	return localData.value.affected_parties.filter(
		(party) => party.written_approval === true,
	)
})

// Open modal for adding new party
const openAddModal = () => {
	editingIndex.value = null
	currentParty.value = {
		party_name: "",
		relationship: "",
		contact_info: "",
		address: "",
		effects: "",
		written_approval: false,
	}
	showModal.value = true
}

// Open modal for editing existing party
const openEditModal = (index) => {
	editingIndex.value = index
	currentParty.value = { ...localData.value.affected_parties[index] }
	showModal.value = true
}

// Close modal
const closeModal = () => {
	showModal.value = false
	editingIndex.value = null
	currentParty.value = {
		party_name: "",
		relationship: "",
		contact_info: "",
		address: "",
		effects: "",
		written_approval: false,
	}
}

// Save party (add or update)
const saveParty = () => {
	if (!currentParty.value.party_name || !currentParty.value.relationship) {
		return
	}

	if (editingIndex.value !== null) {
		// Update existing party
		localData.value.affected_parties[editingIndex.value] = {
			...currentParty.value,
		}
	} else {
		// Add new party
		localData.value.affected_parties.push({ ...currentParty.value })
	}

	closeModal()
}

// Remove party
const removeParty = (index) => {
	if (confirm("Are you sure you want to remove this affected party?")) {
		localData.value.affected_parties.splice(index, 1)
	}
}

// Watch for external changes
watch(
	() => props.modelValue,
	(newVal) => {
		localData.value.affected_parties = newVal.affected_parties || []
		localData.value.aee_consultation_summary =
			newVal.aee_consultation_summary || ""
	},
	{ deep: true },
)

// Watch local changes and emit
watch(
	localData,
	(newVal) => {
		emit("update:modelValue", {
			...props.modelValue,
			affected_parties: newVal.affected_parties,
			aee_consultation_summary: newVal.aee_consultation_summary,
		})
	},
	{ deep: true },
)
</script>
