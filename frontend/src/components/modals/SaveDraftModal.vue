<script setup>
import { Dialog } from "frappe-ui"
import { computed } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const props = defineProps({
	show: {
		type: Boolean,
		required: true,
	},
	draftId: {
		type: String,
		default: null,
	},
})

const emit = defineEmits(["update:show", "close"])

const isOpen = computed({
	get: () => props.show,
	set: (value) => emit("update:show", value),
})

const handleClose = () => {
	emit("update:show", false)
	emit("close")
}

const handleViewDraft = () => {
	if (props.draftId) {
		emit("update:show", false)
		router.push(`/request/${props.draftId}`)
	}
}
</script>

<template>
	<Dialog v-model="isOpen" :options="{ size: 'sm' }">
		<template #body>
			<div class="text-center py-6">
				<div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
					<svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
				</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Draft Saved Successfully</h3>
				<p class="text-sm text-gray-500 mb-4">
					Your progress has been saved. You can return to complete this application later.
				</p>
				<div v-if="draftId" class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
					<p class="text-xs text-gray-500 mb-2">Draft ID</p>
					<p class="text-sm font-mono text-gray-900 mb-3">{{ draftId }}</p>
					<button
						@click="handleViewDraft"
						class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline"
					>
						<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
						</svg>
						View Draft Details
					</button>
				</div>

				<!-- Buttons inside body to avoid overlay issues -->
				<div class="flex justify-between w-full space-x-3 px-4">
					<button
						@click="handleClose"
						class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						Close
					</button>
					<button
						@click="handleClose"
						class="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						Continue Editing
					</button>
				</div>
			</div>
		</template>
	</Dialog>
</template>
