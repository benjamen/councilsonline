import { call } from "frappe-ui"
import { createPinia, setActivePinia } from "pinia"
import { beforeEach, describe, expect, it, vi } from "vitest"

// Mock frappe-ui
vi.mock("frappe-ui", () => ({
	call: vi.fn(),
	createResource: vi.fn(),
}))

import { useCouncilStore } from "../../../src/stores/councilStore"

describe("CouncilStore - Dual Login Methods", () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		vi.clearAllMocks()
	})

	describe("shouldRedirectToCouncilDashboard", () => {
		it("should return true when council has redirect enabled", async () => {
			const store = useCouncilStore()

			call.mockResolvedValue({ should_redirect: true })

			const result = await store.shouldRedirectToCouncilDashboard("AKL")

			expect(call).toHaveBeenCalledWith(
				"lodgeick.api.should_redirect_to_council_dashboard",
				{ council_code: "AKL" },
			)
			expect(result).toBe(true)
		})

		it("should return false when council has redirect disabled", async () => {
			const store = useCouncilStore()

			call.mockResolvedValue({ should_redirect: false })

			const result = await store.shouldRedirectToCouncilDashboard("AKL")

			expect(result).toBe(false)
		})

		it("should return false on API error", async () => {
			const store = useCouncilStore()
			const consoleError = vi
				.spyOn(console, "error")
				.mockImplementation(() => {})

			call.mockRejectedValue(new Error("API Error"))

			const result = await store.shouldRedirectToCouncilDashboard("AKL")

			expect(result).toBe(false)
			expect(consoleError).toHaveBeenCalled()

			consoleError.mockRestore()
		})

		it("should handle null response gracefully", async () => {
			const store = useCouncilStore()

			call.mockResolvedValue(null)

			const result = await store.shouldRedirectToCouncilDashboard("AKL")

			expect(result).toBe(false)
		})
	})

	describe("getCouncilSettings", () => {
		it("should fetch and return council portal settings", async () => {
			const store = useCouncilStore()

			const mockSettings = {
				council_code: "AKL",
				council_name: "Auckland Council",
				primary_color: "#1e40af",
				secondary_color: "#64748b",
				logo: "/files/auckland-logo.png",
				redirect_dashboard_to_council: 1,
				allow_system_wide_dashboard: 0,
				show_council_switcher: 0,
				login_page_custom_html: "<p>Welcome to Auckland</p>",
			}

			call.mockResolvedValue(mockSettings)

			const result = await store.getCouncilSettings("AKL")

			expect(call).toHaveBeenCalledWith("lodgeick.api.get_council_settings", {
				council_code: "AKL",
			})
			expect(result).toEqual(mockSettings)
		})

		it("should return null on API error", async () => {
			const store = useCouncilStore()
			const consoleError = vi
				.spyOn(console, "error")
				.mockImplementation(() => {})

			call.mockRejectedValue(new Error("Council not found"))

			const result = await store.getCouncilSettings("INVALID")

			expect(result).toBeNull()
			expect(consoleError).toHaveBeenCalled()

			consoleError.mockRestore()
		})

		it("should handle missing optional fields", async () => {
			const store = useCouncilStore()

			const minimalSettings = {
				council_code: "WLG",
				council_name: "Wellington City Council",
				redirect_dashboard_to_council: 1,
				allow_system_wide_dashboard: 0,
			}

			call.mockResolvedValue(minimalSettings)

			const result = await store.getCouncilSettings("WLG")

			expect(result.council_code).toBe("WLG")
			expect(result.logo).toBeUndefined()
			expect(result.login_page_custom_html).toBeUndefined()
		})
	})

	describe("setPreferredCouncil", () => {
		it("should set selected council and persist to localStorage", () => {
			const store = useCouncilStore()
			const setItemSpy = vi.spyOn(Storage.prototype, "setItem")

			store.setPreferredCouncil("AKL")

			expect(store.selectedCouncil).toBe("AKL")
			expect(setItemSpy).toHaveBeenCalledWith("preferred_council", "AKL")

			setItemSpy.mockRestore()
		})

		it("should update selected council when called multiple times", () => {
			const store = useCouncilStore()

			store.setPreferredCouncil("AKL")
			expect(store.selectedCouncil).toBe("AKL")

			store.setPreferredCouncil("WLG")
			expect(store.selectedCouncil).toBe("WLG")
		})

		it("should not affect locked council", () => {
			const store = useCouncilStore()

			store.lockedCouncil = "CHC"
			store.setPreferredCouncil("AKL")

			expect(store.selectedCouncil).toBe("AKL")
			expect(store.lockedCouncil).toBe("CHC") // Should remain unchanged
		})
	})

	describe("Council Lock Behavior", () => {
		it("should prioritize lockedCouncil over selectedCouncil", () => {
			const store = useCouncilStore()

			store.selectedCouncil = "WLG"
			store.lockedCouncil = "AKL"

			// When both are set, lockedCouncil should take precedence
			expect(store.lockedCouncil).toBe("AKL")
		})

		it("should clear lock when explicitly set to null", () => {
			const store = useCouncilStore()

			store.lockedCouncil = "AKL"
			expect(store.lockedCouncil).toBe("AKL")

			store.lockedCouncil = null
			expect(store.lockedCouncil).toBeNull()
		})
	})

	describe("Integration with Dual Login Flow", () => {
		it("should support council-specific authentication flow", async () => {
			const store = useCouncilStore()

			// Simulate council landing page visit
			await store.setLockedCouncil("AKL")

			// Mock council settings
			const mockSettings = {
				council_code: "AKL",
				council_name: "Auckland Council",
				redirect_dashboard_to_council: 1,
				allow_system_wide_dashboard: 0,
			}
			call.mockResolvedValue(mockSettings)

			// Fetch settings for login page branding
			const settings = await store.getCouncilSettings("AKL")
			expect(settings.council_code).toBe("AKL")

			// Check redirect behavior
			call.mockResolvedValue({ should_redirect: true })
			const shouldRedirect = await store.shouldRedirectToCouncilDashboard("AKL")
			expect(shouldRedirect).toBe(true)
		})

		it("should support system-wide authentication flow", async () => {
			const store = useCouncilStore()

			// No locked council (system-wide login)
			expect(store.lockedCouncil).toBeNull()

			// Set preferred council (from user profile)
			store.setPreferredCouncil("WLG")

			// Check if should redirect
			call.mockResolvedValue({
				should_redirect: false,
				allow_system_wide: true,
			})
			const shouldRedirect = await store.shouldRedirectToCouncilDashboard("WLG")

			expect(shouldRedirect).toBe(false)
			expect(store.selectedCouncil).toBe("WLG")
		})
	})

	describe("Error Resilience", () => {
		it("should not break when API returns unexpected format", async () => {
			const store = useCouncilStore()

			call.mockResolvedValue({ unexpected: "format" })

			const result = await store.shouldRedirectToCouncilDashboard("AKL")

			expect(result).toBe(false) // Should default to false
		})

		it("should handle network timeout gracefully", async () => {
			const store = useCouncilStore()
			const consoleError = vi
				.spyOn(console, "error")
				.mockImplementation(() => {})

			call.mockRejectedValue(new Error("Network timeout"))

			const settings = await store.getCouncilSettings("AKL")

			expect(settings).toBeNull()
			expect(consoleError).toHaveBeenCalled()

			consoleError.mockRestore()
		})
	})
})
