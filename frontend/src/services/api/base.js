import { createResource } from "frappe-ui"

/**
 * Base API client with standardized error handling
 * Uses frappe-ui's createResource for consistency
 */
export class BaseAPIClient {
	constructor() {
		this.defaultOptions = {
			onError: this.handleError.bind(this),
			onSuccess: this.handleSuccess.bind(this),
		}
	}

	/**
	 * Create Frappe resource with standard options
	 * @param {Object} config - Resource configuration
	 * @returns {Object} Frappe resource instance
	 */
	createResource(config) {
		return createResource({
			...this.defaultOptions,
			...config,
		})
	}

	/**
	 * Standardized error handler
	 * @param {Object|Error} error - Error object
	 * @returns {Object} Error response
	 */
	handleError(error) {
		console.error("[API Error]", error)

		// Extract error message
		const message = error?.exc_type
			? error.exc_type
			: error?.message || "An unexpected error occurred"

		// Store error in global error state (async to avoid blocking)
		// Using dynamic import to avoid issues in browser environments
		import("../../stores/errorStore")
			.then(({ useErrorStore }) => {
				const errorStore = useErrorStore()
				errorStore.addError({ message, type: "api_error", context: error })
			})
			.catch((e) => {
				// Fail silently if store not available
				console.error("Could not add error to store:", e)
			})

		return { error: message }
	}

	/**
	 * Success handler with optional logging
	 * @param {*} data - Response data
	 * @returns {*} Response data
	 */
	handleSuccess(data) {
		return data
	}

	/**
	 * Call Frappe method directly (for non-resource calls)
	 * @param {string} method - Frappe method path (e.g., 'lodgeick.api.create_draft_request')
	 * @param {Object} args - Method arguments
	 * @returns {Promise<*>} Response data
	 */
	async call(method, args = {}) {
		try {
			console.log(`[BaseAPIClient] Calling ${method} with args:`, args)
			console.log(`[BaseAPIClient] Args JSON:`, JSON.stringify(args, null, 2))

			const headers = {
				"Content-Type": "application/json",
			}

			// Add CSRF token if available
			if (window.csrf_token) {
				headers["X-Frappe-CSRF-Token"] = window.csrf_token
			}

			const response = await fetch("/api/method/" + method, {
				method: "POST",
				headers: headers,
				credentials: "include",
				body: JSON.stringify(args),
			})

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`)
			}

			const data = await response.json()

			if (data.exc) {
				throw new Error(data.exc)
			}

			return data.message
		} catch (error) {
			this.handleError(error)
			throw error
		}
	}

	/**
	 * Upload file to Frappe
	 * @param {File} file - File object
	 * @param {Object} options - Upload options (doctype, docname, fieldname, etc.)
	 * @returns {Promise<Object>} File document
	 */
	async uploadFile(file, options = {}) {
		try {
			const formData = new FormData()
			formData.append("file", file)

			if (options.doctype) formData.append("doctype", options.doctype)
			if (options.docname) formData.append("docname", options.docname)
			if (options.fieldname) formData.append("fieldname", options.fieldname)
			if (options.is_private !== undefined) {
				formData.append("is_private", options.is_private ? "1" : "0")
			}

			const headers = {}

			// Add CSRF token if available
			if (window.csrf_token) {
				headers["X-Frappe-CSRF-Token"] = window.csrf_token
			}

			const response = await fetch("/api/method/upload_file", {
				method: "POST",
				headers: headers,
				credentials: "include",
				body: formData,
			})

			if (!response.ok) {
				throw new Error(`Upload failed: ${response.statusText}`)
			}

			const data = await response.json()

			if (data.exc) {
				throw new Error(data.exc)
			}

			return data.message
		} catch (error) {
			this.handleError(error)
			throw error
		}
	}
}

export const apiClient = new BaseAPIClient()
