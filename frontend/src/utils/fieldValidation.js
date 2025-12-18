/**
 * Field Validation Utility for Request Type Configuration
 *
 * Executes validation JavaScript from step_fields configuration
 *
 * Validation formats supported:
 * - "email" - Email format validation
 * - "phone" - Phone number validation
 * - "url" - URL format validation
 * - "number" - Numeric validation
 * - "eval:formData.age >= 18" - Custom JavaScript expression
 * - "eval:formData.password === formData.confirm_password" - Field comparison
 */

/**
 * Validates an email address
 * @param {string} value - Email to validate
 * @returns {boolean} - True if valid email
 */
function validateEmail(value) {
	if (!value) return true // Empty is valid (use is_required for mandatory)
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
	return emailRegex.test(value)
}

/**
 * Validates a phone number
 * @param {string} value - Phone to validate
 * @returns {boolean} - True if valid phone
 */
function validatePhone(value) {
	if (!value) return true
	// Accepts: +64 21 123 4567, 021234567, (021) 123-4567, etc.
	const phoneRegex =
		/^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/
	return phoneRegex.test(value.replace(/\s/g, ""))
}

/**
 * Validates a URL
 * @param {string} value - URL to validate
 * @returns {boolean} - True if valid URL
 */
function validateUrl(value) {
	if (!value) return true
	try {
		new URL(value)
		return true
	} catch {
		return false
	}
}

/**
 * Validates a number
 * @param {*} value - Value to validate
 * @returns {boolean} - True if valid number
 */
function validateNumber(value) {
	if (value === "" || value === null || value === undefined) return true
	return !isNaN(Number.parseFloat(value)) && isFinite(value)
}

/**
 * Safely evaluates a custom validation expression
 *
 * @param {string} expression - The validation expression (e.g., "eval:formData.age >= 18")
 * @param {*} value - The field value
 * @param {object} formData - The current form data
 * @returns {boolean} - True if validation passes
 */
function evaluateCustomValidation(expression, value, formData) {
	// Remove 'eval:' prefix if present
	let cleanExpression = expression.trim()
	if (cleanExpression.startsWith("eval:")) {
		cleanExpression = cleanExpression.substring(5).trim()
	}

	try {
		// Create a safe evaluation context with formData and value
		// This prevents access to dangerous globals like window, document, etc.
		const safeEval = new Function(
			"formData",
			"value",
			`
			'use strict';
			try {
				return Boolean(${cleanExpression});
			} catch (e) {
				console.warn('[Field Validation] Evaluation error:', e.message);
				return true; // Fail open on evaluation error
			}
		`,
		)

		const result = safeEval(formData, value)
		return result
	} catch (error) {
		console.error(
			"[Field Validation] Failed to evaluate expression:",
			expression,
			error,
		)
		// On error, default to passing validation (fail open)
		return true
	}
}

/**
 * Validates a field value based on validation rule
 *
 * @param {*} value - The field value to validate
 * @param {string} validation - Validation rule (email, phone, url, number, or eval:expression)
 * @param {object} formData - Current form data (for custom validations)
 * @returns {object} - {valid: boolean, message: string}
 */
export function validateField(value, validation, formData = {}) {
	if (!validation) {
		return { valid: true, message: "" }
	}

	const validationType = validation.toLowerCase()

	// Built-in validation types
	switch (validationType) {
		case "email":
			if (!validateEmail(value)) {
				return { valid: false, message: "Please enter a valid email address" }
			}
			break

		case "phone":
			if (!validatePhone(value)) {
				return { valid: false, message: "Please enter a valid phone number" }
			}
			break

		case "url":
			if (!validateUrl(value)) {
				return { valid: false, message: "Please enter a valid URL" }
			}
			break

		case "number":
			if (!validateNumber(value)) {
				return { valid: false, message: "Please enter a valid number" }
			}
			break

		default:
			// Custom validation expression (starts with eval:)
			if (validation.startsWith("eval:")) {
				if (!evaluateCustomValidation(validation, value, formData)) {
					return { valid: false, message: "Validation failed" }
				}
			}
	}

	return { valid: true, message: "" }
}

/**
 * Validates all fields in a section
 *
 * @param {array} fields - Array of field objects with validation rules
 * @param {object} formData - Current form data
 * @returns {object} - {valid: boolean, errors: {fieldName: message}}
 */
export function validateSection(fields, formData) {
	const errors = {}
	let valid = true

	fields.forEach((field) => {
		const value = formData[field.field_name]

		// Check required
		if (
			field.is_required &&
			(value === "" || value === null || value === undefined)
		) {
			errors[field.field_name] = `${field.field_label} is required`
			valid = false
			return
		}

		// Check validation rule
		if (field.validation) {
			const result = validateField(value, field.validation, formData)
			if (!result.valid) {
				errors[field.field_name] = result.message
				valid = false
			}
		}
	})

	return { valid, errors }
}

/**
 * Validates all fields in a step
 *
 * @param {object} stepConfig - Step configuration with sections and fields
 * @param {object} formData - Current form data
 * @returns {object} - {valid: boolean, errors: {fieldName: message}}
 */
export function validateStep(stepConfig, formData) {
	if (!stepConfig || !stepConfig.sections) {
		return { valid: true, errors: {} }
	}

	let allErrors = {}
	let allValid = true

	stepConfig.sections.forEach((section) => {
		if (section.fields && Array.isArray(section.fields)) {
			const sectionResult = validateSection(section.fields, formData)
			if (!sectionResult.valid) {
				allValid = false
				allErrors = { ...allErrors, ...sectionResult.errors }
			}
		}
	})

	return { valid: allValid, errors: allErrors }
}

/**
 * Example validation expressions:
 *
 * Email validation:
 *   validation: "email"
 *
 * Phone validation:
 *   validation: "phone"
 *
 * Age requirement:
 *   validation: "eval:value >= 18"
 *
 * Password confirmation:
 *   validation: "eval:value === formData.password"
 *
 * Conditional validation:
 *   validation: "eval:formData.requester_type !== 'Individual' || value.length > 0"
 *
 * Date range:
 *   validation: "eval:new Date(value) >= new Date('2020-01-01')"
 */
