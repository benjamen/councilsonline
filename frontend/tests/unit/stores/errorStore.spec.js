import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useErrorStore } from '../../../src/stores/errorStore'

describe('ErrorStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('initialization', () => {
    it('should initialize with empty state', () => {
      const store = useErrorStore()

      expect(store.errors).toEqual([])
      expect(store.globalError).toBeNull()
    })
  })

  describe('getters', () => {
    it('should identify when errors exist', () => {
      const store = useErrorStore()

      expect(store.hasErrors).toBe(false)

      store.addError('Test error')

      expect(store.hasErrors).toBe(true)
    })

    it('should return latest error', () => {
      const store = useErrorStore()

      store.addError('Error 1')
      store.addError('Error 2')
      store.addError('Error 3')

      expect(store.latestError.message).toBe('Error 3')
    })

    it('should return undefined for latestError when no errors', () => {
      const store = useErrorStore()

      expect(store.latestError).toBeUndefined()
    })
  })

  describe('addError', () => {
    it('should add string error', () => {
      const store = useErrorStore()

      store.addError('Test error message')

      expect(store.errors).toHaveLength(1)
      expect(store.errors[0].message).toBe('Test error message')
      expect(store.errors[0].type).toBe('error')
      expect(store.errors[0].timestamp).toBeInstanceOf(Date)
    })

    it('should add error object', () => {
      const store = useErrorStore()

      store.addError({
        message: 'Custom error',
        type: 'validation'
      })

      expect(store.errors).toHaveLength(1)
      expect(store.errors[0].message).toBe('Custom error')
      expect(store.errors[0].type).toBe('validation')
    })

    it('should generate unique error IDs', () => {
      const store = useErrorStore()

      store.addError('Error 1')
      store.addError('Error 2')

      expect(store.errors[0].id).not.toBe(store.errors[1].id)
    })

    it('should auto-clear non-critical errors after 10 seconds', () => {
      const store = useErrorStore()

      store.addError('Auto-clear error')

      expect(store.errors).toHaveLength(1)

      vi.advanceTimersByTime(10000)

      expect(store.errors).toHaveLength(0)
    })

    it('should NOT auto-clear critical errors', () => {
      const store = useErrorStore()

      store.addError({
        message: 'Critical error',
        type: 'critical'
      })

      expect(store.errors).toHaveLength(1)

      vi.advanceTimersByTime(10000)

      expect(store.errors).toHaveLength(1)
    })
  })

  describe('setGlobalError', () => {
    it('should set global error', () => {
      const store = useErrorStore()

      store.setGlobalError('Global failure')

      expect(store.globalError.message).toBe('Global failure')
      expect(store.globalError.timestamp).toBeInstanceOf(Date)
    })

    it('should overwrite previous global error', () => {
      const store = useErrorStore()

      store.setGlobalError('Error 1')
      store.setGlobalError('Error 2')

      expect(store.globalError.message).toBe('Error 2')
    })
  })

  describe('clearError', () => {
    it('should remove specific error by ID', () => {
      const store = useErrorStore()

      store.addError('Error 1')
      store.addError('Error 2')
      store.addError('Error 3')

      const errorId = store.errors[1].id

      store.clearError(errorId)

      expect(store.errors).toHaveLength(2)
      expect(store.errors.find(e => e.id === errorId)).toBeUndefined()
    })

    it('should do nothing if error ID not found', () => {
      const store = useErrorStore()

      store.addError('Error 1')

      store.clearError('nonexistent-id')

      expect(store.errors).toHaveLength(1)
    })
  })

  describe('clearAllErrors', () => {
    it('should clear all errors and global error', () => {
      const store = useErrorStore()

      store.addError('Error 1')
      store.addError('Error 2')
      store.setGlobalError('Global error')

      store.clearAllErrors()

      expect(store.errors).toEqual([])
      expect(store.globalError).toBeNull()
    })

    it('should work when already empty', () => {
      const store = useErrorStore()

      expect(() => store.clearAllErrors()).not.toThrow()

      expect(store.errors).toEqual([])
      expect(store.globalError).toBeNull()
    })
  })
})
