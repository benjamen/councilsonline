<script setup>
import { computed } from 'vue'

const props = defineProps({
	currentStep: {
		type: Number,
		required: true
	},
	totalSteps: {
		type: Number,
		required: true
	},
	stepTitles: {
		type: Array,
		default: () => []
	}
})

const progressPercentage = computed(() => {
	if (props.totalSteps === 0) return 0
	return Math.round(((props.currentStep + 1) / props.totalSteps) * 100)
})

const getStepStatus = (stepIndex) => {
	if (stepIndex < props.currentStep) return 'completed'
	if (stepIndex === props.currentStep) return 'current'
	return 'upcoming'
}
</script>

<template>
	<div class="mb-8">
		<!-- Progress Bar -->
		<div class="relative mb-6">
			<div class="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
				<div
					:style="{ width: progressPercentage + '%' }"
					class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-600 transition-all duration-500"
				></div>
			</div>
			<div class="flex justify-between mt-2">
				<span class="text-sm font-medium text-gray-700">
					{{ stepTitles[currentStep] || `Step ${currentStep + 1}` }}
				</span>
				<span class="text-sm font-medium text-gray-700">
					{{ progressPercentage }}% Complete
				</span>
			</div>
		</div>

		<!-- Step Indicators (temporarily hidden) -->
		<!-- <nav aria-label="Progress" v-if="stepTitles.length > 0">
			<ol class="flex items-center">
				<li
					v-for="(title, index) in stepTitles"
					:key="index"
					:class="[
						'relative',
						index !== stepTitles.length - 1 ? 'pr-8 sm:pr-20 flex-1' : ''
					]"
				>
					<div
						v-if="index !== stepTitles.length - 1"
						class="absolute inset-0 flex items-center"
						aria-hidden="true"
					>
						<div
							:class="[
								'h-0.5 w-full',
								getStepStatus(index) === 'completed' ? 'bg-blue-600' : 'bg-gray-200'
							]"
						></div>
					</div>

					<div class="relative flex items-center group">
						<span
							:class="[
								'h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold',
								getStepStatus(index) === 'completed'
									? 'bg-blue-600 text-white'
									: getStepStatus(index) === 'current'
									? 'bg-white border-2 border-blue-600 text-blue-600'
									: 'bg-white border-2 border-gray-300 text-gray-500'
							]"
						>
							<template v-if="getStepStatus(index) === 'completed'">
								<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
										clip-rule="evenodd"
									/>
								</svg>
							</template>
							<template v-else>
								{{ index + 1 }}
							</template>
						</span>

						<span
							v-if="title"
							:class="[
								'ml-3 text-sm font-medium hidden sm:block',
								getStepStatus(index) === 'current'
									? 'text-blue-600'
									: getStepStatus(index) === 'completed'
									? 'text-gray-900'
									: 'text-gray-500'
							]"
						>
							{{ title }}
						</span>
					</div>
				</li>
			</ol>
		</nav> -->
	</div>
</template>
