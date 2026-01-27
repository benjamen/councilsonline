import { ref } from "vue"
import { useRouter } from "vue-router"
import { call } from "frappe-ui"
import { useRequestStore } from "../stores/requestStore"

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

			// After successful submission, save any addresses marked for profile saving
			await saveAddressesToProfile()
		} catch (error) {
			console.error("Failed to submit request:", error)
		}
	}

	/**
	 * Save addresses to user profile if marked for saving
	 * Looks for address fields with _save_to_profile flag
	 */
	async function saveAddressesToProfile() {
		const formData = store.formData
		if (!formData) return

		// Check common address field names that might have _save_to_profile flag
		const addressFields = [
			"residential_address",
			"address",
			"property_address",
			"applicant_address",
		]

		for (const fieldName of addressFields) {
			const addressData = formData[fieldName]
			if (
				addressData &&
				typeof addressData === "object" &&
				addressData._save_to_profile
			) {
				try {
					await call("councilsonline.api.auth.add_user_property", {
						street: addressData.address_line,
						barangay: addressData.barangay,
						municipality: addressData.municipality,
						province: addressData.province,
						zip_code: addressData.zip_code,
						is_default: false,
					})
					console.log(`Property saved to profile from field: ${fieldName}`)
				} catch (error) {
					// Don't fail submission if property save fails
					console.error(`Failed to save property from ${fieldName}:`, error)
				}
			}
		}
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
