/**
 * Unified API client for making calls to different Frappe apps
 *
 * This client abstracts away the app-specific API paths, allowing
 * components to work across different apps (platform_core, lodgement_requests,
 * resource_consents, social_services, etc.) without hardcoding app names.
 *
 * @example
 * // In a component
 * import { AppApiClient } from '@lodgeick/ui/api/AppApiClient'
 *
 * const api = new AppApiClient('social_services')
 * const households = await api.getList('Household Record', { is_active: 1 })
 */
export class AppApiClient {
  /**
   * @param {string} appName - The Frappe app name (e.g., 'platform_core', 'social_services')
   */
  constructor(appName) {
    this.appName = appName
  }

  /**
   * Call a whitelisted method in the app's API
   *
   * @param {string} method - Method name (without app prefix)
   * @param {Object} args - Arguments to pass to the method
   * @returns {Promise<any>} Response from the API
   *
   * @example
   * const api = new AppApiClient('lodgement_requests')
   * const steps = await api.call('get_request_type_steps', {
   *   request_type: 'SPISC',
   *   council_code: 'PH-TAY'
   * })
   */
  async call(method, args = {}) {
    const response = await window.frappe?.call({
      method: `${this.appName}.api.${method}`,
      args
    })
    return response?.message
  }

  /**
   * Get a list of documents
   *
   * @param {string} doctype - DocType name
   * @param {Object} filters - Filter conditions
   * @param {string[]} fields - Fields to fetch
   * @param {Object} options - Additional options (limit, order_by, etc.)
   * @returns {Promise<any[]>} List of documents
   *
   * @example
   * const api = new AppApiClient('platform_core')
   * const councils = await api.getList(
   *   'Council',
   *   { is_active: 1 },
   *   ['name', 'council_name', 'primary_color']
   * )
   */
  async getList(doctype, filters = {}, fields = ['name'], options = {}) {
    const response = await window.frappe?.call({
      method: 'frappe.client.get_list',
      args: {
        doctype,
        filters,
        fields,
        ...options
      }
    })
    return response?.message || []
  }

  /**
   * Get a single document
   *
   * @param {string} doctype - DocType name
   * @param {string} name - Document name
   * @returns {Promise<Object>} Document data
   *
   * @example
   * const api = new AppApiClient('social_services')
   * const household = await api.get('Household Record', 'HH-2025-001')
   */
  async get(doctype, name) {
    const response = await window.frappe?.call({
      method: 'frappe.client.get',
      args: { doctype, name }
    })
    return response?.message
  }

  /**
   * Save a document (create or update)
   *
   * @param {string} doctype - DocType name
   * @param {Object} data - Document data
   * @returns {Promise<Object>} Saved document
   *
   * @example
   * const api = new AppApiClient('social_services')
   * const saved = await api.save('Household Record', {
   *   name: 'HH-2025-001',
   *   head_of_household_name: 'Juan Dela Cruz',
   *   barangay: 'San Isidro'
   * })
   */
  async save(doctype, data) {
    const response = await window.frappe?.call({
      method: 'frappe.client.save',
      args: {
        doc: { doctype, ...data }
      }
    })
    return response?.message
  }

  /**
   * Insert a new document
   *
   * @param {string} doctype - DocType name
   * @param {Object} data - Document data
   * @returns {Promise<Object>} Created document
   *
   * @example
   * const api = new AppApiClient('lodgement_requests')
   * const request = await api.insert('Request', {
   *   request_type: 'SPISC',
   *   council: 'PH-TAY',
   *   applicant_email: 'juan@example.com'
   * })
   */
  async insert(doctype, data) {
    const response = await window.frappe?.call({
      method: 'frappe.client.insert',
      args: {
        doc: { doctype, ...data }
      }
    })
    return response?.message
  }

  /**
   * Delete a document
   *
   * @param {string} doctype - DocType name
   * @param {string} name - Document name
   * @returns {Promise<void>}
   *
   * @example
   * const api = new AppApiClient('social_services')
   * await api.delete('Household Record', 'HH-2025-001')
   */
  async delete(doctype, name) {
    await window.frappe?.call({
      method: 'frappe.client.delete',
      args: { doctype, name }
    })
  }

  /**
   * Get a count of documents matching filters
   *
   * @param {string} doctype - DocType name
   * @param {Object} filters - Filter conditions
   * @returns {Promise<number>} Count of matching documents
   *
   * @example
   * const api = new AppApiClient('social_services')
   * const activeCount = await api.getCount('Household Record', { is_active: 1 })
   */
  async getCount(doctype, filters = {}) {
    const response = await window.frappe?.call({
      method: 'frappe.client.get_count',
      args: { doctype, filters }
    })
    return response?.message || 0
  }

  /**
   * Run a database query
   *
   * @param {Object} query - Query object
   * @returns {Promise<any[]>} Query results
   *
   * @example
   * const api = new AppApiClient('platform_core')
   * const results = await api.db({
   *   doctype: 'Council',
   *   fields: ['name', 'council_name'],
   *   filters: { is_active: 1 },
   *   order_by: 'council_name asc'
   * })
   */
  async db(query) {
    const response = await window.frappe?.call({
      method: 'frappe.client.get_list',
      args: query
    })
    return response?.message || []
  }
}
