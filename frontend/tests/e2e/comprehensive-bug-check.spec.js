import { expect, test } from "@playwright/test"

test.describe("Comprehensive Bug Check - Find All Issues", () => {
	test("Complete user journey - find any bugs", async ({ page }) => {
		console.log("\n╔═══════════════════════════════════════════════════╗")
		console.log("║  COMPREHENSIVE BUG CHECK                          ║")
		console.log("╚═══════════════════════════════════════════════════╝\n")

		// Capture all console errors and warnings
		const consoleMessages = {
			errors: [],
			warnings: [],
			logs: [],
		}

		page.on("console", (msg) => {
			const text = msg.text()
			if (msg.type() === "error") {
				consoleMessages.errors.push(text)
				console.log("🔴 CONSOLE ERROR:", text)
			} else if (msg.type() === "warning") {
				consoleMessages.warnings.push(text)
			}
		})

		// Capture network failures
		const networkErrors = []
		page.on("requestfailed", (request) => {
			networkErrors.push({
				url: request.url(),
				failure: request.failure(),
			})
			console.log("🔴 NETWORK ERROR:", request.url(), request.failure())
		})

		// Login
		console.log("\n📝 Step 1: Login...")
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
		console.log("✅ Logged in")

		// Test 1: Navigate to existing request and test all features
		console.log("\n📝 Step 2: Testing existing request page...")
		await page.goto("http://localhost:8090/frontend/request/SPISC-2025-121")
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(3000)

		// Check Send Message
		console.log("\n🧪 Testing Send Message button...")
		const sendMsgBtn = page.locator('button:has-text("Send Message")')
		if (await sendMsgBtn.isVisible().catch(() => false)) {
			await sendMsgBtn.click()
			await page.waitForTimeout(1000)

			// Check if modal/form opened
			const messageModal = page
				.locator(
					'textarea[placeholder*="message"], textarea[placeholder*="Message"]',
				)
				.first()
			const messageModalVisible = await messageModal
				.isVisible({ timeout: 2000 })
				.catch(() => false)
			console.log("Message modal/form visible:", messageModalVisible)

			if (messageModalVisible) {
				console.log("✅ Send Message works")
				// Close it
				const cancelBtn = page
					.locator('button:has-text("Cancel"), button:has-text("Close")')
					.first()
				if (await cancelBtn.isVisible().catch(() => false)) {
					await cancelBtn.click()
					await page.waitForTimeout(500)
				}
			} else {
				console.log("⚠️  Send Message button clicked but no form appeared")
			}
		} else {
			console.log("❌ Send Message button not visible")
		}

		// Check Book Meeting
		console.log("\n🧪 Testing Book Meeting button...")
		const bookMeetingBtn = page.locator(
			'button:has-text("Request Council Meeting")',
		)
		if (await bookMeetingBtn.isVisible().catch(() => false)) {
			await bookMeetingBtn.click()
			await page.waitForTimeout(2000)

			const modalTitle = page.locator(
				'h3:has-text("Request Pre-Application Council Meeting")',
			)
			const modalVisible = await modalTitle
				.isVisible({ timeout: 3000 })
				.catch(() => false)
			console.log("Book Meeting modal visible:", modalVisible)

			if (modalVisible) {
				console.log("✅ Book Meeting modal opens")

				// Check for available slots section
				const viewSlotsBtn = page.locator(
					'button:has-text("View Available Slots")',
				)
				const viewSlotsVisible = await viewSlotsBtn
					.isVisible()
					.catch(() => false)

				if (viewSlotsVisible) {
					console.log("\n🧪 Testing View Available Slots...")
					await viewSlotsBtn.click()
					await page.waitForTimeout(2000)

					// Check for loading or slots
					const slotsLoading = page.locator("text=Loading available time slots")
					const slotsError = page.locator("text=Failed to load available slots")
					const slotsContent = page.locator("text=Available Time Slots")

					const isLoading = await slotsLoading.isVisible().catch(() => false)
					const hasError = await slotsError.isVisible().catch(() => false)
					const hasContent = await slotsContent.isVisible().catch(() => false)

					console.log("Slots loading:", isLoading)
					console.log("Slots error:", hasError)
					console.log("Slots content:", hasContent)

					if (hasError) {
						console.log("❌ Available slots failed to load")
					} else if (hasContent) {
						console.log("✅ Available slots loaded")
					}
				}

				// Try to fill and check validation
				console.log("\n🧪 Testing form validation...")
				const purposeField = page.locator("textarea").first()
				await purposeField.fill("Test purpose")

				const submitBtn = page.locator('button:has-text("Request Meeting")')
				const submitEnabled1 = await submitBtn.isEnabled().catch(() => false)
				console.log("Submit enabled with purpose only:", submitEnabled1)

				// Fill time slot
				const timeSlotInputs = page.locator('input[type="datetime-local"]')
				const now = new Date()
				now.setDate(now.getDate() + 7)
				now.setHours(10, 0, 0, 0)
				const datetime = now.toISOString().slice(0, 16)

				await timeSlotInputs.first().fill(datetime)
				await page.waitForTimeout(500)

				const submitEnabled2 = await submitBtn.isEnabled().catch(() => false)
				console.log("Submit enabled with purpose + time slot:", submitEnabled2)

				if (submitEnabled2) {
					console.log("✅ Form validation works correctly")
				} else {
					console.log("⚠️  Form validation may have issues")
				}

				// Close modal
				const cancelBtn = page.locator('button:has-text("Cancel")').first()
				await cancelBtn.click()
				await page.waitForTimeout(500)
			} else {
				console.log("❌ Book Meeting modal did not open")
			}
		} else {
			console.log("❌ Book Meeting button not visible")
		}

		// Test 2: New request flow with auto-save
		console.log("\n📝 Step 3: Testing new request flow with auto-save...")
		await page.goto(
			"http://localhost:8090/frontend/request/new?council=TAYTAY-PH&locked=true",
		)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Select SPISC
		const spiscCard = page
			.locator("text=Social Pension for Indigent Senior Citizens (SPISC)")
			.first()
		if (await spiscCard.isVisible({ timeout: 3000 }).catch(() => false)) {
			await spiscCard.click()
			await page.waitForTimeout(500)

			const nextBtn = page.locator('button:has-text("Next")').first()
			await nextBtn.click()
			await page.waitForTimeout(1500)

			// Click continue on Process Info
			const continueBtn = page.locator(
				'button:has-text("I Understand - Continue to Application")',
			)
			if (await continueBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				const urlBefore = page.url()
				await continueBtn.click()
				await page.waitForTimeout(3000)

				const urlAfter = page.url()
				const requestIdMatch = urlAfter.match(/request\/([^\\/\\?]+)/)
				const requestId = requestIdMatch ? requestIdMatch[1] : null

				if (requestId && requestId !== "new") {
					console.log("✅ Auto-save worked! ID:", requestId)

					// Check if we're on RequestDetail with features
					await page.waitForTimeout(2000)

					const sendMsgVisible = await page
						.locator('button:has-text("Send Message")')
						.isVisible({ timeout: 2000 })
						.catch(() => false)
					const meetingVisible = await page
						.locator('h2:has-text("Council Meeting")')
						.isVisible({ timeout: 2000 })
						.catch(() => false)

					console.log("Send Message visible after auto-save:", sendMsgVisible)
					console.log(
						"Council Meeting visible after auto-save:",
						meetingVisible,
					)

					if (sendMsgVisible && meetingVisible) {
						console.log("✅ All features available after auto-save")
					} else {
						console.log("⚠️  Some features missing after auto-save")
					}
				} else {
					console.log("❌ Auto-save did not create draft or redirect failed")
				}
			}
		}

		// Screenshot
		await page.screenshot({
			path: "/tmp/comprehensive-bug-check.png",
			fullPage: true,
		})

		// Summary
		console.log("\n╔═══════════════════════════════════════════════════╗")
		console.log("║  BUG CHECK SUMMARY                                ║")
		console.log("╚═══════════════════════════════════════════════════╝\n")

		console.log("Console Errors:", consoleMessages.errors.length)
		if (consoleMessages.errors.length > 0) {
			console.log("Errors found:")
			consoleMessages.errors.forEach((err, i) => {
				console.log(`  ${i + 1}. ${err.substring(0, 100)}...`)
			})
		}

		console.log("\nNetwork Errors:", networkErrors.length)
		if (networkErrors.length > 0) {
			console.log("Network failures:")
			networkErrors.forEach((err, i) => {
				console.log(`  ${i + 1}. ${err.url}`)
			})
		}

		console.log("\n✅ Comprehensive bug check complete")
		console.log("📸 Screenshot: /tmp/comprehensive-bug-check.png\n")
	})
})
