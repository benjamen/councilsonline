import { mount } from "@vue/test-utils"
import { describe, expect, it } from "vitest"
import ProcessStep from "../ProcessStep.vue"

describe("ProcessStep", () => {
	it("renders step number correctly", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "1",
				title: "First Step",
				description: "This is the first step",
			},
		})

		const numberCircle = wrapper.find(".w-16.h-16")
		expect(numberCircle.text()).toBe("1")
	})

	it("renders title correctly", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "2",
				title: "Submit Application",
				description: "Submit your completed application",
			},
		})

		const title = wrapper.find("h4")
		expect(title.exists()).toBe(true)
		expect(title.text()).toBe("Submit Application")
	})

	it("renders description correctly", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "3",
				title: "Review Process",
				description: "We will review your application within 5 business days",
			},
		})

		const description = wrapper.find(".text-gray-600.text-sm")
		expect(description.exists()).toBe(true)
		expect(description.text()).toBe(
			"We will review your application within 5 business days",
		)
	})

	it("applies correct styling to step number circle", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "1",
				title: "Test Step",
				description: "Test description",
			},
		})

		const circle = wrapper.find(".w-16.h-16")
		expect(circle.classes()).toContain("bg-blue-600")
		expect(circle.classes()).toContain("text-white")
		expect(circle.classes()).toContain("rounded-full")
		expect(circle.classes()).toContain("shadow-lg")
	})

	it("shows connector line for non-last steps", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "1",
				title: "First Step",
				description: "Description",
			},
		})

		const connector = wrapper.find(".bg-blue-200")
		expect(connector.exists()).toBe(true)
	})

	it("hides connector line for last step (number 4)", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "4",
				title: "Final Step",
				description: "Last step description",
			},
		})

		const connector = wrapper.find(".bg-blue-200")
		expect(connector.exists()).toBe(false)
	})

	it("applies text-center to container", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "1",
				title: "Test",
				description: "Test",
			},
		})

		const container = wrapper.find(".text-center")
		expect(container.exists()).toBe(true)
	})

	it("renders with different step numbers", () => {
		const numbers = ["1", "2", "3", "4"]

		numbers.forEach((num) => {
			const wrapper = mount(ProcessStep, {
				props: {
					number: num,
					title: `Step ${num}`,
					description: `Description for step ${num}`,
				},
			})

			expect(wrapper.find(".w-16.h-16").text()).toBe(num)
		})
	})

	it("applies correct font styling to title", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "1",
				title: "Test Step",
				description: "Test description",
			},
		})

		const title = wrapper.find("h4")
		expect(title.classes()).toContain("text-xl")
		expect(title.classes()).toContain("font-semibold")
		expect(title.classes()).toContain("text-gray-900")
	})

	it("renders all elements in correct order", () => {
		const wrapper = mount(ProcessStep, {
			props: {
				number: "2",
				title: "Complete Section",
				description: "With full description",
			},
		})

		const container = wrapper.element
		const elements = Array.from(container.children)

		// First element should be the number circle
		expect(elements[0].classList.contains("w-16")).toBe(true)

		// Should have title h4
		expect(wrapper.find("h4").exists()).toBe(true)

		// Should have description paragraph
		expect(wrapper.find(".text-gray-600").exists()).toBe(true)
	})
})
