/**
 * Composable for form validation with error tracking
 *
 * @example
 * ```typescript
 * const { validate, errors, isValid, clearErrors, setError } = useFormValidation()
 *
 * // Define validation rules
 * const rules = {
 *   email: (value) => {
 *     if (!value) return 'Email is required'
 *     if (!value.includes('@')) return 'Invalid email'
 *     return null
 *   },
 *   phone: (value) => {
 *     if (!value) return 'Phone is required'
 *     if (!/^\d{10}$/.test(value)) return 'Phone must be 10 digits'
 *     return null
 *   }
 * }
 *
 * // Validate form
 * if (validate(formData, rules)) {
 *   // Form is valid
 *   submitForm()
 * }
 * ```
 */

import { type Ref, computed, ref } from "vue"

export type ValidationRule<T = any> = (
	value: T,
) => string | null | Promise<string | null>

export type ValidationRules<T> = {
	[K in keyof T]?: ValidationRule<T[K]>
}

export interface FormValidationReturn {
	/** Object containing field names and error messages */
	errors: Ref<Record<string, string>>

	/** Validate all fields according to rules */
	validate: <T extends Record<string, any>>(
		data: T,
		rules: ValidationRules<T>,
	) => Promise<boolean>

	/** Validate a single field */
	validateField: <T = any>(
		fieldName: string,
		value: T,
		rule: ValidationRule<T>,
	) => Promise<boolean>

	/** Clear all errors */
	clearErrors: () => void

	/** Clear error for specific field */
	clearFieldError: (fieldName: string) => void

	/** Set error manually */
	setError: (fieldName: string, message: string) => void

	/** Whether form is valid (no errors) */
	isValid: Ref<boolean>

	/** Whether form has any errors */
	hasErrors: Ref<boolean>

	/** Get error message for field */
	getError: (fieldName: string) => string | undefined

	/** Check if field has error */
	hasError: (fieldName: string) => boolean
}

export function useFormValidation(): FormValidationReturn {
	const errors = ref<Record<string, string>>({})

	const hasErrors = computed(() => Object.keys(errors.value).length > 0)
	const isValid = computed(() => !hasErrors.value)

	const clearErrors = () => {
		errors.value = {}
	}

	const clearFieldError = (fieldName: string) => {
		delete errors.value[fieldName]
	}

	const setError = (fieldName: string, message: string) => {
		errors.value[fieldName] = message
	}

	const getError = (fieldName: string): string | undefined => {
		return errors.value[fieldName]
	}

	const hasError = (fieldName: string): boolean => {
		return fieldName in errors.value
	}

	const validateField = async <T = any>(
		fieldName: string,
		value: T,
		rule: ValidationRule<T>,
	): Promise<boolean> => {
		try {
			const error = await rule(value)
			if (error) {
				setError(fieldName, error)
				return false
			} else {
				clearFieldError(fieldName)
				return true
			}
		} catch (err) {
			console.error(`Validation error for field "${fieldName}":`, err)
			setError(fieldName, "Validation failed")
			return false
		}
	}

	const validate = async <T extends Record<string, any>>(
		data: T,
		rules: ValidationRules<T>,
	): Promise<boolean> => {
		clearErrors()

		const validationPromises = Object.entries(rules).map(
			async ([fieldName, rule]) => {
				if (!rule) return true
				const value = data[fieldName as keyof T]
				return validateField(fieldName, value, rule as ValidationRule)
			},
		)

		const results = await Promise.all(validationPromises)
		return results.every((result) => result === true)
	}

	return {
		errors,
		validate,
		validateField,
		clearErrors,
		clearFieldError,
		setError,
		isValid,
		hasErrors,
		getError,
		hasError,
	}
}

/**
 * Common validation rules
 */
export const ValidationRules = {
	required:
		(message = "This field is required") =>
		(value: any) => {
			if (value === null || value === undefined || value === "") {
				return message
			}
			return null
		},

	email:
		(message = "Invalid email address") =>
		(value: string) => {
			if (!value) return null // Use with required() if needed
			const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
			return emailRegex.test(value) ? null : message
		},

	minLength: (min: number, message?: string) => (value: string) => {
		if (!value) return null
		return value.length >= min
			? null
			: message || `Must be at least ${min} characters`
	},

	maxLength: (max: number, message?: string) => (value: string) => {
		if (!value) return null
		return value.length <= max
			? null
			: message || `Must be at most ${max} characters`
	},

	pattern:
		(regex: RegExp, message = "Invalid format") =>
		(value: string) => {
			if (!value) return null
			return regex.test(value) ? null : message
		},

	phone:
		(message = "Invalid phone number") =>
		(value: string) => {
			if (!value) return null
			// NZ phone number pattern (flexible)
			const phoneRegex = /^[\d\s\-\+\(\)]{8,}$/
			return phoneRegex.test(value) ? null : message
		},

	url:
		(message = "Invalid URL") =>
		(value: string) => {
			if (!value) return null
			try {
				new URL(value)
				return null
			} catch {
				return message
			}
		},

	numeric:
		(message = "Must be a number") =>
		(value: any) => {
			if (value === null || value === undefined || value === "") return null
			return !isNaN(Number(value)) ? null : message
		},

	min: (min: number, message?: string) => (value: number) => {
		if (value === null || value === undefined) return null
		return value >= min ? null : message || `Must be at least ${min}`
	},

	max: (max: number, message?: string) => (value: number) => {
		if (value === null || value === undefined) return null
		return value <= max ? null : message || `Must be at most ${max}`
	},

	oneOf:
		<T = any>(values: T[], message?: string) =>
		(value: T) => {
			if (!value) return null
			return values.includes(value)
				? null
				: message || `Must be one of: ${values.join(", ")}`
		},

	/**
	 * Conditional validation - only validate if condition is true
	 */
	when: <T = any>(
		condition: () => boolean,
		rule: ValidationRule<T>,
	): ValidationRule<T> => {
		return (value: T) => {
			if (!condition()) return null
			return rule(value)
		}
	},

	/**
	 * Combine multiple rules
	 */
	all: <T = any>(...rules: ValidationRule<T>[]): ValidationRule<T> => {
		return async (value: T) => {
			for (const rule of rules) {
				const error = await rule(value)
				if (error) return error
			}
			return null
		}
	},
} as const

/**
 * Example usage:
 *
 * ```typescript
 * const rules = {
 *   email: ValidationRules.all(
 *     ValidationRules.required(),
 *     ValidationRules.email()
 *   ),
 *   phone: ValidationRules.phone(),
 *   owner_name: ValidationRules.when(
 *     () => formData.applicant_is_not_owner,
 *     ValidationRules.required('Owner name is required')
 *   )
 * }
 * ```
 */
