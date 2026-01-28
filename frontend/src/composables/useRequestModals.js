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
	 */
	async function savePersonalInfoToProfile() {
		const formData = store.formData
		if (!formData) return

		// Collect personal info fields from formData
		const personalInfo = {}

		// Personal Details
		if (formData.birth_date) personalInfo.birth_date = formData.birth_date
		if (formData.sex) personalInfo.sex = formData.sex
		if (formData.civil_status) personalInfo.civil_status = formData.civil_status

		// Contact
		if (formData.mobile_number) personalInfo.mobile_number = formData.mobile_number

		// Address
		if (formData.address_line) personalInfo.address_line = formData.address_line
		if (formData.barangay) personalInfo.barangay = formData.barangay
		if (formData.municipality) personalInfo.municipality = formData.municipality
		if (formData.province) personalInfo.province = formData.province

		// Identity Documents
		if (formData.philsys_id) personalInfo.philsys_id = formData.philsys_id
		if (formData.sss_number) personalInfo.sss_number = formData.sss_number
		if (formData.osca_id) personalInfo.osca_id = formData.osca_id

		// Economic Status
		if (formData.monthly_income !== undefined) personalInfo.monthly_income = formData.monthly_income
		if (formData.income_source) personalInfo.income_source = formData.income_source
		if (formData.household_size !== undefined) personalInfo.household_size = formData.household_size
		if (formData.living_arrangement) personalInfo.living_arrangement = formData.living_arrangement
		if (formData.is_4ps_beneficiary !== undefined) personalInfo.is_4ps_beneficiary = formData.is_4ps_beneficiary

		// Payment Preferences
		if (formData.payment_preference) personalInfo.payment_preference = formData.payment_preference
		if (formData.bank_name) personalInfo.bank_name = formData.bank_name
		if (formData.bank_account_number) personalInfo.bank_account_number = formData.bank_account_number
		if (formData.bank_account_holder) personalInfo.bank_account_holder = formData.bank_account_holder

		// Only save if we have data
		if (Object.keys(personalInfo).length > 0) {
			try {
				const result = await call("councilsonline.api.auth.save_personal_info_to_profile", personalInfo)
				if (result && result.fields_count > 0) {
					console.log(`Saved ${result.fields_count} fields to user profile`)
				}
			} catch (error) {
				// Don't fail submission if profile save fails
				console.error("Failed to save personal info to profile:", error)
			}
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
