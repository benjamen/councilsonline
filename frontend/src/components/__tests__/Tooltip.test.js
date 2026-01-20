import { mount } from "@vue/test-utils"
import { describe, expect, it } from "vitest"
import Tooltip from "../Tooltip.vue"

describe("Tooltip", () => {
	it("renders help icon button by default", () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "Help text",
			},
		})

		const button = wrapper.find("button")
		expect(button.exists()).toBe(true)
		expect(button.classes()).toContain("cursor-help")
	})

	it("renders tooltip text when provided", () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "This is help text",
			},
		})

		// Initially hidden
		expect(wrapper.find(".bg-gray-900").exists()).toBe(false)
	})

	it("shows tooltip on mouseenter", async () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "Help text",
			},
		})

		const button = wrapper.find("button")
		await button.trigger("mouseenter")

		const tooltip = wrapper.find(".bg-gray-900")
		expect(tooltip.exists()).toBe(true)
		expect(tooltip.text()).toBe("Help text")
	})

	it("hides tooltip on mouseleave", async () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "Help text",
			},
		})

		const button = wrapper.find("button")
		await button.trigger("mouseenter")
		expect(wrapper.find(".bg-gray-900").exists()).toBe(true)

		await button.trigger("mouseleave")
		// Wait for Vue to update
		await wrapper.vm.$nextTick()
		expect(wrapper.find(".bg-gray-900").exists()).toBe(false)
	})

	it("renders custom slot content instead of text prop", async () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "Fallback text",
			},
			slots: {
				default: '<span class="custom-content">Custom help text</span>',
			},
		})

		const button = wrapper.find("button")
		await button.trigger("mouseenter")

		expect(wrapper.html()).toContain("Custom help text")
		expect(wrapper.html()).not.toContain("Fallback text")
	})

	it("renders custom trigger slot", () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "Help text",
			},
			slots: {
				trigger: '<div class="custom-trigger">?</div>',
			},
		})

		expect(wrapper.find(".custom-trigger").exists()).toBe(true)
		expect(wrapper.find(".custom-trigger").text()).toBe("?")
		expect(wrapper.find("button").exists()).toBe(false)
	})

	describe("top position (default)", () => {
		it("applies top positioning classes", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
					position: "top",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const tooltip = wrapper.find(".bg-gray-900")
			expect(tooltip.classes()).toContain("bottom-full")
			expect(tooltip.classes()).toContain("mb-2")
		})

		it("uses top position by default", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const tooltip = wrapper.find(".bg-gray-900")
			expect(tooltip.classes()).toContain("bottom-full")
		})

		it("displays bottom arrow for top position", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
					position: "top",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const arrow = wrapper.find(".tooltip-arrow")
			expect(arrow.classes()).toContain("tooltip-arrow-bottom")
		})
	})

	describe("bottom position", () => {
		it("applies bottom positioning classes", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
					position: "bottom",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const tooltip = wrapper.find(".bg-gray-900")
			expect(tooltip.classes()).toContain("top-full")
			expect(tooltip.classes()).toContain("mt-2")
		})

		it("displays top arrow for bottom position", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
					position: "bottom",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const arrow = wrapper.find(".tooltip-arrow")
			expect(arrow.classes()).toContain("tooltip-arrow-top")
		})
	})

	describe("left position", () => {
		it("applies left positioning classes", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
					position: "left",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const tooltip = wrapper.find(".bg-gray-900")
			expect(tooltip.classes()).toContain("right-full")
			expect(tooltip.classes()).toContain("mr-2")
		})

		it("displays right arrow for left position", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
					position: "left",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const arrow = wrapper.find(".tooltip-arrow")
			expect(arrow.classes()).toContain("tooltip-arrow-right")
		})
	})

	describe("right position", () => {
		it("applies right positioning classes", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
					position: "right",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const tooltip = wrapper.find(".bg-gray-900")
			expect(tooltip.classes()).toContain("left-full")
			expect(tooltip.classes()).toContain("ml-2")
		})

		it("displays left arrow for right position", async () => {
			const wrapper = mount(Tooltip, {
				props: {
					text: "Help text",
					position: "right",
				},
			})

			const button = wrapper.find("button")
			await button.trigger("mouseenter")

			const arrow = wrapper.find(".tooltip-arrow")
			expect(arrow.classes()).toContain("tooltip-arrow-left")
		})
	})

	it("applies correct styling to tooltip container", async () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "Help text",
			},
		})

		const button = wrapper.find("button")
		await button.trigger("mouseenter")

		const tooltip = wrapper.find(".bg-gray-900")
		expect(tooltip.classes()).toContain("absolute")
		expect(tooltip.classes()).toContain("z-50")
		expect(tooltip.classes()).toContain("rounded-lg")
		expect(tooltip.classes()).toContain("shadow-lg")
		expect(tooltip.classes()).toContain("text-white")
	})

	it("renders SVG help icon", () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "Help text",
			},
		})

		const svg = wrapper.find("svg")
		expect(svg.exists()).toBe(true)
		expect(svg.classes()).toContain("w-4")
		expect(svg.classes()).toContain("h-4")
	})

	it("applies hover styles to button", () => {
		const wrapper = mount(Tooltip, {
			props: {
				text: "Help text",
			},
		})

		const button = wrapper.find("button")
		expect(button.classes()).toContain("hover:text-blue-600")
		expect(button.classes()).toContain("hover:bg-blue-50")
	})
})
