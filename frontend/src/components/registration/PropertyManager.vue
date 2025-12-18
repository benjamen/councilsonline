<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Add Your Properties</h2>
    <p class="text-gray-600 mb-6">Save time on future applications</p>

    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <p class="text-sm text-blue-800">
        ℹ️ Add properties you own or manage. These will auto-fill in your applications.
      </p>
    </div>

    <!-- Properties List -->
    <div v-if="localProperties.length > 0" class="space-y-4 mb-6">
      <div
        v-for="(property, index) in localProperties"
        :key="index"
        class="border-2 rounded-lg p-4"
        :class="property.is_default ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center space-x-2">
              <h4 class="font-medium text-gray-900">{{ property.address.street || 'Property ' + (index + 1) }}</h4>
              <span v-if="property.is_default" class="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">
                Default
              </span>
            </div>
            <p class="text-sm text-gray-600 mt-1">
              {{ property.address.suburb }}, {{ property.address.city }}
              {{ property.address.postcode }}
            </p>
            <p v-if="property.legal_description" class="text-sm text-gray-500 mt-1">
              {{ property.legal_description }}
            </p>
            <p class="text-sm text-gray-500 mt-1">
              {{ property.ownership_status }}
            </p>
          </div>
          <div class="flex space-x-2">
            <button
              type="button"
              @click="editProperty(index)"
              class="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Edit
            </button>
            <button
              type="button"
              @click="removeProperty(index)"
              class="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Property Form/Modal -->
    <div v-if="showPropertyForm" class="border-2 border-blue-300 rounded-lg p-6 mb-6 bg-white">
      <h3 class="font-medium text-gray-900 mb-4">
        {{ editingIndex !== null ? 'Edit Property' : 'Add New Property' }}
      </h3>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Property Address *</label>
          <input
            v-model="propertyForm.address.street"
            type="text"
            placeholder="123 Main Street"
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Suburb</label>
            <input
              v-model="propertyForm.address.suburb"
              type="text"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">City</label>
            <input
              v-model="propertyForm.address.city"
              type="text"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Postcode</label>
          <input
            v-model="propertyForm.address.postcode"
            type="text"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Legal Description / Certificate of Title</label>
          <input
            v-model="propertyForm.legal_description"
            type="text"
            placeholder="e.g., Lot 5 DP 12345, CT 123/456"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">My Ownership Status *</label>
          <select
            v-model="propertyForm.ownership_status"
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select...</option>
            <option value="Sole Owner">Sole Owner</option>
            <option value="Joint Owner">Joint Owner</option>
            <option value="Trustee">Trustee</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <label class="flex items-center">
          <input
            v-model="propertyForm.is_default"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <span class="ml-2 text-sm text-gray-700">
            Set as default property for applications
          </span>
        </label>

        <div class="flex space-x-4">
          <button
            type="button"
            @click="cancelPropertyForm"
            class="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="saveProperty"
            :disabled="!canSaveProperty"
            class="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ editingIndex !== null ? 'Update Property' : 'Add Property' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Property Button -->
    <button
      v-if="!showPropertyForm"
      type="button"
      @click="showPropertyForm = true"
      class="w-full py-3 px-4 border-2 border-dashed border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:border-blue-500 hover:text-blue-500 transition"
    >
      + Add Property
    </button>

    <p class="mt-4 text-sm text-gray-500 text-center">
      You can add more properties later in your profile settings
    </p>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Array,
		default: () => [],
	},
})

const emit = defineEmits(["update:modelValue"])

const localProperties = ref([...props.modelValue])
const showPropertyForm = ref(false)
const editingIndex = ref(null)

const propertyForm = ref({
	address: {
		street: "",
		suburb: "",
		city: "",
		postcode: "",
	},
	legal_description: "",
	ownership_status: "",
	is_default: false,
})

const canSaveProperty = computed(() => {
	return (
		propertyForm.value.address.street && propertyForm.value.ownership_status
	)
})

const saveProperty = () => {
	if (!canSaveProperty.value) return

	const newProperty = { ...propertyForm.value }

	// If setting as default, unset other defaults
	if (newProperty.is_default) {
		localProperties.value.forEach((p) => (p.is_default = false))
	}

	if (editingIndex.value !== null) {
		localProperties.value[editingIndex.value] = newProperty
		editingIndex.value = null
	} else {
		// If this is the first property, make it default
		if (localProperties.value.length === 0) {
			newProperty.is_default = true
		}
		localProperties.value.push(newProperty)
	}

	emit("update:modelValue", localProperties.value)
	cancelPropertyForm()
}

const editProperty = (index) => {
	editingIndex.value = index
	propertyForm.value = { ...localProperties.value[index] }
	showPropertyForm.value = true
}

const removeProperty = (index) => {
	if (confirm("Are you sure you want to remove this property?")) {
		localProperties.value.splice(index, 1)

		// If we removed the default, make the first one default
		if (
			localProperties.value.length > 0 &&
			!localProperties.value.some((p) => p.is_default)
		) {
			localProperties.value[0].is_default = true
		}

		emit("update:modelValue", localProperties.value)
	}
}

const cancelPropertyForm = () => {
	showPropertyForm.value = false
	editingIndex.value = null
	propertyForm.value = {
		address: {
			street: "",
			suburb: "",
			city: "",
			postcode: "",
		},
		legal_description: "",
		ownership_status: "",
		is_default: false,
	}
}

watch(
	() => props.modelValue,
	(newVal) => {
		localProperties.value = [...newVal]
	},
	{ deep: true },
)
</script>
