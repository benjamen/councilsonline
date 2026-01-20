<template>
  <div class="lg:col-span-1">
    <!-- Basic Information -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Request Type Name</label>
          <input
            :value="requestType.name"
            @input="$emit('update-name', $event.target.value)"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., Building Consent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <select
            :value="requestType.category"
            @change="$emit('update-category', $event.target.value)"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select Category</option>
            <option value="Planning">Planning</option>
            <option value="Building">Building</option>
            <option value="Social Assistance">Social Assistance</option>
            <option value="Environmental">Environmental</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            :value="requestType.description"
            @input="$emit('update-description', $event.target.value)"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Describe this request type..."
          ></textarea>
        </div>

        <div class="flex items-center gap-4">
          <label class="flex items-center">
            <input
              :checked="requestType.collects_payment"
              @change="$emit('update-collects-payment', $event.target.checked)"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm text-gray-700">Collects Payment</span>
          </label>
          <label class="flex items-center">
            <input
              :checked="requestType.make_payment"
              @change="$emit('update-make-payment', $event.target.checked)"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm text-gray-700">Makes Payment</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Template Library -->
    <div class="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Template Library</h2>
      <div v-if="loading" class="text-center py-4 text-gray-500">Loading templates...</div>
      <div v-else-if="availableTemplates.length === 0" class="text-center py-4 text-gray-500">No templates available</div>
      <div v-else class="space-y-2">
        <button
          v-for="template in availableTemplates"
          :key="template.name"
          @click="$emit('apply-template', template.name)"
          class="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
        >
          <div class="font-medium text-gray-900">{{ template.title }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ template.description }}</div>
        </button>
      </div>
    </div>

    <!-- JSON Export -->
    <div class="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">JSON Export</h2>
      <button
        @click="$emit('toggle-json-preview')"
        class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200"
      >
        {{ showJsonPreview ? 'Hide' : 'Show' }} JSON Preview
      </button>
      <div v-if="showJsonPreview" class="mt-4">
        <textarea
          :value="jsonPreview"
          readonly
          rows="12"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-xs bg-gray-50"
        ></textarea>
        <button
          @click="$emit('copy-json')"
          class="mt-2 w-full px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
        >
          Copy to Clipboard
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
	requestType: {
		type: Object,
		required: true,
	},
	availableTemplates: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
	showJsonPreview: {
		type: Boolean,
		default: false,
	},
	jsonPreview: {
		type: String,
		default: "",
	},
})

defineEmits([
	"update-name",
	"update-category",
	"update-description",
	"update-collects-payment",
	"update-make-payment",
	"apply-template",
	"toggle-json-preview",
	"copy-json",
])
</script>
