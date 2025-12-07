import { describe, it, expect, beforeEach } from 'vitest'
import { useStepValidation } from '../../../src/composables/useStepValidation'

describe('useStepValidation', () => {
  let validation

  beforeEach(() => {
    validation = useStepValidation()
  })

  describe('initialization', () => {
    it('should initialize with empty errors', () => {
      expect(validation.errors.value).toEqual({})
      expect(validation.isValidating.value).toBe(false)
    })
  })

  describe('validateConfigField', () => {
    it('should validate required field with value', () => {
      const field = {
        field_name: 'applicant_name',
        field_label: 'Applicant Name',
        is_required: 1
      }

      const result = validation.validateConfigField(
        'applicant_name',
        'John Doe',
        field,
        { applicant_name: 'John Doe' }
      )

      expect(result).toBe(true)
      expect(validation.errors.value.applicant_name).toBeUndefined()
    })

    it('should fail required field without value', () => {
      const field = {
        field_name: 'applicant_name',
        field_label: 'Applicant Name',
        is_required: 1
      }

      const result = validation.validateConfigField(
        'applicant_name',
        '',
        field,
        {}
      )

      expect(result).toBe(false)
      expect(validation.errors.value.applicant_name).toBe('Applicant Name is required')
    })

    it('should validate email format', () => {
      const field = {
        field_name: 'email',
        field_label: 'Email',
        validation: 'email',
        is_required: 0
      }

      const validResult = validation.validateConfigField(
        'email',
        'test@example.com',
        field,
        { email: 'test@example.com' }
      )

      expect(validResult).toBe(true)

      const invalidResult = validation.validateConfigField(
        'email',
        'invalid-email',
        field,
        { email: 'invalid-email' }
      )

      expect(invalidResult).toBe(false)
      expect(validation.errors.value.email).toBeDefined()
    })

    it('should allow empty value for non-required field', () => {
      const field = {
        field_name: 'optional_field',
        field_label: 'Optional Field',
        is_required: 0
      }

      const result = validation.validateConfigField(
        'optional_field',
        '',
        field,
        {}
      )

      expect(result).toBe(true)
      expect(validation.errors.value.optional_field).toBeUndefined()
    })
  })

  describe('validateStep', () => {
    it('should validate entire step with all fields valid', async () => {
      const stepConfig = {
        sections: [
          {
            fields: [
              {
                field_name: 'applicant_name',
                field_label: 'Applicant Name',
                is_required: 1
              },
              {
                field_name: 'email',
                field_label: 'Email',
                validation: 'email',
                is_required: 1
              }
            ]
          }
        ]
      }

      const formData = {
        applicant_name: 'John Doe',
        email: 'john@example.com'
      }

      const result = await validation.validateStep(stepConfig, formData)

      expect(result).toBe(true)
      expect(Object.keys(validation.errors.value)).toHaveLength(0)
    })

    it('should fail step validation with invalid fields', async () => {
      const stepConfig = {
        sections: [
          {
            fields: [
              {
                field_name: 'applicant_name',
                field_label: 'Applicant Name',
                is_required: 1
              },
              {
                field_name: 'email',
                field_label: 'Email',
                validation: 'email',
                is_required: 1
              }
            ]
          }
        ]
      }

      const formData = {
        applicant_name: '',
        email: 'invalid-email'
      }

      const result = await validation.validateStep(stepConfig, formData)

      expect(result).toBe(false)
      expect(validation.errors.value.applicant_name).toBeDefined()
      expect(validation.errors.value.email).toBeDefined()
    })

    it('should skip sections with depends_on condition not met', async () => {
      const stepConfig = {
        sections: [
          {
            depends_on: "eval:formData.applicant_type=='Company'",
            fields: [
              {
                field_name: 'company_name',
                field_label: 'Company Name',
                is_required: 1
              }
            ]
          }
        ]
      }

      const formData = {
        applicant_type: 'Individual'
        // company_name not provided, but should be skipped
      }

      const result = await validation.validateStep(stepConfig, formData)

      expect(result).toBe(true)
      expect(validation.errors.value.company_name).toBeUndefined()
    })

    it('should validate sections when depends_on condition is met', async () => {
      const stepConfig = {
        sections: [
          {
            depends_on: "eval:formData.applicant_type=='Company'",
            fields: [
              {
                field_name: 'company_name',
                field_label: 'Company Name',
                is_required: 1
              }
            ]
          }
        ]
      }

      const formData = {
        applicant_type: 'Company',
        company_name: ''
      }

      const result = await validation.validateStep(stepConfig, formData)

      expect(result).toBe(false)
      expect(validation.errors.value.company_name).toBe('Company Name is required')
    })

    it('should skip fields with depends_on condition not met', async () => {
      const stepConfig = {
        sections: [
          {
            fields: [
              {
                field_name: 'has_agent',
                field_label: 'Has Agent',
                is_required: 1
              },
              {
                field_name: 'agent_name',
                field_label: 'Agent Name',
                depends_on: 'eval:formData.has_agent==1',
                is_required: 1
              }
            ]
          }
        ]
      }

      const formData = {
        has_agent: 0
        // agent_name not provided, but should be skipped
      }

      const result = await validation.validateStep(stepConfig, formData)

      expect(result).toBe(true)
      expect(validation.errors.value.agent_name).toBeUndefined()
    })

    it('should set isValidating flag during validation', async () => {
      const stepConfig = {
        sections: [
          {
            fields: [
              {
                field_name: 'test_field',
                field_label: 'Test Field',
                is_required: 1
              }
            ]
          }
        ]
      }

      await validation.validateStep(stepConfig, { test_field: 'value' })

      // Check flag is cleared after validation completes
      expect(validation.isValidating.value).toBe(false)
    })
  })

  describe('clearErrors', () => {
    it('should clear all errors', () => {
      validation.errors.value = {
        field1: 'Error 1',
        field2: 'Error 2'
      }

      validation.clearErrors()

      expect(validation.errors.value).toEqual({})
    })
  })

  describe('clearFieldError', () => {
    it('should clear specific field error', () => {
      validation.errors.value = {
        field1: 'Error 1',
        field2: 'Error 2'
      }

      validation.clearFieldError('field1')

      expect(validation.errors.value.field1).toBeUndefined()
      expect(validation.errors.value.field2).toBe('Error 2')
    })

    it('should do nothing if field has no error', () => {
      validation.errors.value = {
        field1: 'Error 1'
      }

      expect(() => validation.clearFieldError('nonexistent')).not.toThrow()

      expect(validation.errors.value).toEqual({ field1: 'Error 1' })
    })
  })
})
