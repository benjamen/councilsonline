<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Property Details</h2>
    <p class="text-gray-600 mb-8">Add all properties affected by this application</p>

    <div class="space-y-6">
      <!-- Add Property Button -->
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-base font-semibold text-gray-900">Properties</h3>
        <button
          @click="openPropertyModal()"
          type="button"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Property
        </button>
      </div>

      <!-- Properties List -->
      <div v-if="localData.properties && localData.properties.length > 0" class="space-y-3">
        <div
          v-for="(property, index) in localData.properties"
          :key="index"
          class="flex items-start justify-between p-4 border border-gray-200 rounded-lg bg-white"
        >
          <div class="flex-1">
            <div class="font-medium text-gray-900">{{ property.property_address }}</div>
            <p v-if="property.legal_description" class="text-sm text-gray-600 mt-1">
              Legal: {{ property.legal_description }}
            </p>
            <div class="flex gap-4 mt-2 text-xs text-gray-500">
              <span v-if="property.ct_reference">Title: {{ property.ct_reference }}</span>
              <span v-if="property.valuation_reference">Val Ref: {{ property.valuation_reference }}</span>
              <span v-if="property.zone" class="px-2 py-1 bg-gray-100 rounded">{{ property.zone }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-4">
            <button
              @click="openPropertyModal(index)"
              type="button"
              class="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
              title="Edit"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              @click="removeProperty(index)"
              type="button"
              class="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
              title="Remove"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
        <svg class="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <p class="text-sm text-gray-600">No properties added yet</p>
        <p class="text-xs text-gray-500 mt-1">Click "Add Property" to add properties to this application</p>
      </div>
    </div>

    <!-- Property Modal -->
    <div v-if="showPropertyModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingPropertyIndex !== null ? 'Edit Property' : 'Add Property' }}
            </h3>
            <button @click="closePropertyModal" type="button" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="px-6 py-4 space-y-6">
          <!-- Property Address Search -->
          <div class="relative">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search Property Address *</label>
            <input
              v-model="propertySearchQuery"
              @input="handlePropertySearch"
              @focus="showPropertyDropdown = true"
              type="text"
              placeholder="Start typing address... e.g., 123 Main Street"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              autocomplete="off"
            />
            <p class="mt-1 text-xs text-gray-500">Type to search LINZ property database</p>

            <!-- Search Results Dropdown -->
            <div
              v-if="showPropertyDropdown && (propertySearchResults.length > 0 || propertySearchLoading)"
              class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto"
            >
              <div v-if="propertySearchLoading" class="p-4 text-center text-gray-500">
                <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mb-2"></div>
                <p class="text-sm">Searching properties...</p>
              </div>

              <div v-else>
                <button
                  v-for="(result, index) in propertySearchResults"
                  :key="index"
                  @click="selectPropertyFromSearch(result)"
                  type="button"
                  class="w-full text-left px-4 py-3 hover:bg-blue-50 border-b border-gray-100 last:border-b-0 transition-colors"
                >
                  <div class="font-medium text-gray-900">{{ result.address }}</div>
                  <div class="text-sm text-gray-600 mt-1">{{ result.property?.legal_description || 'Legal description not available' }}</div>
                  <div v-if="result.property?.title_no" class="text-xs text-gray-500 mt-1">
                    Title: {{ result.property.title_no }}
                  </div>
                </button>
              </div>

              <div v-if="!propertySearchLoading && propertySearchResults.length === 0 && propertySearchQuery.length >= 3" class="p-4 text-center text-gray-500">
                <p class="text-sm">No properties found. Try a different search.</p>
              </div>
            </div>
          </div>

          <!-- Selected Property Details -->
          <div v-if="currentProperty.property_address" class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <div class="flex-1">
                <p class="text-sm font-medium text-green-900">Property Selected</p>
                <p class="text-sm text-green-700 mt-1">{{ currentProperty.property_address }}</p>
              </div>
              <button
                @click="clearCurrentProperty"
                type="button"
                class="text-green-600 hover:text-green-700"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Property Details (Read-only after selection) -->
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Legal Description</label>
              <input
                v-model="currentProperty.legal_description"
                type="text"
                readonly
                class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Certificate of Title Reference</label>
              <input
                v-model="currentProperty.ct_reference"
                type="text"
                readonly
                class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Valuation Reference</label>
              <input
                v-model="currentProperty.valuation_reference"
                type="text"
                readonly
                class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Zone</label>
              <input
                v-model="currentProperty.zone"
                type="text"
                readonly
                class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            @click="closePropertyModal"
            type="button"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="saveProperty"
            type="button"
            :disabled="!currentProperty.property_address"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {{ editingPropertyIndex !== null ? 'Update Property' : 'Add Property' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import { defineEmits, defineProps, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
	properties: {
		type: Object,
		default: () => ({ data: [], loading: false }),
	},
})

const emit = defineEmits(["update:modelValue", "property-select"])

// Local data
const localData = ref({
	properties: props.modelValue.properties || [],
})

// Modal state
const showPropertyModal = ref(false)
const editingPropertyIndex = ref(null)
const currentProperty = ref({
	property_address: "",
	legal_description: "",
	ct_reference: "",
	valuation_reference: "",
	parcel_id: "",
	zone: "",
})

// Property search state
const propertySearchQuery = ref("")
const propertySearchResults = ref([])
const propertySearchLoading = ref(false)
const showPropertyDropdown = ref(false)
let searchTimeout = null

// Watch for external changes
watch(
	() => props.modelValue,
	(newVal) => {
		localData.value.properties = newVal.properties || []
	},
	{ deep: true },
)

// Watch local changes and emit
watch(
	localData,
	(newVal) => {
		emit("update:modelValue", {
			...props.modelValue,
			properties: newVal.properties,
		})
	},
	{ deep: true },
)

// Property search
const handlePropertySearch = async () => {
	if (searchTimeout) {
		clearTimeout(searchTimeout)
	}

	const query = propertySearchQuery.value.trim()
	if (query.length < 3) {
		propertySearchResults.value = []
		return
	}

	searchTimeout = setTimeout(async () => {
		propertySearchLoading.value = true
		try {
			const results = await call("councilsonline.api.search_property_addresses", {
				query: query,
			})
			propertySearchResults.value = results || []
		} catch (error) {
			console.error("[Step5PropertyDetails] Error searching properties:", error)
			propertySearchResults.value = []
		} finally {
			propertySearchLoading.value = false
		}
	}, 300)
}

// Select property from search results
const selectPropertyFromSearch = (result) => {
	currentProperty.value = {
		property_address: result.address,
		legal_description: result.property?.legal_description || "",
		ct_reference: result.property?.title_no || "",
		valuation_reference: result.property?.valuation_reference || "",
		parcel_id: result.property?.parcel_id || "",
		zone: result.property?.zone || "",
	}

	showPropertyDropdown.value = false
	propertySearchQuery.value = ""
	propertySearchResults.value = []
}

// Clear current property
const clearCurrentProperty = () => {
	currentProperty.value = {
		property_address: "",
		legal_description: "",
		ct_reference: "",
		valuation_reference: "",
		parcel_id: "",
		zone: "",
	}
	propertySearchQuery.value = ""
}

// Open property modal
const openPropertyModal = (index = null) => {
	editingPropertyIndex.value = index
	if (index !== null) {
		currentProperty.value = { ...localData.value.properties[index] }
	} else {
		clearCurrentProperty()
	}
	showPropertyModal.value = true
}

// Close property modal
const closePropertyModal = () => {
	showPropertyModal.value = false
	editingPropertyIndex.value = null
	clearCurrentProperty()
}

// Save property
const saveProperty = () => {
	if (!currentProperty.value.property_address) {
		return
	}

	if (!localData.value.properties) {
		localData.value.properties = []
	}

	if (editingPropertyIndex.value !== null) {
		localData.value.properties[editingPropertyIndex.value] = {
			...currentProperty.value,
		}
	} else {
		localData.value.properties.push({ ...currentProperty.value })
	}

	closePropertyModal()
}

// Remove property
const removeProperty = (index) => {
	if (confirm("Remove this property from the application?")) {
		localData.value.properties.splice(index, 1)
	}
}
</script>
