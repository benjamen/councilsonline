import { apiClient } from "./base"

/**
 * Request Service
 * Handles all Request DocType operations (CRUD, submit, drafts)
 */
export class RequestService {
	/**
	 * Create or update draft request
	 * @param {Object} data - Form data
	 * @param {number} currentStep - Current step number
	 * @returns {Promise<Object>} Response with request_id
	 */
	async createDraft(data, currentStep) {
		return apiClient.call("lodgeick.api.create_draft_request", {
			data,
			current_step: currentStep,
		})
	}

	/**
	 * Get request by ID
	 * @param {string} requestId - Request name/ID
	 * @returns {Object} Frappe resource
	 */
	getRequest(requestId) {
		return apiClient.createResource({
			url: "frappe.client.get",
			params: {
				doctype: "Request",
				name: requestId,
			},
			auto: true,
		})
	}

	/**
	 * Get request type configuration
	 * @param {string} requestTypeCode - Request type code
	 * @returns {Object} Frappe resource
	 */
	getRequestTypeConfig(requestTypeCode) {
		return apiClient.createResource({
			url: "lodgeick.api.get_request_type_config",
			params: { request_type_code: requestTypeCode },
			auto: true,
			// Cache config data per request type for performance
			// Cache invalidates on browser refresh or can be cleared via localStorage
			cache: ["request-type-config", requestTypeCode],
		})
	}

	/**
	 * Clear request type config cache
	 * Call this after updating request type configuration in admin
	 */
	clearRequestTypeConfigCache() {
		// Clear all request-type-config cache entries
		const cacheKeys = Object.keys(localStorage).filter(key =>
			key.startsWith('request-type-config')
		)
		cacheKeys.forEach(key => localStorage.removeItem(key))
	}

	/**
	 * Update request fields
	 * @param {string} requestId - Request name/ID
	 * @param {Object} fields - Fields to update (key-value pairs)
	 * @returns {Promise<void>}
	 */
	async updateRequest(requestId, fields) {
		return apiClient.call("frappe.client.set_value", {
			doctype: "Request",
			name: requestId,
			fieldname: fields,
		})
	}

	/**
	 * Submit request (move from Draft to Submitted state)
	 * @param {string} requestId - Request name/ID
	 * @returns {Promise<void>}
	 */
	async submitRequest(requestId) {
		return apiClient.call("lodgeick.api.submit_request", {
			request_id: requestId,
		})
	}

	/**
	 * Get all requests for current user
	 * @returns {Object} Frappe resource
	 */
	getUserRequests() {
		return apiClient.createResource({
			url: "lodgeick.api.get_user_requests",
			auto: true,
			cache: ["user-requests"],
		})
	}

	/**
	 * Get requests by status
	 * @param {string} status - Request status (Draft, Submitted, Under Review, etc.)
	 * @returns {Object} Frappe resource
	 */
	getRequestsByStatus(status) {
		return apiClient.createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Request",
				filters: { status },
				fields: [
					"name",
					"request_type",
					"requester_name",
					"status",
					"created_at",
					"brief_description",
				],
				order_by: "modified desc",
			},
			auto: true,
		})
	}

	/**
	 * Delete draft request
	 * @param {string} requestId - Request name/ID
	 * @returns {Promise<void>}
	 */
	async deleteDraft(requestId) {
		return apiClient.call("frappe.client.delete", {
			doctype: "Request",
			name: requestId,
		})
	}

	/**
	 * Get request with related application data
	 * @param {string} requestId - Request name/ID
	 * @returns {Promise<Object>} Request with application data
	 */
	async getRequestWithApplication(requestId) {
		return apiClient.call("lodgeick.api.get_request_with_application", {
			request_id: requestId,
		})
	}

	/**
	 * Validate request step
	 * @param {string} requestId - Request name/ID
	 * @param {number} stepNumber - Step number to validate
	 * @param {Object} stepData - Step form data
	 * @returns {Promise<Object>} Validation result { valid: boolean, errors: [] }
	 */
	async validateStep(requestId, stepNumber, stepData) {
		return apiClient.call("lodgeick.api.validate_request_step", {
			request_id: requestId,
			step_number: stepNumber,
			step_data: stepData,
		})
	}
}

export const requestService = new RequestService()
