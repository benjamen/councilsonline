import { mount } from "@vue/test-utils"
import { beforeEach, describe, expect, it, vi } from "vitest"

// Mock frappe-ui components - inline to avoid hoisting issues
let mockPingFetch
let mockCreateResourceInstance

vi.mock("frappe-ui", () => ({
	Button: {
		name: "Button",
		props: ["theme", "variant", "iconLeft", "loading"],
		template: '<button :class="{ loading: loading }"><slot /></button>',
	},
	Dialog: {
		name: "Dialog",
		props: ["title", "modelValue"],
		template:
			'<div v-if="modelValue" class="dialog"><div class="dialog-title">{{ title }}</div><slot /></div>',
	},
	createResource: (options) => {
		mockPingFetch = vi.fn()
		mockCreateResourceInstance = {
			url: options.url,
			auto: options.auto,
			loading: false,
			data: null,
			fetch: mockPingFetch,
		}
		return mockCreateResourceInstance
	},
}))

// Mock session
vi.mock("../../data/session", () => ({
	session: {
		user: "test@example.com",
		logout: {
			submit: vi.fn(),
		},
	},
}))

import { session } from "../../data/session"
import Home from "../Home.vue"

describe("Home", () => {
	// Helper function to mount with stubs
	const mountHome = (options = {}) => {
		return mount(Home, {
			global: {
				stubs: {
					Button: {
						name: "Button",
						props: ["theme", "variant", "iconLeft", "loading"],
						template: '<button :class="{ loading: loading }"><slot /></button>',
					},
					Dialog: {
						name: "Dialog",
						props: ["title", "modelValue"],
						template: '<div v-if="modelValue" class="dialog"><slot /></div>',
					},
				},
				...(options.global || {}),
			},
			...options,
		})
	}

	beforeEach(() => {
		if (mockPingFetch) mockPingFetch.mockClear()
		session.logout.submit.mockClear()
	})

	// ========== Rendering Tests ==========

	it("renders welcome message with user email", () => {
		const wrapper = mountHome()
		const heading = wrapper.find("h2")
		expect(heading.exists()).toBe(true)
		expect(heading.text()).toContain("Welcome")
		expect(heading.text()).toContain("test@example.com")
	})

	it("displays session user in welcome message", () => {
		const wrapper = mountHome()
		expect(wrapper.text()).toContain("Welcome test@example.com!")
	})

	it("renders ping request button", () => {
		const wrapper = mountHome()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const pingButton = buttons.find((btn) => btn.text().includes("ping"))
		expect(pingButton).toBeTruthy()
		expect(pingButton.text()).toContain("Click to send 'ping' request")
	})

	it("renders logout button", () => {
		const wrapper = mountHome()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const logoutButton = buttons.find((btn) => btn.text() === "Logout")
		expect(logoutButton).toBeTruthy()
	})

	it("renders open dialog button", () => {
		const wrapper = mountHome()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const dialogButton = buttons.find((btn) => btn.text() === "Open Dialog")
		expect(dialogButton).toBeTruthy()
	})

	it("renders dialog component", () => {
		const wrapper = mountHome()
		const dialog = wrapper.findComponent({ name: "Dialog" })
		expect(dialog.exists()).toBe(true)
	})

	it("renders pre element for ping data display", () => {
		const wrapper = mountHome()
		const pre = wrapper.find("pre")
		expect(pre.exists()).toBe(true)
	})

	// ========== Button Functionality Tests ==========

	it("calls ping.fetch when ping button is clicked", async () => {
		const wrapper = mountHome()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const pingButton = buttons.find((btn) => btn.text().includes("ping"))

		await pingButton.trigger("click")

		expect(mockPingFetch).toHaveBeenCalled()
	})

	it("calls session.logout.submit when logout button is clicked", async () => {
		const wrapper = mountHome()
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const logoutButton = buttons.find((btn) => btn.text() === "Logout")

		await logoutButton.trigger("click")

		expect(session.logout.submit).toHaveBeenCalled()
	})

	it("shows dialog when open dialog button is clicked", async () => {
		const wrapper = mountHome()
		const dialog = wrapper.findComponent({ name: "Dialog" })
		const buttons = wrapper.findAllComponents({ name: "Button" })
		const dialogButton = buttons.find((btn) => btn.text() === "Open Dialog")

		// Dialog should be hidden initially
		expect(dialog.props("modelValue")).toBe(false)

		// Click button
		await dialogButton.trigger("click")
		await wrapper.vm.$nextTick()

		// Dialog should now be visible
		expect(wrapper.vm.showDialog).toBe(true)
	})

	// ========== Dialog Tests ==========

	it("dialog has correct title prop", () => {
		const wrapper = mountHome()
		const dialog = wrapper.findComponent({ name: "Dialog" })
		expect(dialog.props("title")).toBe("Title")
	})

	// Note: Dialog content is conditionally rendered via v-if, so we test the dialog component exists

	it("dialog is initially hidden", () => {
		const wrapper = mountHome()
		expect(wrapper.vm.showDialog).toBe(false)
	})

	// ========== Ping Resource Tests ==========

	it("initializes ping resource with correct url", () => {
		const wrapper = mountHome()
		expect(wrapper.vm.ping.url).toBe("ping")
	})

	it("initializes ping resource with auto:true", () => {
		const wrapper = mountHome()
		expect(wrapper.vm.ping.auto).toBe(true)
	})

	// ========== Styling Tests ==========

	it("applies correct container styling", () => {
		const wrapper = mountHome()
		const container = wrapper.find(".max-w-3xl")
		expect(container.exists()).toBe(true)
		expect(container.classes()).toContain("py-12")
		expect(container.classes()).toContain("mx-auto")
	})

	it("applies correct heading styling", () => {
		const wrapper = mountHome()
		const heading = wrapper.find("h2")
		expect(heading.classes()).toContain("font-bold")
		expect(heading.classes()).toContain("text-lg")
		expect(heading.classes()).toContain("text-gray-600")
	})

	it("applies correct button container styling", () => {
		const wrapper = mountHome()
		const buttonContainer = wrapper.find(".flex.flex-row")
		expect(buttonContainer.exists()).toBe(true)
		expect(buttonContainer.classes()).toContain("space-x-2")
		expect(buttonContainer.classes()).toContain("mt-4")
	})

	// ========== Complete Structure Test ==========

	it("renders complete home page structure", () => {
		const wrapper = mountHome()

		// Check all major elements exist
		expect(wrapper.find("h2").exists()).toBe(true)
		expect(
			wrapper.findAllComponents({ name: "Button" }).length,
		).toBeGreaterThanOrEqual(3)
		expect(wrapper.findComponent({ name: "Dialog" }).exists()).toBe(true)
		expect(wrapper.find("pre").exists()).toBe(true)
	})
})
