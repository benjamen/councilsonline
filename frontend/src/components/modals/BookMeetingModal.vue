<script setup>
import { Dialog, createResource } from "frappe-ui"
import { computed, ref, watch } from "vue"

const props = defineProps({
	show: {
		type: Boolean,
		required: true,
	},
	requestId: {
		type: String,
		default: null, // Allow null for draft requests
	},
	requestTypeCode: {
		type: String,
		default: null,
	},
	councilCode: {
		type: String,
		default: null,
	},
	meeting: {
		type: Object,
		default: null, // Optional: For editing existing meeting
	},
})

const emit = defineEmits(["update:show", "booked"])

const isOpen = computed({
	get: () => props.show,
	set: (value) => emit("update:show", value),
})

const meetingType = ref("Pre-Application Meeting")
const meetingPurpose = ref("")
const discussionPoints = ref("")
const booking = ref(false)
const error = ref(null)
const success = ref(false)
const emailError = ref("")

// Attendees
const attendees = ref([])
const newAttendeeName = ref("")
const newAttendeeEmail = ref("")
const newAttendeeRole = ref("")

// Constants
const MEETING_DURATION_MS = 60 * 60 * 1000 // 1 hour in milliseconds

// Available slots mode
const showAvailableSlots = ref(false)

// Fetch meeting configuration
const meetingConfig = createResource({
	url: "councilsonline.api.get_meeting_config",
	auto: false,
})

// Fetch available slots
const availableSlots = createResource({
	url: "councilsonline.api.get_available_meeting_slots",
	auto: false,
})

// Watch for modal open to fetch slots if council code is available
watch(
	() => props.show,
	(newVal) => {
		if (newVal && props.councilCode) {
			// Pre-fill form if editing existing meeting
			if (props.meeting) {
				meetingType.value =
					props.meeting.meeting_type || "Pre-Application Meeting"
				meetingPurpose.value = props.meeting.meeting_purpose || ""
				discussionPoints.value = props.meeting.discussion_points || ""

				// Pre-fill preferred time if available
				if (props.meeting.preferred_meeting_times) {
					const times = Array.isArray(props.meeting.preferred_meeting_times)
						? props.meeting.preferred_meeting_times
						: []
					preferredTime.value = times[0]?.preferred_start || ""
				}
			}

			// Pass params directly to fetch() to avoid circular JSON reference
			meetingConfig.fetch({
				council_code: props.councilCode,
				meeting_type: meetingType.value,
			})

			const today = new Date()
			const endDate = new Date()
			endDate.setDate(today.getDate() + 30) // Next 30 days

			availableSlots.fetch({
				council_code: props.councilCode,
				meeting_type: meetingType.value,
				start_date: today.toISOString().split("T")[0],
				end_date: endDate.toISOString().split("T")[0],
			})
		}
	},
)

// Preferred Time Slot (single selection)
const preferredTime = ref("")

// Auto-calculate end time (1 hour after start time)
const calculateEndTime = (startTime) => {
	if (!startTime) return ""
	try {
		const start = new Date(startTime)
		if (isNaN(start.getTime())) throw new Error("Invalid date")
		const end = new Date(start.getTime() + MEETING_DURATION_MS)
		return end.toISOString().slice(0, 16) // Format for datetime-local input
	} catch (e) {
		console.error("Error calculating end time:", e)
		return ""
	}
}

// Format end time for display
const formatEndTime = (startTime) => {
	if (!startTime) return ""
	try {
		const endTime = calculateEndTime(startTime)
		if (!endTime) return "Invalid date"
		return new Date(endTime).toLocaleString()
	} catch (e) {
		return "Invalid date"
	}
}

const isValidEmail = (email) => {
	return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

const isValid = computed(() => {
	// Meeting type and purpose are required
	if (!meetingType.value || !meetingPurpose.value.trim()) return false

	// Preferred time must be selected
	return preferredTime.value && preferredTime.value.trim() !== ""
})

const addAttendee = () => {
	emailError.value = ""

	if (newAttendeeName.value.trim() && newAttendeeEmail.value.trim()) {
		// Validate email format
		if (!isValidEmail(newAttendeeEmail.value.trim())) {
			emailError.value = "Please enter a valid email address"
			return
		}

		attendees.value.push({
			attendee_name: newAttendeeName.value.trim(),
			attendee_email: newAttendeeEmail.value.trim(),
			attendee_role: newAttendeeRole.value.trim() || "Applicant Representative",
		})

		// Clear form
		newAttendeeName.value = ""
		newAttendeeEmail.value = ""
		newAttendeeRole.value = ""
	}
}

const removeAttendee = (index) => {
	attendees.value.splice(index, 1)
}

const selectAvailableSlot = (slot) => {
	// Set the preferred time to this slot
	preferredTime.value = slot.start.slice(0, 16) // Format for datetime-local
}

const toggleAvailableSlotsView = () => {
	showAvailableSlots.value = !showAvailableSlots.value
	if (showAvailableSlots.value && props.councilCode && !availableSlots.data) {
		const today = new Date()
		const endDate = new Date()
		endDate.setDate(today.getDate() + 30) // Next 30 days

		availableSlots.fetch({
			council_code: props.councilCode,
			meeting_type: meetingType.value,
			start_date: today.toISOString().split("T")[0],
			end_date: endDate.toISOString().split("T")[0],
		})
	}
}

const handleClose = () => {
	if (!booking.value) {
		meetingType.value = "Pre-Application Meeting"
		meetingPurpose.value = ""
		discussionPoints.value = ""
		attendees.value = []
		preferredTime.value = ""
		error.value = null
		success.value = false
		emit("update:show", false)
	}
}

const handleBook = async () => {
	if (!isValid.value) return

	booking.value = true
	error.value = null

	try {
		// Build single time slot with calculated end time
		const timeSlot = {
			preference_order: 1,
			preferred_start: preferredTime.value,
			preferred_end: calculateEndTime(preferredTime.value),
		}

		const response = await fetch(
			"/api/method/councilsonline.api.book_council_meeting",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					request_id: props.requestId || "draft",
					request_type_code: props.requestTypeCode,
					meeting_type: meetingType.value,
					meeting_purpose: meetingPurpose.value,
					discussion_points: discussionPoints.value,
					attendees: attendees.value,
					preferred_time_slots: [timeSlot],
				}),
			},
		)

		const data = await response.json()

		if (data.message?.success) {
			// Show success message
			success.value = true
			error.value = null

			// Emit booked event immediately
			emit("booked", data.message)

			// Close modal after 2 seconds so user sees success message
			setTimeout(() => {
				handleClose()
			}, 2000)
		} else {
			error.value =
				data.exc || data._server_messages || "Failed to book meeting"
		}
	} catch (err) {
		console.error("Book meeting error:", err)
		error.value = "Network error. Please try again."
	} finally {
		booking.value = false
	}
}
</script>

<template>
	<Dialog v-model="isOpen" :options="{ size: 'lg' }">
		<template #body>
			<div class="p-6 max-h-[80vh] overflow-y-auto">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Request Pre-Application Council Meeting</h3>

				<div class="space-y-6">
					<!-- Meeting Type -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Meeting Type *</label>
						<select
							v-model="meetingType"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							:disabled="booking"
						>
							<option value="Pre-Application Meeting">Pre-Application Meeting</option>
							<option value="Follow-up Meeting">Follow-up Meeting</option>
							<option value="Clarification Meeting">Clarification Meeting</option>
							<option value="Final Review Meeting">Final Review Meeting</option>
						</select>
					</div>

					<!-- Meeting Purpose -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Meeting Purpose *</label>
						<textarea
							v-model="meetingPurpose"
							rows="3"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="Brief summary of why you need this meeting..."
							:disabled="booking"
						></textarea>
					</div>

					<!-- Discussion Points -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Discussion Points (Optional)</label>
						<textarea
							v-model="discussionPoints"
							rows="4"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="Key topics you'd like to discuss (bullet points)..."
							:disabled="booking"
						></textarea>
					</div>

					<!-- Preferred Time Slot -->
					<div>
						<div class="flex items-center justify-between mb-2">
							<label class="block text-sm font-medium text-gray-700">Preferred Meeting Time *</label>
							<button
								v-if="councilCode && !availableSlots.loading"
								type="button"
								@click="toggleAvailableSlotsView"
								class="text-sm text-blue-600 hover:text-blue-700 font-medium"
								:disabled="booking"
							>
								{{ availableSlots.data ? 'Refresh Available Slots' : 'Load Available Slots' }}
							</button>
						</div>
						<p class="text-xs text-gray-500 mb-3">Select your preferred time slot (1 hour meeting). The council will confirm or propose an alternative.</p>

						<!-- Loading State -->
						<div v-if="availableSlots.loading" class="mb-4 border border-blue-200 rounded-lg p-4 bg-blue-50">
							<div class="text-center py-4">
								<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
								<p class="text-sm text-gray-600 mt-2">Loading available time slots...</p>
							</div>
						</div>

						<!-- Error State -->
						<div v-else-if="availableSlots.error" class="mb-4 border border-red-200 rounded-lg p-4 bg-red-50">
							<p class="text-sm text-red-600">Failed to load available slots. Please enter your preferred time manually below.</p>
						</div>

						<!-- Time Slot Selection -->
						<div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
							<div class="flex items-center justify-between mb-2">
								<span class="text-sm font-medium text-gray-700">Select Time</span>
								<span v-if="preferredTime" class="text-xs text-gray-500">1 hour duration</span>
							</div>
							<div>
								<!-- Dropdown if slots are available -->
								<select
									v-if="availableSlots.data?.slots?.length > 0"
									v-model="preferredTime"
									class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
									:disabled="booking"
								>
									<option value="">-- Select an available time slot --</option>
									<option
										v-for="(availSlot, idx) in availableSlots.data.slots.slice(0, 30)"
										:key="idx"
										:value="availSlot.start.slice(0, 16)"
									>
										{{ availSlot.start_display }} - {{ availSlot.end_display }} ({{ availSlot.day }})
									</option>
								</select>

								<!-- Manual input if no slots available -->
								<input
									v-else
									type="datetime-local"
									v-model="preferredTime"
									class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
									:disabled="booking"
								/>

								<p v-if="preferredTime" class="text-xs text-gray-500 mt-1">
									Meeting will end at {{ formatEndTime(preferredTime) }}
								</p>
							</div>

							<!-- Message when no slots loaded yet -->
							<div v-if="!availableSlots.data && !availableSlots.loading && !availableSlots.error" class="mt-3 text-center">
								<p class="text-xs text-gray-500">
									Click "Load Available Slots" above to see available meeting times.
								</p>
							</div>

							<!-- Message when no slots available -->
							<div v-if="availableSlots.data?.slots?.length === 0" class="mt-3 text-center">
								<p class="text-xs text-gray-600">
									No available slots found in the next 30 days. Please enter your preferred time manually.
								</p>
							</div>
						</div>
					</div>

					<!-- Additional Attendees -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Additional Attendees (Optional)</label>
						<p class="text-xs text-gray-500 mb-3">Add any representatives, consultants, or advisors who will attend with you.</p>

						<!-- Attendee List -->
						<div v-if="attendees.length > 0" class="mb-3 space-y-2">
							<div
								v-for="(attendee, index) in attendees"
								:key="index"
								class="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-3"
							>
								<div class="flex-1">
									<div class="text-sm font-medium text-gray-900">{{ attendee.attendee_name }}</div>
									<div class="text-xs text-gray-600">{{ attendee.attendee_email }} • {{ attendee.attendee_role }}</div>
								</div>
								<button
									@click="removeAttendee(index)"
									class="ml-3 text-red-600 hover:text-red-700"
									:disabled="booking"
								>
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
									</svg>
								</button>
							</div>
						</div>

						<!-- Add Attendee Form -->
						<div class="border border-gray-300 rounded-lg p-4 bg-white space-y-3">
							<div class="grid grid-cols-2 gap-3">
								<div>
									<label class="block text-xs text-gray-600 mb-1">Name</label>
									<input
										type="text"
										v-model="newAttendeeName"
										placeholder="John Smith"
										class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
										:disabled="booking"
									/>
								</div>
								<div>
									<label class="block text-xs text-gray-600 mb-1">Email</label>
									<input
										type="email"
										v-model="newAttendeeEmail"
										placeholder="john@example.com"
										class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
										:class="{ 'border-red-500': emailError }"
										:disabled="booking"
									/>
									<p v-if="emailError" class="text-xs text-red-600 mt-1">{{ emailError }}</p>
								</div>
							</div>
							<div>
								<label class="block text-xs text-gray-600 mb-1">Role/Title</label>
								<input
									type="text"
									v-model="newAttendeeRole"
									placeholder="e.g., Architect, Consultant, Representative"
									class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
									:disabled="booking"
								/>
							</div>
							<button
								@click="addAttendee"
								:disabled="!newAttendeeName || !newAttendeeEmail || booking"
								class="w-full px-3 py-2 text-sm font-medium text-blue-600 border border-blue-300 hover:bg-blue-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Add Attendee
							</button>
						</div>
					</div>

					<!-- Info Box -->
					<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
						<h4 class="text-sm font-semibold text-blue-900 mb-2">What happens next?</h4>
						<ul class="text-sm text-blue-800 space-y-1 list-disc list-inside">
							<li>Your meeting request will be sent to the council</li>
							<li>The council will review and confirm your selected time</li>
							<li>You'll receive a calendar invitation once confirmed</li>
						</ul>
					</div>

					<!-- Success Display -->
					<div v-if="success" class="bg-green-50 border border-green-200 rounded-lg p-4">
						<div class="flex items-center">
							<svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
							</svg>
							<p class="text-sm text-green-800 font-medium">Meeting request submitted! The council will confirm your selected time.</p>
						</div>
					</div>

					<!-- Error Display -->
					<div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
						<p class="text-sm text-red-800">{{ error }}</p>
					</div>

					<!-- Buttons inside body to avoid overlay issues -->
					<div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
						<button
							@click="handleClose"
							:disabled="booking"
							class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
						>
							Cancel
						</button>
						<button
							@click="handleBook"
							:disabled="!isValid || booking"
							class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<span v-if="booking">Requesting...</span>
							<span v-else>Request Meeting</span>
						</button>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>
