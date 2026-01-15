import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

// Mock vue-router
const mockPush = vi.fn()
const mockBack = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
    back: mockBack
  })
}))

// Mock frappe-ui
vi.mock('frappe-ui', () => ({
  Button: {
    name: 'Button',
    props: ['loading', 'variant', 'theme', 'type'],
    template: '<button :type="type" :class="{ loading: loading }"><slot /></button>'
  },
  Input: {
    name: 'Input',
    props: ['modelValue', 'type', 'placeholder', 'required'],
    template: '<input :type="type" :value="modelValue" :placeholder="placeholder" :required="required" @input="$emit(\'update:modelValue\', $event.target.value)" />'
  },
  call: vi.fn()
}))

import Settings from '../Settings.vue'

describe('Settings', () => {
  // Helper function to mount with initial profile data
  const mountSettings = async (profileData = {}) => {
    const wrapper = mount(Settings)

    // Set profile data if provided
    if (Object.keys(profileData).length > 0) {
      wrapper.vm.profile = {
        full_name: 'John Doe',
        email: 'john@example.com',
        first_name: 'John',
        last_name: 'Doe',
        creation: '2025-01-01',
        ...profileData
      }
      wrapper.vm.profileLoading = false
      await wrapper.vm.$nextTick()
    }

    return wrapper
  }

  beforeEach(() => {
    mockPush.mockClear()
    mockBack.mockClear()
  })

  // ========== Header Tests ==========

  it('renders header with title', async () => {
    const wrapper = await mountSettings()
    expect(wrapper.find('h1').text()).toBe('Settings')
    expect(wrapper.text()).toContain('Manage your profile and preferences')
  })

  it('renders back button in header', async () => {
    const wrapper = await mountSettings()
    const backButton = wrapper.find('button svg')
    expect(backButton.exists()).toBe(true)
  })

  it('back button calls router.back when clicked', async () => {
    const wrapper = await mountSettings()
    const backButton = wrapper.findAll('button').at(0)

    await backButton.trigger('click')

    expect(mockBack).toHaveBeenCalled()
  })

  // ========== Tab Navigation Tests ==========

  it('renders all three tabs', async () => {
    const wrapper = await mountSettings()
    expect(wrapper.text()).toContain('Profile')
    expect(wrapper.text()).toContain('Organization')
    expect(wrapper.text()).toContain('Security')
  })

  it('profile tab is selected by default', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    const profileTab = wrapper.findAll('nav button').at(0)
    expect(profileTab.classes()).toContain('bg-blue-50')
    expect(profileTab.classes()).toContain('text-blue-700')
  })

  it('clicking a tab changes currentTab', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    const securityTab = wrapper.findAll('nav button').at(2)

    await securityTab.trigger('click')

    expect(wrapper.vm.currentTab).toBe('security')
  })

  it('inactive tabs have correct styling', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    const orgTab = wrapper.findAll('nav button').at(1)
    expect(orgTab.classes()).toContain('text-gray-700')
    expect(orgTab.classes()).toContain('hover:bg-gray-50')
  })

  // ========== Loading State Tests ==========

  it('shows loading state when profileLoading is true', async () => {
    const wrapper = mount(Settings)
    // profileLoading defaults to true
    expect(wrapper.text()).toContain('Loading settings...')
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })

  it('hides loading state when profileLoading is false', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    expect(wrapper.text()).not.toContain('Loading settings...')
    expect(wrapper.find('.animate-spin').exists()).toBe(false)
  })

  // ========== Profile Tab Tests ==========

  it('shows profile tab content when selected', async () => {
    const wrapper = await mountSettings({ full_name: 'John Doe' })
    wrapper.vm.currentTab = 'profile'
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Profile Information')
  })

  it('displays user initials when no profile image', async () => {
    const wrapper = await mountSettings({
      first_name: 'John',
      last_name: 'Doe',
      full_name: 'John Doe'
    })
    wrapper.vm.currentTab = 'profile'

    const initials = wrapper.find('.text-3xl.font-bold.text-blue-600')
    expect(initials.text()).toBe('JD')
  })

  it('displays user full name and email', async () => {
    const wrapper = await mountSettings({
      full_name: 'John Doe',
      email: 'john@example.com'
    })
    wrapper.vm.currentTab = 'profile'

    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@example.com')
  })

  it('renders profile form fields', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'profile'

    // Check for labels
    expect(wrapper.text()).toContain('First Name')
    expect(wrapper.text()).toContain('Last Name')
    expect(wrapper.text()).toContain('Mobile Phone')
    expect(wrapper.text()).toContain('Phone')
    expect(wrapper.text()).toContain('Location')
    expect(wrapper.text()).toContain('Bio')
  })

  it('renders Save Changes and Cancel buttons on profile tab', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'profile'

    const buttons = wrapper.findAllComponents({ name: 'Button' })
    const saveButton = buttons.find(btn => btn.text() === 'Save Changes')
    const cancelButton = buttons.find(btn => btn.text() === 'Cancel')

    expect(saveButton).toBeTruthy()
    expect(cancelButton).toBeTruthy()
  })

  // ========== Organization Tab Tests ==========

  it('shows organization tab content when selected', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'organization'
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Organization Details')
  })

  it('shows "No Organization Linked" message when no org data', async () => {
    const wrapper = await mountSettings({
      full_name: 'Test User',
      organization_data: null
    })
    wrapper.vm.currentTab = 'organization'
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('No Organization Linked')
    expect(wrapper.text()).toContain('Contact an administrator to link your account')
  })

  it('shows organization form when org data exists', async () => {
    const wrapper = await mountSettings({
      full_name: 'Test User',
      organization_data: { name: 'Test Org' }
    })
    wrapper.vm.currentTab = 'organization'
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Organization Name')
    expect(wrapper.text()).toContain('Contact Email')
    expect(wrapper.text()).toContain('Contact Phone')
  })

  // ========== Security Tab Tests ==========

  it('shows security tab content when selected', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'security'
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Change Password')
  })

  it('renders password form fields', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'security'
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Current Password')
    expect(wrapper.text()).toContain('New Password')
    expect(wrapper.text()).toContain('Confirm New Password')
  })

  it('shows password error message when set', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'security'
    wrapper.vm.passwordError = 'Passwords do not match'
    await wrapper.vm.$nextTick()

    const errorBox = wrapper.find('.bg-red-50')
    expect(errorBox.exists()).toBe(true)
    expect(errorBox.text()).toContain('Passwords do not match')
  })

  it('shows password success message when set', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'security'
    wrapper.vm.passwordSuccess = 'Password changed successfully'
    await wrapper.vm.$nextTick()

    const successBox = wrapper.find('.bg-green-50')
    expect(successBox.exists()).toBe(true)
    expect(successBox.text()).toContain('Password changed successfully')
  })

  it('renders Change Password button', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'security'
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAllComponents({ name: 'Button' })
    const changePasswordBtn = buttons.find(btn => btn.text() === 'Change Password')
    expect(changePasswordBtn).toBeTruthy()
  })

  // ========== Button Loading States Tests ==========

  it('Save Changes button shows loading state', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'profile'
    wrapper.vm.saving = true
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAllComponents({ name: 'Button' })
    const saveButton = buttons.find(btn => btn.text() === 'Save Changes')
    expect(saveButton.props('loading')).toBe(true)
  })

  it('Change Password button shows loading state', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })
    wrapper.vm.currentTab = 'security'
    wrapper.vm.changingPassword = true
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAllComponents({ name: 'Button' })
    const changePasswordBtn = buttons.find(btn => btn.text() === 'Change Password')
    expect(changePasswordBtn.props('loading')).toBe(true)
  })

  // ========== Styling Tests ==========

  it('applies background color to page', async () => {
    const wrapper = await mountSettings()
    const container = wrapper.find('.min-h-screen')
    expect(container.classes()).toContain('bg-gray-50')
  })

  it('applies header styling', async () => {
    const wrapper = await mountSettings()
    const header = wrapper.find('header')
    expect(header.classes()).toContain('bg-white')
    expect(header.classes()).toContain('shadow-sm')
    expect(header.classes()).toContain('border-b')
  })

  it('applies card styling to sidebar nav', async () => {
    const wrapper = await mountSettings()
    const nav = wrapper.find('nav')
    expect(nav.classes()).toContain('bg-white')
    expect(nav.classes()).toContain('rounded-lg')
    expect(nav.classes()).toContain('shadow-sm')
  })

  // ========== Complete Structure Test ==========

  it('renders complete settings page structure', async () => {
    const wrapper = await mountSettings({ full_name: 'Test User' })

    // Check major sections
    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.find('main').exists()).toBe(true)
    expect(wrapper.find('nav').exists()).toBe(true)

    // Check tabs are rendered
    const navButtons = wrapper.findAll('nav button')
    expect(navButtons.length).toBe(3)

    // Check content area exists
    expect(wrapper.find('.lg\\:col-span-3').exists()).toBe(true)
  })
})
