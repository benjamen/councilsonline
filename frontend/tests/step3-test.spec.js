import { expect, test } from "@playwright/test"

test("Test Step 3 Navigation", async ({ page }) => {
	// Login
	await page.goto("http://localhost:8090/frontend")
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	const newRequestButton = page.locator('button:has-text("New Request")')
	const isLoggedIn = await newRequestButton.isVisible().catch(() => false)

	if (!isLoggedIn) {
		// Look for Sign In button or Log In link
		const signInButton = page.locator('button:has-text("Sign In")')
		const logInLink = page.locator(
			'a:has-text("Log In"), button:has-text("Log In")',
		)

		if (await signInButton.isVisible({ timeout: 2000 }).catch(() => false)) {
			await signInButton.click()
			await page.waitForLoadState("networkidle")
		} else if (
			await logInLink.isVisible({ timeout: 2000 }).catch(() => false)
		) {
			await logInLink.click()
			await page.waitForLoadState("networkidle")
		}

		// Fill in the login form
		await page.fill(
			'input[type="email"], input[type="text"], input[placeholder*="email"], input[placeholder*="username"]',
			"Administrator",
		)
		await page.fill(
			'input[type="password"], input[placeholder*="password"]',
			"admin123",
		)

		// Click Sign In button
		await page.click('button:has-text("Sign In")')
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Verify login was successful
		await page.waitForSelector('button:has-text("New Request")', {
			timeout: 10000,
		})
	}

	// Click New Request
	console.log("Clicking New Request...")
	await page.click('button:has-text("New Request")')
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	// Step 1: Select first council
	console.log("Step 1: Selecting council...")
	await page.screenshot({ path: "test-results/debug-step1.png" })
	const councilButtons = await page.locator('button, div[role="button"]').all()
	for (const button of councilButtons) {
		const text = await button.textContent().catch(() => "")
		if (text.includes("Council") && text.length < 100) {
			await button.click()
			break
		}
	}
	await page.waitForTimeout(500)
	await page.click('button:has-text("Next")')
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	// Step 2: Select Building Consent
	console.log("Step 2: Selecting Building Consent...")
	await page.screenshot({ path: "test-results/debug-step2.png" })

	// Find and click Building Consent - Residential New Build card
	const buildingConsentCard = page
		.locator("text=Building Consent - Residential New Build")
		.first()
	await buildingConsentCard.click()
	await page.waitForTimeout(500)

	await page.click('button:has-text("Next")')
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(2000)

	// Step 3: Process Info
	console.log("Step 3: Analyzing page...")
	await page.screenshot({ path: "test-results/debug-step3.png" })

	// Get all text content
	const h1s = await page.locator("h1").allTextContents()
	const h2s = await page.locator("h2").allTextContents()
	const h3s = await page.locator("h3").allTextContents()
	const buttons = await page.locator("button").allTextContents()

	console.log("=== STEP 3 ANALYSIS ===")
	console.log("H1:", h1s)
	console.log("H2:", h2s)
	console.log("H3:", h3s)
	console.log("Buttons:", buttons)

	// Check Next button
	const nextButton = page.locator('button:has-text("Next")')
	const nextVisible = await nextButton.isVisible().catch(() => false)
	const nextEnabled = await nextButton.isEnabled().catch(() => false)
	const nextDisabled = await nextButton.isDisabled().catch(() => false)

	console.log(
		"Next button - Visible:",
		nextVisible,
		"Enabled:",
		nextEnabled,
		"Disabled:",
		nextDisabled,
	)

	// Check for errors in console
	page.on("console", (msg) => {
		if (msg.type() === "error") {
			console.log("Browser console error:", msg.text())
		}
	})

	// Try to click Next
	if (nextVisible) {
		console.log("Attempting to click Next...")
		await nextButton.click({ timeout: 5000 })
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)
		await page.screenshot({ path: "test-results/debug-step4.png" })

		const step4Heading = await page.locator("h1, h2").first().textContent()
		console.log("Successfully navigated! Step 4 heading:", step4Heading)
	} else {
		console.log("ERROR: Next button not visible!")
		throw new Error("Next button not visible on Step 3")
	}
})
