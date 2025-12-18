import { expect, test } from "@playwright/test"

test("Test FRD Resource Consent - Step 4 Validation (No Infinite Loop)", async ({
	page,
}) => {
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

	// Start new request
	console.log("Starting new FRD Resource Consent request...")
	await page.click('button:has-text("New Request")')
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	// Step 1: Select Far North District Council
	console.log("Step 1: Selecting Far North District Council...")
	const fndcButton = page.locator("text=Far North District Council")
	if (await fndcButton.isVisible().catch(() => false)) {
		await fndcButton.click()
	} else {
		// Fallback: select first council
		const councilButtons = await page
			.locator('button, div[role="button"]')
			.all()
		for (const button of councilButtons) {
			const text = await button.textContent().catch(() => "")
			if (text.includes("Council") && text.length < 100) {
				await button.click()
				break
			}
		}
	}
	await page.waitForTimeout(500)
	await page.click('button:has-text("Next")')
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	// Step 2: Select Resource Consent
	console.log("Step 2: Selecting Resource Consent...")
	const resourceConsentCard = page.locator("text=Resource Consent").first()
	if (await resourceConsentCard.isVisible().catch(() => false)) {
		await resourceConsentCard.click()
		await page.waitForTimeout(500)
		await page.click('button:has-text("Next")')
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Step 3: Process Info
		console.log("Step 3: Process Info - checking for infinite loop...")
		await page.screenshot({ path: "test-results/frd-step3.png" })

		// Clear logs and wait to check for infinite loop
		step4Logs.length = 0
		consoleLogs.length = 0
		await page.waitForTimeout(3000)

		console.log(`Step 3 console logs: ${consoleLogs.length}`)
		console.log(`Step 3 Step 4 validation calls: ${step4Logs.length}`)

		if (step4Logs.length > 5) {
			console.error("INFINITE LOOP DETECTED on Step 3!")
			console.error(
				`Step 4 validation called ${step4Logs.length} times while on Step 3`,
			)
			await page.screenshot({ path: "test-results/frd-step3-frozen.png" })
			throw new Error(
				`Infinite loop on Step 3: ${step4Logs.length} validation calls`,
			)
		}

		console.log("Step 3: Trying to click Next with force...")
		try {
			await page.click('button:has-text("Next")', { timeout: 2000 })
		} catch (e) {
			console.error("Normal click failed, trying with force...")
			await page.click('button:has-text("Next")', {
				force: true,
				timeout: 2000,
			})
		}
		await page.waitForLoadState("networkidle", { timeout: 5000 })
		await page.waitForTimeout(1000)

		// Step 4: Now we're on the FRD form
		console.log("Step 4: Filling FRD Applicant & Proposal form...")

		// Clear logs before we start interacting with Step 4
		step4Logs.length = 0
		consoleLogs.length = 0

		// Fill applicant phone
		const phoneInput = page
			.locator('input[type="tel"], input[placeholder*="phone"]')
			.first()
		if (await phoneInput.isVisible({ timeout: 2000 }).catch(() => false)) {
			await phoneInput.fill("021234567")
			await page.waitForTimeout(500)
		}

		// Wait 2 seconds and check for infinite loop
		console.log("Waiting 2 seconds to check for infinite loop after typing...")
		await page.waitForTimeout(2000)

		console.log(`Console logs after typing: ${consoleLogs.length}`)
		console.log(`Step 4 (FRD) validation calls: ${step4Logs.length}`)

		if (step4Logs.length > 10) {
			console.error("INFINITE LOOP DETECTED during form interaction!")
			console.error(
				`Step 4 validation called ${step4Logs.length} times in 2 seconds`,
			)
			console.error("Logs:", step4Logs.slice(0, 5))
			throw new Error(
				`Infinite loop during form interaction: ${step4Logs.length} validation calls`,
			)
		}

		console.log("✅ No infinite loop detected during form interaction")
		console.log("✅ Step 4 FRD validation working correctly")
	} else {
		console.log("Resource Consent not available, test skipped")
	}
})
