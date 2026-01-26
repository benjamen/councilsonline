import { ref, watch } from "vue"
import { onBeforeRouteLeave, useRoute, useRouter } from "vue-router"
import { useRequestStore } from "../stores/requestStore"
import { useSiteCouncilStore } from "../stores/siteCouncil"
import { useUserProfile } from "./useUserProfile"

/**
 * Composable for request form lifecycle management
 * Handles initialization, draft loading, auto-fill, and navigation guards
 *
 * @param {Object} options - Configuration options
 * @param {Function} options.onRequestTypeSelected - Callback when request type is selected
 * @returns {Object} Lifecycle state and methods
 */
export function useRequestLifecycle(options = {}) {
	const route = useRoute()
	const router = useRouter()
	const store = useRequestStore()
	const councilStore = useSiteCouncilStore()

	const { onRequestTypeSelected = () => {} } = options

	// State
	const requestTypes = ref({ loading: false, data: [] })
	const selectedRequestTypeDetails = ref(null)

	/**
	 * Load available request types for the council
	 */
	async function loadRequestTypes() {
		requestTypes.value.loading = true
		await councilStore.loadCouncil()
		requestTypes.value = {
			loading: false,
			data: councilStore.availableRequestTypes || [],
		}
	}

	/**
	 * Handle request type selection
	 * @param {string} requestTypeCode - Selected request type code
	 */
	async function selectRequestType(requestTypeCode) {
		store.updateField("request_type", requestTypeCode)
		await store.initialize(requestTypeCode)
		selectedRequestTypeDetails.value = store.requestTypeConfig

		if (!store.requestTypeConfig) {
			console.error("[Lifecycle] Failed to load request type config")
			return
		}

		onRequestTypeSelected(requestTypeCode)
	}

	/**
	 * Initialize the request form
	 * Handles draft loading, auto-fill, and URL parameters
	 */
	async function initialize() {
		const requestTypeCode = route.query.type
		const draftId = route.query.draft

		console.log(
			"[Lifecycle] Initialization - type:",
			requestTypeCode,
			"draft:",
			draftId,
		)

		// Clean state for fresh requests
		if (!draftId && !route.query.draft) {
			store.reset()
		}

		// Auto-fill user profile data for new requests
		if (!draftId) {
			const { getApplicationAutoFill, applyAutoFill } = useUserProfile()
			try {
				await getApplicationAutoFill()
				applyAutoFill(store.formData, { overrideExisting: false })
			} catch (error) {
				console.warn(
					"[Lifecycle] Failed to load user profile for auto-fill:",
					error,
				)
			}
		}

		// Handle draft loading (takes precedence)
		if (draftId && requestTypeCode) {
			await store.initialize(requestTypeCode, draftId)
			selectedRequestTypeDetails.value = store.requestTypeConfig
			return
		}

		// Load council and request types
		await loadRequestTypes()

		// Handle request type pre-selection from URL
		if (requestTypeCode && !draftId) {
			console.log("[Lifecycle] Request type provided in URL:", requestTypeCode)
			await store.initialize(requestTypeCode)
			selectedRequestTypeDetails.value = store.requestTypeConfig
			store.updateField("request_type", requestTypeCode)
			store.currentStep = 1 // Skip to Process Info
			console.log("[Lifecycle] Advanced to step 1 (Process Info)")
		}
	}

	/**
	 * Setup navigation guard for unsaved changes
	 */
	function setupRouteGuard() {
		onBeforeRouteLeave((to, from, next) => {
			// Allow navigation if submitting or no draft exists
			if (store.isSubmitting || !store.currentRequestId) {
				store.reset()
				next()
				return
			}

			// Check for unsaved changes
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
				!confirm(
					"You have unsaved changes. Do you want to leave without saving?",
				)
			) {
				next(false)
			} else {
				if (!to.path.includes("/request/")) {
					store.reset()
				}
				next()
			}
		})
	}

	/**
	 * Setup age calculation watcher for applications with birth_date field
	 * Auto-calculates age from birth_date for display purposes
	 * Note: Age validation is now configured in Request Type field config (validation: "min_age:60")
	 */
	function setupAgeValidation() {
		watch(
			() => store.formData.birth_date,
			(newDate) => {
				if (newDate) {
					const today = new Date()
					const born = new Date(newDate)
					let age = today.getFullYear() - born.getFullYear()
					const m = today.getMonth() - born.getMonth()
					if (m < 0 || (m === 0 && today.getDate() < born.getDate())) {
						age--
					}
					store.updateField("age", age)
				}
			},
		)
	}

	return {
		// State
		requestTypes,
		selectedRequestTypeDetails,

		// Methods
		loadRequestTypes,
		selectRequestType,
		initialize,
		setupRouteGuard,
		setupAgeValidation,
	}
}
