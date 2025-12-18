<script setup>
import { Button } from "frappe-ui"

const props = defineProps({
	currentStep: {
		type: Number,
		required: true,
	},
	totalSteps: {
		type: Number,
		required: true,
	},
	isLastStep: {
		type: Boolean,
		default: false,
	},
	canGoNext: {
		type: Boolean,
		default: true,
	},
	canSaveDraft: {
		type: Boolean,
		default: true,
	},
	isSaving: {
		type: Boolean,
		default: false,
	},
	isSubmitting: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["next", "previous", "save-draft", "submit"])

const handleNext = () => {
	emit("next")
}

const handlePrevious = () => {
	emit("previous")
}

const handleSaveDraft = () => {
	emit("save-draft")
}

const handleSubmit = () => {
	emit("submit")
}
</script>

<template>
	<div class="mt-8 pt-6 border-t border-gray-200">
		<div class="flex items-center justify-between">
			<!-- Previous Button -->
			<div>
				<Button
					v-if="currentStep > 0"
					@click="handlePrevious"
					variant="outline"
					:disabled="isSaving || isSubmitting"
				>
					<template #prefix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
						</svg>
					</template>
					Previous
				</Button>
			</div>

			<!-- Right side buttons -->
			<div class="flex items-center space-x-3">
				<!-- Save Draft Button - Only show after council, type, and process info steps -->
				<Button
					v-if="canSaveDraft"
					@click="handleSaveDraft"
					variant="outline"
					:loading="isSaving"
					:disabled="isSubmitting"
				>
					<template v-if="!isSaving" #prefix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
						</svg>
					</template>
					{{ isSaving ? 'Saving...' : 'Save Draft' }}
				</Button>

				<!-- Next or Submit Button -->
				<Button
					v-if="!isLastStep"
					@click="handleNext"
					variant="solid"
					theme="blue"
					:disabled="!canGoNext || isSaving || isSubmitting"
				>
					Next
					<template #suffix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
						</svg>
					</template>
				</Button>

				<Button
					v-else
					@click="handleSubmit"
					variant="solid"
					theme="green"
					:loading="isSubmitting"
					:disabled="!canGoNext || isSaving"
				>
					<template v-if="!isSubmitting" #prefix>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</template>
					{{ isSubmitting ? 'Submitting...' : 'Submit Application' }}
				</Button>
			</div>
		</div>

		<!-- Help Text -->
		<div class="mt-4 text-center">
			<p class="text-sm text-gray-500">
				Your progress is automatically saved. You can return to complete this application later.
			</p>
		</div>
	</div>
</template>
