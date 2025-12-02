import { createResource } from 'frappe-ui'

/**
 * Create a new RFQ for a request
 * @param {string} requestId - The request ID
 * @param {string} rfqMessage - Optional custom RFQ message
 * @returns {Promise} Promise resolving to the created RFQ data
 */
export function createRFQ(requestId, rfqMessage = null) {
  const resource = createResource({
    url: 'lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.create_rfq_for_request',
    method: 'POST',
    params: {
      request_id: requestId,
      rfq_message: rfqMessage
    },
    auto: true
  })

  return resource
}

/**
 * Send RFQ to an agent
 * @param {string} rfqId - The RFQ document ID
 * @param {string} agentId - The agent user ID
 * @returns {Promise} Promise resolving to the updated RFQ data
 */
export function sendRFQToAgent(rfqId, agentId) {
  const resource = createResource({
    url: 'lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.send_rfq_to_agent',
    method: 'POST',
    params: {
      rfq_id: rfqId,
      agent_id: agentId
    },
    auto: true
  })

  return resource
}

/**
 * Engage an agent from RFQ (locks the request)
 * @param {string} rfqId - The RFQ document ID
 * @param {number} quoteAmount - The agreed quote amount
 * @param {string} quoteDetails - Optional quote details
 * @returns {Promise} Promise resolving to the updated RFQ data
 */
export function engageAgent(rfqId, quoteAmount = null, quoteDetails = null) {
  const resource = createResource({
    url: 'lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.engage_agent',
    method: 'POST',
    params: {
      rfq_id: rfqId,
      quote_amount: quoteAmount,
      quote_details: quoteDetails
    },
    auto: true
  })

  return resource
}

/**
 * Get available agents for RFQ
 * @returns {Promise} Promise resolving to list of available agents
 */
export function getAvailableAgents() {
  const resource = createResource({
    url: 'lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details.get_available_agents',
    method: 'GET',
    auto: true
  })

  return resource
}

/**
 * Update RFQ details
 * @param {string} rfqId - The RFQ document ID
 * @param {object} data - Updated RFQ data
 * @returns {Promise} Promise resolving to the updated RFQ
 */
export function updateRFQ(rfqId, data) {
  return new Promise((resolve, reject) => {
    frappe.call({
      method: 'frappe.client.set_value',
      args: {
        doctype: 'RFQ Agent Details',
        name: rfqId,
        fieldname: data
      },
      callback: (r) => {
        if (r.message) {
          resolve(r.message)
        } else {
          reject(new Error('Failed to update RFQ'))
        }
      },
      error: (err) => {
        reject(err)
      }
    })
  })
}

/**
 * Get RFQ details by ID
 * @param {string} rfqId - The RFQ document ID
 * @returns {Promise} Promise resolving to RFQ data
 */
export function getRFQ(rfqId) {
  return new Promise((resolve, reject) => {
    frappe.call({
      method: 'frappe.client.get',
      args: {
        doctype: 'RFQ Agent Details',
        name: rfqId
      },
      callback: (r) => {
        if (r.message) {
          resolve(r.message)
        } else {
          reject(new Error('RFQ not found'))
        }
      },
      error: (err) => {
        reject(err)
      }
    })
  })
}

/**
 * Get all RFQs for a request
 * @param {string} requestId - The request ID
 * @returns {Promise} Promise resolving to list of RFQs
 */
export function getRFQsForRequest(requestId) {
  return new Promise((resolve, reject) => {
    frappe.call({
      method: 'frappe.client.get_list',
      args: {
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
      callback: (r) => {
        if (r.message) {
          resolve(r.message)
        } else {
          resolve([])
        }
      },
      error: (err) => {
        reject(err)
      }
    })
  })
}
