<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">
      {{ agentType === 'Company' ? 'Company Details' : 'Business Details' }}
    </h2>

    <div v-if="agentType === 'Company'" class="space-y-4">
      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label for="company_name" class="block text-sm font-medium text-gray-700 mb-2">
            Company Name <span class="text-red-500">*</span>
          </label>
          <Input
            id="company_name"
            :modelValue="companyName"
            @update:modelValue="$emit('update:companyName', $event)"
            type="text"
            :required="agentType === 'Company'"
            placeholder="ABC Planning Consultants Ltd"
            class="w-full"
          />
        </div>
        <div>
          <label for="company_number" class="block text-sm font-medium text-gray-700 mb-2">
            Company Number (Optional)
          </label>
          <Input
            id="company_number"
            :modelValue="companyNumber"
            @update:modelValue="$emit('update:companyNumber', $event)"
            type="text"
            placeholder="1234567"
            class="w-full"
          />
        </div>
      </div>

      <div>
        <label for="nzbn" class="block text-sm font-medium text-gray-700 mb-2">
          NZBN (Optional)
        </label>
        <Input
          id="nzbn"
          :modelValue="nzbn"
          @update:modelValue="$emit('update:nzbn', $event)"
          type="text"
          maxlength="13"
          placeholder="1234567890123"
          class="w-full"
          @blur="$emit('validate-nzbn')"
        />
        <p v-if="nzbnError" class="mt-1 text-xs text-red-600">{{ nzbnError }}</p>
        <p v-else class="mt-1 text-xs text-gray-500">New Zealand Business Number (13 digits)</p>
      </div>
    </div>

    <div v-else>
      <div>
        <label for="trading_name" class="block text-sm font-medium text-gray-700 mb-2">
          Trading Name (Optional)
        </label>
        <Input
          id="trading_name"
          :modelValue="tradingName"
          @update:modelValue="$emit('update:tradingName', $event)"
          type="text"
          placeholder="e.g., Smith Planning Services"
          class="w-full"
        />
        <p class="mt-1 text-xs text-gray-500">If you trade under a business name</p>
      </div>
    </div>

    <!-- Business Address -->
    <div>
      <AddressLookup
        :modelValue="selectedBusinessAddress"
        id="business_address"
        label="Business Address"
        placeholder="Start typing your business address..."
        description="Your business/office address"
        :required="false"
        @address-selected="$emit('business-address-selected', $event)"
      />
    </div>

    <!-- Properties Section -->
    <div class="space-y-4 mt-6">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-sm font-medium text-gray-900">Properties</h3>
          <p class="text-xs text-gray-500 mt-1">Add properties you own or manage (optional)</p>
        </div>
        <button
          type="button"
          @click="$emit('open-add-property')"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Property
        </button>
      </div>

      <!-- Properties List -->
      <div v-if="properties.length > 0" class="space-y-2">
        <div
          v-for="(property, index) in properties"
          :key="index"
          class="border border-gray-200 rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <h4 class="text-sm font-semibold text-gray-900">{{ property.property_name }}</h4>
                <span v-if="property.is_default" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  Default
                </span>
              </div>
              <p class="text-sm text-gray-600 mt-1">{{ property.street }}</p>
              <p class="text-xs text-gray-500">{{ property.suburb }}{{ property.suburb && property.city ? ', ' : '' }}{{ property.city }} {{ property.postcode }}</p>
            </div>
            <div class="flex items-center gap-2 ml-4">
              <button
                v-if="!property.is_default && properties.length > 1"
                type="button"
                @click="$emit('set-default-property', index)"
                class="text-xs text-blue-600 hover:text-blue-800"
              >
                Set as Default
              </button>
              <button
                type="button"
                @click="$emit('remove-property', index)"
                class="text-red-600 hover:text-red-800"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-6 border-2 border-dashed border-gray-300 rounded-lg">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <p class="mt-2 text-sm text-gray-500">No properties added yet</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Input } from "frappe-ui"
import AddressLookup from "../AddressLookup.vue"

const props = defineProps({
	agentType: {
		type: String,
		required: true,
	},
	companyName: {
		type: String,
		default: "",
	},
	companyNumber: {
		type: String,
		default: "",
	},
	nzbn: {
		type: String,
		default: "",
	},
	tradingName: {
		type: String,
		default: "",
	},
	selectedBusinessAddress: {
		type: Object,
		default: null,
	},
	properties: {
		type: Array,
		default: () => [],
	},
	nzbnError: {
		type: String,
		default: "",
	},
})

defineEmits([
	"update:companyName",
	"update:companyNumber",
	"update:nzbn",
	"update:tradingName",
	"validate-nzbn",
	"business-address-selected",
	"open-add-property",
	"remove-property",
	"set-default-property",
])
</script>
