<template>
  <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
    <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
      <h3 class="font-semibold text-gray-900">Affected Parties (RMA s.95A-s.95F)</h3>
    </div>

    <div class="p-6 space-y-6">
      <InfoBox title="About Affected Parties" variant="info">
        <p>
          List all parties (neighbors, landowners, infrastructure providers, etc.) who may be affected by your proposal.
          If you have obtained written approvals under s.95E, upload them as supporting documents. Written approvals can reduce notification requirements.
        </p>
      </InfoBox>

      <!-- Add Affected Party Button -->
      <div class="flex justify-between items-center">
        <p class="text-sm text-gray-700">
          Identify all parties who may experience adverse effects from your proposal
        </p>
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

      <!-- Affected Parties List -->
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
              <span class="text-sm text-gray-500">Written Approval (s.95E):</span>
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

      <div v-else class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="mt-2 text-sm text-gray-500">No affected parties identified yet</p>
        <p class="text-sm text-gray-500 mt-1">Click "Add Affected Party" to get started</p>
      </div>

      <!-- Written Approvals Summary -->
      <div v-if="writtenApprovals.length > 0" class="border-t border-gray-200 pt-4">
        <h4 class="text-sm font-semibold text-gray-900 mb-2">Written Approvals Summary (s.95E RMA)</h4>
        <p class="text-sm text-gray-600 mb-3">
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
        <div class="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-sm text-green-800">
            Remember to upload written approval documents in Step 6 (Plans & Documents).
          </p>
        </div>
      </div>

      <!-- Consultation Notes -->
      <div class="border-t border-gray-200 pt-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Consultation Summary
        </label>
        <textarea
          :value="localData.aee_consultation_summary"
          @input="updateConsultation($event.target.value)"
          rows="6"
          placeholder="Describe who you consulted with, when, how, and the outcomes of consultation. Include any mitigation measures agreed to address concerns..."
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        ></textarea>
        <p class="text-sm text-gray-500 mt-2">
          Documenting consultation efforts can demonstrate good faith engagement and help the council understand community views.
        </p>
      </div>
    </div>

    <!-- Affected Party Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
        <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingIndex !== null ? 'Edit' : 'Add' }} Affected Party
            </h3>
            <button @click="closeModal" type="button" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Party Name *</label>
              <input v-model="currentParty.party_name" type="text" placeholder="e.g., John Smith, ABC Infrastructure Ltd" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Relationship *</label>
              <select v-model="currentParty.relationship" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
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
              <input v-model="currentParty.contact_info" type="text" placeholder="Email or phone number" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Address</label>
              <textarea v-model="currentParty.address" rows="2" placeholder="Physical or postal address" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Potential Effects</label>
              <textarea v-model="currentParty.effects" rows="3" placeholder="Describe how your proposal may affect this party (e.g., visual, noise, access, etc.)" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
            </div>

            <div class="flex items-start">
              <input v-model="currentParty.written_approval" type="checkbox" class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
              <label class="ml-3 text-sm text-gray-700">
                <span class="font-medium">Written approval obtained (s.95E RMA)</span>
                <p class="text-xs text-gray-500 mt-1">
                  Check this if you have obtained written approval from this party (upload approval document in Step 6)
                </p>
              </label>
            </div>
          </div>

          <div class="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-end gap-3">
            <button @click="closeModal" type="button" class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
              Cancel
            </button>
            <button @click="saveParty" type="button" :disabled="!currentParty.party_name || !currentParty.relationship" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              {{ editingIndex !== null ? 'Update' : 'Add' }} Party
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import InfoBox from "../shared/InfoBox.vue"

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(["update:modelValue"])

const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value)
})

const showModal = ref(false)
const editingIndex = ref(null)
const currentParty = ref({
  party_name: "",
  relationship: "",
  contact_info: "",
  address: "",
  effects: "",
  written_approval: false
})

const writtenApprovals = computed(() => {
  return localData.value.affected_parties?.filter(
    (party) => party.written_approval === true
  ) || []
})

const updateConsultation = (value) => {
  const updated = { ...props.modelValue, aee_consultation_summary: value }
  emit("update:modelValue", updated)
}

const openAddModal = () => {
  editingIndex.value = null
  currentParty.value = {
    party_name: "",
    relationship: "",
    contact_info: "",
    address: "",
    effects: "",
    written_approval: false
  }
  showModal.value = true
}

const openEditModal = (index) => {
  editingIndex.value = index
  currentParty.value = { ...localData.value.affected_parties[index] }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingIndex.value = null
  currentParty.value = {
    party_name: "",
    relationship: "",
    contact_info: "",
    address: "",
    effects: "",
    written_approval: false
  }
}

const saveParty = () => {
  if (!currentParty.value.party_name || !currentParty.value.relationship) {
    return
  }

  const updated = { ...props.modelValue }
  if (!updated.affected_parties) updated.affected_parties = []

  if (editingIndex.value !== null) {
    updated.affected_parties[editingIndex.value] = { ...currentParty.value }
  } else {
    updated.affected_parties.push({ ...currentParty.value })
  }

  emit("update:modelValue", updated)
  closeModal()
}

const removeParty = (index) => {
  if (confirm("Are you sure you want to remove this affected party?")) {
    const updated = { ...props.modelValue }
    updated.affected_parties.splice(index, 1)
    emit("update:modelValue", updated)
  }
}
</script>
