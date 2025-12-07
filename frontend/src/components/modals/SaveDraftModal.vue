<script setup>
import { computed } from 'vue'
import { Dialog } from 'frappe-ui'

const props = defineProps({
	show: {
		type: Boolean,
		required: true
	},
	draftId: {
		type: String,
		default: null
	}
})

const emit = defineEmits(['update:show', 'close'])

const isOpen = computed({
	get: () => props.show,
	set: (value) => emit('update:show', value)
})

const handleClose = () => {
	emit('update:show', false)
	emit('close')
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
				<p v-if="draftId" class="text-xs text-gray-400 font-mono bg-gray-50 px-3 py-2 rounded">
					Draft ID: {{ draftId }}
				</p>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-end space-x-2">
				<button
					@click="handleClose"
					class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
					Continue Editing
				</button>
			</div>
		</template>
	</Dialog>
</template>
