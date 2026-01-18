<script setup>
import { Dialog, createResource } from "frappe-ui"
import { computed, ref, watch } from "vue"

const props = defineProps({
	show: {
		type: Boolean,
		required: true,
	},
	teamCode: {
		type: String,
		required: true,
	},
	appointmentType: {
		type: String,
		required: true,
	},
	title: {
		type: String,
		default: "Book Appointment",
	},
	requestId: {
		type: String,
		default: null,
	},
	councilCode: {
		type: String,
		default: null,
	},
	referenceDoctype: {
		type: String,
		default: null,
	},
	referenceName: {
		type: String,
		default: null,
	},
	showPurpose: {
		type: Boolean,
		default: true,
	},
	showContactFields: {
		type: Boolean,
		default: false,
	},
	defaultPurpose: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["update:show", "booked"])

const isOpen = computed({
	get: () => props.show,
	set: (value) => emit("update:show", value),
})

const selectedDate = ref("")
const selectedSlot = ref(null)
const location = ref("")
const purpose = ref("")
const contactName = ref("")
const contactEmail = ref("")
const contactPhone = ref("")
const booking = ref(false)
const error = ref(null)
const success = ref(false)

// Fetch team configuration
const teamConfig = createResource({
	url: "lodgeick.api.scheduling.get_team_config",
	auto: false,
})

// Fetch available slots
const availableSlots = createResource({
	url: "lodgeick.api.scheduling.get_available_slots",
	auto: false,
})

// Watch for modal open to fetch config and slots
watch(
	() => props.show,
	(newVal) => {
		if (newVal && props.teamCode) {
			// Reset form
			selectedDate.value = ""
			selectedSlot.value = null
			location.value = ""
			purpose.value = props.defaultPurpose
			error.value = null
			success.value = false

			// Fetch team config
			teamConfig.fetch({ team_code: props.teamCode })

			// Fetch available slots
			availableSlots.fetch({ team_code: props.teamCode })
		}
	},
)

// Watch for location default when config loads
watch(
	() => teamConfig.data,
	(data) => {
		if (data?.success && data.config?.default_location && !location.value) {
			location.value = data.config.default_location
		}
	},
)

// Computed: dates with available slots
const availableDates = computed(() => {
	if (!availableSlots.data?.success || !availableSlots.data.slots_by_date) {
		return []
	}
	return Object.values(availableSlots.data.slots_by_date)
})

// Computed: slots for selected date
const slotsForSelectedDate = computed(() => {
	if (!selectedDate.value || !availableSlots.data?.success) {
		return []
	}
	const dateData = availableSlots.data.slots_by_date[selectedDate.value]
	return dateData?.slots || []
})

// Computed: locations from config
const locations = computed(() => {
	if (!teamConfig.data?.success) return []
	return teamConfig.data.config.locations || []
})

const isValid = computed(() => {
	return selectedSlot.value && location.value
})

const formatSlotTime = (slot) => {
	return `${slot.start_display} - ${slot.end_display}`
}

const selectDate = (date) => {
	selectedDate.value = date
	selectedSlot.value = null
}

const selectSlot = (slot) => {
	selectedSlot.value = slot
}

const handleClose = () => {
	if (!booking.value) {
		emit("update:show", false)
	}
}

const handleBook = async () => {
	if (!isValid.value || !selectedSlot.value) return

	booking.value = true
	error.value = null

	try {
		const response = await fetch("/api/method/lodgeick.api.scheduling.book_appointment", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": window.csrf_token,
			},
			body: JSON.stringify({
				team_code: props.teamCode,
				scheduled_start: selectedSlot.value.start,
				scheduled_end: selectedSlot.value.end,
				appointment_type: props.appointmentType,
				location: location.value,
				purpose: purpose.value,
				contact_name: contactName.value || null,
				contact_email: contactEmail.value || null,
				contact_phone: contactPhone.value || null,
				reference_doctype: props.referenceDoctype,
				reference_name: props.referenceName,
				request_id: props.requestId,
				council_code: props.councilCode,
			}),
		})

		const data = await response.json()

		if (data.message?.success) {
			success.value = true
			error.value = null

			// Emit booked event with full details
			emit("booked", {
				...data.message,
				slot: selectedSlot.value,
				location: location.value,
			})

			// Close modal after showing success
			setTimeout(() => {
				handleClose()
			}, 2000)
		} else {
			error.value = data.exc || data._server_messages || "Failed to book appointment"
		}
	} catch (err) {
		console.error("Book appointment error:", err)
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
				<h3 class="text-lg font-semibold text-gray-900 mb-4">{{ title }}</h3>

				<!-- Loading State -->
				<div v-if="availableSlots.loading || teamConfig.loading" class="text-center py-8">
					<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
					<p class="text-sm text-gray-600 mt-3">Loading available times...</p>
				</div>

				<!-- Error State -->
				<div v-else-if="availableSlots.error || teamConfig.error" class="bg-red-50 border border-red-200 rounded-lg p-4">
					<p class="text-sm text-red-800">Failed to load scheduling options. Please try again later.</p>
				</div>

				<!-- Main Content -->
				<div v-else-if="availableSlots.data?.success" class="space-y-6">
					<!-- Step 1: Select Date -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-3">1. Select a Date</label>
						<div class="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-48 overflow-y-auto">
							<button
								v-for="dateInfo in availableDates"
								:key="dateInfo.date"
								@click="selectDate(dateInfo.date)"
								:class="[
									'px-3 py-2 text-sm rounded-lg border transition-colors text-left',
									selectedDate === dateInfo.date
										? 'bg-blue-600 text-white border-blue-600'
										: 'bg-white text-gray-700 border-gray-300 hover:border-blue-400',
								]"
								:disabled="booking"
							>
								<div class="font-medium">{{ dateInfo.day }}</div>
								<div class="text-xs opacity-80">{{ dateInfo.date }}</div>
								<div class="text-xs opacity-60">{{ dateInfo.slots.length }} slots</div>
							</button>
						</div>
						<p v-if="availableDates.length === 0" class="text-sm text-gray-500 mt-2">
							No available dates found. Please try again later.
						</p>
					</div>

					<!-- Step 2: Select Time Slot -->
					<div v-if="selectedDate">
						<label class="block text-sm font-medium text-gray-700 mb-3">2. Select a Time</label>
						<div class="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-40 overflow-y-auto">
							<button
								v-for="slot in slotsForSelectedDate"
								:key="slot.start"
								@click="selectSlot(slot)"
								:class="[
									'px-3 py-2 text-sm rounded-lg border transition-colors',
									selectedSlot?.start === slot.start
										? 'bg-blue-600 text-white border-blue-600'
										: 'bg-white text-gray-700 border-gray-300 hover:border-blue-400',
								]"
								:disabled="booking"
							>
								{{ slot.start_display }}
							</button>
						</div>
						<p v-if="selectedSlot" class="text-xs text-gray-500 mt-2">
							Duration: {{ selectedSlot.duration_minutes }} minutes (ends at {{ selectedSlot.end_display }})
						</p>
					</div>

					<!-- Step 3: Select Location -->
					<div v-if="selectedSlot && locations.length > 0">
						<label class="block text-sm font-medium text-gray-700 mb-2">3. Select Location</label>
						<select
							v-model="location"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							:disabled="booking"
						>
							<option value="">-- Select location --</option>
							<option v-for="loc in locations" :key="loc" :value="loc">
								{{ loc }}
							</option>
						</select>
					</div>

					<!-- Purpose (optional) -->
					<div v-if="showPurpose && selectedSlot">
						<label class="block text-sm font-medium text-gray-700 mb-2">Purpose / Notes (Optional)</label>
						<textarea
							v-model="purpose"
							rows="2"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="Any special instructions or notes..."
							:disabled="booking"
						></textarea>
					</div>

					<!-- Contact Fields (optional) -->
					<div v-if="showContactFields && selectedSlot" class="space-y-3">
						<label class="block text-sm font-medium text-gray-700">Contact Information (Optional)</label>
						<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
							<input
								v-model="contactName"
								type="text"
								placeholder="Name"
								class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
								:disabled="booking"
							/>
							<input
								v-model="contactEmail"
								type="email"
								placeholder="Email"
								class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
								:disabled="booking"
							/>
							<input
								v-model="contactPhone"
								type="tel"
								placeholder="Phone"
								class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
								:disabled="booking"
							/>
						</div>
					</div>

					<!-- Summary -->
					<div v-if="selectedSlot && location" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
						<h4 class="text-sm font-semibold text-blue-900 mb-2">Appointment Summary</h4>
						<div class="text-sm text-blue-800 space-y-1">
							<p><span class="font-medium">Date:</span> {{ selectedDate }}</p>
							<p><span class="font-medium">Time:</span> {{ formatSlotTime(selectedSlot) }}</p>
							<p><span class="font-medium">Location:</span> {{ location }}</p>
							<p><span class="font-medium">Duration:</span> {{ selectedSlot.duration_minutes }} minutes</p>
						</div>
					</div>

					<!-- Success Display -->
					<div v-if="success" class="bg-green-50 border border-green-200 rounded-lg p-4">
						<div class="flex items-center">
							<svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
							</svg>
							<p class="text-sm text-green-800 font-medium">Appointment booked successfully!</p>
						</div>
					</div>

					<!-- Error Display -->
					<div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
						<p class="text-sm text-red-800">{{ error }}</p>
					</div>

					<!-- Buttons -->
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
							<span v-if="booking">Booking...</span>
							<span v-else>Book Appointment</span>
						</button>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>
