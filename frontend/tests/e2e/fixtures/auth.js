/**
 * Authentication fixtures for E2E tests
 * Provides reusable login/logout functionality
 */

/**
 * Login to the frontend application
 * @param {Page} page - Playwright page object
 * @param {Object} options - Login options
 * @param {string} options.username - Username (default: 'Administrator')
 * @param {string} options.password - Password (default: 'admin123')
 * @param {string} options.baseUrl - Base URL (default: 'http://localhost:8080')
 */
export async function login(page, options = {}) {
	const {
		username = "Administrator",
		password = "admin",
		baseUrl = "http://localhost:8090",
	} = options

	console.log(`[Auth] Logging in as ${username}`)

	// Navigate to frontend login page
	await page.goto(`${baseUrl}/frontend/account/login`, {
		waitUntil: "networkidle",
	})
	await page.waitForTimeout(2000)

	// Check if already logged in (redirects to dashboard)
	const currentUrl = page.url()
	if (currentUrl.includes("/dashboard") || currentUrl.includes("/home")) {
		console.log("[Auth] Already logged in")
		return true
	}

	// Fill in login form
	const emailInput = page
		.locator('input[type="text"], input[type="email"]')
		.first()
	const passwordInput = page.locator('input[type="password"]').first()

	await emailInput.fill(username)
	await passwordInput.fill(password)

	// Click login button
	await page.waitForTimeout(1000) // Wait for any overlays to clear
	const loginButton = page.locator('button[type="submit"]').first()

	// Wait for button to be ready
	await loginButton.waitFor({ state: "visible", timeout: 5000 })

	// Try clicking, use force if needed
	try {
		await loginButton.click({ timeout: 5000 })
	} catch (e) {
		console.log("[Auth] Normal click failed, using force click")
		await loginButton.click({ force: true })
	}
	console.log("[Auth] Submitted login form")

	// Wait for redirect
	await page.waitForTimeout(5000)

	// Verify login succeeded
	const finalUrl = page.url()
	if (finalUrl.includes("/account/login") || finalUrl.includes("/login")) {
		throw new Error("Login failed - still on login page")
	}

	console.log("[Auth] Login successful - redirected to:", finalUrl)
	return true
}

/**
 * Logout from the frontend application
 * @param {Page} page - Playwright page object
 */
export async function logout(page) {
	console.log("[Auth] Logging out")

	// Look for logout button/link
	const logoutButton = page.locator("text=/logout/i, text=/sign out/i").first()

	if ((await logoutButton.count()) > 0) {
		await logoutButton.click()
		await page.waitForTimeout(1000)
	}

	console.log("[Auth] Logout complete")
}

/**
 * Ensure user is logged in before running test
 * @param {Page} page - Playwright page object
 * @param {Object} options - Login options
 */
export async function ensureLoggedIn(page, options = {}) {
	const baseUrl = options.baseUrl || "http://localhost:8090"

	// Check if we're on a login page
	const currentUrl = page.url()
	if (currentUrl.includes("/account/login") || currentUrl.includes("/login")) {
		await login(page, options)
	} else {
		// Try to access a protected page to verify login status
		console.log("[Auth] Checking login status")
		await page.goto(`${baseUrl}/frontend/dashboard`, {
			waitUntil: "networkidle",
		})
		await page.waitForTimeout(2000)

		if (
			page.url().includes("/account/login") ||
			page.url().includes("/login")
		) {
			await login(page, options)
		} else {
			console.log("[Auth] Already logged in - at:", page.url())
		}
	}
}
