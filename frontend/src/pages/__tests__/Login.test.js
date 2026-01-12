import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  RouterLink: {
    name: 'RouterLink',
    props: ['to'],
    template: '<a :href="typeof to === \'string\' ? to : to.name"><slot /></a>'
  }
}))

// Mock frappe-ui components
vi.mock('frappe-ui', () => ({
  Button: {
    name: 'Button',
    props: ['loading', 'variant', 'type'],
    template: '<button :type="type" :class="{ loading: loading }"><slot /></button>'
  },
  Input: {
    name: 'Input',
    props: ['id', 'name', 'type', 'required', 'placeholder', 'modelValue'],
    template: '<input :id="id" :name="name" :type="type" :required="required" :placeholder="placeholder" :value="modelValue" />'
  }
}))

// Mock session - create inline to avoid hoisting issues
vi.mock('../../data/session', () => ({
  session: {
    isLoggedIn: false,
    login: {
      loading: false,
      error: null,
      submit: vi.fn()
    }
  }
}))

import Login from '../Login.vue'
import { session } from '../../data/session'

describe('Login', () => {
  // Helper function to mount with stubs
  const mountLogin = (options = {}) => {
    return mount(Login, {
      global: {
        stubs: {
          'router-link': {
            name: 'RouterLink',
            props: ['to'],
            template: '<a :href="typeof to === \'string\' ? to : (to.name || \'/\')"><slot /></a>'
          }
        },
        ...(options.global || {})
      },
      ...options
    })
  }

  beforeEach(() => {
    // Reset mocks
    mockPush.mockClear()
    session.login.submit.mockClear()
    session.login.loading = false
    session.login.error = null
    session.isLoggedIn = false
  })

  // ========== Rendering Tests ==========

  it('renders logo icon', () => {
    const wrapper = mountLogin()
    const logo = wrapper.find('.bg-blue-600.rounded-2xl')
    expect(logo.exists()).toBe(true)
    expect(logo.find('svg').exists()).toBe(true)
  })

  it('renders header with correct text', () => {
    const wrapper = mountLogin()
    expect(wrapper.find('h1').text()).toBe('Welcome Back')
    expect(wrapper.text()).toContain('Sign in to your Lodgeick account')
  })

  it('renders email input field with correct attributes', () => {
    const wrapper = mountLogin()
    const emailInput = wrapper.find('input[name="email"]')
    expect(emailInput.exists()).toBe(true)
    expect(emailInput.attributes('id')).toBe('email')
    expect(emailInput.attributes('type')).toBe('text')
    expect(emailInput.attributes('required')).toBeDefined()
    expect(emailInput.attributes('placeholder')).toBe('Administrator or you@example.com')
  })

  it('renders email label', () => {
    const wrapper = mountLogin()
    const label = wrapper.find('label[for="email"]')
    expect(label.exists()).toBe(true)
    expect(label.text()).toBe('Email or Username')
  })

  it('renders password input field with correct attributes', () => {
    const wrapper = mountLogin()
    const passwordInput = wrapper.find('input[name="password"]')
    expect(passwordInput.exists()).toBe(true)
    expect(passwordInput.attributes('id')).toBe('password')
    expect(passwordInput.attributes('type')).toBe('password')
    expect(passwordInput.attributes('required')).toBeDefined()
    expect(passwordInput.attributes('placeholder')).toBe('Enter your password')
  })

  it('renders password label', () => {
    const wrapper = mountLogin()
    const label = wrapper.find('label[for="password"]')
    expect(label.exists()).toBe(true)
    expect(label.text()).toBe('Password')
  })

  it('renders forgot password link', () => {
    const wrapper = mountLogin()
    const forgotLink = wrapper.find('a[href="#"]')
    expect(forgotLink.exists()).toBe(true)
    expect(forgotLink.text()).toBe('Forgot password?')
  })

  it('renders remember me checkbox', () => {
    const wrapper = mountLogin()
    const checkbox = wrapper.find('input[type="checkbox"]#remember-me')
    expect(checkbox.exists()).toBe(true)
  })

  it('renders remember me label', () => {
    const wrapper = mountLogin()
    const label = wrapper.find('label[for="remember-me"]')
    expect(label.exists()).toBe(true)
    expect(label.text()).toBe('Remember me for 30 days')
  })

  it('renders submit button with correct text', () => {
    const wrapper = mountLogin()
    const button = wrapper.findComponent({ name: 'Button' })
    expect(button.exists()).toBe(true)
    expect(button.text()).toContain('Sign In')
  })

  it('renders divider with "or" text', () => {
    const wrapper = mountLogin()
    const divider = wrapper.find('.relative.flex.justify-center span')
    expect(divider.exists()).toBe(true)
    expect(divider.text()).toBe('or')
  })

  it('renders Google SSO button', () => {
    const wrapper = mountLogin()
    const googleBtn = wrapper.find('button[type="button"]')
    expect(googleBtn.exists()).toBe(true)
    expect(googleBtn.text()).toContain('Continue with Google')
    expect(googleBtn.find('svg').exists()).toBe(true)
  })

  it('renders register link', () => {
    const wrapper = mountLogin()
    const registerLink = wrapper.findComponent({ name: 'RouterLink' })
    expect(registerLink.exists()).toBe(true)
    expect(registerLink.text()).toBe('Create one now')
  })

  it('renders register link with correct text above it', () => {
    const wrapper = mountLogin()
    expect(wrapper.text()).toContain("Don't have an account?")
  })

  it('renders back to home link', () => {
    const wrapper = mountLogin()
    const links = wrapper.findAllComponents({ name: 'RouterLink' })
    const homeLink = links.find(link => link.text().includes('Back to home'))
    expect(homeLink).toBeTruthy()
    expect(homeLink.text()).toContain('Back to home')
  })

  // ========== Error Handling Tests ==========

  it('does not display error message when no error', () => {
    session.login.error = null
    const wrapper = mountLogin()
    const errorBox = wrapper.find('.bg-red-50')
    expect(errorBox.exists()).toBe(false)
  })

  it('displays error message when login error exists', () => {
    session.login.error = 'Invalid username or password'
    const wrapper = mountLogin()
    const errorBox = wrapper.find('.bg-red-50')
    expect(errorBox.exists()).toBe(true)
    expect(errorBox.text()).toContain('Invalid username or password')
  })

  it('displays error with correct styling and icon', () => {
    session.login.error = 'Authentication failed'
    const wrapper = mountLogin()
    const errorBox = wrapper.find('.bg-red-50.border.border-red-200')
    expect(errorBox.exists()).toBe(true)
    expect(errorBox.find('svg.text-red-600').exists()).toBe(true)
    expect(errorBox.find('.text-red-700').text()).toBe('Authentication failed')
  })

  // ========== Loading State Tests ==========

  it('shows "Sign In" text when not loading', () => {
    session.login.loading = false
    const wrapper = mountLogin()
    const button = wrapper.findComponent({ name: 'Button' })
    expect(button.props('loading')).toBe(false)
    expect(button.text()).toContain('Sign In')
  })

  it('shows "Signing in..." text when loading', () => {
    session.login.loading = true
    const wrapper = mountLogin()
    const button = wrapper.findComponent({ name: 'Button' })
    expect(button.props('loading')).toBe(true)
    expect(button.text()).toContain('Signing in...')
  })

  it('passes loading state to button component', () => {
    session.login.loading = true
    const wrapper = mountLogin()
    const button = wrapper.findComponent({ name: 'Button' })
    expect(button.props('loading')).toBe(true)
  })

  // ========== Form Submission Tests ==========

  it('calls session.login.submit when form is submitted', async () => {
    const wrapper = mountLogin()
    const form = wrapper.find('form')

    // Set input values
    const emailInput = wrapper.find('input[name="email"]')
    const passwordInput = wrapper.find('input[name="password"]')

    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('testpassword123')

    // Submit form
    await form.trigger('submit')

    expect(session.login.submit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'testpassword123'
    })
  })

  it('extracts form data correctly on submission', async () => {
    const wrapper = mountLogin()
    const form = wrapper.find('form')

    const emailInput = wrapper.find('input[name="email"]')
    const passwordInput = wrapper.find('input[name="password"]')

    await emailInput.setValue('admin')
    await passwordInput.setValue('admin123')

    await form.trigger('submit')

    expect(session.login.submit).toHaveBeenCalledTimes(1)
    const callArgs = session.login.submit.mock.calls[0][0]
    expect(callArgs.email).toBe('admin')
    expect(callArgs.password).toBe('admin123')
  })

  it('prevents default form submission', async () => {
    const wrapper = mountLogin()
    const form = wrapper.find('form')

    const submitEvent = new Event('submit', { cancelable: true })
    const preventDefaultSpy = vi.spyOn(submitEvent, 'preventDefault')

    form.element.dispatchEvent(submitEvent)

    expect(preventDefaultSpy).toHaveBeenCalled()
  })

  // ========== Navigation/Redirect Tests ==========

  // Note: Testing the watch-based redirect requires Vue reactivity which is complex to mock
  // The redirect logic is verified through E2E tests instead

  it('register link has correct "to" prop', () => {
    const wrapper = mountLogin()
    const registerLink = wrapper.findComponent({ name: 'RouterLink' })
    expect(registerLink.props('to')).toEqual({ name: 'Register' })
  })

  it('home link has correct "to" prop', () => {
    const wrapper = mountLogin()
    const links = wrapper.findAllComponents({ name: 'RouterLink' })
    const homeLink = links.find(link => link.props('to') === '/')
    expect(homeLink).toBeTruthy()
    expect(homeLink.props('to')).toBe('/')
  })

  // ========== Styling Tests ==========

  it('applies gradient background to main container', () => {
    const wrapper = mountLogin()
    const container = wrapper.find('.min-h-screen')
    expect(container.classes()).toContain('bg-gradient-to-br')
    expect(container.classes()).toContain('from-blue-50')
    expect(container.classes()).toContain('to-slate-100')
  })

  it('applies card styling to login form container', () => {
    const wrapper = mountLogin()
    const card = wrapper.find('.bg-white.rounded-2xl.shadow-xl')
    expect(card.exists()).toBe(true)
    expect(card.classes()).toContain('p-8')
    expect(card.classes()).toContain('border')
  })

  it('applies correct button styling classes', () => {
    const wrapper = mountLogin()
    const button = wrapper.findComponent({ name: 'Button' })
    expect(button.attributes('class')).toContain('w-full')
    expect(button.attributes('class')).toContain('bg-blue-600')
  })

  // ========== Complete Structure Test ==========

  it('renders complete login page structure', () => {
    const wrapper = mountLogin()

    // Check all major sections exist
    expect(wrapper.find('h1').exists()).toBe(true)
    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input[name="email"]').exists()).toBe(true)
    expect(wrapper.find('input[name="password"]').exists()).toBe(true)
    expect(wrapper.find('input[type="checkbox"]').exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'Button' }).exists()).toBe(true)
    expect(wrapper.find('button[type="button"]').exists()).toBe(true) // Google button
    expect(wrapper.findAllComponents({ name: 'RouterLink' }).length).toBeGreaterThanOrEqual(2)
  })
})
