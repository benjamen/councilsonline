<template>
	<Dialog v-model="isOpen" :options="{ title: 'Request Submitted Successfully', size: 'md' }">
		<template #body-content>
			<div class="success-content text-center py-6">
				<!-- Success Icon -->
				<div class="flex justify-center mb-4">
					<svg
						class="w-16 h-16 text-green-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</div>

				<!-- Request Number -->
				<h3 class="text-xl font-semibold text-gray-900 mb-2">
					Request {{ requestNumber }} Submitted
				</h3>

				<!-- SLA Information -->
				<div v-if="slaInfo" class="mt-4 space-y-2">
					<p class="text-gray-600">
						Your request will be processed within
						<span class="font-semibold text-gray-900">
							{{ slaInfo.processing_days }} business days
						</span>
					</p>

					<p v-if="slaInfo.expected_completion_date" class="text-gray-600">
						Expected completion:
						<span class="font-semibold text-gray-900">
							{{ formatDate(slaInfo.expected_completion_date) }}
						</span>
					</p>
				</div>

				<!-- Next Steps -->
				<div class="mt-6 p-4 bg-blue-50 rounded-lg text-left">
					<h4 class="text-sm font-semibold text-blue-900 mb-2">Next Steps:</h4>
					<ul class="text-sm text-blue-800 space-y-1">
						<li class="flex items-start">
							<svg
								class="w-4 h-4 mr-2 mt-0.5 flex-shrink-0"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
									clip-rule="evenodd"
								/>
							</svg>
							<span>You will receive email updates on your request status</span>
						</li>
						<li class="flex items-start">
							<svg
								class="w-4 h-4 mr-2 mt-0.5 flex-shrink-0"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
									clip-rule="evenodd"
								/>
							</svg>
							<span>Track your request progress from the dashboard</span>
						</li>
						<li class="flex items-start">
							<svg
								class="w-4 h-4 mr-2 mt-0.5 flex-shrink-0"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
									clip-rule="evenodd"
								/>
							</svg>
							<span>Council staff will review your application and contact you if needed</span>
						</li>
					</ul>
				</div>

				<!-- Action Buttons -->
				<div class="mt-6 flex gap-3 justify-center">
					<Button variant="outline" @click="handleViewRequest">
						View Request Details
					</Button>
					<Button appearance="primary" @click="handleGoToDashboard">
						Go to Dashboard
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { Button, Dialog } from "frappe-ui"
import { computed } from "vue"

const props = defineProps({
	open: {
		type: Boolean,
		default: false,
	},
	requestNumber: {
		type: String,
		default: "",
	},
	requestId: {
		type: String,
		default: "",
	},
	slaInfo: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(["close", "viewRequest", "goToDashboard"])

const isOpen = computed({
	get: () => props.open,
	set: (value) => {
		if (!value) {
			emit("close")
		}
	},
})

/**
 * Format date for display
 */
function formatDate(dateStr) {
	if (!dateStr) return "N/A"
	try {
		const date = new Date(dateStr)
		return date.toLocaleDateString("en-NZ", {
			year: "numeric",
			month: "long",
			day: "numeric",
		})
	} catch (error) {
		return dateStr
	}
}

/**
 * Handle view request details
 */
function handleViewRequest() {
	emit("viewRequest", props.requestId)
	isOpen.value = false
}

/**
 * Handle go to dashboard
 */
function handleGoToDashboard() {
	emit("goToDashboard")
	isOpen.value = false
}
</script>

<style scoped>
.success-content {
	min-height: 300px;
}
</style>
