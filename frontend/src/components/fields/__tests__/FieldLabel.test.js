import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FieldLabel from '../FieldLabel.vue'

describe('FieldLabel', () => {
  it('renders label text correctly', () => {
    const wrapper = mount(FieldLabel, {
      props: {
        fieldName: 'email',
        label: 'Email Address',
        required: false
      }
    })

    expect(wrapper.text()).toContain('Email Address')
    expect(wrapper.find('label').attributes('for')).toBe('email')
  })

  it('shows required indicator when required is true', () => {
    const wrapper = mount(FieldLabel, {
      props: {
        fieldName: 'email',
        label: 'Email Address',
        required: true
      }
    })

    const requiredIndicator = wrapper.find('.text-red-500')
    expect(requiredIndicator.exists()).toBe(true)
    expect(requiredIndicator.text()).toBe('*')
  })

  it('does not show required indicator when required is false', () => {
    const wrapper = mount(FieldLabel, {
      props: {
        fieldName: 'email',
        label: 'Email Address',
        required: false
      }
    })

    const requiredIndicator = wrapper.find('.text-red-500')
    expect(requiredIndicator.exists()).toBe(false)
  })

  it('renders help text tooltip when provided', () => {
    const wrapper = mount(FieldLabel, {
      props: {
        fieldName: 'email',
        label: 'Email Address',
        required: false,
        helpText: 'Enter a valid email address'
      }
    })

    // Tooltip component should be rendered (check for tooltip button)
    const tooltipButton = wrapper.find('[type="button"]')
    expect(tooltipButton.exists()).toBe(true)
    // Help text is passed as prop to component
    expect(wrapper.vm.$props.helpText).toBe('Enter a valid email address')
  })

  it('does not render tooltip when help text is not provided', () => {
    const wrapper = mount(FieldLabel, {
      props: {
        fieldName: 'email',
        label: 'Email Address',
        required: false
      }
    })

    // Should not have tooltip
    expect(wrapper.findComponent({ name: 'Tooltip' }).exists()).toBe(false)
  })

  it('applies correct CSS classes', () => {
    const wrapper = mount(FieldLabel, {
      props: {
        fieldName: 'email',
        label: 'Email Address',
        required: false
      }
    })

    const label = wrapper.find('label')
    expect(label.classes()).toContain('block')
    expect(label.classes()).toContain('text-sm')
    expect(label.classes()).toContain('font-medium')
    expect(label.classes()).toContain('text-gray-700')
  })
})
