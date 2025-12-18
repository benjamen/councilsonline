import { apiClient } from "./base"

/**
 * Council Service
 * Handles Council DocType operations and council-specific data
 */
export class CouncilService {
	/**
	 * Get all enabled councils
	 * @returns {Object} Frappe resource
	 */
	getAllCouncils() {
		return apiClient.createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Council",
				filters: { is_enabled: 1 },
				fields: [
					"name",
					"council_name",
					"council_code",
					"region",
					"logo",
					"primary_color",
					"is_enabled",
				],
				order_by: "council_name asc",
			},
			auto: true,
			cache: ["councils"],
		})
	}

	/**
	 * Get council by code
	 * @param {string} councilCode - Council code
	 * @returns {Object} Frappe resource
	 */
	getCouncilByCode(councilCode) {
		return apiClient.createResource({
			url: "frappe.client.get",
			params: {
				doctype: "Council",
				filters: { council_code: councilCode },
			},
			auto: true,
			cache: ["council", councilCode],
		})
	}

	/**
	 * Get request types for a specific council
	 * @param {string} councilCode - Council code
	 * @returns {Object} Frappe resource
	 */
	getCouncilRequestTypes(councilCode) {
		return apiClient.createResource({
			url: "lodgeick.api.get_council_request_types",
			params: { council_code: councilCode },
			auto: true,
			cache: ["council-request-types", councilCode],
		})
	}

	/**
	 * Get council configuration (branding, contact info, etc.)
	 * @param {string} councilCode - Council code
	 * @returns {Promise<Object>} Council configuration
	 */
	async getCouncilConfig(councilCode) {
		return apiClient.call("lodgeick.api.get_council_config", {
			council_code: councilCode,
		})
	}

	/**
	 * Get councils by region
	 * @param {string} region - Region name
	 * @returns {Object} Frappe resource
	 */
	getCouncilsByRegion(region) {
		return apiClient.createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Council",
				filters: {
					region,
					is_enabled: 1,
				},
				fields: ["name", "council_name", "council_code", "logo"],
				order_by: "council_name asc",
			},
			auto: true,
		})
	}

	/**
	 * Search councils by name
	 * @param {string} query - Search query
	 * @returns {Promise<Array>} Matching councils
	 */
	async searchCouncils(query) {
		return apiClient.call("frappe.client.get_list", {
			doctype: "Council",
			filters: {
				council_name: ["like", `%${query}%`],
				is_enabled: 1,
			},
			fields: ["name", "council_name", "council_code"],
			limit: 10,
		})
	}
}

export const councilService = new CouncilService()
