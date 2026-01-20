import { mount } from "@vue/test-utils"
import { describe, expect, it } from "vitest"
import InfoBox from "../InfoBox.vue"

describe("InfoBox", () => {
	it("renders title correctly", () => {
		const wrapper = mount(InfoBox, {
			props: {
				title: "Important Information",
			},
		})

		expect(wrapper.text()).toContain("Important Information")
		const title = wrapper.find("h5")
		expect(title.exists()).toBe(true)
		expect(title.text()).toBe("Important Information")
	})

	it("renders slot content", () => {
		const wrapper = mount(InfoBox, {
			props: {
				title: "Test Title",
			},
			slots: {
				default: "<p>This is the content of the info box</p>",
			},
		})

		expect(wrapper.html()).toContain("This is the content of the info box")
	})

	it("renders info icon", () => {
		const wrapper = mount(InfoBox, {
			props: {
				title: "Test Title",
			},
		})

		const icon = wrapper.find("svg")
		expect(icon.exists()).toBe(true)
		expect(icon.classes()).toContain("w-5")
		expect(icon.classes()).toContain("h-5")
	})

	describe("info variant (default)", () => {
		it("applies blue color classes for info variant", () => {
			const wrapper = mount(InfoBox, {
				props: {
					title: "Info Title",
					variant: "info",
				},
			})

			const container = wrapper.find(".border")
			expect(container.classes()).toContain("bg-blue-50")
			expect(container.classes()).toContain("border-blue-200")

			const title = wrapper.find("h5")
			expect(title.classes()).toContain("text-blue-900")

			const contentDiv = wrapper.find(".text-sm.mt-1")
			expect(contentDiv.classes()).toContain("text-blue-800")
		})

		it("uses info variant as default", () => {
			const wrapper = mount(InfoBox, {
				props: {
					title: "Default Variant",
				},
			})

			const container = wrapper.find(".border")
			expect(container.classes()).toContain("bg-blue-50")
		})
	})

	describe("warning variant", () => {
		it("applies yellow color classes for warning variant", () => {
			const wrapper = mount(InfoBox, {
				props: {
					title: "Warning Title",
					variant: "warning",
				},
			})

			const container = wrapper.find(".border")
			expect(container.classes()).toContain("bg-yellow-50")
			expect(container.classes()).toContain("border-yellow-200")

			const title = wrapper.find("h5")
			expect(title.classes()).toContain("text-yellow-900")

			const contentDiv = wrapper.find(".text-sm.mt-1")
			expect(contentDiv.classes()).toContain("text-yellow-800")
		})
	})

	describe("success variant", () => {
		it("applies green color classes for success variant", () => {
			const wrapper = mount(InfoBox, {
				props: {
					title: "Success Title",
					variant: "success",
				},
			})

			const container = wrapper.find(".border")
			expect(container.classes()).toContain("bg-green-50")
			expect(container.classes()).toContain("border-green-200")

			const title = wrapper.find("h5")
			expect(title.classes()).toContain("text-green-900")

			const contentDiv = wrapper.find(".text-sm.mt-1")
			expect(contentDiv.classes()).toContain("text-green-800")
		})
	})

	describe("error variant", () => {
		it("applies red color classes for error variant", () => {
			const wrapper = mount(InfoBox, {
				props: {
					title: "Error Title",
					variant: "error",
				},
			})

			const container = wrapper.find(".border")
			expect(container.classes()).toContain("bg-red-50")
			expect(container.classes()).toContain("border-red-200")

			const title = wrapper.find("h5")
			expect(title.classes()).toContain("text-red-900")

			const contentDiv = wrapper.find(".text-sm.mt-1")
			expect(contentDiv.classes()).toContain("text-red-800")
		})
	})

	it("applies correct layout classes", () => {
		const wrapper = mount(InfoBox, {
			props: {
				title: "Test",
			},
		})

		const container = wrapper.find(".border")
		expect(container.classes()).toContain("rounded-lg")
		expect(container.classes()).toContain("p-4")

		const flexContainer = wrapper.find(".flex.items-start")
		expect(flexContainer.exists()).toBe(true)
	})

	it("handles complex slot content", () => {
		const wrapper = mount(InfoBox, {
			props: {
				title: "Complex Content",
				variant: "info",
			},
			slots: {
				default: `
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
          </ul>
        `,
			},
		})

		expect(wrapper.html()).toContain("<ul>")
		expect(wrapper.html()).toContain("Item 1")
		expect(wrapper.html()).toContain("Item 2")
		expect(wrapper.html()).toContain("Item 3")
	})
})
