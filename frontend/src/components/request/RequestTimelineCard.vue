<template>
	<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
		<h2 class="text-lg font-semibold text-gray-900 mb-4">Processing Timeline</h2>

		<!-- SLA / Statutory Clock -->
		<div v-if="clockData.statutory_clock_started" class="mb-6 p-4 bg-blue-50 rounded-lg">
			<div class="flex items-center justify-between mb-2">
				<span class="text-sm font-medium text-blue-900">SLA / Statutory Clock</span>
				<span class="text-xs text-blue-700">{{ clockData.working_days_elapsed }} of 20 days</span>
			</div>
			<div class="w-full bg-blue-200 rounded-full h-2">
				<div
					class="bg-blue-600 h-2 rounded-full transition-all duration-300"
					:style="{ width: `${progressPercent}%` }"
				></div>
			</div>
			<p class="mt-2 text-xs text-blue-700">
				{{ clockData.statutory_clock_stopped ? 'Clock stopped (RFI issued)' : `${clockData.working_days_remaining} days remaining` }}
			</p>
		</div>

		<!-- Status History -->
		<div class="space-y-4">
			<div class="flex items-start space-x-3">
				<div class="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
					<svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
					</svg>
				</div>
				<div class="flex-1">
					<p class="text-sm font-medium text-gray-900">Application Created</p>
					<p class="text-xs text-gray-500">{{ formatDate(creation) }}</p>
				</div>
			</div>

			<div v-if="modified !== creation" class="flex items-start space-x-3">
				<div class="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
					<svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
						<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
					</svg>
				</div>
				<div class="flex-1">
					<p class="text-sm font-medium text-gray-900">Last Updated</p>
					<p class="text-xs text-gray-500">{{ formatDate(modified) }}</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
const props = defineProps({
	clockData: {
		type: Object,
		required: true,
		default: () => ({
			statutory_clock_started: false,
			working_days_elapsed: 0,
			working_days_remaining: 20,
			statutory_clock_stopped: false,
		}),
	},
	progressPercent: {
		type: Number,
		default: 0,
	},
	creation: {
		type: String,
		required: true,
	},
	modified: {
		type: String,
		required: true,
	},
})

/**
 * Format date to NZ locale with date and time
 * @param {string} dateStr - ISO date string
 * @returns {string} Formatted date string
 */
const formatDate = (dateStr) => {
	if (!dateStr) return "N/A"
	const date = new Date(dateStr)
	return date.toLocaleDateString("en-NZ", {
		year: "numeric",
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	})
}
</script>
