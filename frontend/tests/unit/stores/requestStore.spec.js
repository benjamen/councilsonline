import { createPinia, setActivePinia } from "pinia"
import { beforeEach, describe, expect, it, vi } from "vitest"

// Mock frappe-ui to avoid icon imports
vi.mock("frappe-ui", () => ({
	createResource: vi.fn(),
}))

// Mock services to avoid import issues
vi.mock("../../../src/services", () => {
	return {
		apiClient: {
			call: vi.fn(),
			createResource: vi.fn(),
		},
		requestService: {
			createDraft: vi.fn(),
			submitRequest: vi.fn(),
			getRequest: vi.fn(),
			getRequestTypeConfig: vi.fn(),
		},
	}
})

import { requestService } from "../../../src/services"
import { useRequestStore } from "../../../src/stores/requestStore"

describe("RequestStore", () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		vi.clearAllMocks()
	})

	describe("initialization", () => {
		it("should initialize with empty state", () => {
			const store = useRequestStore()

			expect(store.currentRequestId).toBeNull()
			expect(store.formData).toEqual({})
			expect(store.currentStep).toBe(0)
			expect(store.isSaving).toBe(false)
			expect(store.isSubmitting).toBe(false)
		})
	})

	describe("getters", () => {
		it("should identify first step correctly", () => {
			const store = useRequestStore()
			store.currentStep = 0

			expect(store.isFirstStep).toBe(true)

			store.currentStep = 1
			expect(store.isFirstStep).toBe(false)
		})

		it("should identify last step correctly", () => {
			const store = useRequestStore()
			// With 3 dynamic steps: totalSteps = 3 + 3 static = 6 (indices 0-5)
			// Last step is index 5
			store.requestTypeConfig = { steps: [{}, {}, {}] }
			store.currentStep = 5

			expect(store.isLastStep).toBe(true)

			store.currentStep = 1
			expect(store.isLastStep).toBe(false)
		})

		it("should calculate completion percentage", () => {
			const store = useRequestStore()
			// With 4 dynamic steps: totalSteps = 4 + 3 static = 7
			store.requestTypeConfig = { steps: [{}, {}, {}, {}] }

			store.currentStep = 0
			// Step 1/7 = 14.3% (rounds to 14)
			expect(store.completionPercentage).toBe(14)

			store.currentStep = 2
			// Step 3/7 = 42.9% (rounds to 43)
			expect(store.completionPercentage).toBe(43)

			store.currentStep = 6
			// Step 7/7 = 100%
			expect(store.completionPercentage).toBe(100)
		})
	})

	describe("navigation", () => {
		it("should navigate to next step", () => {
			const store = useRequestStore()
			store.requestTypeConfig = { steps: [{}, {}, {}] }
			store.currentStep = 0

			store.nextStep()

			expect(store.currentStep).toBe(1)
		})

		it("should not navigate past last step", () => {
			const store = useRequestStore()
			// With 2 dynamic steps: totalSteps = 2 + 3 = 5, last index is 4
			store.requestTypeConfig = { steps: [{}, {}] }
			store.currentStep = 4

			store.nextStep()

			// Should not increment past last step
			expect(store.currentStep).toBe(4)
		})

		it("should navigate to previous step", () => {
			const store = useRequestStore()
			store.currentStep = 2

			store.previousStep()

			expect(store.currentStep).toBe(1)
		})

		it("should not navigate before first step", () => {
			const store = useRequestStore()
			store.currentStep = 0

			store.previousStep()

			expect(store.currentStep).toBe(0)
		})

		it("should jump to specific step", () => {
			const store = useRequestStore()
			store.requestTypeConfig = { steps: [{}, {}, {}, {}] }

			store.goToStep(2)

			expect(store.currentStep).toBe(2)
		})

		it("should not jump to invalid step", () => {
			const store = useRequestStore()
			// With 2 dynamic steps: totalSteps = 2 + 3 = 5 (indices 0-4)
			store.requestTypeConfig = { steps: [{}, {}] }
			store.currentStep = 0

			// Try to jump to step 10 (invalid - beyond totalSteps)
			store.goToStep(10)

			// Should remain at current step
			expect(store.currentStep).toBe(0)
		})
	})

	describe("saveProgress", () => {
		it("should save progress and update request ID", async () => {
			const store = useRequestStore()
			const mockResponse = { request_id: "REQ-001" }
			requestService.createDraft.mockResolvedValue(mockResponse)

			store.formData = { applicant_name: "John Doe" }
			store.currentStep = 1

			await store.saveProgress()

			// First save sends data without request_id (it comes from response)
			expect(requestService.createDraft).toHaveBeenCalledWith(
				{ applicant_name: "John Doe" },
				1,
			)
			// After save, request_id is added to state from response
			expect(store.currentRequestId).toBe("REQ-001")
			expect(store.formData.request_id).toBe("REQ-001")
			expect(store.lastSaved).toBeInstanceOf(Date)
			expect(store.isSaving).toBe(false)
		})

		it("should set isSaving flag during save", async () => {
			const store = useRequestStore()
			store.formData = { applicant_name: "Test User" }
			requestService.createDraft.mockImplementation(
				() =>
					new Promise((resolve) =>
						setTimeout(() => resolve({ request_id: "REQ-001" }), 100),
					),
			)

			const savePromise = store.saveProgress()

			expect(store.isSaving).toBe(true)

			await savePromise

			expect(store.isSaving).toBe(false)
		})

		it("should handle save errors gracefully", async () => {
			const store = useRequestStore()
			store.formData = { applicant_name: "Test User" }
			const consoleError = vi
				.spyOn(console, "error")
				.mockImplementation(() => {})
			requestService.createDraft.mockRejectedValue(new Error("Save failed"))

			await expect(store.saveProgress()).rejects.toThrow("Save failed")

			expect(consoleError).toHaveBeenCalled()
			expect(store.isSaving).toBe(false)

			consoleError.mockRestore()
		})
	})

	describe("submitRequest", () => {
		it("should submit request and reset state", async () => {
			const store = useRequestStore()
			store.currentRequestId = "REQ-001"
			requestService.submitRequest.mockResolvedValue({})

			await store.submitRequest()

			expect(requestService.submitRequest).toHaveBeenCalledWith("REQ-001")
			expect(store.currentRequestId).toBeNull()
			expect(store.formData).toEqual({})
			expect(store.currentStep).toBe(0)
			expect(store.isSubmitting).toBe(false)
		})

		it("should set isSubmitting flag during submit", async () => {
			const store = useRequestStore()
			store.currentRequestId = "REQ-001"
			requestService.submitRequest.mockImplementation(
				() => new Promise((resolve) => setTimeout(resolve, 100)),
			)

			const submitPromise = store.submitRequest()

			expect(store.isSubmitting).toBe(true)

			await submitPromise

			expect(store.isSubmitting).toBe(false)
		})

		it("should handle submit errors", async () => {
			const store = useRequestStore()
			store.currentRequestId = "REQ-001"
			const consoleError = vi
				.spyOn(console, "error")
				.mockImplementation(() => {})
			requestService.submitRequest.mockRejectedValue(new Error("Submit failed"))

			await expect(store.submitRequest()).rejects.toThrow("Submit failed")

			expect(store.isSubmitting).toBe(false)

			consoleError.mockRestore()
		})
	})

	describe("updateField", () => {
		it("should update single field", () => {
			const store = useRequestStore()

			store.updateField("applicant_name", "Jane Doe")

			expect(store.formData.applicant_name).toBe("Jane Doe")
		})

		it("should update multiple fields", () => {
			const store = useRequestStore()

			store.updateField("field1", "value1")
			store.updateField("field2", "value2")

			expect(store.formData.field1).toBe("value1")
			expect(store.formData.field2).toBe("value2")
		})
	})

	describe("setStepValidation", () => {
		it("should track step validation status", () => {
			const store = useRequestStore()

			store.setStepValidation(0, true)
			store.setStepValidation(1, false)

			expect(store.stepValidationStatus[0]).toBe(true)
			expect(store.stepValidationStatus[1]).toBe(false)
		})
	})

	describe("reset", () => {
		it("should reset all state to initial values", () => {
			const store = useRequestStore()

			// Set some state
			store.currentRequestId = "REQ-001"
			store.formData = { test: "data" }
			store.currentStep = 3
			store.isSaving = true
			store.lastSaved = new Date()

			store.reset()

			expect(store.currentRequestId).toBeNull()
			expect(store.formData).toEqual({})
			expect(store.currentStep).toBe(0)
			expect(store.isSaving).toBe(false)
			expect(store.lastSaved).toBeNull()
		})
	})
})
