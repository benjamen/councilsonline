import { expect, test } from "@playwright/test"

test("Test Step 3 - Check for Infinite Loop", async ({ page }) => {
	const consoleLogs = []
	const step4Logs = []

	// Capture console logs
	page.on("console", (msg) => {
		const text = msg.text()
		consoleLogs.push(text)
		if (text.includes("Step 4 (FRD)")) {
			step4Logs.push(text)
		}
	})

	// Login
	await page.goto("http://localhost:8090/frontend")
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	const newRequestButton = page.locator('button:has-text("New Request")')
	const isLoggedIn = await newRequestButton.isVisible().catch(() => false)

	if (!isLoggedIn) {
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

		await page.fill(
			'input[type="email"], input[type="text"], input[placeholder*="email"], input[placeholder*="username"]',
			"Administrator",
		)
		await page.fill(
			'input[type="password"], input[placeholder*="password"]',
			"admin123",
		)
		await page.click('button:has-text("Sign In")')
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)
		await page.waitForSelector('button:has-text("New Request")', {
			timeout: 10000,
		})
	}

	// Click New Request
	console.log("Clicking New Request...")
	await page.click('button:has-text("New Request")')
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	// Step 1: Select council
	console.log("Step 1: Selecting council...")
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
	const buildingConsentCard = page
		.locator("text=Building Consent - Residential New Build")
		.first()
	await buildingConsentCard.click()
	await page.waitForTimeout(500)

	// Clear console logs before Step 3
	step4Logs.length = 0
	consoleLogs.length = 0

	await page.click('button:has-text("Next")')
	await page.waitForLoadState("networkidle")

	// Wait on Step 3 for 3 seconds to see if infinite loop occurs
	console.log("Step 3: Waiting 3 seconds to check for infinite loop...")
	await page.waitForTimeout(3000)

	// Check console logs
	console.log(`Total console logs in 3 seconds: ${consoleLogs.length}`)
	console.log(`Step 4 (FRD) logs in 3 seconds: ${step4Logs.length}`)

	if (step4Logs.length > 5) {
		console.error("INFINITE LOOP DETECTED!")
		console.error(
			`Step 4 validation called ${step4Logs.length} times in 3 seconds`,
		)
		console.error("First 5 logs:", step4Logs.slice(0, 5))
		throw new Error(
			`Infinite loop detected: Step 4 validation called ${step4Logs.length} times`,
		)
	}

	console.log("✅ No infinite loop detected")

	// Now try to navigate to Step 4
	console.log("Step 3: Clicking Next...")
	await page.click('button:has-text("Next")')
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	const step4Heading = await page.locator("h2").first().textContent()
	console.log("Successfully navigated to Step 4:", step4Heading)
})
