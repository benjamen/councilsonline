import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock frappe-ui module to avoid dependency issues in tests
vi.mock('frappe-ui', () => ({
  FeatherIcon: {
    name: 'FeatherIcon',
    props: ['name'],
    template: '<span class="feather-icon" :data-icon="name"></span>'
  }
}))

import StatCard from '../StatCard.vue'

// Helper to mount StatCard with props
const mountStatCard = (props) => {
  return mount(StatCard, { props })
}

describe('StatCard', () => {
  it('renders title correctly', () => {
    const wrapper = mountStatCard({
      title: 'Total Requests',
      value: 42,
      icon: 'inbox'
    })

    const title = wrapper.find('.text-sm.font-medium.text-gray-600')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('Total Requests')
  })

  it('renders numeric value correctly', () => {
    const wrapper = mountStatCard({
        title: 'Total Requests',
        value: 42,
        icon: 'inbox'
    })

    const value = wrapper.find('.text-3xl.font-bold')
    expect(value.exists()).toBe(true)
    expect(value.text()).toBe('42')
  })

  it('renders string value correctly', () => {
    const wrapper = mountStatCard({
        title: 'Status',
        value: 'Active',
        icon: 'check-circle'
    })

    const value = wrapper.find('.text-3xl.font-bold')
    expect(value.text()).toBe('Active')
  })

  it('renders FeatherIcon with correct icon name', () => {
    const wrapper = mountStatCard({
        title: 'New Items',
        value: 15,
        icon: 'alert-circle'
    })

    const icon = wrapper.findComponent({ name: 'FeatherIcon' })
    expect(icon.exists()).toBe(true)
    expect(icon.props('name')).toBe('alert-circle')
  })

  describe('blue color (default)', () => {
    it('applies blue color scheme', () => {
      const wrapper = mountStatCard({
          title: 'Total',
          value: 10,
          icon: 'inbox',
          color: 'blue'
      })

      const value = wrapper.find('.text-3xl.font-bold')
      expect(value.classes()).toContain('text-blue-600')

      const iconContainer = wrapper.find('.w-12.h-12.rounded-lg')
      expect(iconContainer.classes()).toContain('bg-blue-100')

      const icon = wrapper.findComponent({ name: 'FeatherIcon' })
      expect(icon.classes()).toContain('text-blue-600')
    })

    it('uses blue as default color', () => {
      const wrapper = mountStatCard({
          title: 'Default Color',
          value: 5,
          icon: 'inbox'
      })

      const value = wrapper.find('.text-3xl.font-bold')
      expect(value.classes()).toContain('text-blue-600')
    })
  })

  describe('green color', () => {
    it('applies green color scheme', () => {
      const wrapper = mountStatCard({
          title: 'Completed',
          value: 25,
          icon: 'check-circle',
          color: 'green'
      })

      const value = wrapper.find('.text-3xl.font-bold')
      expect(value.classes()).toContain('text-green-600')

      const iconContainer = wrapper.find('.w-12.h-12.rounded-lg')
      expect(iconContainer.classes()).toContain('bg-green-100')

      const icon = wrapper.findComponent({ name: 'FeatherIcon' })
      expect(icon.classes()).toContain('text-green-600')
    })
  })

  describe('yellow color', () => {
    it('applies yellow color scheme', () => {
      const wrapper = mountStatCard({
          title: 'In Progress',
          value: 8,
          icon: 'clock',
          color: 'yellow'
      })

      const value = wrapper.find('.text-3xl.font-bold')
      expect(value.classes()).toContain('text-yellow-600')

      const iconContainer = wrapper.find('.w-12.h-12.rounded-lg')
      expect(iconContainer.classes()).toContain('bg-yellow-100')

      const icon = wrapper.findComponent({ name: 'FeatherIcon' })
      expect(icon.classes()).toContain('text-yellow-600')
    })
  })

  describe('orange color', () => {
    it('applies orange color scheme', () => {
      const wrapper = mountStatCard({
          title: 'Pending',
          value: 12,
          icon: 'help-circle',
          color: 'orange'
      })

      const value = wrapper.find('.text-3xl.font-bold')
      expect(value.classes()).toContain('text-orange-600')

      const iconContainer = wrapper.find('.w-12.h-12.rounded-lg')
      expect(iconContainer.classes()).toContain('bg-orange-100')

      const icon = wrapper.findComponent({ name: 'FeatherIcon' })
      expect(icon.classes()).toContain('text-orange-600')
    })
  })

  describe('red color', () => {
    it('applies red color scheme', () => {
      const wrapper = mountStatCard({
          title: 'Declined',
          value: 3,
          icon: 'x-circle',
          color: 'red'
      })

      const value = wrapper.find('.text-3xl.font-bold')
      expect(value.classes()).toContain('text-red-600')

      const iconContainer = wrapper.find('.w-12.h-12.rounded-lg')
      expect(iconContainer.classes()).toContain('bg-red-100')

      const icon = wrapper.findComponent({ name: 'FeatherIcon' })
      expect(icon.classes()).toContain('text-red-600')
    })
  })

  describe('unknown color', () => {
    it('falls back to blue for unknown color', () => {
      const wrapper = mountStatCard({
          title: 'Test',
          value: 1,
          icon: 'inbox',
          color: 'purple'
      })

      const value = wrapper.find('.text-3xl.font-bold')
      expect(value.classes()).toContain('text-blue-600')

      const iconContainer = wrapper.find('.w-12.h-12.rounded-lg')
      expect(iconContainer.classes()).toContain('bg-blue-100')
    })
  })

  it('applies card base styling', () => {
    const wrapper = mountStatCard({
        title: 'Test',
        value: 0,
        icon: 'inbox'
    })

    const card = wrapper.find('.bg-white.rounded-lg.shadow-sm')
    expect(card.exists()).toBe(true)
    expect(card.classes()).toContain('border')
    expect(card.classes()).toContain('border-gray-200')
    expect(card.classes()).toContain('p-6')
  })

  it('uses flex layout for content and icon', () => {
    const wrapper = mountStatCard({
        title: 'Test',
        value: 0,
        icon: 'inbox'
    })

    const flexContainer = wrapper.find('.flex.items-center.justify-between')
    expect(flexContainer.exists()).toBe(true)
  })
})

