<template>
  <div class="space-y-4">
    <!-- Country Selector -->
    <div v-if="showCountrySelector">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Country
        <span class="text-red-500">*</span>
      </label>
      <select
        v-model="selectedCountry"
        @change="handleCountryChange"
        class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">Select Country</option>
        <option value="NZ">New Zealand</option>
        <option value="AU">Australia</option>
        <option value="PH">Philippines</option>
      </select>
    </div>

    <!-- Address Lookup -->
    <div v-if="selectedCountry" class="relative">
      <label v-if="label" class="block text-sm font-medium text-gray-700 mb-2">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>

      <!-- Search Input -->
      <div class="relative">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          @focus="showDropdown = true"
          @blur="handleBlur"
          type="text"
          :placeholder="getPlaceholder()"
          :required="required"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          :class="{'pr-10': loading}"
          autocomplete="off"
        />
        <div v-if="loading" class="absolute right-3 top-1/2 -translate-y-1/2">
          <svg class="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      </div>

      <p class="mt-1 text-xs text-gray-500">{{ getDescription() }}</p>

      <!-- Validation Error -->
      <p v-if="validationError" class="mt-1 text-xs text-red-600">{{ validationError }}</p>

      <!-- Search Results Dropdown -->
      <div
        v-if="showDropdown && (searchResults.length > 0 || loading)"
        class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto"
      >
        <div v-if="loading" class="p-4 text-center text-gray-500">
          <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mb-2"></div>
          <p class="text-sm">Searching {{ getCountryName() }} addresses...</p>
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
            <div v-if="result.suburb || result.city" class="text-sm text-gray-600 mt-1">
              <span v-if="result.suburb">{{ result.suburb }}, </span>
              <span>{{ result.city }}</span>
              <span v-if="result.state"> {{ result.state }}</span>
            </div>
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
            <div class="text-xs text-green-600 mt-1">
              <span v-if="selectedAddress.suburb">{{ selectedAddress.suburb }}, </span>
              <span>{{ selectedAddress.city }}</span>
              <span v-if="selectedAddress.state">, {{ selectedAddress.state }}</span>
              <span v-if="selectedAddress.postcode"> {{ selectedAddress.postcode }}</span>
              <span v-if="selectedAddress.country"> - {{ selectedAddress.country }}</span>
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
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import { onMounted, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		default: null,
	},
	label: {
		type: String,
		default: "Address",
	},
	required: {
		type: Boolean,
		default: false,
	},
	country: {
		type: String,
		default: "", // If provided, locks to that country; otherwise shows selector
	},
	showCountrySelector: {
		type: Boolean,
		default: true,
	},
})

const emit = defineEmits([
	"update:modelValue",
	"address-selected",
	"country-changed",
])

const selectedCountry = ref(props.country || "")
const searchQuery = ref("")
const searchResults = ref([])
const loading = ref(false)
const showDropdown = ref(false)
const selectedAddress = ref(props.modelValue)
const validationError = ref("")
let searchTimeout = null

onMounted(() => {
	if (props.modelValue) {
		selectedAddress.value = props.modelValue
		searchQuery.value = props.modelValue.full_address || ""
		selectedCountry.value = props.modelValue.country || props.country || ""
	}
})

watch(
	() => props.modelValue,
	(newVal) => {
		selectedAddress.value = newVal
		if (newVal) {
			searchQuery.value = newVal.full_address || ""
			selectedCountry.value = newVal.country || selectedCountry.value
		}
	},
)

watch(
	() => props.country,
	(newVal) => {
		if (newVal && newVal !== selectedCountry.value) {
			selectedCountry.value = newVal
		}
	},
)

function getCountryName() {
	const names = {
		NZ: "New Zealand",
		AU: "Australia",
		PH: "Philippines",
	}
	return names[selectedCountry.value] || selectedCountry.value
}

function getPlaceholder() {
	const placeholders = {
		NZ: "Start typing address... e.g., 123 Main Street, Lower Hutt",
		AU: "Start typing address... e.g., 45 Collins Street, Melbourne",
		PH: "Start typing address... e.g., 123 Rizal Avenue, Manila",
	}
	return placeholders[selectedCountry.value] || "Start typing address..."
}

function getDescription() {
	const descriptions = {
		NZ: "Type to search for addresses in New Zealand (powered by LINZ)",
		AU: "Type to search for addresses in Australia",
		PH: "Type to search for addresses in Philippines",
	}
	return descriptions[selectedCountry.value] || "Type to search for addresses"
}

function handleCountryChange() {
	clearAddress()
	emit("country-changed", selectedCountry.value)
}

async function handleSearch() {
	if (searchTimeout) {
		clearTimeout(searchTimeout)
	}

	const query = searchQuery.value.trim()
	validationError.value = ""

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
			const results = await searchAddresses(query, selectedCountry.value)
			searchResults.value = results || []
		} catch (error) {
			console.error("[UniversalAddressLookup] Error:", error)
			searchResults.value = []
			validationError.value = "Error searching addresses. Please try again."
		} finally {
			loading.value = false
		}
	}, 300)
}

async function searchAddresses(query, country) {
	try {
		// Call unified backend API that routes to appropriate service
		const results = await call("councilsonline.api.search_addresses_universal", {
			query: query,
			country: country,
		})

		return (results || []).map((result) => ({
			...result,
			country: country,
			full_address: result.address || result.full_address,
			street_address:
				result.street_address ||
				result.street ||
				extractStreet(result.address || result.full_address),
			suburb: result.suburb || result.locality || result.barangay,
			city: result.city || result.town || result.municipality,
			state: result.state || result.province,
			postcode: result.postcode || result.postal_code || result.zip_code,
			address_id: result.address_id || result.id,
		}))
	} catch (error) {
		console.error("[UniversalAddressLookup] API error:", error)
		return []
	}
}

function extractStreet(fullAddress) {
	if (!fullAddress) return ""
	return fullAddress.split(",")[0]?.trim() || fullAddress
}

function selectAddress(address) {
	selectedAddress.value = { ...address, country: selectedCountry.value }
	searchQuery.value = address.full_address
	searchResults.value = []
	showDropdown.value = false
	validationError.value = ""

	emit("update:modelValue", selectedAddress.value)
	emit("address-selected", selectedAddress.value)
}

function clearAddress() {
	selectedAddress.value = null
	searchQuery.value = ""
	searchResults.value = []
	validationError.value = ""

	emit("update:modelValue", null)
	emit("address-selected", null)
}

function handleBlur() {
	setTimeout(() => {
		showDropdown.value = false
	}, 200)
}

defineExpose({
	clearAddress,
	selectedAddress,
	selectedCountry,
})
</script>
