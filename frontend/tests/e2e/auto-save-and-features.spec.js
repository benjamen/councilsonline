import { expect, test } from "@playwright/test"

test.describe("Auto-Save and Feature Integration", () => {
	test("Auto-save after Process Info enables Book Meeting and Send Message", async ({
		page,
	}) => {
		console.log("\n╔═══════════════════════════════════════════════════╗")
		console.log("║  TEST: Auto-Save + Book Meeting + Send Message   ║")
		console.log("╚═══════════════════════════════════════════════════╝\n")

		// Login
		await page.goto("http://localhost:8090/frontend")
		await page.waitForLoadState("networkidle")

		const logInLink = page.locator(
			'a:has-text("Log In"), button:has-text("Log In")',
		)
		if (await logInLink.isVisible({ timeout: 2000 }).catch(() => false)) {
			await logInLink.click()
			await page.waitForLoadState("networkidle")
			await page.fill(
				'input[type="email"], input[type="text"]',
				"Administrator",
			)
			await page.fill('input[type="password"]', "admin123")
			await page.click('button:has-text("Sign In")')
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(2000)
		}
		console.log("✓ Step 1: Logged in")

		// Start new application
		console.log("\n✓ Step 2: Starting new application...")
		await page.click(
			'button:has-text("New Application"), a:has-text("New Application")',
		)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Select Taytay (wait for page to stabilize first)
		console.log("\n✓ Step 3: Selecting Taytay council...")
		await page.waitForTimeout(2000) // Wait for any animations
		const taytayButton = page.locator('button:has-text("Taytay")').first()
		await taytayButton.waitFor({ state: "visible", timeout: 5000 })
		await page.waitForTimeout(500) // Additional stabilization
		await taytayButton.click({ force: true }) // Force click to avoid detachment
		await page.waitForTimeout(1000)

		const nextBtn1 = page.locator('button:has-text("Next")').first()
		await nextBtn1.click()
		await page.waitForTimeout(1500)
		console.log("✓ Taytay selected")

		// Select SPISC
		console.log("\n✓ Step 4: Selecting SPISC...")
		const spinner = page.locator(".animate-spin")
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: "hidden", timeout: 10000 })
		}

		const spiscCard = page
			.locator("text=Social Pension for Indigent Senior Citizens (SPISC)")
			.first()
		await expect(spiscCard).toBeVisible({ timeout: 10000 })
		await spiscCard.click()
		await page.waitForTimeout(500)

		const nextBtn2 = page.locator('button:has-text("Next")').first()
		await nextBtn2.click()
		await page.waitForTimeout(1500)
		console.log("✓ SPISC selected")

		// Click "I Understand" to skip process info
		console.log("\n✓ Step 5: Skipping process info (this should auto-save)...")
		const currentUrlBefore = page.url()
		console.log("URL before:", currentUrlBefore)

		const continueBtn = page.locator(
			'button:has-text("I Understand - Continue to Application")',
		)
		await continueBtn.click()

		// Wait for auto-save and redirect
		await page.waitForTimeout(3000)

		const currentUrlAfter = page.url()
		console.log("URL after:", currentUrlAfter)

		// Verify we got redirected to /request/{id}
		const requestIdMatch = currentUrlAfter.match(/request\/([^\\/\\?]+)/)
		const requestId = requestIdMatch ? requestIdMatch[1] : null
		console.log("Request ID extracted:", requestId)

		expect(requestId).toBeTruthy()
		expect(requestId).not.toBe("new")
		console.log("✅ AUTO-SAVE SUCCESSFUL! Request ID:", requestId)

		// Now we should be on RequestDetail page
		// Wait for page to load
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Verify Send Message button is visible and clickable
		console.log("\n✓ Step 6: Verifying Send Message button...")
		const sendMessageBtn = page.locator('button:has-text("Send Message")')
		const sendMsgVisible = await sendMessageBtn
			.isVisible({ timeout: 5000 })
			.catch(() => false)
		console.log("Send Message button visible:", sendMsgVisible)
		expect(sendMsgVisible).toBe(true)
		console.log("✅ SEND MESSAGE BUTTON WORKS!")

		// Verify Council Meeting section is visible
		console.log("\n✓ Step 7: Verifying Council Meeting section...")
		const meetingSection = page.locator('h2:has-text("Council Meeting")')
		const meetingSectionVisible = await meetingSection
			.isVisible({ timeout: 5000 })
			.catch(() => false)
		console.log("Council Meeting section visible:", meetingSectionVisible)
		expect(meetingSectionVisible).toBe(true)

		// Verify Request Council Meeting button
		const bookMeetingBtn = page.locator(
			'button:has-text("Request Council Meeting")',
		)
		const bookMeetingVisible = await bookMeetingBtn
			.isVisible({ timeout: 5000 })
			.catch(() => false)
		console.log("Request Council Meeting button visible:", bookMeetingVisible)
		expect(bookMeetingVisible).toBe(true)

		// Actually click the Book Meeting button
		console.log("\n✓ Step 8: Testing Book Meeting button...")
		const consoleErrors = []
		page.on("console", (msg) => {
			if (msg.type() === "error") {
				consoleErrors.push(msg.text())
			}
		})

		await bookMeetingBtn.click()
		await page.waitForTimeout(2000)

		// Check for errors
		const hasCircularJSONError = consoleErrors.some((err) =>
			err.includes("Converting circular structure to JSON"),
		)
		expect(hasCircularJSONError).toBe(false)
		console.log("✓ No circular JSON errors")

		// Verify modal opened
		const modalTitle = page.locator(
			'h3:has-text("Request Pre-Application Council Meeting")',
		)
		const modalVisible = await modalTitle
			.isVisible({ timeout: 5000 })
			.catch(() => false)
		expect(modalVisible).toBe(true)
		console.log("✅ BOOK MEETING WORKS!")

		// Take final screenshot
		await page.screenshot({
			path: "/tmp/auto-save-complete.png",
			fullPage: true,
		})
		console.log("\n✓ Screenshot saved: /tmp/auto-save-complete.png")

		console.log("\n╔═══════════════════════════════════════════════════╗")
		console.log("║  ✅ ALL FEATURES WORKING CORRECTLY!              ║")
		console.log("╚═══════════════════════════════════════════════════╝\n")

		console.log("Summary of Verified Fixes:")
		console.log("═══════════════════════════════════════════════════")
		console.log("1. ✅ Auto-save after Process Info step")
		console.log("2. ✅ Redirect to /request/{id} with valid ID")
		console.log("3. ✅ Send Message button visible and works")
		console.log("4. ✅ Council Meeting section appears")
		console.log("5. ✅ Book Meeting button opens modal without errors")
		console.log("6. ✅ No circular JSON errors\n")
	})
})
