import { apiClient } from "./base"

/**
 * Request Type Service
 * Handles Request Type DocType operations and configuration management
 */
export class RequestTypeService {
	/**
	 * Get all request types
	 * @param {Object} filters - Optional filters
	 * @returns {Object} Frappe resource
	 */
	getAllRequestTypes(filters = {}) {
		return apiClient.createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Request Type",
				filters: {
					is_enabled: 1,
					...filters,
				},
				fields: [
					"name",
					"request_type_name",
					"request_type_code",
					"category",
					"description",
					"icon",
					"is_enabled",
				],
				order_by: "category asc, request_type_name asc",
			},
			auto: true,
			cache: ["request-types"],
		})
	}

	/**
	 * Get request type by code
	 * @param {string} requestTypeCode - Request type code
	 * @returns {Object} Frappe resource
	 */
	getRequestTypeByCode(requestTypeCode) {
		return apiClient.createResource({
			url: "councilsonline.api.get_request_type_config",
			params: { request_type_code: requestTypeCode },
			auto: true,
			cache: ["request-type", requestTypeCode],
		})
	}

	/**
	 * Get request type by name
	 * @param {string} requestTypeName - Request type name
	 * @returns {Object} Frappe resource
	 */
	getRequestType(requestTypeName) {
		return apiClient.createResource({
			url: "frappe.client.get",
			params: {
				doctype: "Request Type",
				name: requestTypeName,
			},
			auto: true,
		})
	}

	/**
	 * Get request types by category
	 * @param {string} category - Category name
	 * @returns {Object} Frappe resource
	 */
	getRequestTypesByCategory(category) {
		return this.getAllRequestTypes({ category })
	}

	/**
	 * Save request type configuration
	 * @param {Object} config - Request type configuration
	 * @returns {Promise<Object>} Saved configuration
	 */
	async saveRequestTypeConfig(config) {
		return apiClient.call("councilsonline.api.save_request_type_config", {
			config,
		})
	}

	/**
	 * Load request type configuration for editing
	 * @param {string} requestTypeName - Request type name
	 * @returns {Promise<Object>} Request type configuration
	 */
	async loadRequestTypeConfig(requestTypeName) {
		return apiClient.call("councilsonline.api.load_request_type_config", {
			request_type_name: requestTypeName,
		})
	}

	/**
	 * Get available step templates
	 * @returns {Promise<Array>} Step templates
	 */
	async getStepTemplates() {
		return apiClient.call("councilsonline.api.get_step_templates")
	}

	/**
	 * Load specific step template
	 * @param {string} templateName - Template name
	 * @returns {Promise<Object>} Template configuration
	 */
	async loadStepTemplate(templateName) {
		return apiClient.call("councilsonline.api.load_step_template", {
			template_name: templateName,
		})
	}

	/**
	 * Create new request type
	 * @param {Object} requestTypeData - Request type data
	 * @returns {Promise<Object>} Created request type
	 */
	async createRequestType(requestTypeData) {
		return apiClient.call("frappe.client.insert", {
			doc: {
				doctype: "Request Type",
				...requestTypeData,
			},
		})
	}

	/**
	 * Update request type
	 * @param {string} requestTypeName - Request type name
	 * @param {Object} fields - Fields to update
	 * @returns {Promise<void>}
	 */
	async updateRequestType(requestTypeName, fields) {
		return apiClient.call("frappe.client.set_value", {
			doctype: "Request Type",
			name: requestTypeName,
			fieldname: fields,
		})
	}

	/**
	 * Duplicate request type
	 * @param {string} requestTypeName - Request type name to duplicate
	 * @param {string} newName - New request type name
	 * @returns {Promise<Object>} Duplicated request type
	 */
	async duplicateRequestType(requestTypeName, newName) {
		return apiClient.call("councilsonline.api.duplicate_request_type", {
			request_type_name: requestTypeName,
			new_name: newName,
		})
	}

	/**
	 * Archive request type (disable)
	 * @param {string} requestTypeName - Request type name
	 * @returns {Promise<void>}
	 */
	async archiveRequestType(requestTypeName) {
		return this.updateRequestType(requestTypeName, { is_enabled: 0 })
	}

	/**
	 * Get request type categories
	 * @returns {Promise<Array>} Unique categories
	 */
	async getCategories() {
		return apiClient.call("councilsonline.api.get_request_type_categories")
	}

	/**
	 * Validate request type configuration
	 * @param {Object} config - Configuration to validate
	 * @returns {Promise<Object>} Validation result { valid: boolean, errors: [] }
	 */
	async validateRequestTypeConfig(config) {
		return apiClient.call("councilsonline.api.validate_request_type_config", {
			config,
		})
	}
}

export const requestTypeService = new RequestTypeService()
