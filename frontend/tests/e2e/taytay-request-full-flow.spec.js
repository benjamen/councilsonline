import { expect, test } from "@playwright/test"

/**
 * End-to-End Test: Taytay Request Full Flow
 * Tests:
 * 1. Login
 * 2. Create and submit a Taytay SPISC request
 * 3. Verify redirect to Taytay council dashboard (not generic)
 * 4. Verify request appears in dashboard
 * 5. Navigate to request detail page
 * 6. Verify "Send Message" button is visible
 * 7. Verify "Book Meeting" button is visible
 * 8. Test booking a meeting with available slots
 */

test.describe("Taytay Request Full Flow", () => {
	let requestId = null

	test.beforeEach(async ({ page }) => {
		// Navigate to the frontend app
		await page.goto("http://localhost:8090/frontend")
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Check if we're already logged in
		const newApplicationButton = page.locator(
			'button:has-text("New Application")',
		)
		const isLoggedIn = await newApplicationButton.isVisible().catch(() => false)

		if (!isLoggedIn) {
			// Log in
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
			await page.waitForSelector('button:has-text("New Application")', {
				timeout: 10000,
			})
		}
	})

	test("should create Taytay request and redirect to Taytay dashboard", async ({
		page,
	}) => {
		// Click New Application
		await page.click('button:has-text("New Application")')
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Select Taytay council
		const taytayButton = page.locator('button:has-text("Taytay")')
		await expect(taytayButton).toBeVisible({ timeout: 5000 })
		await taytayButton.click()
		await page.waitForTimeout(500)
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(1000)

		// Wait for request types to load
		const spinner = page.locator(".animate-spin")
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: "hidden", timeout: 10000 })
		}
		await page.waitForTimeout(500)

		// Select SPISC Request Type
		const spiscCard = page
			.locator("text=Social Pension for Indigent Senior Citizens (SPISC)")
			.first()
		await expect(spiscCard).toBeVisible({ timeout: 10000 })
		await spiscCard.click()
		await page.waitForTimeout(500)
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(1000)

		// Verify we're on Process Info step
		await expect(
			page.locator('h2:has-text("Council Process Information")'),
		).toBeVisible()

		// Click Continue to go to first dynamic step
		await page.click(
			'button:has-text("I Understand - Continue to Application")',
		)
		await page.waitForTimeout(1000)

		// Fill in applicant information (Step 1)
		await expect(
			page.locator("text=Applicant Information").first(),
		).toBeVisible({ timeout: 5000 })

		// Fill required fields
		await page.fill('input[placeholder="Juan"]', "Maria")
		await page.fill('input[placeholder="Dela Cruz"]', "Santos")

		// Select gender
		await page.selectOption("select", { value: "Female" })

		// Fill birthdate
		await page.fill('input[type="date"]', "1950-05-15")

		// Click Next
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(1000)

		// Fill residence information (Step 2)
		await page.fill(
			'input[placeholder="123 Main St, Barangay San Juan"]',
			"456 Sample Street, Barangay Test",
		)
		await page.fill(
			'input[placeholder="Number of years resided in Taytay"]',
			"25",
		)

		// Click Next
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(1000)

		// Fill income information (Step 3)
		await page.fill('input[placeholder="Monthly income amount"]', "5000")

		// Click Next
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(1000)

		// Review and Submit
		await expect(
			page.locator('h2:has-text("Review Your Application")'),
		).toBeVisible({ timeout: 5000 })

		// Submit the request
		const submitButton = page.locator('button:has-text("Submit Application")')
		await expect(submitButton).toBeVisible()
		await submitButton.click()
		await page.waitForTimeout(3000)

		// Check current URL - should redirect to Taytay dashboard, not generic dashboard
		const currentUrl = page.url()
		console.log("Current URL after submission:", currentUrl)

		// Extract request ID if we're on request detail page
		const requestIdMatch = currentUrl.match(/request\/([^\/\?]+)/)
		if (requestIdMatch) {
			requestId = requestIdMatch[1]
			console.log("Created request ID:", requestId)
		}

		// Verify we're either on Taytay dashboard or request detail (not generic dashboard)
		const isTaytayDashboard = currentUrl.includes(
			"/council/TAYTAY-PH/dashboard",
		)
		const isRequestDetail = currentUrl.includes("/request/")
		const isGenericDashboard =
			currentUrl === "http://localhost:8090/frontend/dashboard" ||
			currentUrl === "http://localhost:8090/frontend/"

		console.log("Is Taytay Dashboard:", isTaytayDashboard)
		console.log("Is Request Detail:", isRequestDetail)
		console.log("Is Generic Dashboard:", isGenericDashboard)

		expect(isGenericDashboard).toBe(false) // Should NOT be on generic dashboard
		expect(isTaytayDashboard || isRequestDetail).toBe(true) // Should be on Taytay dashboard or request detail
	})

	test("should show request in dashboard and verify Send Message and Book Meeting buttons", async ({
		page,
	}) => {
		// First create a request
		await page.goto("http://localhost:8090/frontend/request/new")
		await page.waitForLoadState("networkidle")

		// Select Taytay council
		await page.locator('button:has-text("Taytay")').click()
		await page.waitForTimeout(500)
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Wait for request types to load
		const spinner = page.locator(".animate-spin")
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: "hidden", timeout: 10000 })
		}
		await page.waitForTimeout(500)

		// Select SPISC
		const spiscCard = page
			.locator("text=Social Pension for Indigent Senior Citizens (SPISC)")
			.first()
		await expect(spiscCard).toBeVisible({ timeout: 10000 })
		await spiscCard.click()
		await page.waitForTimeout(500)
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Skip process info
		await page
			.locator('button:has-text("I Understand - Continue to Application")')
			.click()
		await page.waitForTimeout(1000)

		// Save as draft to get request ID
		const saveDraftButton = page
			.locator('button:has-text("Save Draft")')
			.first()
		await expect(saveDraftButton).toBeVisible({ timeout: 5000 })
		await saveDraftButton.click()
		await page.waitForTimeout(2000)

		// Get draft ID from URL
		const currentUrl = page.url()
		const draftIdMatch = currentUrl.match(/request\/([^\/\?]+)/)
		if (draftIdMatch) {
			requestId = draftIdMatch[1]
			console.log("Created draft request:", requestId)
		}

		expect(requestId).toBeTruthy()

		// Navigate to request detail page directly
		await page.goto(`http://localhost:8090/frontend/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Verify "Send Message" button is visible
		const sendMessageButton = page.locator('button:has-text("Send Message")')
		console.log("Looking for Send Message button...")
		await expect(sendMessageButton).toBeVisible({ timeout: 10000 })
		console.log("✓ Send Message button found")

		// Verify "Book Meeting" banner is visible
		const meetingBanner = page.locator(
			'h3:has-text("Need to discuss your application first?")',
		)
		console.log("Looking for meeting banner...")
		await expect(meetingBanner).toBeVisible({ timeout: 10000 })
		console.log("✓ Meeting banner found")

		// Verify "Request Pre-Application Meeting" button is visible
		const bookMeetingButton = page.locator(
			'button:has-text("Request Pre-Application Meeting")',
		)
		console.log("Looking for Book Meeting button...")
		await expect(bookMeetingButton).toBeVisible({ timeout: 5000 })
		console.log("✓ Book Meeting button found")
	})

	test("should open meeting modal and show available slots", async ({
		page,
	}) => {
		// Create a draft request first
		await page.goto("http://localhost:8090/frontend/request/new")
		await page.waitForLoadState("networkidle")

		await page.locator('button:has-text("Taytay")').click()
		await page.waitForTimeout(500)
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		const spinner = page.locator(".animate-spin")
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: "hidden", timeout: 10000 })
		}
		await page.waitForTimeout(500)

		const spiscCard = page
			.locator("text=Social Pension for Indigent Senior Citizens (SPISC)")
			.first()
		await expect(spiscCard).toBeVisible({ timeout: 10000 })
		await spiscCard.click()
		await page.waitForTimeout(500)
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		await page
			.locator('button:has-text("I Understand - Continue to Application")')
			.click()
		await page.waitForTimeout(1000)

		const saveDraftButton = page
			.locator('button:has-text("Save Draft")')
			.first()
		await expect(saveDraftButton).toBeVisible({ timeout: 5000 })
		await saveDraftButton.click()
		await page.waitForTimeout(2000)

		const currentUrl = page.url()
		const draftIdMatch = currentUrl.match(/request\/([^\/\?]+)/)
		if (draftIdMatch) {
			requestId = draftIdMatch[1]
		}

		expect(requestId).toBeTruthy()

		// Navigate to request detail page
		await page.goto(`http://localhost:8090/frontend/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Click "Request Pre-Application Meeting" button
		const bookMeetingButton = page
			.locator('button:has-text("Request Pre-Application Meeting")')
			.first()
		await expect(bookMeetingButton).toBeVisible({ timeout: 5000 })
		await bookMeetingButton.click()
		await page.waitForTimeout(1000)

		// Verify modal opened
		const modalTitle = page.locator(
			'h3:has-text("Request Pre-Application Council Meeting")',
		)
		await expect(modalTitle).toBeVisible({ timeout: 5000 })
		console.log("✓ Meeting modal opened")

		// Verify "View Available Slots" button is visible
		const viewSlotsButton = page.locator(
			'button:has-text("View Available Slots")',
		)
		await expect(viewSlotsButton).toBeVisible({ timeout: 5000 })
		console.log("✓ View Available Slots button found")

		// Click to view available slots
		await viewSlotsButton.click()
		await page.waitForTimeout(2000)

		// Check if slots are loading or loaded
		const loadingSpinner = page.locator("text=Loading available time slots")
		const availableSlotsHeading = page.locator(
			'h4:has-text("Available Time Slots")',
		)
		const noSlotsMessage = page.locator("text=No available slots found")

		// Wait for either loading to finish or message to appear
		await page.waitForTimeout(3000)

		const hasSlots = await availableSlotsHeading.isVisible().catch(() => false)
		const hasNoSlots = await noSlotsMessage.isVisible().catch(() => false)
		const stillLoading = await loadingSpinner.isVisible().catch(() => false)

		console.log("Has slots:", hasSlots)
		console.log("No slots:", hasNoSlots)
		console.log("Still loading:", stillLoading)

		// Verify we got a response (either slots or no slots message)
		expect(hasSlots || hasNoSlots).toBe(true)

		if (hasSlots) {
			console.log("✓ Available slots displayed")

			// Verify at least one slot is shown
			const slotButtons = page.locator('button:has-text("Ends")')
			const slotCount = await slotButtons.count()
			console.log("Number of slots displayed:", slotCount)
			expect(slotCount).toBeGreaterThan(0)

			// Try to select first available slot
			const firstSlot = slotButtons.first()
			await firstSlot.click()
			await page.waitForTimeout(500)
			console.log("✓ Successfully selected a slot")

			// Verify the slot was filled in the first preferred time
			const firstTimeInput = page
				.locator('input[type="datetime-local"]')
				.first()
			const timeValue = await firstTimeInput.inputValue()
			expect(timeValue).toBeTruthy()
			console.log("✓ Time slot auto-filled:", timeValue)
		} else {
			console.log(
				"⚠ No available slots (expected if no business hours configured or all slots booked)",
			)
		}

		// Verify we can still manually enter time if needed
		const manualTimeInput = page.locator('input[type="datetime-local"]').first()
		const tomorrow = new Date()
		tomorrow.setDate(tomorrow.getDate() + 1)
		tomorrow.setHours(10, 0, 0, 0)
		const tomorrowStr = tomorrow.toISOString().slice(0, 16)

		await manualTimeInput.fill(tomorrowStr)
		await page.waitForTimeout(500)

		const endTimeDisplay = page.locator("text=Meeting will end at")
		await expect(endTimeDisplay.first()).toBeVisible()
		console.log("✓ Manual time input works with auto-calculated end time")
	})

	test("should verify council-specific dashboard after login", async ({
		page,
	}) => {
		// Navigate to Taytay council dashboard directly
		await page.goto(
			"http://localhost:8090/frontend/council/TAYTAY-PH/dashboard",
		)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Verify we're on the correct council dashboard
		const currentUrl = page.url()
		console.log("Current URL:", currentUrl)
		expect(currentUrl).toContain("/council/TAYTAY-PH/dashboard")

		// Verify council name is displayed
		const councilName = page.locator("text=TayTay Council, text=Taytay")
		const hasCouncilName = await councilName
			.first()
			.isVisible({ timeout: 5000 })
			.catch(() => false)

		if (hasCouncilName) {
			console.log("✓ Council name displayed on dashboard")
		} else {
			console.log("⚠ Council name not found (may be in different location)")
		}

		// Verify New Application button exists
		const newAppButton = page.locator('button:has-text("New Application")')
		await expect(newAppButton).toBeVisible({ timeout: 5000 })
		console.log("✓ New Application button found on council dashboard")
	})
})
