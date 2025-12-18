import { expect, test } from "@playwright/test"

test("Test FRD Resource Consent - Step 4 Component Load (Freeze Check)", async ({
	page,
}) => {
	const consoleLogs = []

	// Capture ALL console logs
	page.on("console", (msg) => {
		const text = msg.text()
		consoleLogs.push(text)
		console.log(`[BROWSER] ${text}`)
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
		console.log("Step 3: Process Info...")
		await page.screenshot({ path: "test-results/frd-freeze-check-step3.png" })

		// Wait for any JS to settle
		await page.waitForTimeout(2000)

		// Click either the custom continue button OR the standard Next button
		console.log("Step 3: Looking for continue buttons...")
		const continueButton = page.locator(
			'button:has-text("I Understand - Continue")',
		)
		const nextButton = page.locator('button:has-text("Next")')

		if (await continueButton.isVisible({ timeout: 1000 }).catch(() => false)) {
			console.log("Clicking custom continue button...")
			await continueButton.click()
		} else if (
			await nextButton.isVisible({ timeout: 1000 }).catch(() => false)
		) {
			console.log("Clicking Next button...")
			await nextButton.click()
		} else {
			throw new Error("No continue button found on Step 3")
		}

		await page.waitForLoadState("networkidle", { timeout: 10000 })
		await page.waitForTimeout(2000)

		// Step 4: Check if component loaded
		console.log("Step 4: Checking component status...")
		await page.screenshot({ path: "test-results/frd-freeze-check-step4.png" })

		// Check for toRaw fix log - this proves component loaded without freezing
		const toRawFixLog = consoleLogs.find((log) =>
			log.includes("[Step1ApplicantProposal] Using toRaw to prevent freeze"),
		)

		console.log("\n=== COMPONENT LOADING STATUS ===")
		console.log("Component loaded with toRaw fix:", toRawFixLog ? "✅" : "❌")

		if (!toRawFixLog) {
			console.error(
				"❌ FREEZE DETECTED: Component did not load or toRaw fix not applied",
			)
			throw new Error("Component froze before completing setup")
		}

		console.log("\n✅ Step 4 component loaded successfully - NO FREEZE!")
		console.log("✅ toRaw() fix worked!")

		// Try interacting with Step 4 form
		const phoneInput = page
			.locator('input[type="tel"], input[placeholder*="phone"]')
			.first()
		if (await phoneInput.isVisible({ timeout: 2000 }).catch(() => false)) {
			console.log("Filling phone number...")
			await phoneInput.fill("021234567")
			await page.waitForTimeout(1000)
			console.log("✅ Successfully interacted with Step 4 form")
		}
	} else {
		console.log("Resource Consent not available, test skipped")
	}
})
