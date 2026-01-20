<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-sm font-medium text-gray-900">Properties</h3>
        <p class="text-xs text-gray-500 mt-1">
          {{ requesterType === 'Individual' ? 'Add your properties (at least one required)' : 'Add your properties (optional)' }}
        </p>
      </div>
      <button
        type="button"
        @click="$emit('open-add-property')"
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Address
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
              v-if="!property.is_default"
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
</template>

<script setup>
defineProps({
	requesterType: {
		type: String,
		default: "Individual",
	},
	properties: {
		type: Array,
		default: () => [],
	},
})

defineEmits(["open-add-property", "remove-property", "set-default-property"])
</script>
