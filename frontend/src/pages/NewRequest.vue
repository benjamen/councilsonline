<template>
    <div class="min-h-screen bg-gray-50">
        <RequestHeader title="New Application" @back="goBack">
            <template #actions>
                <Button
                    v-if="canSaveDraft"
                    @click="handleSaveDraft"
                    variant="outline"
                    theme="gray"
                    :loading="store.isSaving"
                >
                    Save Draft
                </Button>
                <Button
                    v-if="canSaveDraft"
                    @click="handleSaveAndClose"
                    variant="outline"
                    theme="gray"
                    :loading="store.isSaving"
                >
                    Save and Close
                </Button>
            </template>
        </RequestHeader>

        <div class="bg-white border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <RequestProgress
                    :current-step="store.currentStep"
                    :total-steps="totalSteps"
                    :step-titles="stepTitles"
                />
            </div>
        </div>

        <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                <!-- Skip Council step in single-tenant mode -->
                <div v-if="getCurrentStepTitle() === 'Type'">
                    <Step2RequestType
                        v-model="store.formData"
                        :request-types="requestTypes"
                        @type-selected="selectRequestType"
                    />
                </div>

                <div v-else-if="getCurrentStepTitle() === 'Process Info'">
                    <Step3ProcessInfo
                        :request-type-details="selectedRequestTypeDetails"
                        :council-name="getCouncilName()"
                        v-model="store.formData"
                        @continue="handleNext"
                    />
                </div>

                <!-- Review step: Show when at or beyond last step (defensive check for out-of-bounds) -->
                <div v-else-if="store.currentStep >= totalSteps - 1">
                    <ReviewStep
                        v-model="store.formData"
                        :request-type-config="store.requestTypeConfig"
                    />
                </div>

                <DynamicStepRenderer
                    v-else-if="usesConfigurableSteps && getCurrentStepConfig()"
                    :stepConfig="getCurrentStepConfig()"
                    v-model="store.formData"
                />

                <div v-else>
                    <h2 class="text-xl font-bold text-red-600">ERROR: Step {{ store.currentStep }} Fallback Hit!</h2>
                    <p class="mt-2">The dynamic step condition failed to render. Check the following values:</p>
                    <ul class="list-disc list-inside mt-2 space-y-1 text-sm text-gray-700">
                        <li><strong>Current Step Title:</strong> {{ getCurrentStepTitle() }}</li>
                        <li><strong>Request Config Loaded:</strong> {{ !!store.requestTypeConfig }}</li>
                        <li><strong>Calculated Total Steps:</strong> {{ totalSteps }}</li>
                        <li><strong>Uses Configurable Steps:</strong> {{ usesConfigurableSteps }}</li>
                        <li><strong>Current Step Config:</strong> {{ JSON.stringify(getCurrentStepConfig()) }}</li>
                    </ul>
                    <p class="mt-4 text-sm text-gray-500">If 'Current Step Config' is not null, the issue is likely within DynamicStepRenderer or component registration.</p>
                </div>
            </div>

            <!-- Council Meeting Banner (shown after Process Info step) -->
            <div
                v-if="shouldShowMeetingBanner"
                class="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6 shadow-sm"
            >
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-2">
                            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <h3 class="text-lg font-semibold text-gray-900">Council Meeting Available</h3>
                        </div>
                        <p class="text-sm text-gray-700 mb-3">
                            Schedule a meeting with council planners to discuss your application before submitting.
                            This optional step can help clarify requirements and improve your application.
                        </p>
                        <button
                            @click="handleBookMeeting"
                            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                        >
                            Request Council Meeting
                        </button>
                    </div>
                </div>
            </div>

            <StepNavigation
                :current-step="store.currentStep"
                :total-steps="totalSteps"
                :is-last-step="store.isLastStep"
                :can-go-next="canNavigateNext"
                :can-save-draft="canSaveDraft"
                :is-saving="store.isSaving"
                :is-submitting="store.isSubmitting"
                @next="handleNext"
                @previous="handlePrevious"
                @save-draft="handleSaveDraft"
                @submit="handleSubmit"
            />
        </main>

        <SaveDraftModal
            v-model:show="showSaveDraftModal"
            :draft-id="store.currentRequestId"
        />

        <ValidationErrorModal
            v-model:show="showValidationModal"
            :errors="validationErrors"
        />

        <BookMeetingModal
            v-model:show="showMeetingModal"
            :request-id="store.currentRequestId"
            :request-type-code="store.formData.request_type"
            :council-code="store.formData.council"
            @booked="handleMeetingBooked"
        />

        <SubmissionSuccessModal
            :open="showSubmissionSuccessModal"
            :request-number="submissionResult?.request_number"
            :request-id="submissionResult?.request_id"
            :sla-info="submissionResult?.sla_info"
            @close="showSubmissionSuccessModal = false"
            @view-request="handleViewRequestFromModal"
            @go-to-dashboard="handleGoToDashboardFromModal"
        />
    </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { computed, defineAsyncComponent, onMounted, ref, watch } from "vue"
import { onBeforeRouteLeave, useRoute, useRouter } from "vue-router"

import { useStepValidation } from "../composables/useStepValidation"
import { useUserProfile } from "../composables/useUserProfile"
import { useSiteCouncilStore } from "../stores/siteCouncil"
// Store and composables
import { useRequestStore } from "../stores/requestStore"

// Components
import RequestHeader from "../components/request/RequestHeader.vue"
import RequestProgress from "../components/request/RequestProgress.vue"
import StepNavigation from "../components/request/StepNavigation.vue"
// Lazy-loaded modals (load on demand to reduce bundle size)
const SaveDraftModal = defineAsyncComponent(
	() => import("../components/modals/SaveDraftModal.vue"),
)
const ValidationErrorModal = defineAsyncComponent(
	() => import("../components/modals/ValidationErrorModal.vue"),
)
const BookMeetingModal = defineAsyncComponent(
	() => import("../components/modals/BookMeetingModal.vue"),
)
const SubmissionSuccessModal = defineAsyncComponent(
	() => import("../components/modals/SubmissionSuccessModal.vue"),
)

// Step components
import Step2RequestType from "../components/request-steps/Step2RequestType.vue"
import Step3ProcessInfo from "../components/request-steps/Step3ProcessInfo.vue"
// Lazy-load DynamicStepRenderer (large component with complex logic)
const DynamicStepRenderer = defineAsyncComponent(
	() => import("../components/DynamicStepRenderer.vue"),
)
import ReviewStep from "../components/request-steps/ReviewStep.vue"

const route = useRoute()
const router = useRouter()

// Stores
const store = useRequestStore()
const councilStore = useSiteCouncilStore()

// Validation
const { errors: validationErrors, validateStep } = useStepValidation()

// UI state
const showSaveDraftModal = ref(false)
const showValidationModal = ref(false)
const showMeetingModal = ref(false)
const showSubmissionSuccessModal = ref(false)
const submissionResult = ref(null)
const requestTypes = ref({ loading: false, data: [] })
const selectedRequestTypeDetails = ref(null)

// Computed
const totalSteps = computed(() => {
	if (store.requestTypeConfig?.steps) {
		// Single-tenant: Type (0) + Process Info (1) + Dynamic Steps + Review (Last)
		return store.requestTypeConfig.steps.length + 3
	}
	return 3 // Default: Type, Process Info, Review (no Council step)
})

const stepTitles = computed(() => {
	// Single-tenant: Skip "Council" step
	const titles = ["Type", "Process Info"]
	if (store.requestTypeConfig?.steps) {
		titles.push(...store.requestTypeConfig.steps.map((s) => s.step_title))
	}
	titles.push("Review") // Always add Review as the last step
	return titles
})

const usesConfigurableSteps = computed(() => {
	return (
		store.requestTypeConfig?.steps && store.requestTypeConfig.steps.length > 0
	)
})

const canNavigateNext = computed(() => {
	// Always allow navigation for now (validation happens on attempt)
	return true
})

/**
 * Can only save draft after:
 * - Step 0: Request type selected
 * - Step 1: Process info read and confirmed
 * So allow saving from step 2 onwards (step index >= 2) - single-tenant
 */
const canSaveDraft = computed(() => {
	return store.currentStep >= 2
})

// Get configuration for current step (for dynamic validation)
const currentStepConfig = computed(() => {
	if (!store.requestTypeConfig?.steps) return null

	// Single-tenant: Steps 0-1 are fixed (Type, Process Info)
	// Dynamic steps start at index 2
	const dynamicStepIndex = store.currentStep - 2

	if (
		dynamicStepIndex >= 0 &&
		dynamicStepIndex < store.requestTypeConfig.steps.length
	) {
		return store.requestTypeConfig.steps[dynamicStepIndex]
	}

	return null
})

// Show meeting banner after Process Info (step 3) if council meetings are available
const shouldShowMeetingBanner = computed(() => {
	return (
		store.currentStep > 1 && // After Process Info step (single-tenant: step 1)
		store.currentStep < totalSteps.value - 1 && // Before Review step
		store.requestTypeConfig?.council_meeting_available === 1
	)
})

// Methods
function handleBookMeeting() {
	showMeetingModal.value = true
}

function handleMeetingBooked(meetingData) {
	console.log("Meeting booked:", meetingData)
	// Optionally show a success message or refresh data
}

function getCurrentStepTitle() {
	const index = store.currentStep
	if (index >= 0 && index < stepTitles.value.length) {
		return stepTitles.value[index]
	}
	return ""
}

function getCurrentStepConfig() {
	const index = store.currentStep
	const dynamicStepsStart = 2 // Single-tenant: 0=Type, 1=Process Info, 2+=Dynamic

	// Check if the current step is within the dynamic steps range (2 up to totalSteps - 2)
	// totalSteps - 1 is the Review step index.
	if (index < dynamicStepsStart || index >= totalSteps.value - 1) {
		return null
	}

	if (store.requestTypeConfig?.steps) {
		const stepIndex = index - dynamicStepsStart

		if (stepIndex >= 0 && stepIndex < store.requestTypeConfig.steps.length) {
			return store.requestTypeConfig.steps[stepIndex]
		}
	}

	return null
}

function getCouncilName() {
	// Single-tenant: always return the one council's name
	return councilStore.councilData?.council_name || "Council"
}

async function loadRequestTypes() {
	// Single-tenant: load request types for the site's council
	requestTypes.value.loading = true
	await councilStore.loadCouncil()
	requestTypes.value = {
		loading: false,
		data: councilStore.availableRequestTypes || [],
	}
}

async function selectRequestType(requestTypeCode) {
	// Store request type in formData (required for draft creation)
	store.updateField("request_type", requestTypeCode)

	// Load request type configuration
	await store.initialize(requestTypeCode)
	selectedRequestTypeDetails.value = store.requestTypeConfig

	// Validate config loaded
	if (!store.requestTypeConfig) {
		console.error("[NewRequest] Failed to load request type config")
		return
	}
}

async function handleNext() {
	// Single-tenant: Step 0 is Request Type Selection (no council step)
	if (store.currentStep === 0 && !store.formData.request_type) {
		alert("Please select a request type before continuing.")
		return
	}

	// Validate current step before allowing navigation (for dynamic steps)
	if (
		store.currentStep >= 1 &&
		usesConfigurableSteps.value &&
		currentStepConfig.value
	) {
		const isValid = await validateStep(currentStepConfig.value, store.formData)

		if (!isValid) {
			console.error("[NewRequest] Validation failed:", validationErrors.value)
			showValidationModal.value = true
			return // Block navigation
		}
	}

	// Auto-save after Process Info step (step 1 in single-tenant) to create draft
	// This ensures the request has an ID for features like "Book Meeting" and "Send Message"
	if (store.currentStep === 1 && !store.currentRequestId) {
		console.log("[NewRequest] Auto-saving draft after Process Info step...")
		console.log("[NewRequest] requestTypeConfig:", store.requestTypeConfig)
		console.log(
			"[NewRequest] usesConfigurableSteps:",
			usesConfigurableSteps.value,
		)
		console.log("[NewRequest] config steps:", store.requestTypeConfig?.steps)

		await store.saveDraft()
		console.log("[NewRequest] Draft saved with ID:", store.currentRequestId)

		// Only redirect if there are NO dynamic steps configured
		// If there are dynamic steps, user needs to fill them out first
		if (!usesConfigurableSteps.value) {
			// No dynamic steps - redirect to detail page
			if (store.currentRequestId) {
				console.log(
					"[NewRequest] No dynamic steps configured, redirecting to detail page...",
				)
				router.push(`/request/${store.currentRequestId}`)
				return // Don't call nextStep, the redirect will handle navigation
			}
		} else {
			console.log(
				"[NewRequest] Dynamic steps configured, continuing to next step...",
			)
		}
	}

	// Auto-save existing drafts before navigation
	if (store.currentRequestId) {
		await store.saveProgress()
	}

	// Don't advance beyond the last step (Review step should use Submit button)
	if (store.currentStep < totalSteps.value - 1) {
		store.nextStep()
	}
}

function handlePrevious() {
	store.previousStep()
}

async function handleSaveDraft() {
	try {
		await store.saveDraft()
		// Redirect to request detail page to show Send Message and Book Meeting buttons
		if (store.currentRequestId) {
			router.push(`/request/${store.currentRequestId}`)
		} else {
			showSaveDraftModal.value = true
		}
	} catch (error) {
		console.error("Failed to save draft:", error)
	}
}

async function handleSaveAndClose() {
	try {
		await store.saveDraft()
		store.reset() // Clear state after successful save
		// Redirect to dashboard
		router.push({ name: "Dashboard" })
	} catch (error) {
		console.error("Failed to save draft:", error)
		// Don't reset on error - preserve state for retry
	}
}

async function handleSubmit() {
	// Validation logic (omitted for brevity)

	try {
		const result = await store.submitRequest()

		// Store submission result for modal
		submissionResult.value = result

		// Show success modal with SLA info
		showSubmissionSuccessModal.value = true
	} catch (error) {
		console.error("Failed to submit request:", error)
	}
}

function goBack() {
	store.reset() // Clear all state before navigation
	router.push("/dashboard")
}

/**
 * Handle view request from success modal
 */
function handleViewRequestFromModal(requestId) {
	showSubmissionSuccessModal.value = false
	router.push(`/request/${requestId}`)
}

/**
 * Handle go to dashboard from success modal
 */
function handleGoToDashboardFromModal() {
	showSubmissionSuccessModal.value = false
	// Redirect to council-specific dashboard if available
	const councilCode = store.formData.council
	if (councilCode) {
		router.push(`/council/${councilCode}/dashboard`)
	} else {
		router.push("/dashboard")
	}
}

// Watch block for step changes
watch(
	() => store.currentStep,
	() => {
		// Step changed - trigger reactivity
	},
	{ immediate: true },
)

// Watch birth_date for age calculation (SPISC applications)
watch(
	() => store.formData.birth_date,
	(newDate) => {
		if (newDate && store.formData.request_type?.includes("SPISC")) {
			// Calculate age
			const today = new Date()
			const born = new Date(newDate)
			let age = today.getFullYear() - born.getFullYear()
			const m = today.getMonth() - born.getMonth()
			if (m < 0 || (m === 0 && today.getDate() < born.getDate())) {
				age--
			}

			// Update age in form data
			store.updateField("age", age)

			// Validate minimum age for SPISC (60 years)
			if (age < 60) {
				validationErrors.value["birth_date"] =
					"Applicant must be 60 years or older for SPISC"
			} else {
				// Clear birth_date validation errors if age is valid
				delete validationErrors.value["birth_date"]
			}
		}
	},
)

// Initialize
onMounted(async () => {
	const requestTypeCode = route.query.type
	const draftId = route.query.draft

	console.log(
		"[NewRequest] Initialization - type:",
		requestTypeCode,
		"draft:",
		draftId,
	)

	// If starting fresh request (no draft ID), ensure clean state
	if (!draftId && !route.query.draft) {
		store.reset() // Clear any lingering state
	}

	// Auto-fill user profile data for new requests (not drafts)
	if (!draftId) {
		const { getApplicationAutoFill, applyAutoFill } = useUserProfile()
		try {
			await getApplicationAutoFill()
			applyAutoFill(store.formData, {
				overrideExisting: false, // Don't overwrite user input
			})
		} catch (error) {
			console.warn(
				"[NewRequest] Failed to load user profile for auto-fill:",
				error,
			)
		}
	}

	// Handle draft loading (this takes precedence)
	if (draftId && requestTypeCode) {
		await store.initialize(requestTypeCode, draftId)
		selectedRequestTypeDetails.value = store.requestTypeConfig
		// Draft loading sets the step automatically, so return early
		return
	}

	// Single-tenant: Load council and request types once
	await loadRequestTypes()

	// Handle request type pre-selection from URL
	if (requestTypeCode && !draftId) {
		console.log("[NewRequest] Request type provided in URL:", requestTypeCode)

		// Initialize request type config
		await store.initialize(requestTypeCode)
		selectedRequestTypeDetails.value = store.requestTypeConfig
		store.updateField("request_type", requestTypeCode)

		// Skip directly to step 1 (Process Info) since we don't have Council step
		store.currentStep = 1
		console.log("[NewRequest] Advanced to step 1 (Process Info)")
	}
})

// Navigation guard - warn about unsaved changes
onBeforeRouteLeave((to, from, next) => {
	// Allow navigation if submitting or no draft exists
	if (store.isSubmitting || !store.currentRequestId) {
		store.reset() // Clear state when leaving without draft
		next()
		return
	}

	// Check if there are unsaved changes
	const hasChanges =
		store.formData &&
		Object.keys(store.formData).some(
			(key) =>
				store.formData[key] !== undefined &&
				store.formData[key] !== null &&
				store.formData[key] !== "",
		)

	if (
		hasChanges &&
		!confirm("You have unsaved changes. Do you want to leave without saving?")
	) {
		next(false) // Cancel navigation
	} else {
		// User confirmed or no unsaved changes
		if (!to.path.includes("/request/")) {
			store.reset() // Clear state when navigating away from requests
		}
		next() // Allow navigation
	}
})
</script>