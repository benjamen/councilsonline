<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Property Details</h2>
    <p class="text-gray-600 mb-8">Provide details about the property for this application</p>

    <div class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Select Existing Property or Enter New
        </label>
        <select
          v-model="localData.property"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          @change="handlePropertySelect"
        >
          <option value="">-- Select a property or enter new --</option>
          <option v-for="prop in properties.data" :key="prop.name" :value="prop.name">
            {{ prop.street_address }}, {{ prop.suburb }}{{ prop.legal_description ? ' - ' + prop.legal_description : '' }}
          </option>
        </select>
      </div>

      <div class="space-y-4">
        <div v-if="localData.property_address" class="relative">
          <label class="block text-sm font-medium text-gray-700 mb-2">Property Address *</label>
          <div class="flex gap-2">
            <input
              v-model="localData.property_address"
              type="text"
              readonly
              class="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-900"
            />
            <button
              @click="clearPropertyAddress"
              type="button"
              class="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 border border-blue-600 rounded-lg hover:bg-blue-50"
            >
              Change
            </button>
          </div>
          <p class="mt-1 text-xs text-green-600">✓ Address selected from LINZ database</p>
        </div>

        <div v-else class="relative">
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
                @click="selectProperty(result)"
                type="button"
                class="w-full text-left px-4 py-3 hover:bg-blue-50 border-b border-gray-100 last:border-b-0 transition-colors focus:outline-none focus:bg-blue-50"
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

        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Legal Description</label>
            <input
              v-model="localData.legal_description"
              type="text"
              placeholder="Lot 1 DP 12345"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              readonly
            />
            <p v-if="localData.legal_description" class="mt-1 text-xs text-green-600">
              ✓ Auto-populated from LINZ
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Certificate of Title</label>
            <input
              v-model="localData.ct_reference"
              type="text"
              placeholder="WN123/456"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              readonly
            />
            <p v-if="localData.ct_reference" class="mt-1 text-xs text-green-600">
              ✓ Auto-populated from LINZ
            </p>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Upload Certificate of Title (Optional)
          </label>
          <input
            type="file"
            @change="handleCTUpload"
            accept=".pdf,.jpg,.jpeg,.png"
            class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
          />
          <p v-if="localData.certificate_of_title_document" class="text-xs text-green-600 mt-1">
            ✓ Document uploaded
          </p>
          <p class="mt-1 text-xs text-gray-500">Upload a copy of the Certificate of Title if available</p>
        </div>

        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Valuation Reference</label>
            <input
              v-model="localData.valuation_reference"
              type="text"
              placeholder="Auto-populated"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              readonly
            />
            <p v-if="localData.valuation_reference" class="mt-1 text-xs text-green-600">
              ✓ Valuation Reference
            </p>
            <p v-else class="mt-1 text-xs text-gray-500">
              Will be populated when address is selected
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Parcel ID</label>
            <input
              v-model="localData.parcel_id"
              type="text"
              placeholder="Auto-populated"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              readonly
            />
            <p v-if="localData.parcel_id" class="mt-1 text-xs text-green-600">
              ✓ LINZ Parcel ID
            </p>
          </div>
        </div>

        <div class="grid md:grid-cols-1 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Zone</label>
            <input
              v-model="localData.zone"
              type="text"
              placeholder="Auto-populated from District Plan"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              readonly
            />
            <p v-if="localData.zone" class="mt-1 text-xs text-green-600">
              ✓ District Plan zone
            </p>
            <p v-else class="mt-1 text-xs text-gray-500">
              Will be populated when address is selected
            </p>
          </div>
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
		required: true,
	},
})

const emit = defineEmits(["update:modelValue", "property-select"])

// Local data
const localData = ref({
	property: props.modelValue.property || "",
	property_address: props.modelValue.property_address || "",
	legal_description: props.modelValue.legal_description || "",
	ct_reference: props.modelValue.ct_reference || "",
	certificate_of_title_document:
		props.modelValue.certificate_of_title_document || "",
	valuation_reference: props.modelValue.valuation_reference || "",
	parcel_id: props.modelValue.parcel_id || "",
	zone: props.modelValue.zone || "",
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
		localData.value.property = newVal.property || ""
		localData.value.property_address = newVal.property_address || ""
		localData.value.legal_description = newVal.legal_description || ""
		localData.value.ct_reference = newVal.ct_reference || ""
		localData.value.certificate_of_title_document =
			newVal.certificate_of_title_document || ""
		localData.value.valuation_reference = newVal.valuation_reference || ""
		localData.value.parcel_id = newVal.parcel_id || ""
		localData.value.zone = newVal.zone || ""
	},
	{ deep: true },
)

// Watch local changes and emit
watch(
	localData,
	(newVal) => {
		emit("update:modelValue", {
			...props.modelValue,
			property: newVal.property,
			property_address: newVal.property_address,
			legal_description: newVal.legal_description,
			ct_reference: newVal.ct_reference,
			certificate_of_title_document: newVal.certificate_of_title_document,
			valuation_reference: newVal.valuation_reference,
			parcel_id: newVal.parcel_id,
			zone: newVal.zone,
		})
	},
	{ deep: true },
)

// Property selection
const handlePropertySelect = () => {
	emit("property-select")
}

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
			const results = await call("lodgeick.api.search_property_addresses", {
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
const selectProperty = (result) => {
	localData.value.property_address = result.address
	localData.value.legal_description = result.property?.legal_description || ""
	localData.value.ct_reference = result.property?.title_no || ""
	localData.value.valuation_reference =
		result.property?.valuation_reference || ""
	localData.value.parcel_id = result.property?.parcel_id || ""
	localData.value.zone = result.property?.zone || ""

	showPropertyDropdown.value = false
	propertySearchQuery.value = ""
	propertySearchResults.value = []
}

// Clear property address
const clearPropertyAddress = () => {
	localData.value.property = ""
	localData.value.property_address = ""
	localData.value.legal_description = ""
	localData.value.ct_reference = ""
	localData.value.valuation_reference = ""
	localData.value.parcel_id = ""
	localData.value.zone = ""
	propertySearchQuery.value = ""
}

// Handle CT upload
const handleCTUpload = (event) => {
	const file = event.target.files[0]
	if (file) {
		// File upload will be handled by the parent component
		emit("update:modelValue", {
			...props.modelValue,
			certificate_of_title_document: file.name,
		})
	}
}
</script>
