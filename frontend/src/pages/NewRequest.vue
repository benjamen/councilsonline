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
                        :council-name="store.formData.council || 'Council'"
                        :request-type-name="store.formData.request_type || 'Application'"
                        :application-fee="formatApplicationFee(store.requestTypeConfig?.base_fee)"
                        :is-resource-consent="isResourceConsent"
                        :step-configs="store.requestTypeConfig?.steps || []"
                        :uses-configurable-steps="usesConfigurableSteps"
                        :request-type-details="store.requestTypeConfig"
                    />
                </div>

                <DynamicStepRenderer
                    v-else-if="usesConfigurableSteps && getCurrentStepConfig()"
                    :stepConfig="getCurrentStepConfig()"
                    v-model="store.formData"
                />

                <div v-else class="text-center py-12">
                    <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100 mb-4">
                        <svg class="h-8 w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Unable to Load This Step</h3>
                    <p class="text-sm text-gray-600 mb-6">
                        We're having trouble loading this step. Please try refreshing or go back to continue your application.
                    </p>
                    <div class="flex gap-3 justify-center">
                        <button
                            @click="location.reload()"
                            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                        >
                            Refresh Page
                        </button>
                        <button
                            @click="handlePrevious"
                            class="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
                        >
                            Go Back
                        </button>
                        <button
                            @click="router.push('/dashboard')"
                            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                        >
                            Return to Dashboard
                        </button>
                    </div>
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
import { computed, defineAsyncComponent, onMounted } from "vue"
import { useRouter } from "vue-router"

// Composables - all logic extracted for maintainability
import { useRequestModals } from "../composables/useRequestModals"
import { useStepConfiguration } from "../composables/useStepConfiguration"
import { useRequestFormNavigation } from "../composables/useRequestFormNavigation"
import { useRequestLifecycle } from "../composables/useRequestLifecycle"
import { useRequestStore } from "../stores/requestStore"

// Components
import RequestHeader from "../components/request/RequestHeader.vue"
import RequestProgress from "../components/request/RequestProgress.vue"
import StepNavigation from "../components/request/StepNavigation.vue"

// Lazy-loaded modals
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
const DynamicStepRenderer = defineAsyncComponent(
	() => import("../components/DynamicStepRenderer.vue"),
)
import ReviewStep from "../components/request-steps/ReviewStep.vue"

const router = useRouter()
const store = useRequestStore()

// Step configuration (totalSteps, stepTitles, etc.)
const {
	totalSteps,
	stepTitles,
	usesConfigurableSteps,
	shouldShowMeetingBanner,
	getCurrentStepTitle,
	getCurrentStepConfig,
	getCouncilName,
} = useStepConfiguration()

// Modal management
const {
	showSaveDraftModal,
	showValidationModal,
	showMeetingModal,
	showSubmissionSuccessModal,
	submissionResult,
	handleBookMeeting,
	handleMeetingBooked,
	handleSaveDraft,
	handleSaveAndClose,
	handleSubmit,
	handleViewRequestFromModal,
	handleGoToDashboardFromModal,
} = useRequestModals()

// Navigation (with validation callback)
const {
	canNavigateNext,
	canSaveDraft,
	validationErrors,
	handleNext,
	handlePrevious,
	goBack,
} = useRequestFormNavigation({
	getCurrentStepConfig,
	totalSteps,
	usesConfigurableSteps,
	onValidationError: () => {
		showValidationModal.value = true
	},
})

// Lifecycle (initialization, route guards, request types)
const {
	requestTypes,
	selectedRequestTypeDetails,
	selectRequestType,
	initialize,
	setupRouteGuard,
	setupAgeValidation,
} = useRequestLifecycle()

// Setup route guard and age calculation (validation comes from field config)
setupRouteGuard()
setupAgeValidation()

// Check if current request type is Resource Consent
const isResourceConsent = computed(() => {
	const requestType = store.formData.request_type || ""
	return requestType.toLowerCase().includes("resource consent")
})

// Format application fee for display
const formatApplicationFee = (fee) => {
	if (!fee && fee !== 0) return "Free"
	if (fee === 0) return "Free"
	// Check if it's Philippines (PHP) or NZ (NZD)
	const isPH = store.formData.council?.includes("TAYTAY") || store.formData.council?.includes("PH")
	const currency = isPH ? "PHP" : "NZD"
	const symbol = isPH ? "₱" : "$"
	return `${symbol}${Number(fee).toLocaleString("en", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency}`
}

// Initialize on mount
onMounted(() => {
	initialize()
})
</script>