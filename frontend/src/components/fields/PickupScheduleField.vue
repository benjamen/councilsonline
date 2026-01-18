<script setup>
import { ref, computed, watch } from "vue"
import BookSlotModal from "../modals/BookSlotModal.vue"

const props = defineProps({
	field: {
		type: Object,
		required: true,
	},
	modelValue: {
		type: Object,
		default: () => ({}),
	},
	teamCode: {
		type: String,
		default: "PAYMENTS",
	},
	appointmentType: {
		type: String,
		default: "Pickup",
	},
	councilCode: {
		type: String,
		default: null,
	},
	requestId: {
		type: String,
		default: null,
	},
	validationError: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["update:modelValue", "validate"])

const showModal = ref(false)

// Local copy of the appointment data
const appointmentData = computed({
	get: () => props.modelValue || {},
	set: (value) => emit("update:modelValue", value),
})

const hasAppointment = computed(() => {
	return appointmentData.value?.appointment_id || appointmentData.value?.scheduled_start
})

const formattedDate = computed(() => {
	if (!appointmentData.value?.scheduled_start) return ""
	const date = new Date(appointmentData.value.scheduled_start)
	return date.toLocaleDateString("en-US", {
		weekday: "long",
		year: "numeric",
		month: "long",
		day: "numeric",
	})
})

const formattedTime = computed(() => {
	if (!appointmentData.value?.scheduled_start) return ""
	const start = new Date(appointmentData.value.scheduled_start)
	const end = appointmentData.value.scheduled_end ? new Date(appointmentData.value.scheduled_end) : null

	const startTime = start.toLocaleTimeString("en-US", {
		hour: "numeric",
		minute: "2-digit",
		hour12: true,
	})

	if (end) {
		const endTime = end.toLocaleTimeString("en-US", {
			hour: "numeric",
			minute: "2-digit",
			hour12: true,
		})
		return `${startTime} - ${endTime}`
	}

	return startTime
})

const openScheduler = () => {
	showModal.value = true
}

const handleBooked = (result) => {
	// Store appointment details in the form data
	appointmentData.value = {
		appointment_id: result.appointment_id,
		scheduled_start: result.scheduled_start,
		scheduled_end: result.scheduled_end,
		location: result.location,
		status: result.status,
	}

	emit("validate")
}

const clearAppointment = () => {
	appointmentData.value = {}
	emit("validate")
}
</script>

<template>
	<div class="form-group" :data-fieldname="field.field_name">
		<label class="block text-sm font-medium text-gray-700 mb-2">
			{{ field.field_label }}
			<span v-if="field.is_required" class="text-red-500 ml-1">*</span>
		</label>

		<!-- No appointment scheduled -->
		<div v-if="!hasAppointment" class="space-y-3">
			<p class="text-sm text-gray-600">
				Please schedule a pickup date and time for collecting your payment.
			</p>
			<button
				type="button"
				@click="openScheduler"
				class="inline-flex items-center px-4 py-2 border border-blue-600 rounded-lg text-sm font-medium text-blue-600 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
			>
				<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
					/>
				</svg>
				Schedule Pickup Time
			</button>
		</div>

		<!-- Appointment scheduled -->
		<div v-else class="bg-green-50 border border-green-200 rounded-lg p-4">
			<div class="flex items-start justify-between">
				<div class="flex items-start space-x-3">
					<div class="flex-shrink-0">
						<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<div>
						<p class="text-sm font-medium text-green-900">Pickup Scheduled</p>
						<p v-if="appointmentData.appointment_id" class="text-xs text-green-700 mb-1">
							Ref: {{ appointmentData.appointment_id }}
						</p>
						<p class="text-sm text-green-800">
							<span class="font-medium">{{ formattedDate }}</span>
						</p>
						<p class="text-sm text-green-800">
							<span class="font-medium">Time:</span> {{ formattedTime }}
						</p>
						<p v-if="appointmentData.location" class="text-sm text-green-800">
							<span class="font-medium">Location:</span> {{ appointmentData.location }}
						</p>
					</div>
				</div>
				<button
					type="button"
					@click="clearAppointment"
					class="text-sm text-green-700 hover:text-green-900 underline"
				>
					Reschedule
				</button>
			</div>
		</div>

		<!-- Validation error -->
		<p v-if="validationError" class="mt-2 text-sm text-red-600">
			{{ validationError }}
		</p>

		<!-- Booking Modal -->
		<BookSlotModal
			v-model:show="showModal"
			:team-code="teamCode"
			:appointment-type="appointmentType"
			:council-code="councilCode"
			:request-id="requestId"
			title="Schedule Pickup Time"
			:show-purpose="false"
			@booked="handleBooked"
		/>
	</div>
</template>
