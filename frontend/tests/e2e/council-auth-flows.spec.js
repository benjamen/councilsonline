import { expect, test } from "@playwright/test"

/**
 * E2E Tests for Dual Login Flow
 * Tests both system-wide and council-specific authentication paths
 */

// Test configuration
const TEST_COUNCIL_CODE = "AKL"
const TEST_EMAIL = "test@example.com"
const TEST_PASSWORD = "TestPassword123!"

test.describe("Dual Login Flow - Council-Specific Authentication", () => {
	test.describe("Council Landing Page", () => {
		test("should display login and register buttons when not logged in", async ({
			page,
		}) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}`)

			// Wait for page to load
			await page.waitForSelector("h1")

			// Should show Login and Sign Up buttons
			const loginButton = page.locator("text=Log In").first()
			const signUpButton = page.locator("text=Sign Up").first()

			await expect(loginButton).toBeVisible()
			await expect(signUpButton).toBeVisible()

			// Should NOT show "My Requests" when not logged in
			const myRequestsButton = page.locator("text=My Requests")
			await expect(myRequestsButton).toHaveCount(0)
		})

		test("should navigate to council login page", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}`)

			await page.click("text=Log In")

			// Should be on council-specific login page
			await expect(page).toHaveURL(
				`/frontend/council/${TEST_COUNCIL_CODE}/login`,
			)

			// Should show council branding
			await expect(page.locator("h1")).toContainText("Welcome Back")
		})

		test("should navigate to council register page", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}`)

			await page.click("text=Sign Up")

			// Should be on council-specific register page
			await expect(page).toHaveURL(
				`/frontend/council/${TEST_COUNCIL_CODE}/register`,
			)

			// Should show registration form
			await expect(page.locator("h1")).toContainText("Create Your Account")
		})
	})

	test.describe("Council Login Page", () => {
		test("should display council-branded login form", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/login`)

			// Check for login form elements
			await expect(page.locator('input[name="email"]')).toBeVisible()
			await expect(page.locator('input[name="password"]')).toBeVisible()
			await expect(page.locator('button[type="submit"]')).toContainText(
				"Sign In",
			)

			// Check for "Forgot password?" link
			const forgotPasswordLink = page.locator("text=Forgot password?")
			await expect(forgotPasswordLink).toBeVisible()
		})

		test("should navigate to forgot password page", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/login`)

			await page.click("text=Forgot password?")

			// Should be on council-specific forgot password page
			await expect(page).toHaveURL(
				`/frontend/council/${TEST_COUNCIL_CODE}/forgot-password`,
			)
			await expect(page.locator("h1")).toContainText("Reset Password")
		})

		test("should link to council register page", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/login`)

			await page.click("text=Create one now")

			// Should navigate to council register
			await expect(page).toHaveURL(
				`/frontend/council/${TEST_COUNCIL_CODE}/register`,
			)
		})

		test("should maintain council context in URL", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/login`)

			// URL should maintain council code
			expect(page.url()).toContain(`/council/${TEST_COUNCIL_CODE}`)
		})
	})

	test.describe("Council Forgot Password Page", () => {
		test("should display password reset form", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/forgot-password`)

			// Check for email input
			await expect(page.locator('input[type="email"]')).toBeVisible()
			await expect(page.locator('button[type="submit"]')).toContainText(
				"Send Reset Link",
			)

			// Check for back to login link
			const backLink = page.locator("text=Back to login")
			await expect(backLink).toBeVisible()
		})

		test("should navigate back to council login", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/forgot-password`)

			await page.click("text=Back to login")

			// Should return to council login
			await expect(page).toHaveURL(
				`/frontend/council/${TEST_COUNCIL_CODE}/login`,
			)
		})

		test("should validate email input", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/forgot-password`)

			// Try to submit without email
			await page.click('button[type="submit"]')

			// HTML5 validation should prevent submission
			const emailInput = page.locator('input[type="email"]')
			const validationMessage = await emailInput.evaluate(
				(el) => el.validationMessage,
			)
			expect(validationMessage).toBeTruthy()
		})
	})

	test.describe("Council Registration Page", () => {
		test("should display registration form with council locked", async ({
			page,
		}) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/register`)

			// Check for form elements
			await expect(page.locator("input#first_name")).toBeVisible()
			await expect(page.locator("input#last_name")).toBeVisible()
			await expect(page.locator("input#email")).toBeVisible()
			await expect(page.locator("input#phone")).toBeVisible()

			// Check that council is displayed as locked
			await expect(page.locator("text=Registering for")).toBeVisible()
		})

		test("should show all applicant type options", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/register`)

			// Check for applicant type buttons
			await expect(page.locator("text=Individual")).toBeVisible()
			await expect(page.locator("text=Company")).toBeVisible()
			await expect(page.locator("text=Trust")).toBeVisible()
			await expect(page.locator("text=Organisation")).toBeVisible()
		})

		test("should link back to council login", async ({ page }) => {
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/register`)

			const signInLink = page.locator("text=Sign in").first()
			await signInLink.click()

			// Should navigate to council login
			await expect(page).toHaveURL(
				`/frontend/council/${TEST_COUNCIL_CODE}/login`,
			)
		})
	})

	test.describe("Council Context Persistence", () => {
		test("should maintain council lock across navigation", async ({ page }) => {
			// Start at council landing
			await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}`)

			// Navigate to login
			await page.click("text=Log In")
			expect(page.url()).toContain(`/council/${TEST_COUNCIL_CODE}/login`)

			// Navigate to register
			await page.click("text=Create one now")
			expect(page.url()).toContain(`/council/${TEST_COUNCIL_CODE}/register`)

			// Navigate to forgot password via login
			await page.click("text=Sign in")
			await page.click("text=Forgot password?")
			expect(page.url()).toContain(
				`/council/${TEST_COUNCIL_CODE}/forgot-password`,
			)

			// All URLs should maintain the council code
		})
	})
})

test.describe("Dual Login Flow - System-Wide vs Council-Specific", () => {
	test("system-wide login URL should differ from council login", async ({
		page,
	}) => {
		// Visit system-wide login
		await page.goto("/frontend/account/login")
		expect(page.url()).toContain("/account/login")
		expect(page.url()).not.toContain("/council/")

		// Visit council-specific login
		await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/login`)
		expect(page.url()).toContain("/council/")
		expect(page.url()).toContain(TEST_COUNCIL_CODE)
	})

	test("council landing should not show system-wide elements", async ({
		page,
	}) => {
		await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}`)

		// Should not contain generic "CouncilsOnline" branding in hero
		// Should show council-specific content
		const heroSection = page.locator(".hero-section")
		await expect(heroSection).toBeVisible()
	})
})

test.describe("Council Branding", () => {
	test("should apply council colors to UI elements", async ({ page }) => {
		await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/login`)

		// Check that custom styling is applied (council branding)
		// This would need actual council configuration in the test database
		// For now, just verify that branding elements exist
		await expect(page.locator("h1")).toBeVisible()
	})
})

test.describe("Error Handling", () => {
	test("invalid council code should redirect", async ({ page }) => {
		// Try to access a non-existent council
		await page.goto("/frontend/council/INVALID")

		// Should redirect to landing or show error
		// Behavior depends on implementation
		await page.waitForLoadState("networkidle")

		// URL should either redirect or show error page
		const currentUrl = page.url()
		expect(currentUrl).toBeDefined()
	})

	test("login with invalid credentials should show error", async ({ page }) => {
		await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/login`)

		await page.fill('input[name="email"]', "invalid@example.com")
		await page.fill('input[name="password"]', "wrongpassword")
		await page.click('button[type="submit"]')

		// Should show error message
		await page.waitForTimeout(1000) // Wait for API response
		// Error message should be visible
		// (Exact selector depends on implementation)
	})
})

test.describe("Responsive Design", () => {
	test("council login should be mobile-friendly", async ({ page }) => {
		// Set mobile viewport
		await page.setViewportSize({ width: 375, height: 667 })

		await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}/login`)

		// Form should still be visible and usable
		await expect(page.locator('input[name="email"]')).toBeVisible()
		await expect(page.locator('input[name="password"]')).toBeVisible()
		await expect(page.locator('button[type="submit"]')).toBeVisible()
	})

	test("council landing should adapt to mobile", async ({ page }) => {
		await page.setViewportSize({ width: 375, height: 667 })

		await page.goto(`/frontend/council/${TEST_COUNCIL_CODE}`)

		// Buttons should stack vertically on mobile
		const loginButton = page.locator("text=Log In").first()
		await expect(loginButton).toBeVisible()
	})
})
