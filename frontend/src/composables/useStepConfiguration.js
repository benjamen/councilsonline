import { computed } from "vue"
import { useRequestStore } from "../stores/requestStore"
import { useSiteCouncilStore } from "../stores/siteCouncil"

/**
 * Composable for request step configuration
 * Manages step titles, totals, and dynamic step configuration
 *
 * @returns {Object} Step configuration computed properties and methods
 */
export function useStepConfiguration() {
	const store = useRequestStore()
	const councilStore = useSiteCouncilStore()

	/**
	 * Total number of steps including fixed and dynamic steps
	 * Single-tenant: Type (0) + Process Info (1) + Dynamic Steps + Review (Last)
	 */
	const totalSteps = computed(() => {
		if (store.requestTypeConfig?.steps) {
			return store.requestTypeConfig.steps.length + 3
		}
		return 3 // Default: Type, Process Info, Review
	})

	/**
	 * Array of step titles for progress indicator
	 */
	const stepTitles = computed(() => {
		const titles = ["Type", "Process Info"]
		if (store.requestTypeConfig?.steps) {
			titles.push(...store.requestTypeConfig.steps.map((s) => s.step_title))
		}
		titles.push("Review")
		return titles
	})

	/**
	 * Whether the request type uses configurable dynamic steps
	 */
	const usesConfigurableSteps = computed(() => {
		return (
			store.requestTypeConfig?.steps && store.requestTypeConfig.steps.length > 0
		)
	})

	/**
	 * Current step configuration (for dynamic validation)
	 */
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

	/**
	 * Whether to show the council meeting banner
	 */
	const shouldShowMeetingBanner = computed(() => {
		return (
			store.currentStep > 1 &&
			store.currentStep < totalSteps.value - 1 &&
			store.requestTypeConfig?.council_meeting_available === 1
		)
	})

	/**
	 * Get the title of the current step
	 * @returns {string} Current step title
	 */
	function getCurrentStepTitle() {
		const index = store.currentStep
		if (index >= 0 && index < stepTitles.value.length) {
			return stepTitles.value[index]
		}
		return ""
	}

	/**
	 * Get the configuration for the current step
	 * @returns {Object|null} Step configuration or null for fixed steps
	 */
	function getCurrentStepConfig() {
		const index = store.currentStep
		const dynamicStepsStart = 2 // Single-tenant: 0=Type, 1=Process Info, 2+=Dynamic

		// Return null for fixed steps and Review step
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

	/**
	 * Get the council name for display
	 * @returns {string} Council name
	 */
	function getCouncilName() {
		return councilStore.councilData?.council_name || "Council"
	}

	return {
		// Computed
		totalSteps,
		stepTitles,
		usesConfigurableSteps,
		currentStepConfig,
		shouldShowMeetingBanner,

		// Methods
		getCurrentStepTitle,
		getCurrentStepConfig,
		getCouncilName,
	}
}
