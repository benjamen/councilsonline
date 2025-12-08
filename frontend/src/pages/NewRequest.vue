<template>
	<div class="min-h-screen bg-gray-50">
		<!-- Header -->
		<header class="bg-white shadow-sm border-b border-gray-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex items-center justify-between py-4">
					<div class="flex items-center space-x-3">
						<button @click="goBack" class="text-gray-500 hover:text-gray-700">
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
							</svg>
						</button>
						<div>
							<h1 class="text-xl font-bold text-gray-900">New Application</h1>
							<p class="text-sm text-gray-500">Step {{ store.currentStep + 1 }} of {{ totalSteps }}</p>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<Button @click="handleSaveDraft" variant="outline" theme="gray" :loading="store.isSaving">
							Save Draft
						</Button>
					</div>
				</div>
			</div>
		</header>

		<!-- Progress Indicator -->
		<div class="bg-white border-b border-gray-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
				<RequestProgress
					:current-step="store.currentStep"
					:total-steps="totalSteps"
					:step-titles="stepTitles"
				/>
			</div>
		</div>

		<!-- Main Content -->
		<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
				<!-- Council Selection Step -->
				<div v-if="getCurrentStepTitle() === 'Council'">
					<Step1CouncilSelection
						v-model="store.formData"
						@council-change="onCouncilChange"
					/>
				</div>

				<!-- Request Type Selection Step -->
				<div v-else-if="getCurrentStepTitle() === 'Type'">
					<Step2RequestType
						v-model="store.formData"
						:request-types="requestTypes"
						@type-selected="selectRequestType"
					/>
				</div>

				<!-- Process Info Step -->
				<div v-else-if="getCurrentStepTitle() === 'Process Info'">
					<Step3ProcessInfo
						:request-type-details="selectedRequestTypeDetails"
						:council-name="getCouncilName()"
						v-model="store.formData"
					/>
				</div>

				<!-- Dynamic Steps (configured request types) -->
				<DynamicStepRenderer
					v-else-if="usesConfigurableSteps && getCurrentStepConfig()"
					:stepConfig="getCurrentStepConfig()"
					v-model="store.formData"
				/>

				<!-- Review Step -->
				<div v-else-if="getCurrentStepTitle() === 'Review'">
					<ReviewStep
						v-model="store.formData"
						:request-type-config="store.requestTypeConfig"
					/>
				</div>
			</div>

			<!-- Navigation -->
			<StepNavigation
				:current-step="store.currentStep"
				:total-steps="totalSteps"
				:is-last-step="store.isLastStep"
				:can-go-next="canNavigateNext"
				:is-saving="store.isSaving"
				:is-submitting="store.isSubmitting"
				@next="handleNext"
				@previous="handlePrevious"
				@save-draft="handleSaveDraft"
				@submit="handleSubmit"
			/>
		</main>

		<!-- Modals -->
		<SaveDraftModal
			v-model:show="showSaveDraftModal"
			:draft-id="store.currentRequestId"
		/>

		<ValidationErrorModal
			v-model:show="showValidationModal"
			:errors="validationErrors"
		/>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button } from 'frappe-ui'

// Store and composables
import { useRequestStore } from '../stores/requestStore'
import { useCouncilStore } from '../stores/councilStore'
import { useStepValidation } from '../composables/useStepValidation'

// Components
import RequestProgress from '../components/request/RequestProgress.vue'
import StepNavigation from '../components/request/StepNavigation.vue'
import SaveDraftModal from '../components/modals/SaveDraftModal.vue'
import ValidationErrorModal from '../components/modals/ValidationErrorModal.vue'

// Step components
import Step1CouncilSelection from '../components/request-steps/Step1CouncilSelection.vue'
import Step2RequestType from '../components/request-steps/Step2RequestType.vue'
import Step3ProcessInfo from '../components/request-steps/Step3ProcessInfo.vue'
import DynamicStepRenderer from '../components/DynamicStepRenderer.vue'
import ReviewStep from '../components/request-steps/ReviewStep.vue'

const route = useRoute()
const router = useRouter()

// Stores
const store = useRequestStore()
const councilStore = useCouncilStore()

// Validation
const { errors: validationErrors, validateStep } = useStepValidation()

// UI state
const showSaveDraftModal = ref(false)
const showValidationModal = ref(false)
const requestTypes = ref({ loading: false, data: [] })
const selectedRequestTypeDetails = ref(null)

// Computed
const totalSteps = computed(() => {
	if (store.requestTypeConfig?.steps) {
		return store.requestTypeConfig.steps.length + 3 // council + type + process info
	}
	return 9 // default fallback
})

const stepTitles = computed(() => {
	const titles = ['Council', 'Type', 'Process Info']
	if (store.requestTypeConfig?.steps) {
		titles.push(...store.requestTypeConfig.steps.map(s => s.step_title))
	}
	return titles
})

const usesConfigurableSteps = computed(() => {
	return store.requestTypeConfig?.steps && store.requestTypeConfig.steps.length > 0
})

const canNavigateNext = computed(() => {
	// Always allow navigation for now (validation happens on attempt)
	return true
})

// Methods
function getCurrentStepTitle() {
	const index = store.currentStep
	if (index === 0) return 'Council'
	if (index === 1) return 'Type'
	if (index === 2) return 'Process Info'
	if (index === totalSteps.value - 1) return 'Review'

	// Dynamic step
	if (store.requestTypeConfig?.steps) {
		const stepIndex = index - 3
		return store.requestTypeConfig.steps[stepIndex]?.step_title
	}
	return ''
}

function getCurrentStepConfig() {
	const index = store.currentStep
	if (index <= 2 || index === totalSteps.value - 1) return null

	if (store.requestTypeConfig?.steps) {
		const stepIndex = index - 3
		return store.requestTypeConfig.steps[stepIndex]
	}
	return null
}

function getCouncilName() {
	const councilCode = store.formData.council
	if (!councilCode) return ''

	const council = councilStore.councils.find(c => c.council_code === councilCode)
	return council?.council_name || councilCode
}

async function onCouncilChange(councilCode) {
	// Load request types for selected council
	console.log('[NewRequest] onCouncilChange called with:', councilCode)
	requestTypes.value.loading = true
	await councilStore.loadRequestTypesForCouncil(councilCode)
	console.log('[NewRequest] councilStore.requestTypes:', councilStore.requestTypes)
	requestTypes.value = {
		loading: false,
		data: councilStore.requestTypes || []
	}
	console.log('[NewRequest] requestTypes.value set to:', requestTypes.value)
}

async function selectRequestType(requestTypeCode) {
	// Load request type configuration
	await store.initialize(requestTypeCode)
	selectedRequestTypeDetails.value = store.requestTypeConfig
}

async function handleNext() {
	// Validate current step if it's a dynamic step
	const stepConfig = getCurrentStepConfig()
	if (stepConfig) {
		const isValid = await validateStep(stepConfig, store.formData)
		if (!isValid) {
			showValidationModal.value = true
			return
		}
	}

	// Auto-save before navigation
	if (store.currentRequestId) {
		await store.saveProgress()
	}

	store.nextStep()
}

function handlePrevious() {
	store.previousStep()
}

async function handleSaveDraft() {
	try {
		await store.saveDraft()
		showSaveDraftModal.value = true
	} catch (error) {
		console.error('Failed to save draft:', error)
	}
}

async function handleSubmit() {
	// Validate all steps
	if (store.requestTypeConfig?.steps) {
		for (const stepConfig of store.requestTypeConfig.steps) {
			const isValid = await validateStep(stepConfig, store.formData)
			if (!isValid) {
				showValidationModal.value = true
				return
			}
		}
	}

	try {
		await store.submitRequest()
		router.push('/dashboard')
	} catch (error) {
		console.error('Failed to submit request:', error)
	}
}

function goBack() {
	router.push('/dashboard')
}

// Initialize
onMounted(async () => {
	const requestTypeCode = route.query.type
	const draftId = route.query.draft

	if (requestTypeCode) {
		await store.initialize(requestTypeCode, draftId)
		selectedRequestTypeDetails.value = store.requestTypeConfig
	}
})
</script>
