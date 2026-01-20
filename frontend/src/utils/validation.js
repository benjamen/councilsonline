/**
 * Validation utilities for CouncilsOnline
 */

/**
 * Validates New Zealand phone numbers
 * Accepts landline and mobile formats:
 * - Mobile: 021, 022, 027, 028, 029 (with or without spaces)
 * - Landline: 03-09 area codes (with or without spaces)
 * - International format: +64 prefix
 *
 * @param {string} phone - Phone number to validate
 * @returns {Object} - { isValid: boolean, message: string, formatted: string }
 */
export function validateNZPhoneNumber(phone) {
	if (!phone || phone.trim() === "") {
		return {
			isValid: false,
			message: "Phone number is required",
			formatted: "",
		}
	}

	// Remove spaces, hyphens, and parentheses
	const cleaned = phone.replace(/[\s\-()]/g, "")

	// Check for international prefix
	const hasInternationalPrefix =
		cleaned.startsWith("+64") || cleaned.startsWith("0064")

	// Remove international prefix for validation
	let numberToValidate = cleaned
	if (cleaned.startsWith("+64")) {
		numberToValidate = "0" + cleaned.substring(3)
	} else if (cleaned.startsWith("0064")) {
		numberToValidate = "0" + cleaned.substring(4)
	}

	// Check if it contains only digits (after removing valid prefixes)
	if (!/^[0-9]+$/.test(numberToValidate)) {
		return {
			isValid: false,
			message:
				"Phone number should contain only numbers, spaces, hyphens, or parentheses",
			formatted: "",
		}
	}

	// Mobile number validation (021, 022, 027, 028, 029)
	const mobilePattern = /^0(2[1278]|29)[0-9]{6,8}$/
	if (mobilePattern.test(numberToValidate)) {
		// Format as: 021 234 5678
		const formatted = numberToValidate.replace(
			/^(0\d{2})(\d{3})(\d{4})$/,
			"$1 $2 $3",
		)
		return {
			isValid: true,
			message: "",
			formatted: formatted,
		}
	}

	// Landline validation (03-09 area codes)
	const landlinePattern = /^0[3-9][0-9]{7,8}$/
	if (landlinePattern.test(numberToValidate)) {
		// Format as: 09 123 4567 or 03 123 4567
		if (numberToValidate.length === 9) {
			const formatted = numberToValidate.replace(
				/^(0\d)(\d{3})(\d{4})$/,
				"$1 $2 $3",
			)
			return {
				isValid: true,
				message: "",
				formatted: formatted,
			}
		} else if (numberToValidate.length === 10) {
			const formatted = numberToValidate.replace(
				/^(0\d)(\d{3})(\d{5})$/,
				"$1 $2 $3",
			)
			return {
				isValid: true,
				message: "",
				formatted: formatted,
			}
		}
	}

	// Too short
	if (numberToValidate.length < 9) {
		return {
			isValid: false,
			message: "Phone number is too short. NZ phone numbers are 9-10 digits.",
			formatted: "",
		}
	}

	// Too long
	if (numberToValidate.length > 11) {
		return {
			isValid: false,
			message: "Phone number is too long. NZ phone numbers are 9-10 digits.",
			formatted: "",
		}
	}

	// Invalid format
	return {
		isValid: false,
		message:
			"Invalid NZ phone number. Mobile numbers start with 02, landlines with 03-09.",
		formatted: "",
	}
}

/**
 * Format phone number for display
 * @param {string} phone - Phone number to format
 * @returns {string} - Formatted phone number
 */
export function formatPhoneNumber(phone) {
	const validation = validateNZPhoneNumber(phone)
	return validation.formatted || phone
}

/**
 * Validates email address
 * @param {string} email - Email address to validate
 * @returns {Object} - { isValid: boolean, message: string }
 */
export function validateEmail(email) {
	if (!email || email.trim() === "") {
		return {
			isValid: false,
			message: "Email address is required",
		}
	}

	const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
	if (!emailPattern.test(email)) {
		return {
			isValid: false,
			message: "Please enter a valid email address",
		}
	}

	return {
		isValid: true,
		message: "",
	}
}

/**
 * Validates NZBN (New Zealand Business Number)
 * @param {string} nzbn - NZBN to validate
 * @returns {Object} - { isValid: boolean, message: string }
 */
export function validateNZBN(nzbn) {
	if (!nzbn || nzbn.trim() === "") {
		return { isValid: true, message: "" } // Optional field
	}

	const cleaned = nzbn.replace(/[\s\-]/g, "")

	if (!/^\d{13}$/.test(cleaned)) {
		return {
			isValid: false,
			message: "NZBN must be exactly 13 digits",
		}
	}

	return {
		isValid: true,
		message: "",
	}
}

/**
 * Validates password strength
 * @param {string} password - Password to validate
 * @returns {Object} - { isValid: boolean, message: string, strength: string }
 */
export function validatePassword(password) {
	if (!password || password.trim() === "") {
		return {
			isValid: false,
			message: "Password is required",
			strength: "none",
		}
	}

	if (password.length < 8) {
		return {
			isValid: false,
			message: "Password must be at least 8 characters long",
			strength: "weak",
		}
	}

	let strength = "weak"
	let strengthScore = 0

	// Check for length
	if (password.length >= 12) strengthScore++

	// Check for uppercase
	if (/[A-Z]/.test(password)) strengthScore++

	// Check for lowercase
	if (/[a-z]/.test(password)) strengthScore++

	// Check for numbers
	if (/[0-9]/.test(password)) strengthScore++

	// Check for special characters
	if (/[^A-Za-z0-9]/.test(password)) strengthScore++

	if (strengthScore >= 4) strength = "strong"
	else if (strengthScore >= 2) strength = "medium"

	return {
		isValid: true,
		message: "",
		strength: strength,
	}
}
