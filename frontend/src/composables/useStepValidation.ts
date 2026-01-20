/**
 * Step-based validation for Request Type configuration
 * Integrates with existing fieldValidation.js utility
 */

import { type Ref, ref } from "vue"
import { evaluateCondition } from "../utils/conditionalLogic"
import { validateField as utilValidateField } from "../utils/fieldValidation"

export interface StepValidationReturn {
	/** Object containing field names and error messages */
	errors: Ref<Record<string, string>>

	/** Whether validation is in progress */
	isValidating: Ref<boolean>

	/** Validate single field with config */
	validateConfigField: (
		fieldName: string,
		value: any,
		fieldConfig: any,
		formData?: any,
	) => boolean

	/** Validate entire step */
	validateStep: (stepConfig: any, formData: any) => Promise<boolean>

	/** Clear all errors */
	clearErrors: () => void

	/** Clear specific field error */
	clearFieldError: (fieldName: string) => void
}

export function useStepValidation(): StepValidationReturn {
	const errors = ref<Record<string, string>>({})
	const isValidating = ref(false)

	/**
	 * Validate single field with Request Type config
	 */
	function validateConfigField(
		fieldName: string,
		value: any,
		fieldConfig: any,
		formData: any = {},
	): boolean {
		// Use utility validation
		const result = utilValidateField(value, fieldConfig.validation, formData)

		if (!result.valid) {
			errors.value[fieldName] = result.message
			return false
		}

		// Check required
		if (
			fieldConfig.is_required &&
			(value === "" || value === null || value === undefined)
		) {
			errors.value[fieldName] = `${fieldConfig.field_label} is required`
			return false
		}

		// Clear error if valid
		delete errors.value[fieldName]
		return true
	}

	/**
	 * Validate entire step based on config
	 */
	async function validateStep(
		stepConfig: any,
		formData: any,
	): Promise<boolean> {
		isValidating.value = true
		errors.value = {}

		let isValid = true

		for (const section of stepConfig.sections || []) {
			// Check section depends_on
			if (section.depends_on) {
				const shouldShow = evaluateDependsOn(section.depends_on, formData)
				if (!shouldShow) continue
			}

			for (const field of section.fields || []) {
				// Check field depends_on
				if (field.depends_on) {
					const shouldShow = evaluateDependsOn(field.depends_on, formData)
					if (!shouldShow) continue
				}

				// Get field value - check for nested address fields
				let value = formData[field.field_name]

				// Philippine address component fields are nested in address_line object
				const addressComponentFields = [
					"barangay",
					"municipality",
					"province",
					"city",
					"region",
					"zip_code",
					"postal_code",
				]
				if (addressComponentFields.includes(field.field_name) && !value) {
					// Check if there's an address_line object containing this field
					const addressLineData =
						formData["address_line"] ||
						formData["street"] ||
						formData["residential_address"] ||
						formData["property_address"]
					if (addressLineData && typeof addressLineData === "object") {
						value = addressLineData[field.field_name]
					}
				}

				const fieldValid = validateConfigField(
					field.field_name,
					value,
					field,
					formData,
				)

				if (!fieldValid) {
					isValid = false
				}
			}
		}

		isValidating.value = false
		return isValid
	}

	/**
	 * Evaluate depends_on expression
	 */
	function evaluateDependsOn(expression: string, formData: any): boolean {
		try {
			return evaluateCondition(expression, formData)
		} catch (error) {
			console.error("Error evaluating depends_on:", error)
			return true // Show field on error
		}
	}

	/**
	 * Clear all errors
	 */
	function clearErrors() {
		errors.value = {}
	}

	/**
	 * Clear specific field error
	 */
	function clearFieldError(fieldName: string) {
		delete errors.value[fieldName]
	}

	return {
		errors,
		isValidating,
		validateConfigField,
		validateStep,
		clearErrors,
		clearFieldError,
	}
}

/**
 * Example usage in NewRequest.vue:
 *
 * ```typescript
 * import { useStepValidation } from '@/composables/useStepValidation'
 *
 * const { errors, validateStep, clearErrors } = useStepValidation()
 *
 * async function handleNext() {
 *   const isValid = await validateStep(currentStepConfig.value, formData.value)
 *   if (!isValid) {
 *     showValidationModal.value = true
 *     return
 *   }
 *   // Continue...
 * }
 * ```
 */
