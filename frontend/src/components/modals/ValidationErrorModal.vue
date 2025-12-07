<script setup>
import { computed } from 'vue'
import { Dialog } from 'frappe-ui'

const props = defineProps({
	show: {
		type: Boolean,
		required: true
	},
	errors: {
		type: Object,
		default: () => ({})
	}
})

const emit = defineEmits(['update:show', 'close'])

const isOpen = computed({
	get: () => props.show,
	set: (value) => emit('update:show', value)
})

const errorList = computed(() => {
	return Object.entries(props.errors).map(([field, message]) => ({
		field,
		message
	}))
})

const handleClose = () => {
	emit('update:show', false)
	emit('close')
}
</script>

<template>
	<Dialog v-model="isOpen" :options="{ size: 'md' }">
		<template #body>
			<div class="py-4">
				<div class="flex items-start mb-4">
					<div class="flex-shrink-0">
						<div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
							<svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
							</svg>
						</div>
					</div>
					<div class="ml-4">
						<h3 class="text-lg font-medium text-gray-900 mb-1">Validation Errors</h3>
						<p class="text-sm text-gray-500">
							Please fix the following errors before continuing:
						</p>
					</div>
				</div>

				<div v-if="errorList.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
					<ul class="list-disc list-inside space-y-2">
						<li
							v-for="(error, index) in errorList"
							:key="index"
							class="text-sm text-red-800"
						>
							<span class="font-medium">{{ error.field }}:</span>
							{{ error.message }}
						</li>
					</ul>
				</div>

				<div v-else class="text-sm text-gray-500 text-center py-4">
					No validation errors found.
				</div>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-end">
				<button
					@click="handleClose"
					class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
				>
					Close and Fix Errors
				</button>
			</div>
		</template>
	</Dialog>
</template>
