import { expect, test } from "@playwright/test"

test("SPISC save draft with filled form", async ({ page }) => {
	// Login
	await page.goto("http://localhost:8090/frontend")
	await page.waitForLoadState("networkidle")

	const isLoggedIn = await page
		.locator('button:has-text("New Request")')
		.isVisible()
		.catch(() => false)

	if (!isLoggedIn) {
		const signInButton = page.locator('button:has-text("Sign In")')
		if (await signInButton.isVisible({ timeout: 2000 }).catch(() => false)) {
			await signInButton.click()
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
	}

	// Go to new request
	await page.goto("http://localhost:8090/frontend/request/new")
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(2000)

	// Select Taytay
	await page.locator('button:has-text("Taytay")').click()
	await page.waitForTimeout(1000)

	// Wait for request types to load
	await page.waitForTimeout(2000)

	// Select SPISC - try multiple approaches
	const spiscSelectors = [
		"text=Social Pension for Indigent Senior Citizens",
		"text=SPISC",
		'[class*="card"]:has-text("Social Pension")',
		'button:has-text("Social Pension")',
	]

	let clicked = false
	for (const selector of spiscSelectors) {
		if (
			await page
				.locator(selector)
				.first()
				.isVisible({ timeout: 2000 })
				.catch(() => false)
		) {
			await page.locator(selector).first().click()
			clicked = true
			console.log(`✓ Clicked SPISC using selector: ${selector}`)
			break
		}
	}

	if (!clicked) {
		// Take screenshot to see what's on the page
		await page.screenshot({
			path: "test-results/spisc-not-found.png",
			fullPage: true,
		})
		const bodyText = await page.locator("body").textContent()
		console.log("Page content:", bodyText.substring(0, 500))
		throw new Error("Could not find SPISC request type on page")
	}

	await page.waitForTimeout(1500)

	// Click continue on Process Info
	await page.locator('button:has-text("I Understand - Continue")').click()
	await page.waitForTimeout(1500)

	// Fill required fields
	await page.fill('input[name="full_name"]', "Test SPISC Applicant")
	await page.fill('input[name="birth_date"]', "1950-05-15")
	await page.selectOption('select[name="sex"]', "Male")
	await page.selectOption('select[name="civil_status"]', "Married")

	// Click Save Draft
	await page.locator('button:has-text("Save Draft")').click()
	await page.waitForTimeout(3000)

	// Check for errors
	const errorVisible = await page
		.locator("text=/error|Error|failed|Failed/i")
		.isVisible({ timeout: 2000 })
		.catch(() => false)

	if (errorVisible) {
		await page.screenshot({
			path: "test-results/save-draft-error.png",
			fullPage: true,
		})
		const errorText = await page
			.locator("text=/error|Error|failed|Failed/i")
			.first()
			.textContent()
		console.log("Error found:", errorText)
	}

	expect(errorVisible).toBe(false)
	console.log("✓ Save draft completed without visible errors")
})
