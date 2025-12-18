<template>
  <div class="relative">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Search Input -->
    <div class="relative">
      <input
        :id="id"
        v-model="searchQuery"
        @input="handleSearch"
        @focus="showDropdown = true"
        @blur="handleBlur"
        type="text"
        :placeholder="placeholder"
        :required="required"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        autocomplete="off"
      />
      <div v-if="loading" class="absolute right-3 top-1/2 -translate-y-1/2">
        <svg class="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    </div>

    <p v-if="description" class="mt-1 text-xs text-gray-500">{{ description }}</p>

    <!-- Validation Error -->
    <p v-if="validationError" class="mt-1 text-xs text-red-600">{{ validationError }}</p>

    <!-- Search Results Dropdown -->
    <div
      v-if="showDropdown && (searchResults.length > 0 || loading)"
      class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto"
    >
      <div v-if="loading" class="p-4 text-center text-gray-500">
        <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mb-2"></div>
        <p class="text-sm">Searching addresses...</p>
      </div>

      <div v-else>
        <button
          v-for="(result, index) in searchResults"
          :key="index"
          @mousedown.prevent="selectAddress(result)"
          type="button"
          class="w-full text-left px-4 py-3 hover:bg-blue-50 border-b border-gray-100 last:border-b-0 transition-colors"
        >
          <div class="font-medium text-gray-900">{{ result.full_address }}</div>
          <div v-if="result.suburb" class="text-sm text-gray-600 mt-1">{{ result.suburb }}, {{ result.city }}</div>
          <div v-if="result.address_id" class="text-xs text-gray-500 mt-1">
            ID: {{ result.address_id }}
          </div>
        </button>
      </div>

      <div v-if="!loading && searchResults.length === 0 && searchQuery.length >= 3" class="p-4 text-center text-gray-500">
        <p class="text-sm">No addresses found. Try a different search.</p>
        <p class="text-xs mt-2 text-gray-400">Make sure to include street number and name</p>
      </div>
    </div>

    <!-- Selected Address Display -->
    <div v-if="selectedAddress" class="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="text-sm font-medium text-green-900">Selected Address</p>
          <p class="text-sm text-green-700 mt-1">{{ selectedAddress.full_address }}</p>
          <div v-if="selectedAddress.suburb || selectedAddress.city" class="text-xs text-green-600 mt-1">
            <span v-if="selectedAddress.suburb">{{ selectedAddress.suburb }}, </span>
            <span>{{ selectedAddress.city }}</span>
            <span v-if="selectedAddress.postcode"> {{ selectedAddress.postcode }}</span>
          </div>
        </div>
        <button
          @click="clearAddress"
          type="button"
          class="text-green-600 hover:text-green-700 ml-2"
          title="Clear selection"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import { ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		default: null,
	},
	id: {
		type: String,
		default: "address-lookup",
	},
	label: {
		type: String,
		default: "Property Address",
	},
	placeholder: {
		type: String,
		default: "Start typing address... e.g., 123 Main Street",
	},
	description: {
		type: String,
		default: "Type to search for addresses in New Zealand",
	},
	required: {
		type: Boolean,
		default: false,
	},
	apiMethod: {
		type: String,
		default: "lodgeick.api.search_property_addresses",
	},
})

const emit = defineEmits(["update:modelValue", "address-selected"])

const searchQuery = ref("")
const searchResults = ref([])
const loading = ref(false)
const showDropdown = ref(false)
const selectedAddress = ref(props.modelValue)
const validationError = ref("")
let searchTimeout = null

// Watch for external changes to modelValue
watch(
	() => props.modelValue,
	(newVal) => {
		selectedAddress.value = newVal
		if (newVal) {
			searchQuery.value = newVal.full_address || ""
		}
	},
)

// Handle search input
const handleSearch = async () => {
	if (searchTimeout) {
		clearTimeout(searchTimeout)
	}

	const query = searchQuery.value.trim()

	// Clear validation error
	validationError.value = ""

	// Clear selected address if user is typing new search
	if (selectedAddress.value && query !== selectedAddress.value.full_address) {
		selectedAddress.value = null
		emit("update:modelValue", null)
	}

	if (query.length < 3) {
		searchResults.value = []
		return
	}

	searchTimeout = setTimeout(async () => {
		loading.value = true
		try {
			// TODO: Replace with actual LINZ API integration
			// For now, we'll use the existing property search or create a stub
			const results = await searchAddresses(query)
			searchResults.value = results || []
		} catch (error) {
			console.error("[AddressLookup] Error searching addresses:", error)
			searchResults.value = []
			validationError.value = "Error searching addresses. Please try again."
		} finally {
			loading.value = false
		}
	}, 300)
}

// Search for addresses - integrates with backend API
const searchAddresses = async (query) => {
	try {
		// Call backend API that searches LINZ or property database
		const results = await call(props.apiMethod, {
			query: query,
		})

		// Transform results to standardized format
		return results.map((result) => ({
			full_address: result.address || result.full_address,
			street_address: result.street_address || extractStreet(result.address),
			suburb: result.suburb || result.locality,
			city: result.city || result.town,
			postcode: result.postcode || result.postal_code,
			address_id: result.address_id || result.id,
			// Additional property data if available
			property_id: result.property?.parcel_id,
			legal_description: result.property?.legal_description,
			title_no: result.property?.title_no,
			valuation_reference: result.property?.valuation_reference,
			zone: result.property?.zone,
		}))
	} catch (error) {
		console.error("[AddressLookup] API error:", error)
		// Return empty array or stub data for development
		return []
	}
}

// Extract street address from full address
const extractStreet = (fullAddress) => {
	if (!fullAddress) return ""
	// Simple extraction - take first part before comma
	return fullAddress.split(",")[0]?.trim() || fullAddress
}

// Select an address from search results
const selectAddress = (address) => {
	selectedAddress.value = address
	searchQuery.value = address.full_address
	searchResults.value = []
	showDropdown.value = false
	validationError.value = ""

	emit("update:modelValue", address)
	emit("address-selected", address)
}

// Clear selected address
const clearAddress = () => {
	selectedAddress.value = null
	searchQuery.value = ""
	searchResults.value = []
	validationError.value = ""

	emit("update:modelValue", null)
	emit("address-selected", null)
}

// Handle blur event (delayed to allow click on dropdown)
const handleBlur = () => {
	setTimeout(() => {
		showDropdown.value = false
	}, 200)
}

// Expose methods for parent component
defineExpose({
	clearAddress,
	selectedAddress,
})
</script>
