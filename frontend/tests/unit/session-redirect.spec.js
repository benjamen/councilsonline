import { createPinia, setActivePinia } from "pinia"
import { beforeEach, describe, expect, it, vi } from "vitest"

// Mock router
const mockRouterReplace = vi.fn()
vi.mock("@/router", () => ({
	default: {
		replace: mockRouterReplace,
	},
}))

// Mock frappe-ui
vi.mock("frappe-ui", () => ({
	createResource: vi.fn((config) => {
		return {
			...config,
			submit: vi.fn(),
			reset: vi.fn(),
			loading: false,
			error: null,
		}
	}),
}))

// Mock userResource
vi.mock("@/data/user", () => ({
	userResource: {
		reload: vi.fn(),
		promise: Promise.resolve(),
		data: { name: "test@example.com" },
	},
}))

describe("Session Login Redirect Logic", () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		vi.clearAllMocks()
	})

	describe("Council-Specific Login Redirect", () => {
		it("should redirect to council dashboard when logged in via council page", async () => {
			// Import after mocks are set up
			const { session } = await import("../../../src/data/session")
			const { useCouncilStore } = await import(
				"../../../src/stores/councilStore"
			)

			const councilStore = useCouncilStore()
			councilStore.lockedCouncil = "AKL"

			// Simulate login success
			await session.login.onSuccess()

			// Should redirect to council dashboard
			expect(mockRouterReplace).toHaveBeenCalledWith({
				name: "CouncilDashboard",
				params: { councilCode: "AKL" },
			})
		})

		it("should maintain council lock during login", async () => {
			const { useCouncilStore } = await import(
				"../../../src/stores/councilStore"
			)

			const councilStore = useCouncilStore()

			// Set council lock (simulating route guard)
			councilStore.lockedCouncil = "WLG"

			// Lock should persist
			expect(councilStore.lockedCouncil).toBe("WLG")
		})
	})

	describe("System-Wide Login Redirect", () => {
		it("should redirect to dashboard when no council is locked", async () => {
			const { session } = await import("../../../src/data/session")
			const { useCouncilStore } = await import(
				"../../../src/stores/councilStore"
			)

			const councilStore = useCouncilStore()
			councilStore.lockedCouncil = null

			// Simulate login success
			await session.login.onSuccess()

			// Should redirect to system-wide dashboard
			expect(mockRouterReplace).toHaveBeenCalledWith({
				name: "Dashboard",
			})
		})
	})

	describe("Session State Management", () => {
		it("should update session user after successful login", async () => {
			const { session } = await import("../../../src/data/session")

			// Mock sessionUser function
			vi.mock("../../../src/data/session", async () => {
				const actual = await vi.importActual("../../../src/data/session")
				return {
					...actual,
					sessionUser: () => "test@example.com",
				}
			})

			await session.login.onSuccess()

			// Session user should be updated
			expect(session.user).toBeDefined()
		})

		it("should reload user resource after login", async () => {
			const { session } = await import("../../../src/data/session")
			const { userResource } = await import("../../../src/data/user")

			await session.login.onSuccess()

			// User resource should be reloaded
			expect(userResource.reload).toHaveBeenCalled()
		})

		it("should reset login form after success", async () => {
			const { session } = await import("../../../src/data/session")

			const resetSpy = vi.spyOn(session.login, "reset")

			await session.login.onSuccess()

			// Login form should be reset
			expect(resetSpy).toHaveBeenCalled()
		})
	})

	describe("Logout Behavior", () => {
		it("should redirect to login page after logout", async () => {
			const { session } = await import("../../../src/data/session")

			await session.logout.onSuccess()

			// Should redirect to system-wide login
			expect(mockRouterReplace).toHaveBeenCalledWith({
				name: "Login",
			})
		})

		it("should reset user resource after logout", async () => {
			const { session } = await import("../../../src/data/session")
			const { userResource } = await import("../../../src/data/user")

			const resetSpy = vi.spyOn(userResource, "reset")

			await session.logout.onSuccess()

			// User resource should be reset
			expect(resetSpy).toHaveBeenCalled()
		})
	})

	describe("Council Lock Edge Cases", () => {
		it("should handle empty council code", async () => {
			const { session } = await import("../../../src/data/session")
			const { useCouncilStore } = await import(
				"../../../src/stores/councilStore"
			)

			const councilStore = useCouncilStore()
			councilStore.lockedCouncil = ""

			await session.login.onSuccess()

			// Should treat empty string as no lock -> redirect to Dashboard
			expect(mockRouterReplace).toHaveBeenCalledWith({
				name: "Dashboard",
			})
		})

		it("should handle undefined council code", async () => {
			const { session } = await import("../../../src/data/session")
			const { useCouncilStore } = await import(
				"../../../src/stores/councilStore"
			)

			const councilStore = useCouncilStore()
			councilStore.lockedCouncil = undefined

			await session.login.onSuccess()

			// Should redirect to system-wide dashboard
			expect(mockRouterReplace).toHaveBeenCalledWith({
				name: "Dashboard",
			})
		})
	})
})

describe("Session Integration with CouncilStore", () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		vi.clearAllMocks()
	})

	it("should use councilStore during login flow", async () => {
		const { session } = await import("../../../src/data/session")
		const { useCouncilStore } = await import("../../../src/stores/councilStore")

		const councilStore = useCouncilStore()
		const storeAccessSpy = vi.spyOn(councilStore, "lockedCouncil", "get")

		councilStore.lockedCouncil = "CHC"

		await session.login.onSuccess()

		// CouncilStore should be accessed during redirect decision
		expect(storeAccessSpy).toHaveBeenCalled()
		expect(mockRouterReplace).toHaveBeenCalledWith({
			name: "CouncilDashboard",
			params: { councilCode: "CHC" },
		})
	})

	it("should maintain separation between locked and selected council", async () => {
		const { useCouncilStore } = await import("../../../src/stores/councilStore")

		const councilStore = useCouncilStore()

		councilStore.lockedCouncil = "AKL"
		councilStore.selectedCouncil = "WLG"

		// Both should coexist independently
		expect(councilStore.lockedCouncil).toBe("AKL")
		expect(councilStore.selectedCouncil).toBe("WLG")
	})
})
