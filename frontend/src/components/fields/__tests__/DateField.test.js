import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DateField from '../DateField.vue'
import FieldLabel from '../FieldLabel.vue'
import FieldError from '../FieldError.vue'

describe('DateField', () => {
  const mockField = {
    field_name: 'birth_date',
    field_label: 'Date of Birth',
    is_required: 1,
    description: 'Enter your date of birth'
  }

  it('renders input with type date', () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('type')).toBe('date')
    expect(input.attributes('id')).toBe('birth_date')
    expect(input.attributes('name')).toBe('birth_date')
  })

  it('renders FieldLabel component with correct props', () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: ''
      }
    })

    const label = wrapper.findComponent(FieldLabel)
    expect(label.exists()).toBe(true)
    expect(label.props('fieldName')).toBe('birth_date')
    expect(label.props('label')).toBe('Date of Birth')
    expect(label.props('required')).toBe(true)
  })

  it('renders FieldError component with correct props', () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: '',
        validationError: 'This field is required'
      }
    })

    const error = wrapper.findComponent(FieldError)
    expect(error.exists()).toBe(true)
    expect(error.props('error')).toBe('This field is required')
    expect(error.props('description')).toBe('Enter your date of birth')
  })

  it('displays current date value', () => {
    const dateValue = '2000-06-15'
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: dateValue
      }
    })

    const input = wrapper.find('input')
    expect(input.element.value).toBe(dateValue)
  })

  it('emits update:modelValue when date changes', async () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    const newDate = '2025-12-25'
    await input.setValue(newDate)

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([newDate])
  })

  it('emits validate event on blur', async () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: '2000-01-01'
      }
    })

    const input = wrapper.find('input')
    await input.trigger('blur')

    expect(wrapper.emitted('validate')).toBeTruthy()
  })

  it('renders calendar icon', () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: ''
      }
    })

    const icon = wrapper.find('.absolute svg')
    expect(icon.exists()).toBe(true)
    expect(icon.classes()).toContain('h-5')
    expect(icon.classes()).toContain('w-5')
    expect(icon.classes()).toContain('text-gray-400')
  })

  it('applies error styles when validationError is present', () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: '',
        validationError: 'Invalid date'
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-red-500')
    expect(input.classes()).toContain('ring-red-100')
  })

  it('applies success styles when value is present and no error', () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: '2025-01-12',
        validationError: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-blue-500')
    expect(input.classes()).toContain('ring-blue-100')
  })

  it('marks input as required when field.is_required is truthy', () => {
    const wrapper = mount(DateField, {
      props: {
        field: { ...mockField, is_required: 1 },
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('required')).toBeDefined()
  })

  it('handles empty date value', () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.element.value).toBe('')
    // Should not have success styling when empty
    expect(input.classes()).not.toContain('border-blue-500')
  })

  it('applies base styling classes', () => {
    const wrapper = mount(DateField, {
      props: {
        field: mockField,
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('block')
    expect(input.classes()).toContain('w-full')
    expect(input.classes()).toContain('rounded-lg')
    expect(input.classes()).toContain('focus:ring-2')
    expect(input.classes()).toContain('focus:ring-blue-500')
  })
})
