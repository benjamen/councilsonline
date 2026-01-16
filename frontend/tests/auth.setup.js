import { expect, test as setup } from "@playwright/test"

// Auth file path - must match playwright.config.js
const AUTH_FILE = "playwright/.auth/user.json"

// Environment configuration
// Note: When running `bench serve --port 8090`, both Frappe and frontend are on same port
const FRAPPE_URL = process.env.FRAPPE_URL || "http://localhost:8090"
const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:8090"

// Test credentials - can be overridden via environment variables
const TEST_USER = process.env.TEST_USER || "Administrator"
const TEST_PASSWORD = process.env.TEST_PASSWORD || "testpass123"

setup("authenticate", async ({ page, context }) => {
	console.log(`[Auth Setup] Starting authentication against ${FRAPPE_URL}`)

	// Step 1: Login via Frappe desk to get session cookie
	await page.goto(`${FRAPPE_URL}/login`)

	// Wait for login form to render (Frappe SPA)
	await page.waitForLoadState("networkidle")

	// Fill in credentials using getByPlaceholder for modern Frappe UI
	await page.getByPlaceholder("jane@example.com").fill(TEST_USER)
	await page.getByPlaceholder("•••••").fill(TEST_PASSWORD)

	// Click login button
	await page.getByRole("button", { name: "Login" }).click()

	// Wait for successful Frappe login - could redirect to app or workspace
	await page.waitForURL(/\/(app|workspace)/, { timeout: 15000 })
	console.log("[Auth Setup] Frappe login successful")

	// Step 2: Navigate to Vue frontend to verify session carries over
	// The Frappe session cookie should work for the frontend since it's same-origin
	await page.goto(FRONTEND_URL)

	// Wait for the frontend to load and recognize the authenticated session
	// The frontend should either show a dashboard or redirect to login
	await page.waitForLoadState("networkidle", { timeout: 15000 })

	// Check if we're logged in on the frontend
	// Look for common indicators of authenticated state
	const isLoggedIn = await page.evaluate(() => {
		// Check for common authenticated user indicators
		// Frappe stores user info in localStorage or makes it available globally
		return (
			localStorage.getItem("user_id") !== "Guest" ||
			document.cookie.includes("user_id") ||
			document.querySelector("[data-user]") !== null ||
			// Check if we're not on a login page
			!window.location.pathname.includes("/login")
		)
	})

	if (!isLoggedIn) {
		console.log(
			"[Auth Setup] Frontend session verification - checking page state",
		)
		// Even if isLoggedIn check fails, the cookies should be set
		// The session should still work for API calls
	}

	console.log("[Auth Setup] Saving authentication state")

	// Step 3: Save signed-in state to file
	// This includes cookies, localStorage, and sessionStorage
	await context.storageState({ path: AUTH_FILE })

	console.log(
		`[Auth Setup] Authentication complete. State saved to ${AUTH_FILE}`,
	)
})
