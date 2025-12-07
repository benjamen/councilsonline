import { apiClient } from './base'

/**
 * RFQ (Request for Quote) Service
 * Handles RFQ Agent Details operations
 */
export class RFQService {
	/**
	 * Create a new RFQ for a request
	 * @param {string} requestId - The request ID
	 * @param {string} rfqMessage - Optional custom RFQ message
	 * @returns {Object} Frappe resource
	 */
	createRFQ(requestId, rfqMessage = null) {
		return apiClient.createResource({
			url: 'lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.create_rfq_for_request',
			method: 'POST',
			params: {
				request_id: requestId,
				rfq_message: rfqMessage
			},
			auto: true
		})
	}

	/**
	 * Send RFQ to an agent
	 * @param {string} rfqId - The RFQ document ID
	 * @param {string} agentId - The agent user ID
	 * @returns {Object} Frappe resource
	 */
	sendRFQToAgent(rfqId, agentId) {
		return apiClient.createResource({
			url: 'lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.send_rfq_to_agent',
			method: 'POST',
			params: {
				rfq_id: rfqId,
				agent_id: agentId
			},
			auto: true
		})
	}

	/**
	 * Engage an agent from RFQ (locks the request)
	 * @param {string} rfqId - The RFQ document ID
	 * @param {number} quoteAmount - The agreed quote amount
	 * @param {string} quoteDetails - Optional quote details
	 * @returns {Object} Frappe resource
	 */
	engageAgent(rfqId, quoteAmount = null, quoteDetails = null) {
		return apiClient.createResource({
			url: 'lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.engage_agent',
			method: 'POST',
			params: {
				rfq_id: rfqId,
				quote_amount: quoteAmount,
				quote_details: quoteDetails
			},
			auto: true
		})
	}

	/**
	 * Get available agents for RFQ
	 * @returns {Object} Frappe resource
	 */
	getAvailableAgents() {
		return apiClient.createResource({
			url: 'lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.get_available_agents',
			method: 'GET',
			auto: true,
			cache: ['available-agents']
		})
	}

	/**
	 * Get RFQ details by ID
	 * @param {string} rfqId - The RFQ document ID
	 * @returns {Object} Frappe resource
	 */
	getRFQ(rfqId) {
		return apiClient.createResource({
			url: 'frappe.client.get',
			params: {
				doctype: 'RFQ Agent Details',
				name: rfqId
			},
			auto: true
		})
	}

	/**
	 * Update RFQ details
	 * @param {string} rfqId - The RFQ document ID
	 * @param {Object} data - Updated RFQ data
	 * @returns {Promise<void>}
	 */
	async updateRFQ(rfqId, data) {
		return apiClient.call('frappe.client.set_value', {
			doctype: 'RFQ Agent Details',
			name: rfqId,
			fieldname: data
		})
	}

	/**
	 * Get all RFQs for a request
	 * @param {string} requestId - The request ID
	 * @returns {Object} Frappe resource
	 */
	getRFQsForRequest(requestId) {
		return apiClient.createResource({
			url: 'frappe.client.get_list',
			params: {
				doctype: 'RFQ Agent Details',
				filters: {
					request: requestId
				},
				fields: [
					'name',
					'status',
					'created_date',
					'rfq_message',
					'agent',
					'agent_name',
					'agent_email',
					'agent_phone',
					'agent_engaged',
					'agent_engaged_date',
					'quote_amount',
					'quote_details',
					'quote_received_date'
				],
				order_by: 'created_date desc'
			},
			auto: true
		})
	}

	/**
	 * Cancel RFQ
	 * @param {string} rfqId - The RFQ document ID
	 * @param {string} reason - Cancellation reason
	 * @returns {Promise<void>}
	 */
	async cancelRFQ(rfqId, reason = null) {
		return apiClient.call('lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.cancel_rfq', {
			rfq_id: rfqId,
			cancellation_reason: reason
		})
	}

	/**
	 * Accept agent quote
	 * @param {string} rfqId - The RFQ document ID
	 * @returns {Promise<void>}
	 */
	async acceptQuote(rfqId) {
		return apiClient.call('lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.accept_quote', {
			rfq_id: rfqId
		})
	}

	/**
	 * Reject agent quote
	 * @param {string} rfqId - The RFQ document ID
	 * @param {string} reason - Rejection reason
	 * @returns {Promise<void>}
	 */
	async rejectQuote(rfqId, reason = null) {
		return apiClient.call('lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.reject_quote', {
			rfq_id: rfqId,
			rejection_reason: reason
		})
	}
}

export const rfqService = new RFQService()
