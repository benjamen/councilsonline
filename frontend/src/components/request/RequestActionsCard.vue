<template>
	<div>
		<!-- Quick Actions -->
		<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>

			<div class="space-y-3">
				<Button
					v-if="workflowState === 'Draft'"
					@click="$emit('edit-draft')"
					variant="solid"
					theme="blue"
					class="w-full justify-start"
				>
					<template #prefix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
						</svg>
					</template>
					Edit Draft
				</Button>

				<Button
					@click="$emit('send-message')"
					variant="outline"
					class="w-full justify-start"
				>
					<template #prefix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
						</svg>
					</template>
					Send Message
				</Button>

				<Button
					@click="$emit('print-application')"
					variant="outline"
					class="w-full justify-start"
				>
					<template #prefix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
						</svg>
					</template>
					Print Application
				</Button>

				<Button
					v-if="workflowState === 'Draft'"
					@click="$emit('delete-draft')"
					variant="outline"
					class="w-full justify-start text-red-600 hover:text-red-700"
					:loading="deleting"
				>
					<template #prefix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 1 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
						</svg>
					</template>
					Delete Draft
				</Button>
			</div>
		</div>

		<!-- Contact Info -->
		<div class="bg-blue-50 rounded-lg border border-blue-200 p-6 mt-6">
			<h3 class="text-sm font-semibold text-blue-900 mb-3">Need Help?</h3>
			<p class="text-xs text-blue-800 mb-4">Contact {{ councilDetails.data?.council_name || 'the council' }} for assistance with your application.</p>
			<div v-if="councilDetails.loading" class="text-xs text-blue-800">
				Loading contact information...
			</div>
			<div v-else-if="councilDetails.data" class="space-y-2 text-xs text-blue-900">
				<div v-if="councilDetails.data.contact_email" class="flex items-center space-x-2">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
					</svg>
					<a :href="`mailto:${councilDetails.data.contact_email}`" class="hover:underline">
						{{ councilDetails.data.contact_email }}
					</a>
				</div>
				<div v-if="councilDetails.data.contact_phone" class="flex items-center space-x-2">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
					</svg>
					<a :href="`tel:${councilDetails.data.contact_phone}`" class="hover:underline">
						{{ councilDetails.data.contact_phone }}
					</a>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Button } from "frappe-ui"

defineProps({
	workflowState: {
		type: String,
		required: true,
	},
	councilDetails: {
		type: Object,
		required: true,
		default: () => ({ loading: false, data: null }),
	},
	deleting: {
		type: Boolean,
		default: false,
	},
})

defineEmits(["edit-draft", "send-message", "print-application", "delete-draft"])
</script>
