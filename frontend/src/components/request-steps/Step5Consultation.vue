<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Consultation with Other Parties</h2>
    <p class="text-gray-600 mb-8">Document consultation undertaken with iwi, community groups, and other relevant organizations (RMA Schedule 4)</p>

    <div class="space-y-6">
      <!-- Consultation Overview -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">About Consultation</h5>
            <p class="text-blue-800 text-sm mt-1">
              Under RMA Schedule 4, Assessment of Environmental Effects should include consultation undertaken.
              Document any consultation with iwi/hapū, community groups, infrastructure providers, or other relevant organizations.
            </p>
            <p class="text-blue-800 text-sm mt-2">
              <strong>Tip:</strong> Proactive consultation demonstrates good planning and can help identify concerns early,
              potentially reducing notification requirements and processing timeframes.
            </p>
          </div>
        </div>
      </div>

      <!-- Consultation Status -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Consultation Undertaken</h3>
        </div>

        <div class="p-6">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Have you consulted with any organizations or groups about this proposal?
            </label>
            <div class="flex gap-4">
              <label class="flex items-center">
                <input
                  v-model="localData.consultation_undertaken"
                  type="radio"
                  :value="true"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">Yes</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="localData.consultation_undertaken"
                  type="radio"
                  :value="false"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">No</span>
              </label>
            </div>
          </div>

          <!-- No consultation explanation -->
          <div v-if="localData.consultation_undertaken === false" class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Reason for no consultation (optional)
            </label>
            <textarea
              v-model="localData.no_consultation_reason"
              rows="3"
              placeholder="Explain why consultation was not undertaken (e.g., proposal has minimal effects, consultation not required by council policy, etc.)"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Consulted Organizations (FRD Section 7) -->
      <div v-if="localData.consultation_undertaken === true" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">Organizations Consulted</h3>
          <button
            @click="openAddModal"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Organization
          </button>
        </div>

        <div class="p-6">
          <div v-if="localData.consulted_organizations && localData.consulted_organizations.length > 0" class="space-y-3">
            <div
              v-for="(org, index) in localData.consulted_organizations"
              :key="index"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50"
            >
              <div class="flex items-start justify-between mb-3">
                <div>
                  <h4 class="font-semibold text-gray-900 flex items-center gap-2">
                    {{ org.organisation_name || 'Unnamed Organization' }}
                    <span v-if="org.is_iwi" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                      Iwi/Hapū
                    </span>
                  </h4>
                  <p v-if="org.contact_name" class="text-sm text-gray-600 mt-1">Contact: {{ org.contact_name }}</p>
                </div>
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
                    @click="removeOrganization(index)"
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
                  <span class="text-sm text-gray-500">Contact:</span>
                  <p class="font-medium">{{ org.email || org.phone || 'Not specified' }}</p>
                </div>
                <div>
                  <span class="text-sm text-gray-500">Concerns Raised:</span>
                  <p class="font-medium">
                    <span v-if="org.had_concerns" class="text-amber-600">Yes</span>
                    <span v-else class="text-green-600">No</span>
                  </p>
                </div>
              </div>

              <div v-if="org.had_concerns && org.concern_details" class="mt-3 border-t border-gray-200 pt-3">
                <span class="text-sm text-gray-500">Concerns Raised:</span>
                <p class="text-sm mt-1">{{ org.concern_details }}</p>
              </div>

              <div v-if="org.resolution_details" class="mt-3 border-t border-gray-200 pt-3">
                <span class="text-sm text-gray-500">Resolution/Response:</span>
                <p class="text-sm mt-1">{{ org.resolution_details }}</p>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p class="mt-2 text-sm text-gray-500">No organizations added yet</p>
            <p class="text-sm text-gray-500 mt-1">Click "Add Organization" to document your consultation</p>
          </div>
        </div>
      </div>

      <!-- Consultation Summary -->
      <div v-if="localData.consultation_undertaken === true" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Overall Consultation Summary</h3>
        </div>

        <div class="p-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Summary of Consultation Process and Outcomes
          </label>
          <textarea
            v-model="localData.consultation_summary"
            rows="6"
            placeholder="Provide an overall summary of your consultation process:&#10;• When and how consultation was undertaken&#10;• Key issues raised across all consultees&#10;• How concerns were addressed or why they were not&#10;• Any commitments or agreements made&#10;• Overall feedback on the proposal"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
          <p class="text-sm text-gray-500 mt-2">
            This summary will be included in your Assessment of Environmental Effects (AEE) under Schedule 4 clause 2(1)(d).
          </p>
        </div>
      </div>

      <!-- Iwi Consultation Guidance -->
      <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-purple-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-purple-900 text-sm">Iwi/Hapū Consultation Guidance</h5>
            <p class="text-purple-800 text-sm mt-2">
              Under sections 6(e), 7(a), and 8 of the RMA, councils must consider:
            </p>
            <ul class="text-purple-800 text-sm mt-2 space-y-1 list-disc list-inside">
              <li>The relationship of Māori and their culture and traditions with ancestral lands, water, sites, wāhi tapu, and other taonga</li>
              <li>Kaitiakitanga (guardianship)</li>
              <li>The principles of the Treaty of Waitangi</li>
            </ul>
            <p class="text-purple-800 text-sm mt-2">
              <strong>Check with your council</strong> to identify relevant iwi/hapū authorities in your area and their preferred consultation processes.
              Many councils maintain iwi contact lists and consultation protocols.
            </p>
          </div>
        </div>
      </div>

      <!-- General Guidance -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Who to Consider for Consultation</h5>
            <ul class="text-yellow-800 text-sm mt-2 space-y-1 list-disc list-inside">
              <li><strong>Iwi/Hapū:</strong> Local mana whenua with interests in the area</li>
              <li><strong>Infrastructure Providers:</strong> Power companies, telecommunications, water suppliers</li>
              <li><strong>Community Groups:</strong> Resident associations, environmental groups, heritage groups</li>
              <li><strong>Government Agencies:</strong> NZTA, DoC, Heritage NZ (for significant proposals)</li>
              <li><strong>Special Interest Groups:</strong> Organizations with relevant expertise or advocacy roles</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Organization Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
        @click.self="closeModal"
      >
        <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingIndex !== null ? 'Edit' : 'Add' }} Consulted Organization
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
              <label class="block text-sm font-medium text-gray-700 mb-2">Organisation Name *</label>
              <input
                v-model="currentOrg.organisation_name"
                type="text"
                placeholder="e.g., Ngāti Whātua, Auckland Residents Association"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div class="flex items-start">
              <input
                v-model="currentOrg.is_iwi"
                type="checkbox"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label class="ml-3 text-sm text-gray-700">
                <span class="font-medium">This is an Iwi/Hapū organization</span>
                <p class="text-xs text-gray-500 mt-1">
                  Check this if consulting with a mana whenua iwi or hapū
                </p>
              </label>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Contact Name</label>
              <input
                v-model="currentOrg.contact_name"
                type="text"
                placeholder="Primary contact person"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  v-model="currentOrg.email"
                  type="email"
                  placeholder="contact@organization.nz"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                <input
                  v-model="currentOrg.phone"
                  type="tel"
                  placeholder="09 123 4567"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Address</label>
              <textarea
                v-model="currentOrg.address"
                rows="2"
                placeholder="Physical or postal address"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <div class="grid md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">RD Number</label>
                <input
                  v-model="currentOrg.rd_number"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Suburb</label>
                <input
                  v-model="currentOrg.suburb"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">City</label>
                <input
                  v-model="currentOrg.city"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Postcode</label>
              <input
                v-model="currentOrg.postcode"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div class="border-t border-gray-200 pt-4 mt-4">
              <div class="flex items-start mb-4">
                <input
                  v-model="currentOrg.had_concerns"
                  type="checkbox"
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label class="ml-3 text-sm text-gray-700">
                  <span class="font-medium">This organization raised concerns</span>
                  <p class="text-xs text-gray-500 mt-1">
                    Check this if concerns or issues were raised during consultation
                  </p>
                </label>
              </div>

              <div v-if="currentOrg.had_concerns" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Concerns/Issues Raised</label>
                  <textarea
                    v-model="currentOrg.concern_details"
                    rows="3"
                    placeholder="Describe the specific concerns or issues raised..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Resolution/Response</label>
                  <textarea
                    v-model="currentOrg.resolution_details"
                    rows="3"
                    placeholder="Describe how concerns were addressed or responded to..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>
              </div>
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
              @click="saveOrganization"
              type="button"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              :disabled="!currentOrg.organisation_name"
            >
              {{ editingIndex !== null ? 'Update' : 'Add' }} Organization
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps, ref } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

const localData = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

// Modal state
const showModal = ref(false)
const editingIndex = ref(null)
const currentOrg = ref({
	organisation_name: "",
	is_iwi: false,
	contact_name: "",
	email: "",
	phone: "",
	address: "",
	rd_number: "",
	suburb: "",
	city: "",
	postcode: "",
	had_concerns: false,
	concern_details: "",
	resolution_details: "",
})

// Open modal for adding new organization
const openAddModal = () => {
	editingIndex.value = null
	currentOrg.value = {
		organisation_name: "",
		is_iwi: false,
		contact_name: "",
		email: "",
		phone: "",
		address: "",
		rd_number: "",
		suburb: "",
		city: "",
		postcode: "",
		had_concerns: false,
		concern_details: "",
		resolution_details: "",
	}
	showModal.value = true
}

// Open modal for editing existing organization
const openEditModal = (index) => {
	editingIndex.value = index
	currentOrg.value = { ...localData.value.consulted_organizations[index] }
	showModal.value = true
}

// Close modal
const closeModal = () => {
	showModal.value = false
	editingIndex.value = null
	currentOrg.value = {
		organisation_name: "",
		is_iwi: false,
		contact_name: "",
		email: "",
		phone: "",
		address: "",
		rd_number: "",
		suburb: "",
		city: "",
		postcode: "",
		had_concerns: false,
		concern_details: "",
		resolution_details: "",
	}
}

// Save organization (add or update)
const saveOrganization = () => {
	if (!currentOrg.value.organisation_name) {
		return
	}

	const updatedData = { ...props.modelValue }
	if (!updatedData.consulted_organizations) {
		updatedData.consulted_organizations = []
	}

	if (editingIndex.value !== null) {
		// Update existing organization
		updatedData.consulted_organizations[editingIndex.value] = {
			...currentOrg.value,
		}
	} else {
		// Add new organization
		updatedData.consulted_organizations.push({ ...currentOrg.value })
	}

	emit("update:modelValue", updatedData)
	closeModal()
}

// Remove organization
const removeOrganization = (index) => {
	if (confirm("Are you sure you want to remove this organization?")) {
		const updatedData = { ...props.modelValue }
		updatedData.consulted_organizations.splice(index, 1)
		emit("update:modelValue", updatedData)
	}
}
</script>
