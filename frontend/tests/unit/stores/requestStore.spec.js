import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock frappe-ui to avoid icon imports
vi.mock('frappe-ui', () => ({
  createResource: vi.fn()
}))

// Mock services to avoid import issues
vi.mock('../../../src/services', () => {
  return {
    apiClient: {
      call: vi.fn(),
      createResource: vi.fn()
    },
    requestService: {
      createDraft: vi.fn(),
      submitRequest: vi.fn(),
      getRequest: vi.fn(),
      getRequestTypeConfig: vi.fn()
    }
  }
})

import { useRequestStore } from '../../../src/stores/requestStore'
import { requestService } from '../../../src/services'

describe('RequestStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('initialization', () => {
    it('should initialize with empty state', () => {
      const store = useRequestStore()

      expect(store.currentRequestId).toBeNull()
      expect(store.formData).toEqual({})
      expect(store.currentStep).toBe(0)
      expect(store.isSaving).toBe(false)
      expect(store.isSubmitting).toBe(false)
    })
  })

  describe('getters', () => {
    it('should identify first step correctly', () => {
      const store = useRequestStore()
      store.currentStep = 0

      expect(store.isFirstStep).toBe(true)

      store.currentStep = 1
      expect(store.isFirstStep).toBe(false)
    })

    it('should identify last step correctly', () => {
      const store = useRequestStore()
      store.requestTypeConfig = { steps: [{}, {}, {}] }
      store.currentStep = 2

      expect(store.isLastStep).toBe(true)

      store.currentStep = 1
      expect(store.isLastStep).toBe(false)
    })

    it('should calculate completion percentage', () => {
      const store = useRequestStore()
      store.requestTypeConfig = { steps: [{}, {}, {}, {}] }

      store.currentStep = 0
      expect(store.completionPercentage).toBe(25)

      store.currentStep = 2
      expect(store.completionPercentage).toBe(75)

      store.currentStep = 3
      expect(store.completionPercentage).toBe(100)
    })
  })

  describe('navigation', () => {
    it('should navigate to next step', () => {
      const store = useRequestStore()
      store.requestTypeConfig = { steps: [{}, {}, {}] }
      store.currentStep = 0

      store.nextStep()

      expect(store.currentStep).toBe(1)
    })

    it('should not navigate past last step', () => {
      const store = useRequestStore()
      store.requestTypeConfig = { steps: [{}, {}] }
      store.currentStep = 1

      store.nextStep()

      expect(store.currentStep).toBe(1)
    })

    it('should navigate to previous step', () => {
      const store = useRequestStore()
      store.currentStep = 2

      store.previousStep()

      expect(store.currentStep).toBe(1)
    })

    it('should not navigate before first step', () => {
      const store = useRequestStore()
      store.currentStep = 0

      store.previousStep()

      expect(store.currentStep).toBe(0)
    })

    it('should jump to specific step', () => {
      const store = useRequestStore()
      store.requestTypeConfig = { steps: [{}, {}, {}, {}] }

      store.goToStep(2)

      expect(store.currentStep).toBe(2)
    })

    it('should not jump to invalid step', () => {
      const store = useRequestStore()
      store.requestTypeConfig = { steps: [{}, {}] }
      store.currentStep = 0

      store.goToStep(5)

      expect(store.currentStep).toBe(0)
    })
  })

  describe('saveProgress', () => {
    it('should save progress and update request ID', async () => {
      const store = useRequestStore()
      const mockResponse = { request_id: 'REQ-001' }
      requestService.createDraft.mockResolvedValue(mockResponse)

      store.formData = { applicant_name: 'John Doe' }
      store.currentStep = 1

      await store.saveProgress()

      expect(requestService.createDraft).toHaveBeenCalledWith(
        { applicant_name: 'John Doe' },
        1
      )
      expect(store.currentRequestId).toBe('REQ-001')
      expect(store.lastSaved).toBeInstanceOf(Date)
      expect(store.isSaving).toBe(false)
    })

    it('should set isSaving flag during save', async () => {
      const store = useRequestStore()
      requestService.createDraft.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ request_id: 'REQ-001' }), 100))
      )

      const savePromise = store.saveProgress()

      expect(store.isSaving).toBe(true)

      await savePromise

      expect(store.isSaving).toBe(false)
    })

    it('should handle save errors gracefully', async () => {
      const store = useRequestStore()
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      requestService.createDraft.mockRejectedValue(new Error('Save failed'))

      await expect(store.saveProgress()).rejects.toThrow('Save failed')

      expect(consoleError).toHaveBeenCalled()
      expect(store.isSaving).toBe(false)

      consoleError.mockRestore()
    })
  })

  describe('submitRequest', () => {
    it('should submit request and reset state', async () => {
      const store = useRequestStore()
      store.currentRequestId = 'REQ-001'
      requestService.submitRequest.mockResolvedValue({})

      await store.submitRequest()

      expect(requestService.submitRequest).toHaveBeenCalledWith('REQ-001')
      expect(store.currentRequestId).toBeNull()
      expect(store.formData).toEqual({})
      expect(store.currentStep).toBe(0)
      expect(store.isSubmitting).toBe(false)
    })

    it('should set isSubmitting flag during submit', async () => {
      const store = useRequestStore()
      store.currentRequestId = 'REQ-001'
      requestService.submitRequest.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      )

      const submitPromise = store.submitRequest()

      expect(store.isSubmitting).toBe(true)

      await submitPromise

      expect(store.isSubmitting).toBe(false)
    })

    it('should handle submit errors', async () => {
      const store = useRequestStore()
      store.currentRequestId = 'REQ-001'
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      requestService.submitRequest.mockRejectedValue(new Error('Submit failed'))

      await expect(store.submitRequest()).rejects.toThrow('Submit failed')

      expect(store.isSubmitting).toBe(false)

      consoleError.mockRestore()
    })
  })

  describe('updateField', () => {
    it('should update single field', () => {
      const store = useRequestStore()

      store.updateField('applicant_name', 'Jane Doe')

      expect(store.formData.applicant_name).toBe('Jane Doe')
    })

    it('should update multiple fields', () => {
      const store = useRequestStore()

      store.updateField('field1', 'value1')
      store.updateField('field2', 'value2')

      expect(store.formData.field1).toBe('value1')
      expect(store.formData.field2).toBe('value2')
    })
  })

  describe('setStepValidation', () => {
    it('should track step validation status', () => {
      const store = useRequestStore()

      store.setStepValidation(0, true)
      store.setStepValidation(1, false)

      expect(store.stepValidationStatus[0]).toBe(true)
      expect(store.stepValidationStatus[1]).toBe(false)
    })
  })

  describe('reset', () => {
    it('should reset all state to initial values', () => {
      const store = useRequestStore()

      // Set some state
      store.currentRequestId = 'REQ-001'
      store.formData = { test: 'data' }
      store.currentStep = 3
      store.isSaving = true
      store.lastSaved = new Date()

      store.reset()

      expect(store.currentRequestId).toBeNull()
      expect(store.formData).toEqual({})
      expect(store.currentStep).toBe(0)
      expect(store.isSaving).toBe(false)
      expect(store.lastSaved).toBeNull()
    })
  })
})
