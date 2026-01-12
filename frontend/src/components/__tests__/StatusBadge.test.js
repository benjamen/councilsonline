import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '../StatusBadge.vue'

describe('StatusBadge', () => {
  it('renders status text correctly', () => {
    const wrapper = mount(StatusBadge, {
      props: {
        status: 'Submitted'
      }
    })

    expect(wrapper.text()).toBe('Submitted')
  })

  it('renders status indicator dot', () => {
    const wrapper = mount(StatusBadge, {
      props: {
        status: 'Draft'
      }
    })

    const dot = wrapper.find('.w-1\\.5.h-1\\.5.rounded-full')
    expect(dot.exists()).toBe(true)
  })

  describe('Draft status', () => {
    it('applies gray colors for Draft status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'Draft'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-gray-100')
      expect(badge.classes()).toContain('text-gray-800')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-gray-400')
    })
  })

  describe('Submitted status', () => {
    it('applies blue colors for Submitted status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'Submitted'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-blue-100')
      expect(badge.classes()).toContain('text-blue-800')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-blue-400')
    })
  })

  describe('Under Review status', () => {
    it('applies yellow colors for Under Review status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'Under Review'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-yellow-100')
      expect(badge.classes()).toContain('text-yellow-800')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-yellow-400')
    })
  })

  describe('RFI Issued status', () => {
    it('applies orange colors for RFI Issued status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'RFI Issued'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-orange-100')
      expect(badge.classes()).toContain('text-orange-800')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-orange-400')
    })
  })

  describe('Approved status', () => {
    it('applies green colors for Approved status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'Approved'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-green-100')
      expect(badge.classes()).toContain('text-green-800')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-green-400')
    })
  })

  describe('Declined status', () => {
    it('applies red colors for Declined status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'Declined'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-red-100')
      expect(badge.classes()).toContain('text-red-800')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-red-400')
    })
  })

  describe('Withdrawn status', () => {
    it('applies gray colors for Withdrawn status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'Withdrawn'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-gray-100')
      expect(badge.classes()).toContain('text-gray-600')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-gray-400')
    })
  })

  describe('Closed status', () => {
    it('applies gray colors for Closed status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'Closed'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-gray-100')
      expect(badge.classes()).toContain('text-gray-600')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-gray-400')
    })
  })

  describe('Unknown status', () => {
    it('applies fallback gray colors for unknown status', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'Unknown Status'
        }
      })

      const badge = wrapper.find('span')
      expect(badge.classes()).toContain('bg-gray-100')
      expect(badge.classes()).toContain('text-gray-800')

      const dot = wrapper.find('.w-1\\.5')
      expect(dot.classes()).toContain('bg-gray-400')
    })
  })

  it('applies base styling classes', () => {
    const wrapper = mount(StatusBadge, {
      props: {
        status: 'Draft'
      }
    })

    const badge = wrapper.find('span')
    expect(badge.classes()).toContain('inline-flex')
    expect(badge.classes()).toContain('items-center')
    expect(badge.classes()).toContain('rounded-full')
    expect(badge.classes()).toContain('text-xs')
    expect(badge.classes()).toContain('font-medium')
  })
})
