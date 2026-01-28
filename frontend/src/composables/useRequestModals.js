import { ref } from "vue"
import { useRouter } from "vue-router"
import { call } from "frappe-ui"
import { useRequestStore } from "../stores/requestStore"
import {
	extractPersonalInfo,
	validateAndExtractAddress,
	ADDRESS_FIELD_CONFIGS,
} from "../utils/fieldMappers"

/**
 * Composable for managing request form modals
 * Handles save draft, validation error, meeting booking, and submission success modals
 *
 * @returns {Object} Modal state and handlers
 */
export function useRequestModals() {
	const router = useRouter()
	const store = useRequestStore()

	// Modal visibility state
	const showSaveDraftModal = ref(false)
	const showValidationModal = ref(false)
	const showMeetingModal = ref(false)
	const showSubmissionSuccessModal = ref(false)

	// Submission result data
	const submissionResult = ref(null)

	/**
	 * Open meeting booking modal
	 */
	function handleBookMeeting() {
		showMeetingModal.value = true
	}

	/**
	 * Handle meeting booked callback
	 * @param {Object} meetingData - Data about the booked meeting
	 */
	function handleMeetingBooked(meetingData) {
		console.log("Meeting booked:", meetingData)
		showMeetingModal.value = false
	}

	/**
	 * Show validation errors modal
	 * @param {Object} errors - Validation errors to display
	 */
	function showValidationErrors(errors) {
		showValidationModal.value = true
	}

	/**
	 * Handle save draft action
	 */
	async function handleSaveDraft() {
		try {
			await store.saveDraft()
			if (store.currentRequestId) {
				router.push(`/request/${store.currentRequestId}`)
			} else {
				showSaveDraftModal.value = true
			}
		} catch (error) {
			console.error("Failed to save draft:", error)
		}
	}

	/**
	 * Handle save and close action
	 */
	async function handleSaveAndClose() {
		try {
			await store.saveDraft()
			store.reset()
			router.push({ name: "Dashboard" })
		} catch (error) {
			console.error("Failed to save draft:", error)
		}
	}

	/**
	 * Handle form submission
	 */
	async function handleSubmit() {
		try {
			const result = await store.submitRequest()
			submissionResult.value = result
			showSubmissionSuccessModal.value = true

			// After successful submission, auto-save personal info to profile
			await savePersonalInfoToProfile()

			// Also save any addresses marked for profile saving
			await saveAddressesToProfile()
		} catch (error) {
			console.error("Failed to submit request:", error)
		}
	}

	/**
	 * Save personal information to user profile after submission
	 * Auto-saves all personal details, identity docs, economic status, and payment preferences
	 * @returns {Object} Result with success status and saved fields count
	 */
	async function savePersonalInfoToProfile() {
		const formData = store.formData
		if (!formData) return { success: false, fields_count: 0 }

		// Use utility function to extract personal info fields
		const personalInfo = extractPersonalInfo(formData)

		// Only save if we have data
		if (Object.keys(personalInfo).length === 0) {
			return { success: true, fields_count: 0 }
		}

		try {
			const result = await call(
				"councilsonline.api.auth.save_personal_info_to_profile",
				personalInfo,
			)
			if (result && result.fields_count > 0) {
				console.log(`Saved ${result.fields_count} fields to user profile`)
			}
			return { success: true, fields_count: result?.fields_count || 0 }
		} catch (error) {
			// Don't fail submission if profile save fails
			console.error("Failed to save personal info to profile:", error)
			return { success: false, error: error.message }
		}
	}

	/**
	 * Save addresses to user profile if marked for saving
	 * Looks for address fields with _save_to_profile flag
	 * @returns {Object} Result with saved and failed addresses
	 */
	async function saveAddressesToProfile() {
		const formData = store.formData
		if (!formData) return { savedAddresses: [], failedAddresses: [] }

		const savedAddresses = []
		const failedAddresses = []

		// Check each configured address field
		for (const [fieldName, config] of Object.entries(ADDRESS_FIELD_CONFIGS)) {
			const addressData = formData[fieldName]

			// Skip if no data or not marked for profile saving
			if (!addressData || typeof addressData !== "object") continue
			if (!addressData._save_to_profile) continue

			// Validate and extract address data
			const validation = validateAndExtractAddress(addressData, config)

			if (!validation.valid) {
				failedAddresses.push({
					field: fieldName,
					reason: validation.error,
				})
				console.warn(
					`Skipping address from ${fieldName}: ${validation.error}`,
				)
				continue
			}

			try {
				await call("councilsonline.api.auth.add_user_property", {
					...validation.data,
					is_default: false,
				})
				savedAddresses.push(fieldName)
				console.log(`Property saved to profile from field: ${fieldName}`)
			} catch (error) {
				failedAddresses.push({
					field: fieldName,
					reason: error.message || "Unknown error",
				})
				// Don't fail submission if property save fails
				console.error(`Failed to save property from ${fieldName}:`, error)
			}
		}

		// Log summary
		if (failedAddresses.length > 0) {
			console.warn("Some addresses failed to save:", failedAddresses)
		}

		return { savedAddresses, failedAddresses }
	}

	/**
	 * Handle view request from success modal
	 * @param {string} requestId - Request ID to view
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
		const councilCode = store.formData.council
		if (councilCode) {
			router.push(`/council/${councilCode}/dashboard`)
		} else {
			router.push("/dashboard")
		}
	}

	return {
		// Modal visibility
		showSaveDraftModal,
		showValidationModal,
		showMeetingModal,
		showSubmissionSuccessModal,

		// Data
		submissionResult,

		// Handlers
		handleBookMeeting,
		handleMeetingBooked,
		showValidationErrors,
		handleSaveDraft,
		handleSaveAndClose,
		handleSubmit,
		handleViewRequestFromModal,
		handleGoToDashboardFromModal,
	}
}
