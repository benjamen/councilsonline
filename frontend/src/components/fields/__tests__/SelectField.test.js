import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SelectField from '../SelectField.vue'
import FieldLabel from '../FieldLabel.vue'
import FieldError from '../FieldError.vue'

describe('SelectField', () => {
  const mockField = {
    field_name: 'country',
    field_label: 'Country',
    is_required: 1,
    description: 'Select your country'
  }

  const mockOptions = ['New Zealand', 'Australia', 'United States', 'United Kingdom']

  it('renders select element with correct attributes', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    expect(select.attributes('id')).toBe('country')
    expect(select.attributes('name')).toBe('country')
  })

  it('renders FieldLabel component with correct props', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: mockOptions
      }
    })

    const label = wrapper.findComponent(FieldLabel)
    expect(label.exists()).toBe(true)
    expect(label.props('fieldName')).toBe('country')
    expect(label.props('label')).toBe('Country')
    expect(label.props('required')).toBe(true)
  })

  it('renders FieldError component with correct props', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: mockOptions,
        validationError: 'This field is required'
      }
    })

    const error = wrapper.findComponent(FieldError)
    expect(error.exists()).toBe(true)
    expect(error.props('error')).toBe('This field is required')
    expect(error.props('description')).toBe('Select your country')
  })

  it('renders placeholder option', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: mockOptions
      }
    })

    const options = wrapper.findAll('option')
    expect(options[0].text()).toBe('Select Country')
    expect(options[0].attributes('value')).toBe('')
  })

  it('renders all provided options', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: mockOptions
      }
    })

    const options = wrapper.findAll('option')
    // +1 for placeholder option
    expect(options.length).toBe(mockOptions.length + 1)

    mockOptions.forEach((option, index) => {
      expect(options[index + 1].text()).toBe(option)
      expect(options[index + 1].attributes('value')).toBe(option)
    })
  })

  it('displays current selected value', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: 'Australia',
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    expect(select.element.value).toBe('Australia')
  })

  it('emits update:modelValue when selection changes', async () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    await select.setValue('New Zealand')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['New Zealand'])
  })

  it('emits validate event on blur', async () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: 'Australia',
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    await select.trigger('blur')

    expect(wrapper.emitted('validate')).toBeTruthy()
  })

  it('applies error styles when validationError is present', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: mockOptions,
        validationError: 'Invalid selection'
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('border-red-500')
    expect(select.classes()).toContain('ring-red-100')
  })

  it('applies success styles when value is selected and no error', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: 'New Zealand',
        options: mockOptions,
        validationError: ''
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('border-blue-500')
    expect(select.classes()).toContain('ring-blue-100')
  })

  it('renders dropdown arrow icon', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: mockOptions
      }
    })

    const icon = wrapper.find('.absolute svg')
    expect(icon.exists()).toBe(true)
    expect(icon.classes()).toContain('h-5')
    expect(icon.classes()).toContain('w-5')
  })

  it('marks select as required when field.is_required is truthy', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: { ...mockField, is_required: 1 },
        modelValue: '',
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    expect(select.attributes('required')).toBeDefined()
  })

  it('handles empty options array', () => {
    const wrapper = mount(SelectField, {
      props: {
        field: mockField,
        modelValue: '',
        options: []
      }
    })

    const options = wrapper.findAll('option')
    // Only placeholder option should exist
    expect(options.length).toBe(1)
    expect(options[0].text()).toBe('Select Country')
  })
})
