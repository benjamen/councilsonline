import { mount } from "@vue/test-utils"
import { describe, expect, it } from "vitest"
import CheckboxField from "../CheckboxField.vue"
import FieldError from "../FieldError.vue"

describe("CheckboxField", () => {
	const mockField = {
		field_name: "terms_accepted",
		field_label: "I accept the terms and conditions",
		is_required: 1,
		description: "You must accept the terms to continue",
	}

	it("renders checkbox input with correct attributes", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
			},
		})

		const checkbox = wrapper.find('input[type="checkbox"]')
		expect(checkbox.exists()).toBe(true)
		expect(checkbox.attributes("id")).toBe("terms_accepted")
		expect(checkbox.attributes("name")).toBe("terms_accepted")
	})

	it("renders label with correct text", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
			},
		})

		const label = wrapper.find("label")
		expect(label.exists()).toBe(true)
		expect(label.text()).toContain("I accept the terms and conditions")
		expect(label.attributes("for")).toBe("terms_accepted")
	})

	it("shows required indicator when field is required", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: { ...mockField, is_required: 1 },
				modelValue: false,
			},
		})

		const requiredIndicator = wrapper.find(".text-red-500")
		expect(requiredIndicator.exists()).toBe(true)
		expect(requiredIndicator.text()).toBe("*")
	})

	it("does not show required indicator when field is not required", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: { ...mockField, is_required: 0 },
				modelValue: false,
			},
		})

		const requiredIndicator = wrapper.find(".text-red-500")
		expect(requiredIndicator.exists()).toBe(false)
	})

	it("renders FieldError component with correct props", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
				validationError: "You must accept the terms",
			},
		})

		const error = wrapper.findComponent(FieldError)
		expect(error.exists()).toBe(true)
		expect(error.props("error")).toBe("You must accept the terms")
		expect(error.props("description")).toBe(
			"You must accept the terms to continue",
		)
	})

	it("reflects checked state when modelValue is true", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: true,
			},
		})

		const checkbox = wrapper.find('input[type="checkbox"]')
		expect(checkbox.element.checked).toBe(true)
	})

	it("reflects unchecked state when modelValue is false", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
			},
		})

		const checkbox = wrapper.find('input[type="checkbox"]')
		expect(checkbox.element.checked).toBe(false)
	})

	it("emits update:modelValue with true when checkbox is checked", async () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
			},
		})

		const checkbox = wrapper.find('input[type="checkbox"]')
		await checkbox.setValue(true)

		expect(wrapper.emitted("update:modelValue")).toBeTruthy()
		expect(wrapper.emitted("update:modelValue")[0]).toEqual([true])
	})

	it("emits update:modelValue with false when checkbox is unchecked", async () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: true,
			},
		})

		const checkbox = wrapper.find('input[type="checkbox"]')
		await checkbox.setValue(false)

		expect(wrapper.emitted("update:modelValue")).toBeTruthy()
		expect(wrapper.emitted("update:modelValue")[0]).toEqual([false])
	})

	it("emits validate event on blur", async () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
			},
		})

		const checkbox = wrapper.find('input[type="checkbox"]')
		await checkbox.trigger("blur")

		expect(wrapper.emitted("validate")).toBeTruthy()
	})

	it("applies error styles when validationError is present", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
				validationError: "Required field",
			},
		})

		const container = wrapper.find(".border.rounded-lg")
		expect(container.classes()).toContain("border-red-500")
		expect(container.classes()).toContain("bg-red-50")
	})

	it("applies default styles when no validation error", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
				validationError: "",
			},
		})

		const container = wrapper.find(".border.rounded-lg")
		expect(container.classes()).toContain("border-gray-200")
		expect(container.classes()).not.toContain("border-red-500")
		expect(container.classes()).not.toContain("bg-red-50")
	})

	it("applies hover effect class", () => {
		const wrapper = mount(CheckboxField, {
			props: {
				field: mockField,
				modelValue: false,
			},
		})

		const container = wrapper.find(".border.rounded-lg")
		expect(container.classes()).toContain("hover:border-blue-300")
	})
})
