import { mount } from "@vue/test-utils"
import { beforeEach, describe, expect, it, vi } from "vitest"

// Mock vue-router
const mockPush = vi.fn()
vi.mock("vue-router", () => ({
	useRouter: () => ({ push: mockPush }),
}))

// Mock frappe-ui
vi.mock("frappe-ui", () => ({
	Button: {
		name: "Button",
		props: ["size", "variant", "theme"],
		template: '<button><slot name="prefix" /><slot /></button>',
	},
}))

import Landing from "../Landing.vue"

describe("Landing", () => {
	// Helper function to mount with stubs
	const mountLanding = (options = {}) => {
		return mount(Landing, {
			global: {
				stubs: {
					FeatureCard: {
						name: "FeatureCard",
						props: ["icon", "title", "description"],
						template:
							'<div class="feature-card"><h4>{{ title }}</h4><p>{{ description }}</p></div>',
					},
					ProcessStep: {
						name: "ProcessStep",
						props: ["number", "title", "description"],
						template:
							'<div class="process-step"><span>{{ number }}</span><h5>{{ title }}</h5><p>{{ description }}</p></div>',
					},
					Button: {
						name: "Button",
						props: ["size", "variant", "theme"],
						template: '<button><slot name="prefix" /><slot /></button>',
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
		const wrapper = mountLanding()
		const logo = wrapper.find(".w-10.h-10.bg-blue-600.rounded-lg")
		expect(logo.exists()).toBe(true)
		expect(logo.find("svg").exists()).toBe(true)
	})

	it("renders site title and tagline", () => {
		const wrapper = mountLanding()
		expect(wrapper.find("h1").text()).toBe("Councils Online")
		expect(wrapper.text()).toContain("Council Request Management")
	})

	it("renders navigation links", () => {
		const wrapper = mountLanding()
		const nav = wrapper.find("nav")
		expect(nav.exists()).toBe(true)
		expect(nav.text()).toContain("Features")
		expect(nav.text()).toContain("How it Works")
		expect(nav.text()).toContain("Contact")
	})

	it("renders header login button", () => {
		const wrapper = mountLanding()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const headerLoginBtn = buttons[0]
		expect(headerLoginBtn.text()).toContain("Log In")
	})

	// ========== Hero Section Tests ==========

	it("renders hero badge", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("Modern Council Request Management")
	})

	it('renders hero title with blue "Online" text', () => {
		const wrapper = mountLanding()
		const heroTitle = wrapper.find("h2")
		expect(heroTitle.exists()).toBe(true)
		expect(heroTitle.text()).toContain("Request Council Services")
		expect(heroTitle.text()).toContain("Online")
		expect(heroTitle.find(".text-blue-600").text()).toBe("Online")
	})

	it("renders hero description", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain(
			"comprehensive platform for ratepayers, civilians, and suppliers",
		)
		expect(wrapper.text()).toContain(
			"Submit consents, service requests, and applications online",
		)
	})

	it("renders Create Account CTA button", () => {
		const wrapper = mountLanding()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const createAccountBtn = buttons.find((btn) =>
			btn.text().includes("Create Account"),
		)
		expect(createAccountBtn).toBeTruthy()
	})

	it("renders Sign In CTA button", () => {
		const wrapper = mountLanding()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const signInBtn = buttons.find((btn) => btn.text().includes("Sign In"))
		expect(signInBtn).toBeTruthy()
	})

	it("renders trust indicators with stats", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("Trusted by councils across New Zealand")
		expect(wrapper.text()).toContain("20+")
		expect(wrapper.text()).toContain("Councils")
		expect(wrapper.text()).toContain("10k+")
		expect(wrapper.text()).toContain("Applications")
		expect(wrapper.text()).toContain("99.9%")
		expect(wrapper.text()).toContain("Uptime")
	})

	it("renders sample request cards in hero image", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("BC-2025-001 Approved")
		expect(wrapper.text()).toContain("Building Consent - New Dwelling")
		expect(wrapper.text()).toContain("RC-2025-042 Under Review")
		expect(wrapper.text()).toContain("15 days remaining")
		expect(wrapper.text()).toContain("RFI Required")
	})

	it("renders floating secure badge", () => {
		const wrapper = mountLanding()
		const badge = wrapper.find(".bg-green-500.text-white.rounded-full")
		expect(badge.exists()).toBe(true)
		expect(badge.text()).toContain("✓ Secure & Compliant")
	})

	// ========== Features Section Tests ==========

	it("renders features section heading", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("Everything You Need for Council Requests")
		expect(wrapper.text()).toContain("Streamline your council interactions")
	})

	it("renders 6 feature cards", () => {
		const wrapper = mountLanding()
		const featureCards = wrapper.findAllComponents({ name: "FeatureCard" })
		expect(featureCards.length).toBe(6)
	})

	it("renders Digital Requests feature card", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("Digital Requests")
		expect(wrapper.text()).toContain(
			"Submit consents, service requests, and applications online",
		)
	})

	it("renders all feature titles", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("Digital Requests")
		expect(wrapper.text()).toContain("Real-time Tracking")
		expect(wrapper.text()).toContain("Secure Payments")
		expect(wrapper.text()).toContain("Direct Communication")
		expect(wrapper.text()).toContain("Document Management")
		expect(wrapper.text()).toContain("Transparent Process")
	})

	// ========== How It Works Section Tests ==========

	it("renders how it works section heading", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("Simple Process, Powerful Results")
		expect(wrapper.text()).toContain(
			"Submit your council request in 4 easy steps",
		)
	})

	it("renders 4 process steps", () => {
		const wrapper = mountLanding()
		const processSteps = wrapper.findAllComponents({ name: "ProcessStep" })
		expect(processSteps.length).toBe(4)
	})

	it("renders all process step titles", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("Create Account")
		expect(wrapper.text()).toContain("Submit Request")
		expect(wrapper.text()).toContain("Track Progress")
		expect(wrapper.text()).toContain("Get Result")
	})

	// ========== CTA Section Tests ==========

	it("renders CTA section with heading", () => {
		const wrapper = mountLanding()
		expect(wrapper.text()).toContain("Ready to Get Started?")
		expect(wrapper.text()).toContain(
			"Join thousands of ratepayers and suppliers",
		)
	})

	it("renders CTA section buttons", () => {
		const wrapper = mountLanding()
		const ctaSection = wrapper.find(".bg-gradient-to-r.from-blue-600")
		expect(ctaSection.exists()).toBe(true)
		expect(ctaSection.text()).toContain("Create Free Account")
		expect(ctaSection.text()).toContain("Sign In to Existing Account")
	})

	// ========== Footer Tests ==========

	it("renders footer with company info", () => {
		const wrapper = mountLanding()
		const footer = wrapper.find("footer")
		expect(footer.exists()).toBe(true)
		expect(footer.text()).toContain("Councils Online")
		expect(footer.text()).toContain("Modern request management platform")
	})

	it("renders footer navigation sections", () => {
		const wrapper = mountLanding()
		const footer = wrapper.find("footer")
		expect(footer.text()).toContain("Product")
		expect(footer.text()).toContain("Support")
		expect(footer.text()).toContain("Contact")
	})

	it("renders footer contact information", () => {
		const wrapper = mountLanding()
		const footer = wrapper.find("footer")
		expect(footer.text()).toContain("support@councilsonline.com")
		expect(footer.text()).toContain("0800 COUNCILS")
		expect(footer.text()).toContain("Wellington, New Zealand")
	})

	it("renders footer copyright", () => {
		const wrapper = mountLanding()
		const footer = wrapper.find("footer")
		expect(footer.text()).toContain("© 2025 Councils Online")
		expect(footer.text()).toContain("Built with ❤️ in Aotearoa")
	})

	// ========== Navigation/Interaction Tests ==========

	it("calls goToLogin when header login button is clicked", async () => {
		const wrapper = mountLanding()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const headerLoginBtn = buttons[0]

		await headerLoginBtn.trigger("click")

		expect(mockPush).toHaveBeenCalledWith({ name: "Login" })
	})

	it("calls goToRegister when Create Account button is clicked", async () => {
		const wrapper = mountLanding()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const createAccountBtn = buttons.find((btn) =>
			btn.text().includes("Create Account"),
		)

		await createAccountBtn.trigger("click")

		expect(mockPush).toHaveBeenCalledWith({ name: "Register" })
	})

	it("calls goToLogin when Sign In button is clicked", async () => {
		const wrapper = mountLanding()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const signInBtn = buttons.find(
			(btn) =>
				btn.text().includes("Sign In") &&
				!btn.text().includes("Sign In to Existing"),
		)

		await signInBtn.trigger("click")

		expect(mockPush).toHaveBeenCalledWith({ name: "Login" })
	})

	it("calls goToRegister when CTA Create Free Account button is clicked", async () => {
		const wrapper = mountLanding()
		const ctaButtons = wrapper.findAll("button")
		const ctaCreateBtn = ctaButtons.find((btn) =>
			btn.text().includes("Create Free Account"),
		)

		await ctaCreateBtn.trigger("click")

		expect(mockPush).toHaveBeenCalledWith({ name: "Register" })
	})

	it("calls goToLogin when CTA Sign In button is clicked", async () => {
		const wrapper = mountLanding()
		const ctaButtons = wrapper.findAll("button")
		const ctaSignInBtn = ctaButtons.find((btn) =>
			btn.text().includes("Sign In to Existing Account"),
		)

		await ctaSignInBtn.trigger("click")

		expect(mockPush).toHaveBeenCalledWith({ name: "Login" })
	})

	// ========== Styling Tests ==========

	it("applies gradient background to main container", () => {
		const wrapper = mountLanding()
		const container = wrapper.find(".min-h-screen")
		expect(container.classes()).toContain("bg-gradient-to-br")
		expect(container.classes()).toContain("from-blue-50")
		expect(container.classes()).toContain("to-slate-100")
	})

	it("applies gradient to CTA section", () => {
		const wrapper = mountLanding()
		const ctaSection = wrapper.find(
			".bg-gradient-to-r.from-blue-600.to-blue-700",
		)
		expect(ctaSection.exists()).toBe(true)
	})

	it("applies correct footer styling", () => {
		const wrapper = mountLanding()
		const footer = wrapper.find("footer")
		expect(footer.classes()).toContain("bg-gray-900")
		expect(footer.classes()).toContain("text-gray-300")
	})

	// ========== Complete Structure Test ==========

	it("renders complete landing page structure", () => {
		const wrapper = mountLanding()

		// Check all major sections exist
		expect(wrapper.find("header").exists()).toBe(true)
		expect(wrapper.find("h2").exists()).toBe(true) // Hero title
		expect(wrapper.findAllComponents({ name: "FeatureCard" }).length).toBe(6)
		expect(wrapper.findAllComponents({ name: "ProcessStep" }).length).toBe(4)
		expect(wrapper.find("footer").exists()).toBe(true)
		expect(
			wrapper.findAllComponents({ name: "Button" }).length,
		).toBeGreaterThanOrEqual(3)
	})
})
