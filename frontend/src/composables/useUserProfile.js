/**
 * Composable for User Profile management and auto-fill functionality
 * Loads user profile data and provides auto-fill for application forms
 */

import { computed, ref } from "vue"

const userProfile = ref(null)
const loading = ref(false)
const error = ref(null)

export function useUserProfile() {
	/**
	 * Fetch user profile from backend
	 */
	const loadUserProfile = async () => {
		loading.value = true
		error.value = null

		try {
			const headers = {
				"Content-Type": "application/json",
			}

			// Add CSRF token if available
			if (window.csrf_token) {
				headers["X-Frappe-CSRF-Token"] = window.csrf_token
			}

			const response = await fetch(
				"/api/method/councilsonline.api.get_user_profile",
				{
					method: "GET",
					headers: headers,
					credentials: "include",
				},
			)

			const result = await response.json()

			// Backend returns profile data directly in result.message
			// No need to check for success flag
			if (result.message) {
				userProfile.value = result.message
				return userProfile.value
			} else {
				throw new Error("Failed to load profile")
			}
		} catch (err) {
			error.value = err.message
			console.error("Error loading user profile:", err)
			return null
		} finally {
			loading.value = false
		}
	}

	/**
	 * Get default property
	 */
	const defaultProperty = computed(() => {
		if (!userProfile.value?.properties) return null
		return (
			userProfile.value.properties.find((p) => p.is_default) ||
			userProfile.value.properties[0]
		)
	})

	/**
	 * Get default council
	 */
	const defaultCouncil = computed(() => {
		if (!userProfile.value?.councils) return null
		return (
			userProfile.value.councils.find((c) => c.is_default) ||
			userProfile.value.councils[0]
		)
	})

	/**
	 * Get auto-fill data for Resource Consent Application
	 * Returns object with all fields that can be auto-filled from profile
	 */
	const getApplicationAutoFill = () => {
		if (!userProfile.value) return {}

		const profile = userProfile.value
		const autoFillData = {}

		// STEP 1: Council Selection
		if (defaultCouncil.value) {
			autoFillData.council = defaultCouncil.value.council_id
			autoFillData.council_name = defaultCouncil.value.council_name
		}

		// STEP 4: Applicant & Proposal (FRD Step 1)
		// Basic Applicant Details
		autoFillData.requester_name = profile.full_name
		autoFillData.requester_email = profile.user // Email from User account
		autoFillData.requester_phone = profile.phone
		autoFillData.requester_type = profile.user_role // 'Individual' or 'Agent'

		// Individual: Postal Address
		if (profile.user_role === "Individual") {
			if (profile.postal_street) {
				autoFillData.applicant_address =
					`${profile.postal_street}, ${profile.postal_suburb || ""}, ${profile.postal_city || ""} ${profile.postal_postcode || ""}`.trim()
			}
		}

		// Agent: Business Details
		if (profile.user_role === "Agent") {
			autoFillData.agent_required = true
			autoFillData.agent_id = profile.user
			autoFillData.agent_company = profile.company_name
			autoFillData.agent_email = profile.business_email || profile.user
			autoFillData.agent_phone = profile.business_phone || profile.phone

			if (profile.business_street) {
				autoFillData.agent_address =
					`${profile.business_street}, ${profile.business_suburb || ""}, ${profile.business_city || ""} ${profile.business_postcode || ""}`.trim()
			}

			// Agent preferences
			if (profile.default_communication_route) {
				autoFillData.correspondence_recipient =
					profile.default_communication_route === "Agent Only"
						? "Agent"
						: "Both"
			}

			if (profile.default_invoice_recipient) {
				autoFillData.invoice_responsible_party =
					profile.default_invoice_recipient
			}
		}

		// Default Property
		if (defaultProperty.value) {
			const prop = defaultProperty.value
			autoFillData.property =
				`${prop.street}, ${prop.suburb || ""}, ${prop.city || ""} ${prop.postcode || ""}`.trim()
			autoFillData.property_address = autoFillData.property
			autoFillData.property_legal_description = prop.legal_description
			autoFillData.ownership_status = prop.ownership_status
		}

		// Communication Preferences
		if (profile.comm_email || profile.comm_phone || profile.comm_post) {
			autoFillData.communication_preferences = {
				email: profile.comm_email || false,
				phone: profile.comm_phone || false,
				post: profile.comm_post || false,
			}
		}

		// Invoice Preference
		if (profile.invoice_preference) {
			autoFillData.invoice_delivery_method = profile.invoice_preference
		}

		// ===== PHILIPPINES PERSONAL INFORMATION (SPISC) =====

		// Personal Details (Philippines)
		if (profile.birth_date) {
			autoFillData.birth_date = profile.birth_date
		}
		if (profile.sex) {
			autoFillData.sex = profile.sex
		}
		if (profile.civil_status) {
			autoFillData.civil_status = profile.civil_status
		}

		// Mobile number (use phone)
		if (profile.phone) {
			autoFillData.mobile_number = profile.phone
		}

		// PH Address fields
		if (profile.postal_street) {
			autoFillData.address_line = profile.postal_street
		}
		if (profile.postal_suburb) {
			autoFillData.barangay = profile.postal_suburb
		}
		if (profile.postal_city) {
			autoFillData.municipality = profile.postal_city
		}
		if (profile.postal_province) {
			autoFillData.province = profile.postal_province
		}

		// Identity Documents
		if (profile.philsys_id) {
			autoFillData.philsys_id = profile.philsys_id
		}
		if (profile.sss_number) {
			autoFillData.sss_number = profile.sss_number
		}
		if (profile.osca_id) {
			autoFillData.osca_id = profile.osca_id
		}

		// Economic Status
		if (profile.monthly_income !== undefined && profile.monthly_income !== null) {
			autoFillData.monthly_income = profile.monthly_income
		}
		if (profile.income_source) {
			autoFillData.income_source = profile.income_source
		}
		if (profile.household_size !== undefined && profile.household_size !== null) {
			autoFillData.household_size = profile.household_size
		}
		if (profile.living_arrangement) {
			autoFillData.living_arrangement = profile.living_arrangement
		}
		if (profile.is_4ps_beneficiary !== undefined) {
			autoFillData.is_4ps_beneficiary = profile.is_4ps_beneficiary
		}

		// Payment Preferences
		if (profile.preferred_payment_method) {
			autoFillData.payment_preference = profile.preferred_payment_method
		}
		if (profile.bank_name) {
			autoFillData.bank_name = profile.bank_name
		}
		if (profile.bank_account_number) {
			autoFillData.bank_account_number = profile.bank_account_number
		}
		if (profile.bank_account_holder) {
			autoFillData.bank_account_holder = profile.bank_account_holder
		}

		return autoFillData
	}

	/**
	 * Apply auto-fill to form data
	 * @param {Object} formData - The form data object to update
	 * @param {Object} options - Options for auto-fill behavior
	 * @returns {Object} Updated form data
	 */
	const applyAutoFill = (formData, options = {}) => {
		const {
			overrideExisting = false, // If true, override existing values
			fieldsToSkip = [], // Array of field names to skip
		} = options

		const autoFillData = getApplicationAutoFill()

		Object.keys(autoFillData).forEach((key) => {
			// Skip if field is in skip list
			if (fieldsToSkip.includes(key)) return

			// Skip if field already has value and we're not overriding
			if (!overrideExisting && formData[key]) return

			// Apply auto-fill value
			formData[key] = autoFillData[key]
		})

		return formData
	}

	/**
	 * Get all properties for dropdown/selection
	 */
	const getAllProperties = computed(() => {
		return userProfile.value?.properties || []
	})

	/**
	 * Get all councils for dropdown/selection
	 */
	const getAllCouncils = computed(() => {
		return userProfile.value?.councils || []
	})

	/**
	 * Get all clients (Agent only)
	 */
	const getAllClients = computed(() => {
		return userProfile.value?.clients || []
	})

	/**
	 * Check if profile is complete
	 */
	const isProfileComplete = computed(() => {
		if (!userProfile.value) return false

		const profile = userProfile.value

		// Basic required fields
		const hasBasicInfo = profile.full_name && profile.phone && profile.user_role

		// Role-specific completeness
		if (profile.user_role === "Individual") {
			return (
				hasBasicInfo &&
				(profile.properties?.length > 0 || false) &&
				(profile.councils?.length > 0 || false)
			)
		} else if (profile.user_role === "Agent") {
			return (
				hasBasicInfo &&
				profile.company_name &&
				(profile.councils?.length > 0 || false)
			)
		}

		return hasBasicInfo
	})

	/**
	 * Get profile completion percentage
	 */
	const profileCompletionPercentage = computed(() => {
		if (!userProfile.value) return 0

		const profile = userProfile.value
		let completed = 0
		let total = 0

		// Basic fields (weight: 30%)
		const basicFields = ["full_name", "phone", "user_role"]
		basicFields.forEach((field) => {
			total++
			if (profile[field]) completed++
		})

		// Contact preferences (weight: 10%)
		total++
		if (profile.comm_email || profile.comm_phone || profile.comm_post)
			completed++

		// Properties (weight: 30%)
		total++
		if (profile.properties && profile.properties.length > 0) completed++

		// Councils (weight: 20%)
		total++
		if (profile.councils && profile.councils.length > 0) completed++

		// Role-specific (weight: 10%)
		if (profile.user_role === "Agent") {
			total++
			if (profile.company_name) completed++
		} else {
			total++
			if (profile.postal_street) completed++
		}

		return Math.round((completed / total) * 100)
	})

	return {
		userProfile,
		loading,
		error,
		loadUserProfile,
		getApplicationAutoFill,
		applyAutoFill,
		defaultProperty,
		defaultCouncil,
		getAllProperties,
		getAllCouncils,
		getAllClients,
		isProfileComplete,
		profileCompletionPercentage,
	}
}

// Export singleton instance for global state
let instance = null

export function useGlobalUserProfile() {
	if (!instance) {
		instance = useUserProfile()
	}
	return instance
}
