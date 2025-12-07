import { describe, it, expect, vi, beforeEach } from 'vitest'
import { requestService } from '../../../src/services/api/request.service'
import { apiClient } from '../../../src/services/api/base'

// Mock apiClient
vi.mock('../../../src/services/api/base', () => ({
  apiClient: {
    call: vi.fn(),
    createResource: vi.fn()
  }
}))

describe('RequestService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('createDraft', () => {
    it('should call API with correct parameters', async () => {
      const mockResponse = { request_id: 'REQ-001' }
      apiClient.call.mockResolvedValue(mockResponse)

      const data = { applicant_name: 'John Doe' }
      const result = await requestService.createDraft(data, 0)

      expect(apiClient.call).toHaveBeenCalledWith(
        'lodgeick.api.create_draft_request',
        { data, current_step: 0 }
      )
      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      const mockError = { error: 'Failed to create draft' }
      apiClient.call.mockResolvedValue(mockError)

      const result = await requestService.createDraft({}, 0)

      expect(result).toEqual(mockError)
    })
  })

  describe('getRequest', () => {
    it('should create resource with correct config', () => {
      const mockResource = { data: {}, loading: false, error: null }
      apiClient.createResource.mockReturnValue(mockResource)

      const result = requestService.getRequest('REQ-001')

      expect(apiClient.createResource).toHaveBeenCalledWith({
        url: 'frappe.client.get',
        params: {
          doctype: 'Request',
          name: 'REQ-001'
        },
        auto: true
      })
      expect(result).toEqual(mockResource)
    })
  })

  describe('submitRequest', () => {
    it('should call submit API', async () => {
      apiClient.call.mockResolvedValue({ status: 'success' })

      await requestService.submitRequest('REQ-001')

      expect(apiClient.call).toHaveBeenCalledWith(
        'lodgeick.api.submit_request',
        { request_id: 'REQ-001' }
      )
    })
  })

  describe('getUserRequests', () => {
    it('should create resource with caching', () => {
      const mockResource = { data: [], loading: false, error: null }
      apiClient.createResource.mockReturnValue(mockResource)

      const result = requestService.getUserRequests()

      expect(apiClient.createResource).toHaveBeenCalledWith({
        url: 'lodgeick.api.get_user_requests',
        auto: true,
        cache: ['user-requests']
      })
      expect(result).toEqual(mockResource)
    })
  })

  describe('deleteDraft', () => {
    it('should call delete API', async () => {
      apiClient.call.mockResolvedValue({ status: 'deleted' })

      await requestService.deleteDraft('REQ-001')

      expect(apiClient.call).toHaveBeenCalledWith(
        'frappe.client.delete',
        {
          doctype: 'Request',
          name: 'REQ-001'
        }
      )
    })
  })
})
