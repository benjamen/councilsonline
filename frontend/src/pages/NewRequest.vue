<template>
    <div class="min-h-screen bg-gray-50">
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
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
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
                    </div>
                </div>
            </div>
        </header>

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
                <div v-if="getCurrentStepTitle() === 'Council'">
                    <Step1CouncilSelection
                        v-model="store.formData"
                        @council-change="onCouncilChange"
                    />
                </div>

                <div v-else-if="getCurrentStepTitle() === 'Type'">
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

                <div v-else-if="getCurrentStepTitle() === 'Review'">
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
                            <h3 class="text-lg font-semibold text-gray-900">Pre-Application Meeting Available</h3>
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
import BookMeetingModal from '../components/modals/BookMeetingModal.vue'

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
const showMeetingModal = ref(false)
const requestTypes = ref({ loading: false, data: [] })
const selectedRequestTypeDetails = ref(null)

// Computed
const totalSteps = computed(() => {
    if (store.requestTypeConfig?.steps) {
        // Council (0) + Type (1) + Process Info (2) + Dynamic Steps + Review (Last)
        return store.requestTypeConfig.steps.length + 4
    }
    return 4 // Default: Council, Type, Process Info, Review
})

const stepTitles = computed(() => {
    const titles = ['Council', 'Type', 'Process Info']
    if (store.requestTypeConfig?.steps) {
        titles.push(...store.requestTypeConfig.steps.map(s => s.step_title))
    }
    titles.push('Review') // Always add Review as the last step
    return titles
})

const usesConfigurableSteps = computed(() => {
    return store.requestTypeConfig?.steps && store.requestTypeConfig.steps.length > 0
})

const canNavigateNext = computed(() => {
    // Always allow navigation for now (validation happens on attempt)
    return true
})

/**
 * Can only save draft after:
 * - Step 1: Council selected
 * - Step 2: Request type selected
 * - Step 3: Process info read and confirmed
 * So allow saving from step 4 onwards (step index >= 3)
 */
const canSaveDraft = computed(() => {
    return store.currentStep >= 3
})

// Show meeting banner after Process Info (step 3) if council meetings are available
const shouldShowMeetingBanner = computed(() => {
    return store.currentStep > 2 && // After Process Info step
           store.currentStep < totalSteps.value - 1 && // Before Review step
           store.requestTypeConfig?.council_meeting_available === 1
})

// Methods
function handleBookMeeting() {
    showMeetingModal.value = true
}

function handleMeetingBooked(meetingData) {
    console.log('Meeting booked:', meetingData)
    // Optionally show a success message or refresh data
}

function getCurrentStepTitle() {
    const index = store.currentStep
    if (index >= 0 && index < stepTitles.value.length) {
        return stepTitles.value[index]
    }
    return ''
}

function getCurrentStepConfig() {
    const index = store.currentStep
    const dynamicStepsStart = 3;

    // Check if the current step is within the dynamic steps range (3 up to totalSteps - 2)
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
    const councilCode = store.formData.council
    if (!councilCode) return ''

    const council = councilStore.councils.find(c => c.council_code === councilCode)
    return council?.council_name || councilCode
}

async function onCouncilChange(councilCode) {
    // Load request types for selected council
    requestTypes.value.loading = true
    await councilStore.loadRequestTypesForCouncil(councilCode)
    requestTypes.value = {
        loading: false,
        data: councilStore.requestTypes || []
    }
}

async function selectRequestType(requestTypeCode) {
    // Store request type in formData (required for draft creation)
    store.updateField('request_type', requestTypeCode)

    // Load request type configuration
    await store.initialize(requestTypeCode)
    selectedRequestTypeDetails.value = store.requestTypeConfig

    // Validate config loaded
    if (!store.requestTypeConfig) {
        console.error('[NewRequest] Failed to load request type config')
        return
    }
}

async function handleNext() {
    // Validation for Step 0 (Council Selection)
    if (store.currentStep === 0 && !store.formData.council) {
        alert('Please select a council before continuing.')
        return
    }

    // Validation for Step 1 (Request Type Selection)
    if (store.currentStep === 1 && !store.formData.request_type) {
        alert('Please select a request type before continuing.')
        return
    }

    // Auto-save after Process Info step (step 2) to create draft
    // This ensures the request has an ID for features like "Book Meeting" and "Send Message"
    if (store.currentStep === 2 && !store.currentRequestId) {
        console.log('[NewRequest] Auto-saving draft after Process Info step...')
        console.log('[NewRequest] requestTypeConfig:', store.requestTypeConfig)
        console.log('[NewRequest] usesConfigurableSteps:', usesConfigurableSteps.value)
        console.log('[NewRequest] config steps:', store.requestTypeConfig?.steps)

        await store.saveDraft()
        console.log('[NewRequest] Draft saved with ID:', store.currentRequestId)

        // Only redirect if there are NO dynamic steps configured
        // If there are dynamic steps, user needs to fill them out first
        if (!usesConfigurableSteps.value) {
            // No dynamic steps - redirect to detail page
            if (store.currentRequestId) {
                console.log('[NewRequest] No dynamic steps configured, redirecting to detail page...')
                router.push(`/request/${store.currentRequestId}`)
                return // Don't call nextStep, the redirect will handle navigation
            }
        } else {
            console.log('[NewRequest] Dynamic steps configured, continuing to next step...')
        }
    }

    // Auto-save existing drafts before navigation
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
        // Redirect to request detail page to show Send Message and Book Meeting buttons
        if (store.currentRequestId) {
            router.push(`/request/${store.currentRequestId}`)
        } else {
            showSaveDraftModal.value = true
        }
    } catch (error) {
        console.error('Failed to save draft:', error)
    }
}

async function handleSaveAndClose() {
    try {
        await store.saveDraft()
        // Redirect to dashboard
        router.push({ name: 'Dashboard' })
    } catch (error) {
        console.error('Failed to save draft:', error)
    }
}

async function handleSubmit() {
    // Validation logic (omitted for brevity)

    try {
        await store.submitRequest()
        // Redirect to council-specific dashboard instead of generic dashboard
        const councilCode = store.formData.council
        if (councilCode) {
            router.push(`/council/${councilCode}/dashboard`)
        } else {
            router.push('/dashboard')
        }
    } catch (error) {
        console.error('Failed to submit request:', error)
    }
}

function goBack() {
    router.push('/dashboard')
}

// Watch block for step changes
watch(() => store.currentStep, () => {
    // Step changed - trigger reactivity
}, { immediate: true })

// Initialize
onMounted(async () => {
    const requestTypeCode = route.query.type
    const draftId = route.query.draft
    const councilCode = route.query.council
    const isLocked = route.query.locked === 'true'

    // Handle draft loading (this takes precedence)
    if (draftId && requestTypeCode) {
        await store.initialize(requestTypeCode, draftId)
        selectedRequestTypeDetails.value = store.requestTypeConfig
        // Draft loading sets the step automatically, so return early
        return
    }

    // Handle council pre-selection from URL (e.g., from council website)
    if (councilCode && !draftId) {
        store.updateField('council', councilCode)

        // Pre-load request types for this council
        await onCouncilChange(councilCode)

        // If council is locked (from council website), skip to step 1 (Type selection)
        if (isLocked) {
            store.currentStep = 1

            // If request type is also provided, load config and skip to step 2 (Process Info)
            if (requestTypeCode) {
                await store.initialize(requestTypeCode)
                selectedRequestTypeDetails.value = store.requestTypeConfig
                store.updateField('request_type', requestTypeCode)
                store.currentStep = 2
            }
        }
    } else if (requestTypeCode && !draftId && !councilCode) {
        // Just request type provided (unusual case, but handle it)
        await store.initialize(requestTypeCode)
        selectedRequestTypeDetails.value = store.requestTypeConfig
        store.updateField('request_type', requestTypeCode)
    }
})
</script>