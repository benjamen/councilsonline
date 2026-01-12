import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FormSection from '../FormSection.vue'

describe('FormSection', () => {
  it('renders title correctly', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Personal Information'
      }
    })

    const title = wrapper.find('h3')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('Personal Information')
  })

  it('renders subtitle when provided', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Contact Details',
        subtitle: 'Please provide your contact information'
      }
    })

    const subtitle = wrapper.find('.text-sm.text-gray-600')
    expect(subtitle.exists()).toBe(true)
    expect(subtitle.text()).toBe('Please provide your contact information')
  })

  it('does not render subtitle when not provided', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Contact Details'
      }
    })

    const subtitle = wrapper.find('.text-sm.text-gray-600')
    expect(subtitle.exists()).toBe(false)
  })

  it('displays required badge when required is true', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Required Section',
        required: true
      }
    })

    const badge = wrapper.find('.bg-red-100.text-red-800')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('Required')
  })

  it('does not display required badge when required is false', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Optional Section',
        required: false
      }
    })

    const badge = wrapper.find('.bg-red-100.text-red-800')
    expect(badge.exists()).toBe(false)
  })

  it('renders default slot content', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Test Section'
      },
      slots: {
        default: '<div class="test-content">Form fields go here</div>'
      }
    })

    expect(wrapper.find('.test-content').exists()).toBe(true)
    expect(wrapper.find('.test-content').text()).toBe('Form fields go here')
  })

  it('renders default icon when no icon slot provided', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Test Section'
      }
    })

    const icon = wrapper.find('.w-10.h-10.rounded-lg.bg-blue-100 svg')
    expect(icon.exists()).toBe(true)
    expect(icon.classes()).toContain('text-blue-600')
  })

  it('renders custom icon slot when provided', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Test Section'
      },
      slots: {
        icon: '<div class="custom-icon">★</div>'
      }
    })

    const customIcon = wrapper.find('.custom-icon')
    expect(customIcon.exists()).toBe(true)
    expect(customIcon.text()).toBe('★')
  })

  it('renders footer slot when provided', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Test Section'
      },
      slots: {
        footer: '<button class="footer-button">Submit</button>'
      }
    })

    const footer = wrapper.find('.bg-gray-50.border-t')
    expect(footer.exists()).toBe(true)
    expect(footer.find('.footer-button').text()).toBe('Submit')
  })

  it('does not render footer when no footer slot provided', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Test Section'
      }
    })

    const footer = wrapper.find('.bg-gray-50.border-t')
    expect(footer.exists()).toBe(false)
  })

  it('applies correct base styling classes', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Test Section'
      }
    })

    const container = wrapper.find('.bg-white.rounded-xl')
    expect(container.exists()).toBe(true)
    expect(container.classes()).toContain('shadow-sm')
    expect(container.classes()).toContain('border')
    expect(container.classes()).toContain('border-gray-200')
  })

  it('applies gradient background to header', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Test Section'
      }
    })

    const header = wrapper.find('.bg-gradient-to-r')
    expect(header.exists()).toBe(true)
    expect(header.classes()).toContain('from-blue-50')
    expect(header.classes()).toContain('to-indigo-50')
  })

  it('renders all elements in correct structure', () => {
    const wrapper = mount(FormSection, {
      props: {
        title: 'Complete Section',
        subtitle: 'With all features',
        required: true
      },
      slots: {
        default: '<p>Content</p>',
        footer: '<p>Footer</p>'
      }
    })

    // Verify structure: header, content, footer
    const container = wrapper.element
    expect(container.children.length).toBeGreaterThanOrEqual(3)

    // Header with title and required badge
    expect(wrapper.find('h3').text()).toBe('Complete Section')
    expect(wrapper.find('.text-sm.text-gray-600').text()).toBe('With all features')
    expect(wrapper.find('.bg-red-100').text()).toContain('Required')

    // Content
    expect(wrapper.html()).toContain('<p>Content</p>')

    // Footer
    expect(wrapper.html()).toContain('<p>Footer</p>')
  })
})
