import { mount } from "@vue/test-utils"
import { describe, expect, it } from "vitest"
import FieldError from "../FieldError.vue"

describe("FieldError", () => {
	it("renders error message when error prop is provided", () => {
		const wrapper = mount(FieldError, {
			props: {
				error: "This field is required",
				description: "",
			},
		})

		expect(wrapper.text()).toContain("This field is required")
		const errorParagraph = wrapper.find(".text-red-600")
		expect(errorParagraph.exists()).toBe(true)
	})

	it("renders description when error is not provided", () => {
		const wrapper = mount(FieldError, {
			props: {
				error: "",
				description: "Enter your full name as it appears on your ID",
			},
		})

		expect(wrapper.text()).toContain(
			"Enter your full name as it appears on your ID",
		)
		const descriptionParagraph = wrapper.find(".text-gray-500")
		expect(descriptionParagraph.exists()).toBe(true)
	})

	it("prioritizes error over description when both are provided", () => {
		const wrapper = mount(FieldError, {
			props: {
				error: "Invalid email format",
				description: "Enter your email address",
			},
		})

		expect(wrapper.text()).toContain("Invalid email format")
		expect(wrapper.text()).not.toContain("Enter your email address")
	})

	it("renders nothing when neither error nor description is provided", () => {
		const wrapper = mount(FieldError, {
			props: {
				error: "",
				description: "",
			},
		})

		// Should render empty div with Vue comment for v-if
		expect(wrapper.text()).toBe("")
		expect(wrapper.find("p").exists()).toBe(false)
	})

	it("applies correct CSS classes to error message", () => {
		const wrapper = mount(FieldError, {
			props: {
				error: "Error message",
				description: "",
			},
		})

		const errorParagraph = wrapper.find("p")
		expect(errorParagraph.classes()).toContain("mt-1")
		expect(errorParagraph.classes()).toContain("text-xs")
		expect(errorParagraph.classes()).toContain("text-red-600")
	})

	it("applies correct CSS classes to description", () => {
		const wrapper = mount(FieldError, {
			props: {
				error: "",
				description: "Description text",
			},
		})

		const descriptionParagraph = wrapper.find("p")
		expect(descriptionParagraph.classes()).toContain("mt-1")
		expect(descriptionParagraph.classes()).toContain("text-xs")
		expect(descriptionParagraph.classes()).toContain("text-gray-500")
	})
})
