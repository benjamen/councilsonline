<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="$emit('close')"></div>

      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add Property</h3>

          <div class="space-y-4">
            <div>
              <label for="property_name_agent" class="block text-sm font-medium text-gray-700 mb-2">
                Property Name <span class="text-red-500">*</span>
              </label>
              <input
                id="property_name_agent"
                :value="propertyName"
                @input="$emit('update:propertyName', $event.target.value)"
                type="text"
                required
                placeholder="e.g., Office, Client Property A, Development Site"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <AddressLookup
                :modelValue="selectedPropertyAddress"
                id="property_address_modal_agent"
                label="Property Address"
                placeholder="Start typing the property address..."
                description="Search for the property address in New Zealand"
                :required="true"
                @address-selected="$emit('property-address-selected', $event)"
              />
            </div>

            <div>
              <label class="flex items-center">
                <input
                  :checked="isDefault"
                  @change="$emit('update:isDefault', $event.target.checked)"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700">Set as default property</span>
              </label>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-2">
          <button
            type="button"
            @click="$emit('add-property')"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
          >
            Add Property
          </button>
          <button
            type="button"
            @click="$emit('close')"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AddressLookup from "../AddressLookup.vue"

defineProps({
  show: {
    type: Boolean,
    required: true
  },
  propertyName: {
    type: String,
    default: ""
  },
  selectedPropertyAddress: {
    type: Object,
    default: null
  },
  isDefault: {
    type: Boolean,
    default: false
  }
})

defineEmits([
  'close',
  'update:propertyName',
  'update:isDefault',
  'property-address-selected',
  'add-property'
])
</script>
