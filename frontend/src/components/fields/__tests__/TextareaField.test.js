import { mount } from "@vue/test-utils"
import { describe, expect, it } from "vitest"
import FieldError from "../FieldError.vue"
import FieldLabel from "../FieldLabel.vue"
import TextareaField from "../TextareaField.vue"

describe("TextareaField", () => {
	const mockField = {
		field_name: "description",
		field_label: "Project Description",
		is_required: 1,
		description: "Provide a detailed description of your project",
	}

	it("renders textarea with correct attributes", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "",
				placeholder: "Enter description...",
			},
		})

		const textarea = wrapper.find("textarea")
		expect(textarea.exists()).toBe(true)
		expect(textarea.attributes("id")).toBe("description")
		expect(textarea.attributes("name")).toBe("description")
		expect(textarea.attributes("placeholder")).toBe("Enter description...")
		expect(textarea.attributes("rows")).toBe("4")
	})

	it("renders FieldLabel component with correct props", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "",
			},
		})

		const label = wrapper.findComponent(FieldLabel)
		expect(label.exists()).toBe(true)
		expect(label.props("fieldName")).toBe("description")
		expect(label.props("label")).toBe("Project Description")
		expect(label.props("required")).toBe(true)
	})

	it("renders FieldError component with correct props", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "",
				validationError: "This field is required",
			},
		})

		const error = wrapper.findComponent(FieldError)
		expect(error.exists()).toBe(true)
		expect(error.props("error")).toBe("This field is required")
		expect(error.props("description")).toBe(
			"Provide a detailed description of your project",
		)
	})

	it("displays current value in textarea", () => {
		const testValue =
			"This is a detailed project description\nwith multiple lines of text."
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: testValue,
			},
		})

		const textarea = wrapper.find("textarea")
		expect(textarea.element.value).toBe(testValue)
	})

	it("emits update:modelValue when content changes", async () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "",
			},
		})

		const textarea = wrapper.find("textarea")
		const newValue = "New multi-line\ntext content"
		await textarea.setValue(newValue)

		expect(wrapper.emitted("update:modelValue")).toBeTruthy()
		expect(wrapper.emitted("update:modelValue")[0]).toEqual([newValue])
	})

	it("emits validate event on blur", async () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "Some text",
			},
		})

		const textarea = wrapper.find("textarea")
		await textarea.trigger("blur")

		expect(wrapper.emitted("validate")).toBeTruthy()
	})

	it("applies error styles when validationError is present", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "",
				validationError: "Invalid input",
			},
		})

		const textarea = wrapper.find("textarea")
		expect(textarea.classes()).toContain("border-red-500")
		expect(textarea.classes()).toContain("ring-red-100")
	})

	it("applies success styles when value is present and no error", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "Valid description text",
				validationError: "",
			},
		})

		const textarea = wrapper.find("textarea")
		expect(textarea.classes()).toContain("border-blue-500")
		expect(textarea.classes()).toContain("ring-blue-100")
	})

	it("includes resize-y class for vertical resizing", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "",
			},
		})

		const textarea = wrapper.find("textarea")
		expect(textarea.classes()).toContain("resize-y")
	})

	it("marks textarea as required when field.is_required is truthy", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: { ...mockField, is_required: 1 },
				modelValue: "",
			},
		})

		const textarea = wrapper.find("textarea")
		expect(textarea.attributes("required")).toBeDefined()
	})

	it("handles empty value correctly", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "",
			},
		})

		const textarea = wrapper.find("textarea")
		expect(textarea.element.value).toBe("")
		// Should not have success styling when empty
		expect(textarea.classes()).not.toContain("border-blue-500")
	})

	it("applies base styling classes", () => {
		const wrapper = mount(TextareaField, {
			props: {
				field: mockField,
				modelValue: "",
			},
		})

		const textarea = wrapper.find("textarea")
		expect(textarea.classes()).toContain("block")
		expect(textarea.classes()).toContain("w-full")
		expect(textarea.classes()).toContain("rounded-lg")
		expect(textarea.classes()).toContain("focus:ring-2")
		expect(textarea.classes()).toContain("focus:ring-blue-500")
	})
})
