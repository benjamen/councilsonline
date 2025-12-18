<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Council Process Information</h2>
    <p class="text-gray-600 mb-6">Understanding {{ councilName }}'s process for this application</p>

    <div v-if="requestTypeDetails" class="space-y-6">

      <!-- Note: Pre-Application Meeting booking has been moved to before the application starts -->
      <!-- Users can book meetings from the request type selection page -->

      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-xl font-semibold text-gray-900">{{ requestTypeDetails.request_type_name }}</h3>
            <p v-if="requestTypeDetails.category" class="text-sm text-gray-500 mt-1">
              {{ requestTypeDetails.category }}
            </p>
          </div>
        </div>

        <div class="grid md:grid-cols-3 gap-4 mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div>
            <div class="text-xs text-blue-600 font-medium uppercase">Application Fee</div>
            <div class="text-2xl font-bold text-blue-900 mt-1">
              ${{ requestTypeDetails.base_fee || '0' }}
            </div>
            <div class="text-xs text-blue-600 mt-1">Plus any additional costs</div>
          </div>
          <div>
            <div class="text-xs text-blue-600 font-medium uppercase">Processing Time</div>
            <div class="text-2xl font-bold text-blue-900 mt-1">
              {{ requestTypeDetails.sla_days || 'N/A' }} <span class="text-base">days</span>
            </div>
            <div class="text-xs text-blue-600 mt-1">Standard timeframe</div>
          </div>
          <div>
            <div class="text-xs text-blue-600 font-medium uppercase">Payment Required</div>
            <div class="text-2xl font-bold text-blue-900 mt-1">
              {{ requestTypeDetails.requires_payment ? 'Yes' : 'No' }}
            </div>
            <div class="text-xs text-blue-600 mt-1">Before processing</div>
          </div>
        </div>
      </div>

      <div v-if="requestTypeDetails.process_description" class="bg-white border border-gray-200 rounded-lg p-6">
        <h4 class="text-lg font-semibold text-gray-900 mb-4">How This Works</h4>
        <div class="prose prose-sm max-w-none text-gray-700" v-html="requestTypeDetails.process_description"></div>
      </div>

      <div v-else-if="requestTypeDetails.description" class="bg-white border border-gray-200 rounded-lg p-6">
        <h4 class="text-lg font-semibold text-gray-900 mb-4">About This Application</h4>
        <div class="prose prose-sm max-w-none text-gray-700" v-html="requestTypeDetails.description"></div>
      </div>

      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Before You Continue</h5>
            <p class="text-yellow-800 text-sm mt-1">
              Please review this information carefully. Make sure you understand the process, fees, and timeframes before proceeding with your application.
            </p>
          </div>
        </div>
      </div>

      <div class="flex justify-center pt-4">
        <button
          type="button"
          @click="handleContinue"
          class="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          I Understand - Continue to Application
        </button>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-500">No request type selected. Please go back and select a request type.</p>
    </div>
  </div>
</template>

<script setup>
import { session } from "@/data/session"
import { defineEmits, defineProps } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const props = defineProps({
	requestTypeDetails: {
		type: Object,
		default: null,
	},
	councilName: {
		type: String,
		default: "",
	},
	modelValue: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(["continue", "update:modelValue"])

const handleContinue = () => {
	// Check if user is logged in before allowing them to continue
	if (!session.isLoggedIn) {
		// Save current URL to redirect back after login
		const currentPath = window.location.pathname + window.location.search
		router.push({
			name: "Login",
			query: { redirect: currentPath },
		})
		return
	}

	// User is logged in, proceed normally
	emit("continue")
}
</script>
