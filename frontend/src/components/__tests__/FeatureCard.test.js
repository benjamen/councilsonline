import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock frappe-ui
vi.mock('frappe-ui', () => ({
  FeatherIcon: {
    name: 'FeatherIcon',
    props: ['name'],
    template: '<span class="feather-icon" :data-icon="name"></span>'
  }
}))

import FeatureCard from '../FeatureCard.vue'

describe('FeatureCard', () => {
  it('renders icon correctly', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'check-circle',
        title: 'Fast Processing',
        description: 'Quick turnaround times'
      }
    })

    const icon = wrapper.findComponent({ name: 'FeatherIcon' })
    expect(icon.exists()).toBe(true)
    expect(icon.props('name')).toBe('check-circle')
  })

  it('renders title correctly', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'star',
        title: 'Excellent Service',
        description: 'Top-rated by users'
      }
    })

    const title = wrapper.find('h4')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('Excellent Service')
  })

  it('renders description correctly', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'shield',
        title: 'Secure Platform',
        description: 'Your data is protected with enterprise-grade security'
      }
    })

    const description = wrapper.find('p')
    expect(description.exists()).toBe(true)
    expect(description.text()).toBe('Your data is protected with enterprise-grade security')
  })

  it('applies base card styling classes', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'file',
        title: 'Test Card',
        description: 'Test description'
      }
    })

    const card = wrapper.find('.bg-gray-50')
    expect(card.exists()).toBe(true)
    expect(card.classes()).toContain('rounded-xl')
    expect(card.classes()).toContain('border')
    expect(card.classes()).toContain('border-gray-100')
  })

  it('applies hover shadow effect class', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'zap',
        title: 'Fast',
        description: 'Lightning speed'
      }
    })

    const card = wrapper.element
    expect(card.classList.contains('hover:shadow-lg')).toBe(true)
    expect(card.classList.contains('transition-shadow')).toBe(true)
  })

  it('applies correct icon container styling', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'heart',
        title: 'Favorite',
        description: 'Most loved feature'
      }
    })

    const iconContainer = wrapper.find('.bg-blue-100')
    expect(iconContainer.exists()).toBe(true)
    expect(iconContainer.classes()).toContain('rounded-lg')
    expect(iconContainer.classes()).toContain('w-12')
    expect(iconContainer.classes()).toContain('h-12')
  })

  it('applies correct title styling', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'award',
        title: 'Award Winning',
        description: 'Recognized excellence'
      }
    })

    const title = wrapper.find('h4')
    expect(title.classes()).toContain('text-lg')
    expect(title.classes()).toContain('font-semibold')
    expect(title.classes()).toContain('text-gray-900')
  })

  it('applies correct description styling', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'info',
        title: 'Information',
        description: 'Helpful details'
      }
    })

    const description = wrapper.find('p')
    expect(description.classes()).toContain('text-gray-600')
    expect(description.classes()).toContain('text-sm')
    expect(description.classes()).toContain('leading-relaxed')
  })

  it('renders all elements in correct structure', () => {
    const wrapper = mount(FeatureCard, {
      props: {
        icon: 'package',
        title: 'Complete Package',
        description: 'Everything you need in one place'
      }
    })

    // Check card container
    expect(wrapper.find('.bg-gray-50').exists()).toBe(true)

    // Check icon container
    const iconContainer = wrapper.find('.bg-blue-100')
    expect(iconContainer.exists()).toBe(true)

    // Check icon inside container
    const icon = iconContainer.findComponent({ name: 'FeatherIcon' })
    expect(icon.exists()).toBe(true)

    // Check title
    expect(wrapper.find('h4').exists()).toBe(true)

    // Check description
    expect(wrapper.find('p').exists()).toBe(true)
  })

  it('renders with different icons', () => {
    const icons = ['check', 'star', 'heart', 'shield', 'zap']

    icons.forEach(iconName => {
      const wrapper = mount(FeatureCard, {
        props: {
          icon: iconName,
          title: `Test ${iconName}`,
          description: 'Test description'
        }
      })

      const icon = wrapper.findComponent({ name: 'FeatherIcon' })
      expect(icon.props('name')).toBe(iconName)
    })
  })
})
