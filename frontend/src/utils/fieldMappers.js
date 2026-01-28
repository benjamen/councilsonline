/**
 * Field mapping utilities for profile synchronization
 * Centralizes field definitions and extraction logic
 */

// Personal info fields that can be synced to profile
export const PERSONAL_INFO_FIELDS = [
	// Personal Details
	"birth_date",
	"sex",
	"civil_status",
	// Contact
	"mobile_number",
	// Address
	"address_line",
	"barangay",
	"municipality",
	"province",
	"postal_postcode",
	// Identity Documents
	"philsys_id",
	"sss_number",
	"osca_id",
	// Economic Status
	"monthly_income",
	"income_source",
	"household_size",
	"living_arrangement",
	"is_4ps_beneficiary",
	// Payment Preferences
	"payment_preference",
	"bank_name",
	"bank_account_number",
	"bank_account_holder",
]

// Address field configurations for different request types
export const ADDRESS_FIELD_CONFIGS = {
	residential_address: {
		required: ["address_line", "municipality"],
		mapping: {
			street: "address_line",
			barangay: "barangay",
			municipality: "municipality",
			province: "province",
			zip_code: "zip_code",
		},
	},
	address: {
		required: ["address_line"],
		mapping: {
			street: "address_line",
			barangay: "barangay",
			municipality: "municipality",
			province: "province",
			zip_code: "zip_code",
		},
	},
	property_address: {
		required: ["street"],
		mapping: {
			street: "street",
			barangay: "suburb",
			municipality: "city",
			province: "province",
			zip_code: "postcode",
		},
	},
	applicant_address: {
		required: ["address_line"],
		mapping: {
			street: "address_line",
			barangay: "barangay",
			municipality: "municipality",
			province: "province",
			zip_code: "zip_code",
		},
	},
}

/**
 * Check if a value is meaningful (not null, undefined, or empty string)
 * @param {*} val - Value to check
 * @returns {boolean}
 */
export function hasValue(val) {
	if (val === null || val === undefined || val === "") return false
	if (Array.isArray(val)) return val.length > 0
	return true
}

/**
 * Extract personal info fields from form data
 * @param {Object} formData - Form data object
 * @returns {Object} Personal info fields with values
 */
export function extractPersonalInfo(formData) {
	if (!formData) return {}

	return PERSONAL_INFO_FIELDS.reduce((acc, field) => {
		const value = formData[field]
		if (value !== undefined && value !== null && value !== "") {
			acc[field] = value
		}
		return acc
	}, {})
}

/**
 * Validate and extract address data for profile saving
 * @param {Object} addressData - Address data object
 * @param {Object} config - Address field configuration
 * @returns {Object} Result with valid flag, data, and any errors
 */
export function validateAndExtractAddress(addressData, config) {
	if (!addressData || typeof addressData !== "object") {
		return { valid: false, error: "Invalid address data" }
	}

	// Check required fields
	const missingFields = config.required.filter((f) => !hasValue(addressData[f]))
	if (missingFields.length > 0) {
		return {
			valid: false,
			error: `Missing required fields: ${missingFields.join(", ")}`,
		}
	}

	// Extract and map fields
	const extractedData = {}
	for (const [apiField, sourceField] of Object.entries(config.mapping)) {
		if (hasValue(addressData[sourceField])) {
			extractedData[apiField] = addressData[sourceField]
		}
	}

	return { valid: true, data: extractedData }
}
