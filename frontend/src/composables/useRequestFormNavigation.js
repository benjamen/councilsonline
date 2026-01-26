import { computed } from "vue"
import { useRouter } from "vue-router"
import { useRequestStore } from "../stores/requestStore"
import { useStepValidation } from "./useStepValidation"

/**
 * Composable for request form navigation logic
 * Handles step navigation, validation, auto-save, and draft management
 *
 * @param {Object} options - Configuration options
 * @param {Function} options.getCurrentStepConfig - Function to get current step config
 * @param {import('vue').ComputedRef} options.totalSteps - Total number of steps
 * @param {import('vue').ComputedRef} options.usesConfigurableSteps - Whether using configurable steps
 * @param {Function} options.onValidationError - Callback for validation errors
 * @returns {Object} Navigation functions and computed properties
 */
export function useRequestFormNavigation(options = {}) {
	const router = useRouter()
	const store = useRequestStore()
	const { errors: validationErrors, validateStep } = useStepValidation()

	const {
		getCurrentStepConfig = () => null,
		totalSteps = computed(() => 3),
		usesConfigurableSteps = computed(() => false),
		onValidationError = () => {},
	} = options

	/**
	 * Whether user can navigate to next step
	 * Always returns true as validation happens on attempt
	 */
	const canNavigateNext = computed(() => true)

	/**
	 * Whether user can save draft
	 * Only allowed after step 2 (single-tenant mode)
	 */
	const canSaveDraft = computed(() => store.currentStep >= 2)

	/**
	 * Navigate to next step with validation and auto-save
	 */
	async function handleNext() {
		// Step 0: Require request type selection
		if (store.currentStep === 0 && !store.formData.request_type) {
			alert("Please select a request type before continuing.")
			return
		}

		// Check for existing validation errors (e.g., age validation for SPISC)
		// These are set by watchers and should block navigation
		const existingErrors = { ...validationErrors.value }

		// Validate current step for dynamic steps
		if (
			store.currentStep >= 1 &&
			usesConfigurableSteps.value &&
			getCurrentStepConfig()
		) {
			const stepConfig = getCurrentStepConfig()
			const isValid = await validateStep(stepConfig, store.formData)

			// Merge back existing errors that validateStep may have cleared
			Object.assign(validationErrors.value, existingErrors)

			if (!isValid || Object.keys(existingErrors).length > 0) {
				console.error("[Navigation] Validation failed:", validationErrors.value)
				onValidationError(validationErrors.value)
				return // Block navigation
			}
		}

		// Auto-save after Process Info step to create draft
		if (store.currentStep === 1 && !store.currentRequestId) {
			console.log("[Navigation] Auto-saving draft after Process Info step...")
			await store.saveDraft()
			console.log("[Navigation] Draft saved with ID:", store.currentRequestId)

			// Redirect if no dynamic steps configured
			if (!usesConfigurableSteps.value && store.currentRequestId) {
				console.log(
					"[Navigation] No dynamic steps, redirecting to detail page...",
				)
				router.push(`/request/${store.currentRequestId}`)
				return
			}
		}

		// Auto-save existing drafts before navigation
		if (store.currentRequestId) {
			await store.saveProgress()
		}

		// Advance to next step (but not beyond Review step)
		if (store.currentStep < totalSteps.value - 1) {
			store.nextStep()
		}
	}

	/**
	 * Navigate to previous step
	 */
	function handlePrevious() {
		store.previousStep()
	}

	/**
	 * Go back to dashboard
	 */
	function goBack() {
		store.reset()
		router.push("/dashboard")
	}

	return {
		canNavigateNext,
		canSaveDraft,
		validationErrors,
		handleNext,
		handlePrevious,
		goBack,
	}
}
