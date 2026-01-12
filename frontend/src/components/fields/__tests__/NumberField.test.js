import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import NumberField from '../NumberField.vue'
import FieldLabel from '../FieldLabel.vue'
import FieldError from '../FieldError.vue'

describe('NumberField', () => {
  const mockField = {
    field_name: 'amount',
    field_label: 'Amount',
    is_required: 1,
    description: 'Enter a numeric value'
  }

  it('renders input with type number', () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 0
      }
    })

    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('type')).toBe('number')
  })

  it('renders FieldLabel and FieldError components', () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 0
      }
    })

    expect(wrapper.findComponent(FieldLabel).exists()).toBe(true)
    expect(wrapper.findComponent(FieldError).exists()).toBe(true)
  })

  describe('int variant', () => {
    it('sets step attribute to 1 for integers', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'int'
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('step')).toBe('1')
    })

    it('displays number icon for int variant', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'int'
        }
      })

      const icon = wrapper.find('.absolute svg')
      expect(icon.exists()).toBe(true)
    })

    it('does not display currency symbol for int variant', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'int'
        }
      })

      // Check for the currency symbol container specifically
      const currencySymbolContainer = wrapper.find('.inset-y-0.left-0')
      expect(currencySymbolContainer.exists()).toBe(false)
    })
  })

  describe('float variant', () => {
    it('sets step attribute to 0.01 for floats', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'float'
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('step')).toBe('0.01')
    })

    it('displays number icon for float variant', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'float'
        }
      })

      const icon = wrapper.find('.absolute svg')
      expect(icon.exists()).toBe(true)
    })
  })

  describe('currency variant', () => {
    it('sets step attribute to 0.01 for currency', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'currency'
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('step')).toBe('0.01')
    })

    it('displays currency symbol', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'currency'
        }
      })

      const currencySymbol = wrapper.find('.text-gray-500')
      expect(currencySymbol.exists()).toBe(true)
      expect(currencySymbol.text()).toBe('₱')
    })

    it('applies left padding for currency symbol', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'currency'
        }
      })

      const input = wrapper.find('input')
      expect(input.classes()).toContain('pl-10')
    })

    it('uses currency placeholder (0.00) when variant is currency', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'currency',
          placeholder: 'Custom placeholder'
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('placeholder')).toBe('0.00')
    })

    it('does not display number icon for currency variant', () => {
      const wrapper = mount(NumberField, {
        props: {
          field: mockField,
          modelValue: 0,
          variant: 'currency'
        }
      })

      // Currency variant should not have the number icon
      const icon = wrapper.find('.absolute.right-3 svg')
      expect(icon.exists()).toBe(false)
    })
  })

  it('displays current numeric value', () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 12345.67
      }
    })

    const input = wrapper.find('input')
    expect(input.element.value).toBe('12345.67')
  })

  it('emits parsed float value on input', async () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 0
      }
    })

    const input = wrapper.find('input')
    await input.setValue('42.5')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([42.5])
  })

  it('emits 0 when input is invalid or empty', async () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 10
      }
    })

    const input = wrapper.find('input')
    // Set value to empty string to trigger parseFloat fallback
    await input.setValue('')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    // parseFloat('') returns NaN, so the || 0 fallback should give us 0
    expect(wrapper.emitted('update:modelValue')[0][0]).toBe(0)
  })

  it('emits validate event on blur', async () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 100
      }
    })

    const input = wrapper.find('input')
    await input.trigger('blur')

    expect(wrapper.emitted('validate')).toBeTruthy()
  })

  it('applies error styles when validationError is present', () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 0,
        validationError: 'Invalid number'
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-red-500')
    expect(input.classes()).toContain('ring-red-100')
  })

  it('applies success styles when value is present and no error', () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 123,
        validationError: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-blue-500')
    expect(input.classes()).toContain('ring-blue-100')
  })

  it('uses custom placeholder for non-currency variants', () => {
    const wrapper = mount(NumberField, {
      props: {
        field: mockField,
        modelValue: 0,
        variant: 'int',
        placeholder: 'Enter quantity'
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('placeholder')).toBe('Enter quantity')
  })
})
