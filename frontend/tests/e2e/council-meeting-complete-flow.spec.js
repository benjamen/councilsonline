import { expect, test } from "@playwright/test"

test.describe("Council Meeting Complete Flow", () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto("http://localhost:8090/frontend")
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Check if already logged in by looking for user menu or New Request button
		const newRequestBtn = page.locator(
			'button:has-text("New Request"), a:has-text("New Request"), button:has-text("New Application"), a:has-text("New Application")',
		)
		const isLoggedIn = await newRequestBtn
			.isVisible({ timeout: 2000 })
			.catch(() => false)

		if (!isLoggedIn) {
			console.log("Not logged in, attempting to log in...")
			const logInLink = page
				.locator(
					'a:has-text("Log In"), button:has-text("Log In"), button:has-text("Sign In")',
				)
				.first()

			if (await logInLink.isVisible({ timeout: 2000 }).catch(() => false)) {
				await logInLink.click()
				await page.waitForLoadState("networkidle")
				await page.waitForTimeout(1000)
			}

			// Fill login form
			const usernameField = page
				.locator('input[type="email"], input[type="text"]')
				.first()
			const passwordField = page.locator('input[type="password"]').first()

			await usernameField.fill("Administrator")
			await page.waitForTimeout(300)
			await passwordField.fill("admin123")
			await page.waitForTimeout(300)
			await page
				.locator('button:has-text("Sign In"), button[type="submit"]')
				.first()
				.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(2000)

			// Verify login successful
			await page.waitForSelector(
				'button:has-text("New Request"), a:has-text("New Request"), button:has-text("New Application")',
				{
					timeout: 10000,
				},
			)
			console.log("Login successful!")
		} else {
			console.log("Already logged in")
		}
	})

	test("Meeting banner appears during application flow and modal works", async ({
		page,
	}) => {
		console.log("\n=== TEST: Meeting Banner During Application Flow ===\n")

		// Start new application
		console.log("Step 1: Starting new application...")
		await page.click(
			'button:has-text("New Request"), a:has-text("New Request"), button:has-text("New Application"), a:has-text("New Application")',
		)
		await page.waitForLoadState("networkidle")
		console.log("✓ New application/request clicked")

		// Single-tenant: Skip council selection step (removed in v1.4)
		console.log(
			"\nStep 2: Selecting SPISC request type (council pre-selected)...",
		)
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
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)
		console.log("✓ SPISC selected")

		// Skip process info (Step 3)
		console.log("\nStep 3: Skipping process info...")
		await page
			.locator('button:has-text("I Understand - Continue to Application")')
			.click()
		await page.waitForTimeout(1000)
		console.log("✓ On application step")

		// CRITICAL: Verify meeting banner is now visible
		console.log("\nStep 4: Checking for meeting banner...")
		const meetingBanner = page.locator(
			'h3:has-text("Council Meeting Available")',
		)
		const bannerVisible = await meetingBanner
			.isVisible({ timeout: 5000 })
			.catch(() => false)
		console.log("Meeting banner visible:", bannerVisible)
		expect(bannerVisible).toBe(true)
		console.log("✓ Meeting banner is visible!")

		// Verify button exists
		const requestMeetingBtn = page.locator(
			'button:has-text("Request Council Meeting")',
		)
		const btnVisible = await requestMeetingBtn
			.isVisible({ timeout: 2000 })
			.catch(() => false)
		console.log("Request Council Meeting button visible:", btnVisible)
		expect(btnVisible).toBe(true)

		// CRITICAL: Click the button to open modal
		console.log("\nStep 5: Clicking Request Council Meeting button...")

		// Listen for console errors
		const consoleErrors = []
		page.on("console", (msg) => {
			if (msg.type() === "error") {
				consoleErrors.push(msg.text())
			}
		})

		await requestMeetingBtn.click()
		await page.waitForTimeout(2000) // Wait for modal to open and resources to load

		// Check for circular JSON errors
		const hasCircularJSONError = consoleErrors.some((err) =>
			err.includes("Converting circular structure to JSON"),
		)
		console.log("Has circular JSON error:", hasCircularJSONError)
		expect(hasCircularJSONError).toBe(false)
		console.log("✓ No circular JSON errors!")

		// Verify modal opened
		const modalTitle = page.locator(
			'h3:has-text("Request Pre-Application Council Meeting")',
		)
		const modalVisible = await modalTitle
			.isVisible({ timeout: 5000 })
			.catch(() => false)
		console.log("Modal visible:", modalVisible)
		expect(modalVisible).toBe(true)
		console.log("✓ Modal opened successfully!")

		// Verify modal fields are present
		console.log("\nStep 7: Verifying modal fields...")
		const meetingTypeField = page.locator("select").first()
		const purposeField = page.locator("textarea").first()
		// Time slots can be either select dropdowns (when available slots loaded) or datetime-local inputs
		const timeSlotSelects = page.locator(
			'select:has-text("-- Select a time slot --")',
		)
		const timeSlotInputs = page.locator('input[type="datetime-local"]')
		const hasTimeSlotFields =
			(await timeSlotSelects.count()) > 0 || (await timeSlotInputs.count()) > 0

		expect(await meetingTypeField.isVisible()).toBe(true)
		expect(await purposeField.isVisible()).toBe(true)
		expect(hasTimeSlotFields).toBe(true)
		console.log("✓ All form fields present")

		// Fill out the form
		console.log("\nStep 8: Filling out meeting request form...")
		await purposeField.fill(
			"I would like to discuss the requirements for my SPISC application and ensure I have all the necessary documentation.",
		)

		// Fill first time slot - check if it's a select or input field
		if ((await timeSlotSelects.count()) > 0) {
			// If available slots exist, select the first option from dropdown
			const firstSelect = timeSlotSelects.first()
			const options = await firstSelect.locator("option").allTextContents()
			if (options.length > 1) {
				// Skip the "-- Select a time slot --" option
				await firstSelect.selectOption({ index: 1 })
				console.log("✓ Form filled (selected available slot)")
			}
		} else if ((await timeSlotInputs.count()) > 0) {
			// Otherwise use datetime-local input
			const now = new Date()
			now.setDate(now.getDate() + 7) // One week from now
			now.setHours(10, 0, 0, 0) // 10:00 AM
			const datetime = now.toISOString().slice(0, 16) // Format: YYYY-MM-DDTHH:mm
			await timeSlotInputs.first().fill(datetime)
			console.log("✓ Form filled (manual datetime)")
		}

		// Verify the "Request Meeting" button is enabled
		const submitButton = page.locator('button:has-text("Request Meeting")')
		const submitEnabled = await submitButton.isEnabled()
		console.log("Submit button enabled:", submitEnabled)
		expect(submitEnabled).toBe(true)

		// Take screenshot before submitting
		await page.screenshot({ path: "/tmp/meeting-modal-filled.png" })
		console.log("✓ Screenshot saved: /tmp/meeting-modal-filled.png")

		console.log("\n✓ MEETING FLOW TEST PASSED!")
		console.log("  - Meeting banner appears on application steps")
		console.log("  - Button clickable without errors")
		console.log("  - Modal opens successfully")
		console.log("  - No circular JSON errors")
		console.log("  - Form fields work correctly\n")
	})

	test("Meeting banner on RequestDetail page also works", async ({ page }) => {
		console.log("\n=== TEST: Meeting Banner on RequestDetail Page ===\n")

		// Navigate to existing SPISC request
		console.log("Step 1: Navigating to existing request...")
		await page.goto("http://localhost:8090/frontend/request/SPISC-2025-121")
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(3000) // Wait for async resources
		console.log("✓ Request detail page loaded")

		// Verify Council Meeting section appears
		console.log("\nStep 2: Checking Council Meeting section...")
		const meetingH2 = page.locator('h2:has-text("Council Meeting")')

		// Wait for the section to appear (with longer timeout for mobile)
		try {
			await meetingH2.waitFor({ state: "visible", timeout: 10000 })
			console.log("Council Meeting section visible: true")
		} catch (e) {
			// If not visible, scroll down (might be below fold on mobile)
			await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
			await page.waitForTimeout(1000)

			// Try again after scrolling
			const sectionVisible = await meetingH2
				.isVisible({ timeout: 5000 })
				.catch(() => false)
			console.log(
				"Council Meeting section visible after scroll:",
				sectionVisible,
			)
			expect(sectionVisible).toBe(true)
		}

		// Check if meeting already exists (shows "Edit Request" button) or not (shows "Request Council Meeting")
		const requestMeetingBtn = page.locator(
			'button:has-text("Request Council Meeting")',
		)
		const editRequestBtn = page.locator('button:has-text("Edit Request")')

		const hasRequestBtn = await requestMeetingBtn
			.isVisible({ timeout: 2000 })
			.catch(() => false)
		const hasEditBtn = await editRequestBtn
			.isVisible({ timeout: 2000 })
			.catch(() => false)

		console.log("Request Council Meeting button visible:", hasRequestBtn)
		console.log("Edit Request button visible (meeting exists):", hasEditBtn)

		// Meeting section should show either request or edit button
		const hasMeetingButton = hasRequestBtn || hasEditBtn

		if (!hasMeetingButton) {
			await page.screenshot({ path: "/tmp/request-detail-debug.png" })
			console.log("Debug screenshot saved: /tmp/request-detail-debug.png")
		}

		expect(hasMeetingButton).toBe(true)

		if (hasRequestBtn) {
			// No existing meeting - test Request button
			console.log(
				"\nStep 3: No existing meeting - clicking Request Council Meeting button...",
			)
			const consoleErrors = []
			page.on("console", (msg) => {
				if (msg.type() === "error") {
					consoleErrors.push(msg.text())
				}
			})

			await requestMeetingBtn.click()
			await page.waitForTimeout(2000)

			// Check for errors
			const hasCircularJSONError = consoleErrors.some((err) =>
				err.includes("Converting circular structure to JSON"),
			)
			expect(hasCircularJSONError).toBe(false)
			console.log("✓ No circular JSON errors on RequestDetail page!")

			// Verify modal
			const modalTitle = page.locator(
				'h3:has-text("Request Pre-Application Council Meeting")',
			)
			const modalVisible = await modalTitle
				.isVisible({ timeout: 5000 })
				.catch(() => false)
			expect(modalVisible).toBe(true)
			console.log("✓ Modal works on RequestDetail page too!\n")
		} else {
			// Meeting already exists - verify Edit button works
			console.log(
				"\nStep 3: Meeting already requested - Edit Request button is available",
			)
			console.log(
				"✓ Meeting section displays correctly on RequestDetail page!\n",
			)
		}
	})
})
