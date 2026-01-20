<template>
	<div v-if="show" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
		<div class="flex justify-between items-start mb-4">
			<div>
				<h2 class="text-lg font-semibold text-gray-900">Council Meeting</h2>
				<p class="text-sm text-gray-600 mt-1">
					Schedule a meeting with council planners to discuss your application
				</p>
			</div>

			<!-- Status Badge if meeting exists -->
			<span
				v-if="meetings && meetings.length > 0"
				class="px-3 py-1 rounded-full text-sm font-medium"
				:class="{
					'bg-yellow-100 text-yellow-800': meetings[0].status === 'Requested',
					'bg-blue-100 text-blue-800': meetings[0].status === 'Scheduled' || meetings[0].status === 'Confirmed',
					'bg-green-100 text-green-800': meetings[0].status === 'Completed',
					'bg-gray-100 text-gray-800': meetings[0].status === 'Cancelled'
				}"
			>
				{{ meetings[0].status }}
			</span>
		</div>

		<!-- Meeting Details (if exists) -->
		<div v-if="meetings && meetings.length > 0" class="space-y-4">
			<div v-for="meeting in meetings" :key="meeting.name" class="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
				<div class="grid grid-cols-2 gap-3 text-sm">
					<div>
						<span class="font-medium text-gray-700">Type:</span>
						<span class="ml-2 text-gray-900">{{ meeting.meeting_type }}</span>
					</div>
					<div>
						<span class="font-medium text-gray-700">Status:</span>
						<span class="ml-2 text-gray-900">{{ meeting.status }}</span>
					</div>
					<div v-if="meeting.scheduled_start" class="col-span-2">
						<span class="font-medium text-gray-700">Scheduled:</span>
						<span class="ml-2 text-gray-900">{{ formatMeetingDate(meeting.scheduled_start) }}</span>
					</div>
					<div v-if="meeting.meeting_format" class="col-span-2">
						<span class="font-medium text-gray-700">Format:</span>
						<span class="ml-2 text-gray-900">{{ meeting.meeting_format }}</span>
					</div>
					<div v-if="meeting.meeting_location" class="col-span-2">
						<span class="font-medium text-gray-700">Location:</span>
						<span class="ml-2 text-gray-900">{{ meeting.meeting_location }}</span>
					</div>
					<div v-if="meeting.google_meet_link" class="col-span-2">
						<span class="font-medium text-gray-700">Meeting Link:</span>
						<a :href="meeting.google_meet_link" target="_blank" class="ml-2 text-blue-600 hover:underline">Join Meeting</a>
					</div>
				</div>

				<div v-if="meeting.meeting_purpose" class="mt-3 pt-3 border-t border-blue-200">
					<span class="font-medium text-gray-700 text-sm">Purpose:</span>
					<p class="mt-1 text-sm text-gray-900">{{ meeting.meeting_purpose }}</p>
				</div>

				<!-- Proposed Time Slots -->
				<div v-if="meeting.status === 'Requested' && meeting.proposed_slots && meeting.proposed_slots.length > 0" class="mt-3 pt-3 border-t border-blue-200">
					<span class="font-medium text-gray-700 text-sm">Proposed Time Slots:</span>
					<ul class="mt-2 space-y-1">
						<li v-for="(slot, index) in meeting.proposed_slots" :key="index" class="text-sm text-gray-900 flex items-center">
							<svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							{{ formatMeetingDate(slot) }}
						</li>
					</ul>
				</div>

				<!-- Action Buttons -->
				<div v-if="meeting.status === 'Requested' || meeting.status === 'Scheduled'" class="mt-4 pt-3 border-t border-blue-200 flex space-x-3">
					<button
						@click="$emit('edit-meeting', meeting)"
						class="flex-1 px-4 py-2 bg-white border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors text-sm font-medium"
					>
						<svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
						</svg>
						Edit Request
					</button>
					<button
						@click="$emit('cancel-meeting', meeting)"
						:disabled="cancelling"
						class="flex-1 px-4 py-2 bg-white border border-red-600 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
						Cancel Meeting
					</button>
				</div>
			</div>
		</div>

		<!-- Request Meeting Button -->
		<div v-else class="text-center py-6">
			<svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
			</svg>
			<p class="text-sm text-gray-600 mb-4">
				No meeting scheduled yet. Book a meeting to discuss your application with council planners.
			</p>
			<button
				@click="$emit('book-meeting')"
				class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				Request Council Meeting
			</button>
		</div>
	</div>
</template>

<script setup>
const props = defineProps({
	show: {
		type: Boolean,
		default: false,
	},
	meetings: {
		type: Array,
		default: () => [],
	},
	cancelling: {
		type: Boolean,
		default: false,
	},
})

defineEmits(["book-meeting", "edit-meeting", "cancel-meeting"])

const formatMeetingDate = (dateString) => {
	if (!dateString) return "N/A"
	const date = new Date(dateString)
	return date.toLocaleString("en-NZ", {
		weekday: "short",
		year: "numeric",
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	})
}
</script>
