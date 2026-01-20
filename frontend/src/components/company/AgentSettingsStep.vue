<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">Default Settings</h2>

    <!-- Single-tenant: No council selection needed -->

    <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h3 class="text-sm font-medium text-blue-900 mb-2">Agent Permissions</h3>
      <ul class="text-sm text-blue-800 space-y-1">
        <li class="flex items-start">
          <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Create and submit applications on behalf of clients
        </li>
        <li class="flex items-start">
          <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Manage multiple client applications
        </li>
        <li class="flex items-start">
          <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Receive notifications on application progress
        </li>
        <li class="flex items-start">
          <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Professional dashboard for tracking all applications
        </li>
      </ul>
    </div>

    <!-- Terms and Conditions -->
    <div class="flex items-start">
      <input
        id="terms"
        :checked="terms"
        @change="$emit('update:terms', $event.target.checked)"
        type="checkbox"
        required
        class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
      />
      <label for="terms" class="ml-2 block text-sm text-gray-700">
        I agree to the
        <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Terms of Service</a>
        and
        <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Privacy Policy</a>
      </label>
    </div>
  </div>
</template>

<script setup>
defineProps({
	terms: {
		type: Boolean,
		default: false,
	},
})

defineEmits(["update:terms"])
</script>
