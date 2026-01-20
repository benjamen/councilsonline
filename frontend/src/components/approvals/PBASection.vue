<template>
  <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
    <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
      <h3 class="font-semibold text-gray-900">Permitted Boundary Activity (PBA) Approvals</h3>
    </div>

    <div class="p-6 space-y-4">
      <InfoBox title="About Permitted Boundary Activities" variant="info">
        <p>
          A Permitted Boundary Activity is an activity within prescribed proximity to a property boundary that would normally be permitted.
          Under s.87BA RMA, if you obtain written approval from the affected neighbor(s), the activity may be permitted without consent.
        </p>
        <p class="mt-2">
          <strong>Note:</strong> If you are applying for consent because you could not obtain PBA approval, please complete this section.
        </p>
      </InfoBox>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Does this application relate to a Permitted Boundary Activity?
        </label>
        <div class="flex gap-4">
          <label class="flex items-center">
            <input
              :checked="localData.pba_approval_required === true"
              @change="updatePBARequired(true)"
              type="radio"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span class="ml-2 text-sm text-gray-700">Yes</span>
          </label>
          <label class="flex items-center">
            <input
              :checked="localData.pba_approval_required === false"
              @change="updatePBARequired(false)"
              type="radio"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span class="ml-2 text-sm text-gray-700">No</span>
          </label>
        </div>
      </div>

      <!-- PBA Details -->
      <div v-if="localData.pba_approval_required" class="space-y-4 border-t border-gray-200 pt-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">PBA Status</label>
          <select
            :value="localData.pba_status"
            @change="updateField('pba_status', $event.target.value)"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select status</option>
            <option value="Approval sought but not obtained">Approval sought but not obtained</option>
            <option value="Approval obtained from some neighbors">Approval obtained from some neighbors</option>
            <option value="Approval obtained from all neighbors">Approval obtained from all neighbors</option>
            <option value="Approval not sought">Approval not sought</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">PBA Details</label>
          <textarea
            :value="localData.pba_details"
            @input="updateField('pba_details', $event.target.value)"
            rows="3"
            placeholder="Describe the boundary activity, which neighbors were approached, and the outcome..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
        </div>

        <!-- PBA Affected Neighbors -->
        <div class="border-t border-gray-200 pt-4">
          <div class="flex justify-between items-center mb-3">
            <label class="block text-sm font-medium text-gray-700">
              Neighbors Affected by Boundary Activity
            </label>
            <button
              @click="openModal"
              type="button"
              class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Add Neighbor
            </button>
          </div>

          <!-- PBA Contacts List -->
          <div v-if="localData.pba_contacts && localData.pba_contacts.length > 0" class="space-y-2">
            <div
              v-for="(contact, index) in localData.pba_contacts"
              :key="index"
              class="border border-gray-200 rounded-lg p-3 bg-gray-50 flex justify-between items-start"
            >
              <div class="flex-1">
                <div class="font-medium text-gray-900">{{ contact.organisation_name || contact.contact_name }}</div>
                <div class="text-sm text-gray-600 mt-1">
                  {{ contact.contact_name }}
                  <span v-if="contact.email"> • {{ contact.email }}</span>
                  <span v-if="contact.phone"> • {{ contact.phone }}</span>
                </div>
                <div v-if="contact.address" class="text-xs text-gray-500 mt-1">
                  {{ [contact.address, contact.rd_number, contact.suburb, contact.city, contact.postcode].filter(Boolean).join(', ') }}
                </div>
              </div>
              <div class="flex gap-2">
                <button
                  @click="editContact(index)"
                  type="button"
                  class="text-blue-600 hover:text-blue-800 p-1"
                  title="Edit"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  @click="removeContact(index)"
                  type="button"
                  class="text-red-600 hover:text-red-800 p-1"
                  title="Remove"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
            <p class="text-sm text-gray-500">No neighbors added yet</p>
          </div>
        </div>

        <!-- PBA Document Upload -->
        <div class="border-t border-gray-200 pt-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Upload PBA Documents (if applicable)
          </label>
          <input
            type="file"
            @change="handleDocumentUpload"
            accept=".pdf,.doc,.docx"
            multiple
            class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
          />
          <p v-if="localData.pba_documents && localData.pba_documents.length > 0" class="text-xs text-green-600 mt-1">
            ✓ {{ localData.pba_documents.length }} document(s) uploaded
          </p>
          <p class="mt-1 text-xs text-gray-500">Upload PBA forms, neighbor correspondence, or written approvals (PDF or Word)</p>
        </div>
      </div>
    </div>

    <!-- PBA Contact Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeModal"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingIndex !== null ? 'Edit' : 'Add' }} PBA Neighbor Contact
            </h3>
            <button @click="closeModal" type="button" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="px-6 py-4 space-y-4">
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Organisation Name</label>
                <input v-model="form.organisation_name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Contact Name *</label>
                <input v-model="form.contact_name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input v-model="form.email" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                <input v-model="form.phone" type="tel" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Street Address</label>
              <input v-model="form.address" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>

            <div class="grid md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">RD Number</label>
                <input v-model="form.rd_number" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Suburb</label>
                <input v-model="form.suburb" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">City</label>
                <input v-model="form.city" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Postcode</label>
              <input v-model="form.postcode" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>

          <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
            <button @click="closeModal" type="button" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100">
              Cancel
            </button>
            <button @click="saveContact" type="button" :disabled="!form.contact_name" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {{ editingIndex !== null ? 'Update' : 'Add' }} Contact
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from "vue"
import InfoBox from "../shared/InfoBox.vue"

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

const showModal = ref(false)
const editingIndex = ref(null)
const form = reactive({
	organisation_name: "",
	contact_name: "",
	email: "",
	phone: "",
	address: "",
	rd_number: "",
	suburb: "",
	city: "",
	postcode: "",
})

const updatePBARequired = (value) => {
	const updated = { ...props.modelValue, pba_approval_required: value }
	emit("update:modelValue", updated)
}

const updateField = (field, value) => {
	const updated = { ...props.modelValue, [field]: value }
	emit("update:modelValue", updated)
}

const resetForm = () => {
	Object.assign(form, {
		organisation_name: "",
		contact_name: "",
		email: "",
		phone: "",
		address: "",
		rd_number: "",
		suburb: "",
		city: "",
		postcode: "",
	})
}

const openModal = () => {
	editingIndex.value = null
	resetForm()
	showModal.value = true
}

const editContact = (index) => {
	editingIndex.value = index
	Object.assign(form, localData.value.pba_contacts[index])
	showModal.value = true
}

const removeContact = (index) => {
	if (confirm("Remove this PBA contact?")) {
		const updated = { ...props.modelValue }
		updated.pba_contacts.splice(index, 1)
		emit("update:modelValue", updated)
	}
}

const saveContact = () => {
	if (!form.contact_name) return

	const updated = { ...props.modelValue }
	if (!updated.pba_contacts) updated.pba_contacts = []

	const contactData = { ...form }

	if (editingIndex.value !== null) {
		updated.pba_contacts[editingIndex.value] = contactData
	} else {
		updated.pba_contacts.push(contactData)
	}

	emit("update:modelValue", updated)
	closeModal()
}

const closeModal = () => {
	showModal.value = false
	editingIndex.value = null
	resetForm()
}

const handleDocumentUpload = (event) => {
	const files = Array.from(event.target.files)
	if (files.length > 0) {
		const updated = { ...props.modelValue }
		if (!updated.pba_documents) updated.pba_documents = []

		files.forEach((file) => {
			const maxSize = 10 * 1024 * 1024
			if (file.size > maxSize) {
				alert(`File ${file.name} exceeds 10MB. Please upload a smaller file.`)
				return
			}
			updated.pba_documents.push(file.name)
		})

		emit("update:modelValue", updated)
	}
}
</script>
