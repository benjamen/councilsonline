import { apiClient } from "./base"

/**
 * Application Service
 * Handles Application DocTypes (SPISC, Resource Consent, Building Consent, etc.)
 */
export class ApplicationService {
	/**
	 * Create application for a request
	 * @param {string} requestId - Parent request ID
	 * @param {string} applicationType - Application DocType (e.g., 'SPISC Application')
	 * @param {Object} applicationData - Application data
	 * @returns {Promise<Object>} Created application
	 */
	async createApplication(requestId, applicationType, applicationData) {
		return apiClient.call("lodgeick.api.create_application", {
			request_id: requestId,
			application_type: applicationType,
			application_data: applicationData,
		})
	}

	/**
	 * Get application by ID
	 * @param {string} applicationType - Application DocType
	 * @param {string} applicationId - Application name/ID
	 * @returns {Object} Frappe resource
	 */
	getApplication(applicationType, applicationId) {
		return apiClient.createResource({
			url: "frappe.client.get",
			params: {
				doctype: applicationType,
				name: applicationId,
			},
			auto: true,
		})
	}

	/**
	 * Update application
	 * @param {string} applicationType - Application DocType
	 * @param {string} applicationId - Application name/ID
	 * @param {Object} fields - Fields to update
	 * @returns {Promise<void>}
	 */
	async updateApplication(applicationType, applicationId, fields) {
		return apiClient.call("frappe.client.set_value", {
			doctype: applicationType,
			name: applicationId,
			fieldname: fields,
		})
	}

	/**
	 * Get application by request ID
	 * @param {string} requestId - Parent request ID
	 * @returns {Promise<Object>} Application data
	 */
	async getApplicationByRequest(requestId) {
		return apiClient.call("lodgeick.api.get_application_by_request", {
			request_id: requestId,
		})
	}

	/**
	 * Get SPISC application
	 * @param {string} applicationId - SPISC Application ID
	 * @returns {Object} Frappe resource
	 */
	getSPISCApplication(applicationId) {
		return this.getApplication("SPISC Application", applicationId)
	}

	/**
	 * Get Resource Consent application
	 * @param {string} applicationId - Resource Consent Application ID
	 * @returns {Object} Frappe resource
	 */
	getResourceConsentApplication(applicationId) {
		return this.getApplication("Resource Consent Application", applicationId)
	}

	/**
	 * Get Building Consent application
	 * @param {string} applicationId - Building Consent Application ID
	 * @returns {Object} Frappe resource
	 */
	getBuildingConsentApplication(applicationId) {
		return this.getApplication("Building Consent Application", applicationId)
	}

	/**
	 * Submit application for review
	 * @param {string} applicationType - Application DocType
	 * @param {string} applicationId - Application name/ID
	 * @returns {Promise<void>}
	 */
	async submitApplication(applicationType, applicationId) {
		return apiClient.call("lodgeick.api.submit_application", {
			application_type: applicationType,
			application_id: applicationId,
		})
	}

	/**
	 * Get application status history
	 * @param {string} applicationType - Application DocType
	 * @param {string} applicationId - Application name/ID
	 * @returns {Promise<Array>} Status history
	 */
	async getApplicationStatusHistory(applicationType, applicationId) {
		return apiClient.call("lodgeick.api.get_application_status_history", {
			application_type: applicationType,
			application_id: applicationId,
		})
	}

	/**
	 * Assign application to officer
	 * @param {string} applicationType - Application DocType
	 * @param {string} applicationId - Application name/ID
	 * @param {string} officerEmail - Officer user email
	 * @returns {Promise<void>}
	 */
	async assignToOfficer(applicationType, applicationId, officerEmail) {
		return apiClient.call("lodgeick.api.assign_application", {
			application_type: applicationType,
			application_id: applicationId,
			officer_email: officerEmail,
		})
	}

	/**
	 * Add comment to application
	 * @param {string} applicationType - Application DocType
	 * @param {string} applicationId - Application name/ID
	 * @param {string} comment - Comment text
	 * @returns {Promise<void>}
	 */
	async addComment(applicationType, applicationId, comment) {
		return apiClient.call("frappe.desk.form.utils.add_comment", {
			reference_doctype: applicationType,
			reference_name: applicationId,
			content: comment,
			comment_email: frappe.session.user,
			comment_by: frappe.session.user_fullname,
		})
	}

	/**
	 * Get application comments
	 * @param {string} applicationType - Application DocType
	 * @param {string} applicationId - Application name/ID
	 * @returns {Promise<Array>} Comments
	 */
	async getComments(applicationType, applicationId) {
		return apiClient.call("frappe.desk.form.load.get_comments", {
			doctype: applicationType,
			name: applicationId,
		})
	}
}

export const applicationService = new ApplicationService()
