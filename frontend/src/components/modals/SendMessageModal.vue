<script setup>
import { Button, Dialog, Input } from "frappe-ui"
import { computed, ref } from "vue"

const props = defineProps({
	show: {
		type: Boolean,
		required: true,
	},
	requestId: {
		type: String,
		required: true,
	},
})

const emit = defineEmits(["update:show", "sent"])

const isOpen = computed({
	get: () => props.show,
	set: (value) => emit("update:show", value),
})

const subject = ref("")
const message = ref("")
const communicationType = ref("Email")
const sending = ref(false)
const error = ref(null)
const success = ref(false)

const isValid = computed(() => {
	return subject.value.trim() && message.value.trim()
})

const handleClose = () => {
	if (!sending.value) {
		subject.value = ""
		message.value = ""
		communicationType.value = "Email"
		error.value = null
		success.value = false
		emit("update:show", false)
	}
}

const handleSend = async () => {
	if (!isValid.value) return

	sending.value = true
	error.value = null

	try {
		const response = await fetch(
			"/api/method/councilsonline.api.send_request_message",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					request_id: props.requestId,
					subject: subject.value,
					message: message.value,
					communication_type: communicationType.value,
				}),
			},
		)

		const data = await response.json()

		if (data.message?.success) {
			// Show success message
			success.value = true
			error.value = null

			// Emit sent event immediately
			emit("sent")

			// Close modal after 2 seconds so user sees success message
			setTimeout(() => {
				handleClose()
			}, 2000)
		} else {
			error.value =
				data.exc || data._server_messages || "Failed to send message"
		}
	} catch (err) {
		console.error("Send message error:", err)
		error.value = "Network error. Please try again."
	} finally {
		sending.value = false
	}
}
</script>

<template>
	<Dialog v-model="isOpen" :options="{ size: 'lg' }">
		<template #body>
			<div class="p-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Send Message to Council</h3>

				<div class="space-y-4">
					<!-- Subject Input -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Subject *</label>
						<Input
							v-model="subject"
							placeholder="Brief description of your message"
							:disabled="sending"
						/>
					</div>

					<!-- Message Content -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Message *</label>
						<textarea
							v-model="message"
							rows="8"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							placeholder="Type your message to the council..."
							:disabled="sending"
						></textarea>
					</div>

					<!-- Communication Type -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Communication Type</label>
						<select
							v-model="communicationType"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							:disabled="sending"
						>
							<option value="Email">Email</option>
							<option value="Phone">Phone Call Follow-up</option>
							<option value="Letter">Letter</option>
							<option value="Other">Other</option>
						</select>
					</div>

					<!-- Info Note -->
					<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
						<p class="text-sm text-blue-800">
							Your message will be sent to the council processing team.
							They typically respond within 2-3 business days.
						</p>
					</div>

					<!-- Success Display -->
					<div v-if="success" class="bg-green-50 border border-green-200 rounded-lg p-4">
						<div class="flex items-center">
							<svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
							</svg>
							<p class="text-sm text-green-800 font-medium">Message sent successfully! The council will respond within 2-3 business days.</p>
						</div>
					</div>

					<!-- Error Display -->
					<div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
						<p class="text-sm text-red-800">{{ error }}</p>
					</div>

					<!-- Buttons inside body to avoid overlay issues -->
					<div class="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
						<button
							@click="handleClose"
							:disabled="sending"
							class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
						>
							Cancel
						</button>
						<button
							@click="handleSend"
							:disabled="!isValid || sending"
							class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<span v-if="sending">Sending...</span>
							<span v-else>Send Message</span>
						</button>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>
