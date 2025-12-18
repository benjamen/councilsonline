<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="rfq-modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="closeModal"></div>

      <!-- Center modal -->
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <!-- Header -->
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900" id="rfq-modal-title">
              Request for Quote - Agent Details
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Status Badge -->
          <div class="mb-4">
            <span :class="[
              'inline-flex px-3 py-1 text-sm font-medium rounded-full',
              rfqData.status === 'Draft' ? 'bg-gray-100 text-gray-800' :
              rfqData.status === 'Sent to Agent' ? 'bg-blue-100 text-blue-800' :
              rfqData.status === 'Quote Received' ? 'bg-yellow-100 text-yellow-800' :
              rfqData.status === 'Agent Engaged' ? 'bg-green-100 text-green-800' :
              rfqData.status === 'Cancelled' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            ]">
              {{ rfqData.status || 'Draft' }}
            </span>
          </div>

          <!-- RFQ ID and Dates -->
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label class="block text-sm font-medium text-gray-700">RFQ ID</label>
              <p class="mt-1 text-sm text-gray-900">{{ rfqData.rfq_id || 'Not assigned' }}</p>
            </div>
            <div v-if="rfqData.created_date">
              <label class="block text-sm font-medium text-gray-700">Created Date</label>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(rfqData.created_date) }}</p>
            </div>
          </div>

          <!-- RFQ Message -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              RFQ Message
              <span v-if="!rfqData.agent_engaged" class="text-xs text-gray-500 ml-2">(Editable)</span>
            </label>

            <div v-if="rfqData.status === 'Draft' || rfqData.status === 'Sent to Agent'" class="border rounded-lg p-3">
              <textarea
                v-model="rfqData.rfq_message"
                rows="6"
                class="w-full border-0 focus:ring-0 text-sm text-gray-700 resize-none"
                :disabled="rfqData.agent_engaged"
                placeholder="Enter RFQ message..."
              ></textarea>
            </div>
            <div v-else class="border rounded-lg p-3 bg-gray-50">
              <div class="text-sm text-gray-700 whitespace-pre-wrap" v-html="sanitizeHtml(rfqData.rfq_message)"></div>
            </div>
          </div>

          <!-- Agent Selection (if not yet engaged) -->
          <div v-if="!rfqData.agent_engaged && availableAgents.length > 0" class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Select Agent</label>
            <select
              v-model="selectedAgent"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">-- Choose an agent --</option>
              <option v-for="agent in availableAgents" :key="agent.value" :value="agent.value">
                {{ agent.label }}
              </option>
            </select>
          </div>

          <!-- Agent Details (if agent engaged) -->
          <div v-if="rfqData.agent_name" class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 class="text-sm font-semibold text-blue-900 mb-2">Engaged Agent</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-blue-700">Agent Name</label>
                <p class="text-sm text-blue-900">{{ rfqData.agent_name }}</p>
              </div>
              <div v-if="rfqData.agent_email">
                <label class="block text-xs font-medium text-blue-700">Email</label>
                <p class="text-sm text-blue-900">{{ rfqData.agent_email }}</p>
              </div>
              <div v-if="rfqData.agent_phone">
                <label class="block text-xs font-medium text-blue-700">Phone</label>
                <p class="text-sm text-blue-900">{{ rfqData.agent_phone }}</p>
              </div>
              <div v-if="rfqData.agent_engaged_date">
                <label class="block text-xs font-medium text-blue-700">Engaged Date</label>
                <p class="text-sm text-blue-900">{{ formatDate(rfqData.agent_engaged_date) }}</p>
              </div>
            </div>
          </div>

          <!-- Quote Details (if quote received) -->
          <div v-if="rfqData.status === 'Quote Received' || rfqData.status === 'Agent Engaged'" class="mb-6">
            <h4 class="text-sm font-semibold text-gray-900 mb-3">Quote Details</h4>
            <div class="grid grid-cols-2 gap-4">
              <div v-if="rfqData.quote_amount">
                <label class="block text-xs font-medium text-gray-700">Quote Amount</label>
                <p class="text-sm text-gray-900">${{ rfqData.quote_amount }}</p>
              </div>
              <div v-if="rfqData.quote_received_date">
                <label class="block text-xs font-medium text-gray-700">Quote Received</label>
                <p class="text-sm text-gray-900">{{ formatDate(rfqData.quote_received_date) }}</p>
              </div>
            </div>
            <div v-if="rfqData.quote_details" class="mt-3">
              <label class="block text-xs font-medium text-gray-700 mb-1">Quote Details</label>
              <div class="text-sm text-gray-900 bg-gray-50 p-3 rounded border border-gray-200">
                {{ rfqData.quote_details }}
              </div>
            </div>
          </div>

          <!-- Warning Message -->
          <div v-if="!rfqData.agent_engaged" class="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
            <div class="flex">
              <svg class="h-5 w-5 text-orange-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              <div class="text-sm text-orange-700">
                <p class="font-medium">Important Notice</p>
                <p class="mt-1">Once you engage an agent, you will not be able to make any more changes or complete this application.</p>
              </div>
            </div>
          </div>

          <!-- Locked Message (if agent engaged) -->
          <div v-if="rfqData.agent_engaged" class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <div class="flex">
              <svg class="h-5 w-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
              <div class="text-sm text-green-700">
                <p class="font-medium">Application Locked</p>
                <p class="mt-1">This application has been locked and is now being managed by the engaged agent.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-3">
          <!-- Engage Agent Button (only show if quote received and not yet engaged) -->
          <button
            v-if="rfqData.status === 'Quote Received' && !rfqData.agent_engaged"
            @click="engageAgent"
            :disabled="saving"
            class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Engaging...' : 'Engage Agent' }}
          </button>

          <!-- Send to Agent Button (only show if draft) -->
          <button
            v-if="rfqData.status === 'Draft' && selectedAgent"
            @click="sendToAgent"
            :disabled="saving || !selectedAgent"
            class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Sending...' : 'Send to Agent' }}
          </button>

          <!-- Save Button (only if draft or sent) -->
          <button
            v-if="!rfqData.agent_engaged && (rfqData.status === 'Draft' || rfqData.status === 'Sent to Agent')"
            @click="saveRFQ"
            :disabled="saving"
            class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>

          <!-- Cancel/Close Button -->
          <button
            @click="closeModal"
            :disabled="saving"
            class="mt-3 sm:mt-0 w-full sm:w-auto inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ rfqData.agent_engaged ? 'Close' : 'Cancel' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue"
import { getAvailableAgents } from "../../api/rfq"

const props = defineProps({
	isOpen: {
		type: Boolean,
		default: false,
	},
	rfq: {
		type: Object,
		default: () => ({}),
	},
	requestId: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["close", "save", "send-to-agent", "engage-agent"])

// Local copy of RFQ data for editing
const rfqData = ref({ ...props.rfq })
const selectedAgent = ref(props.rfq.agent || "")
const saving = ref(false)
const availableAgents = ref([])
const loadingAgents = ref(false)

// Load available agents on component mount
onMounted(async () => {
	await loadAvailableAgents()
})

const loadAvailableAgents = async () => {
	try {
		loadingAgents.value = true
		const resource = getAvailableAgents()

		// Wait for the resource to load
		await new Promise((resolve) => {
			const checkLoaded = setInterval(() => {
				if (resource.data) {
					clearInterval(checkLoaded)
					resolve()
				}
			}, 100)

			// Timeout after 5 seconds
			setTimeout(() => {
				clearInterval(checkLoaded)
				resolve()
			}, 5000)
		})

		if (resource.data && Array.isArray(resource.data)) {
			availableAgents.value = resource.data
		} else {
			// Fallback to hardcoded agents if API fails
			availableAgents.value = [
				{ value: "agent-1", label: "Smith Planning Consultants Ltd" },
				{ value: "agent-2", label: "Jones Resource Consent Services" },
				{ value: "agent-3", label: "Wellington Planning Professionals" },
			]
		}
	} catch (error) {
		console.error("Failed to load available agents:", error)
		// Use fallback agents
		availableAgents.value = [
			{ value: "agent-1", label: "Smith Planning Consultants Ltd" },
			{ value: "agent-2", label: "Jones Resource Consent Services" },
			{ value: "agent-3", label: "Wellington Planning Professionals" },
		]
	} finally {
		loadingAgents.value = false
	}
}

// Watch for prop changes
watch(
	() => props.rfq,
	(newRfq) => {
		rfqData.value = { ...newRfq }
		selectedAgent.value = newRfq.agent || ""
	},
	{ deep: true },
)

watch(
	() => props.isOpen,
	(isOpen) => {
		if (isOpen) {
			rfqData.value = { ...props.rfq }
			selectedAgent.value = props.rfq.agent || ""
			// Reload agents when modal opens
			if (availableAgents.value.length === 0) {
				loadAvailableAgents()
			}
		}
	},
)

const closeModal = () => {
	if (!saving.value) {
		emit("close")
	}
}

const saveRFQ = async () => {
	saving.value = true
	try {
		await emit("save", rfqData.value)
		// closeModal() // Don't close automatically, let parent handle it
	} finally {
		saving.value = false
	}
}

const sendToAgent = async () => {
	if (!selectedAgent.value) {
		alert("Please select an agent first")
		return
	}

	saving.value = true
	try {
		await emit("send-to-agent", {
			rfq: rfqData.value,
			agent: selectedAgent.value,
		})
		rfqData.value.status = "Sent to Agent"
		rfqData.value.agent = selectedAgent.value
	} finally {
		saving.value = false
	}
}

const engageAgent = async () => {
	if (
		!confirm(
			"Are you sure you want to engage this agent? This will lock your application and you will not be able to make further changes.",
		)
	) {
		return
	}

	saving.value = true
	try {
		await emit("engage-agent", rfqData.value)
		rfqData.value.status = "Agent Engaged"
		rfqData.value.agent_engaged = true
	} finally {
		saving.value = false
	}
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	const date = new Date(dateString)
	return date.toLocaleDateString("en-NZ", {
		year: "numeric",
		month: "short",
		day: "numeric",
	})
}

const sanitizeHtml = (html) => {
	if (!html) return ""
	// Basic HTML sanitization - in production, use a library like DOMPurify
	return html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
}
</script>

<style scoped>
/* Modal animations */
.fixed {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
