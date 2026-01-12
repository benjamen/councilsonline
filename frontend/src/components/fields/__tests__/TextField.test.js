import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TextField from '../TextField.vue'
import FieldLabel from '../FieldLabel.vue'
import FieldError from '../FieldError.vue'

describe('TextField', () => {
  const mockField = {
    field_name: 'full_name',
    field_label: 'Full Name',
    is_required: 1,
    description: 'Enter your full legal name'
  }

  it('renders input with correct attributes', () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: '',
        placeholder: 'John Doe'
      }
    })

    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('type')).toBe('text')
    expect(input.attributes('id')).toBe('full_name')
    expect(input.attributes('name')).toBe('full_name')
    expect(input.attributes('placeholder')).toBe('John Doe')
  })

  it('renders FieldLabel component with correct props', () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: ''
      }
    })

    const label = wrapper.findComponent(FieldLabel)
    expect(label.exists()).toBe(true)
    expect(label.props('fieldName')).toBe('full_name')
    expect(label.props('label')).toBe('Full Name')
    expect(label.props('required')).toBe(true)
  })

  it('renders FieldError component with correct props', () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: '',
        validationError: 'This field is required'
      }
    })

    const error = wrapper.findComponent(FieldError)
    expect(error.exists()).toBe(true)
    expect(error.props('error')).toBe('This field is required')
    expect(error.props('description')).toBe('Enter your full legal name')
  })

  it('displays current value in input', () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: 'Jane Smith'
      }
    })

    const input = wrapper.find('input')
    expect(input.element.value).toBe('Jane Smith')
  })

  it('emits update:modelValue when input changes', async () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    await input.setValue('New Value')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['New Value'])
  })

  it('emits validate event on blur', async () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: 'Test'
      }
    })

    const input = wrapper.find('input')
    await input.trigger('blur')

    expect(wrapper.emitted('validate')).toBeTruthy()
  })

  it('applies error styles when validationError is present', () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: '',
        validationError: 'Invalid input'
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-red-500')
    expect(input.classes()).toContain('ring-red-100')
  })

  it('applies success styles when value is present and no error', () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: 'Valid input',
        validationError: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-blue-500')
    expect(input.classes()).toContain('ring-blue-100')
  })

  it('renders icon when provided', () => {
    const iconSvg = '<svg class="w-5 h-5"><path d="M10 10"/></svg>'
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: '',
        icon: iconSvg
      }
    })

    const iconContainer = wrapper.find('.absolute.right-3')
    expect(iconContainer.exists()).toBe(true)
    expect(iconContainer.html()).toContain('<svg')
  })

  it('does not render icon container when icon is not provided', () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: '',
        icon: ''
      }
    })

    const iconContainer = wrapper.find('.absolute.right-3')
    expect(iconContainer.exists()).toBe(false)
  })

  it('marks input as required when field.is_required is truthy', () => {
    const wrapper = mount(TextField, {
      props: {
        field: { ...mockField, is_required: 1 },
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('required')).toBeDefined()
  })

  it('handles numeric modelValue', () => {
    const wrapper = mount(TextField, {
      props: {
        field: mockField,
        modelValue: 12345
      }
    })

    const input = wrapper.find('input')
    expect(input.element.value).toBe('12345')
  })
})
