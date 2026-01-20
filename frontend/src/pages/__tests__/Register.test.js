import { mount } from "@vue/test-utils"
import { beforeEach, describe, expect, it, vi } from "vitest"

// Mock vue-router
const mockPush = vi.fn()
const mockRoute = { query: {} }
vi.mock("vue-router", () => ({
	useRouter: () => ({ push: mockPush }),
	useRoute: () => mockRoute,
	RouterLink: {
		name: "RouterLink",
		props: ["to"],
		template: "<a :href=\"typeof to === 'string' ? to : to.name\"><slot /></a>",
	},
}))

// Mock frappe-ui
vi.mock("frappe-ui", () => ({
	Button: {
		name: "Button",
		props: ["loading", "variant", "type"],
		template:
			'<button :type="type" :class="{ loading: loading }"><slot /></button>',
	},
	Input: {
		name: "Input",
		props: ["modelValue", "type", "placeholder"],
		template:
			'<input :type="type" :value="modelValue" :placeholder="placeholder" />',
	},
}))

// Mock validation utils
vi.mock("../../utils/validation", () => ({
	validateEmail: vi.fn(() => true),
	validateNZPhoneNumber: vi.fn(() => true),
	validatePassword: vi.fn(() => ({ valid: true, strength: "strong" })),
}))

import Register from "../Register.vue"

describe("Register", () => {
	// Helper function to mount with stubs
	const mountRegister = (options = {}) => {
		return mount(Register, {
			global: {
				stubs: {
					"router-link": {
						name: "RouterLink",
						props: ["to"],
						template:
							"<a :href=\"typeof to === 'string' ? to : (to.name || '/')\"><slot /></a>",
					},
					AccountTypeSelector: {
						name: "AccountTypeSelector",
						props: ["modelValue"],
						template: '<div class="account-type-selector"></div>',
					},
					PersonalInfoFields: {
						name: "PersonalInfoFields",
						props: [
							"firstName",
							"lastName",
							"email",
							"phone",
							"emailError",
							"phoneError",
						],
						template: '<div class="personal-info-fields"></div>',
					},
					PropertySection: {
						name: "PropertySection",
						props: ["requesterType", "properties"],
						template: '<div class="property-section"></div>',
					},
					AddPropertyModal: {
						name: "AddPropertyModal",
						props: [
							"show",
							"propertyName",
							"selectedPropertyAddress",
							"isDefault",
						],
						template: '<div v-if="show" class="add-property-modal"></div>',
					},
					EntityDetailsFields: {
						name: "EntityDetailsFields",
						props: [
							"requesterType",
							"organizationName",
							"companyNumber",
							"trustName",
						],
						template: '<div class="entity-details-fields"></div>',
					},
					PasswordFields: {
						name: "PasswordFields",
						props: [
							"password",
							"confirmPassword",
							"passwordError",
							"confirmPasswordError",
							"passwordStrength",
						],
						template: '<div class="password-fields"></div>',
					},
					TermsCheckbox: {
						name: "TermsCheckbox",
						props: ["modelValue"],
						template: '<div class="terms-checkbox"></div>',
					},
					AddressLookup: {
						name: "AddressLookup",
						template: '<div class="address-lookup"></div>',
					},
				},
				...(options.global || {}),
			},
			...options,
		})
	}

	beforeEach(() => {
		mockPush.mockClear()
	})

	// ========== Header Section Tests ==========

	it("renders logo icon", () => {
		const wrapper = mountRegister()
		const logo = wrapper.find(".w-16.h-16.bg-blue-600.rounded-2xl")
		expect(logo.exists()).toBe(true)
		expect(logo.find("svg").exists()).toBe(true)
	})

	it("renders header with correct text", () => {
		const wrapper = mountRegister()
		expect(wrapper.find("h1").text()).toBe("Create Your Account")
		expect(wrapper.text()).toContain(
			"Join thousands using CouncilsOnline for council requests",
		)
	})

	// ========== Account Type Selection Tests ==========

	it("renders account type selection section", () => {
		const wrapper = mountRegister()
		expect(wrapper.find("h2").text()).toBe("Choose Account Type")
	})

	it("renders requester option as selected by default", () => {
		const wrapper = mountRegister()
		expect(wrapper.text()).toContain("Register as Requester")
		expect(wrapper.text()).toContain(
			"Submit requests for yourself or on behalf of an organization",
		)
		expect(wrapper.text()).toContain("✓ Currently selected")
	})

	it("renders agent option with navigation button", () => {
		const wrapper = mountRegister()
		expect(wrapper.text()).toContain("Register as Agent")
		expect(wrapper.text()).toContain(
			"Consultants or representatives submitting on behalf of clients",
		)
		expect(wrapper.text()).toContain("Click to register as agent")
	})

	it("agent button is clickable and exists", () => {
		const wrapper = mountRegister()
		const agentButton = wrapper.find('button[type="button"]')

		// Verify button exists (navigation tested via E2E)
		expect(agentButton.exists()).toBe(true)
	})

	// ========== Form Structure Tests ==========

	it("renders registration form", () => {
		const wrapper = mountRegister()
		const form = wrapper.find("form")
		expect(form.exists()).toBe(true)
	})

	it("renders all form component sections", () => {
		const wrapper = mountRegister()
		expect(
			wrapper.findComponent({ name: "AccountTypeSelector" }).exists(),
		).toBe(true)
		expect(wrapper.findComponent({ name: "PersonalInfoFields" }).exists()).toBe(
			true,
		)
		expect(wrapper.findComponent({ name: "PropertySection" }).exists()).toBe(
			true,
		)
		expect(
			wrapper.findComponent({ name: "EntityDetailsFields" }).exists(),
		).toBe(true)
		expect(wrapper.findComponent({ name: "PasswordFields" }).exists()).toBe(
			true,
		)
		expect(wrapper.findComponent({ name: "TermsCheckbox" }).exists()).toBe(true)
	})

	// ========== Error Display Tests ==========

	it("does not display error message when no error", () => {
		const wrapper = mountRegister()
		const errorBox = wrapper.find(".bg-red-50")
		expect(errorBox.exists()).toBe(false)
	})

	it("displays error message when error exists", async () => {
		const wrapper = mountRegister()

		// Set error message via component data
		wrapper.vm.errorMessage = "Email is already registered"
		await wrapper.vm.$nextTick()

		const errorBox = wrapper.find(".bg-red-50")
		expect(errorBox.exists()).toBe(true)
		expect(errorBox.text()).toContain("Email is already registered")
	})

	it("displays error with correct icon", async () => {
		const wrapper = mountRegister()

		wrapper.vm.errorMessage = "Registration failed"
		await wrapper.vm.$nextTick()

		const errorBox = wrapper.find(".bg-red-50.border.border-red-200")
		expect(errorBox.exists()).toBe(true)
		expect(errorBox.find("svg.text-red-600").exists()).toBe(true)
	})

	// ========== Submit Button Tests ==========

	it("renders submit button with correct text", () => {
		const wrapper = mountRegister()
		const button = wrapper.findComponent({ name: "Button" })
		expect(button.exists()).toBe(true)
		expect(button.text()).toContain("Create Account")
	})

	it('shows "Creating account..." text when loading', async () => {
		const wrapper = mountRegister()

		wrapper.vm.isLoading = true
		await wrapper.vm.$nextTick()

		const button = wrapper.findComponent({ name: "Button" })
		expect(button.props("loading")).toBe(true)
		expect(button.text()).toContain("Creating account...")
	})

	it('shows "Create Account" text when not loading', () => {
		const wrapper = mountRegister()
		const button = wrapper.findComponent({ name: "Button" })
		expect(button.props("loading")).toBe(false)
		expect(button.text()).toContain("Create Account")
	})

	// ========== SSO Section Tests ==========

	it('renders divider with "or" text', () => {
		const wrapper = mountRegister()
		const divider = wrapper.find(".relative.flex.justify-center span")
		expect(divider.exists()).toBe(true)
		expect(divider.text()).toBe("or")
	})

	it("renders Google SSO button", () => {
		const wrapper = mountRegister()
		const buttons = wrapper.findAll("button")
		// First button is agent selection, second might be Google SSO
		const googleBtn = buttons.find((btn) =>
			btn.text().includes("Sign up with Google"),
		)
		expect(googleBtn).toBeTruthy()
		expect(googleBtn.find("svg").exists()).toBe(true)
	})

	// ========== Navigation Links Tests ==========

	it("renders sign in link", () => {
		const wrapper = mountRegister()
		expect(wrapper.text()).toContain("Already have an account?")
		const links = wrapper.findAllComponents({ name: "RouterLink" })
		const signInLink = links.find((link) => link.text().includes("Sign in"))
		expect(signInLink).toBeTruthy()
	})

	it('sign in link has correct "to" prop', () => {
		const wrapper = mountRegister()
		const links = wrapper.findAllComponents({ name: "RouterLink" })
		const signInLink = links.find((link) => link.text().includes("Sign in"))
		expect(signInLink.props("to")).toEqual({ name: "Login" })
	})

	it("renders back to home link", () => {
		const wrapper = mountRegister()
		const links = wrapper.findAllComponents({ name: "RouterLink" })
		const homeLink = links.find((link) => link.text().includes("Back to home"))
		expect(homeLink).toBeTruthy()
		expect(homeLink.text()).toContain("Back to home")
	})

	it('home link has correct "to" prop', () => {
		const wrapper = mountRegister()
		const links = wrapper.findAllComponents({ name: "RouterLink" })
		const homeLink = links.find((link) => link.props("to") === "/")
		expect(homeLink).toBeTruthy()
	})

	// ========== Styling Tests ==========

	it("applies gradient background to main container", () => {
		const wrapper = mountRegister()
		const container = wrapper.find(".min-h-screen")
		expect(container.classes()).toContain("bg-gradient-to-br")
		expect(container.classes()).toContain("from-blue-50")
		expect(container.classes()).toContain("to-slate-100")
	})

	it("applies card styling to account type selection", () => {
		const wrapper = mountRegister()
		const accountTypeCard = wrapper.findAll(
			".bg-white.rounded-2xl.shadow-xl",
		)[0]
		expect(accountTypeCard.exists()).toBe(true)
	})

	it("applies card styling to registration form container", () => {
		const wrapper = mountRegister()
		const formCard = wrapper.findAll(".bg-white.rounded-2xl.shadow-xl")[1]
		expect(formCard.exists()).toBe(true)
		expect(formCard.classes()).toContain("p-8")
		expect(formCard.classes()).toContain("border")
	})

	// ========== Complete Structure Test ==========

	it("renders complete registration page structure", () => {
		const wrapper = mountRegister()

		// Check all major sections exist
		expect(wrapper.find("h1").exists()).toBe(true)
		expect(wrapper.find("h2").exists()).toBe(true)
		expect(wrapper.find("form").exists()).toBe(true)
		expect(wrapper.findComponent({ name: "Button" }).exists()).toBe(true)
		expect(
			wrapper.findAllComponents({ name: "RouterLink" }).length,
		).toBeGreaterThanOrEqual(2)
		expect(
			wrapper.findComponent({ name: "AccountTypeSelector" }).exists(),
		).toBe(true)
		expect(wrapper.findComponent({ name: "PersonalInfoFields" }).exists()).toBe(
			true,
		)
		expect(wrapper.findComponent({ name: "PasswordFields" }).exists()).toBe(
			true,
		)
		expect(wrapper.findComponent({ name: "TermsCheckbox" }).exists()).toBe(true)
	})
})
