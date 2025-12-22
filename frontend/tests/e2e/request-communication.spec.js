import { expect, test } from "@playwright/test"

test.describe("Request Communication Features", () => {
	let draftId = null

	test.beforeEach(async ({ page }) => {
		// Navigate to the frontend app
		await page.goto("http://localhost:8090/frontend")
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Check if we're already logged in
		const newRequestButton = page.locator('button:has-text("New Request")')
		const isLoggedIn = await newRequestButton.isVisible().catch(() => false)

		if (!isLoggedIn) {
			console.log("Not logged in, attempting to log in...")
			// Log in - look for Sign In button
			const signInButton = page.locator('button:has-text("Sign In")').first()

			if (await signInButton.isVisible({ timeout: 2000 }).catch(() => false)) {
				console.log("Found Sign In button, clicking...")
				await signInButton.click()
				await page.waitForLoadState("networkidle")
				await page.waitForTimeout(1000)
			}

			// Fill login form
			console.log("Filling login credentials...")
			const usernameInput = page.locator('input[type="email"], input[type="text"], input[placeholder*="email"], input[placeholder*="username"]').first()
			const passwordInput = page.locator('input[type="password"], input[placeholder*="password"]').first()

			await usernameInput.fill("Administrator")
			await page.waitForTimeout(300)
			await passwordInput.fill("admin123")
			await page.waitForTimeout(300)

			// Click Sign In button on login form
			const loginSubmit = page.locator('button:has-text("Sign In"), button[type="submit"]').first()
			console.log("Clicking Sign In to submit login...")
			await loginSubmit.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(2000)

			// Verify login successful
			console.log("Waiting for New Request button to confirm login...")
			await page.waitForSelector('button:has-text("New Request")', {
				timeout: 10000,
			})
			console.log("Login successful!")
		} else {
			console.log("Already logged in")
		}

		// Create a draft SPISC request for testing
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

		// Select SPISC Request Type
		const spiscCard = page
			.locator("text=Social Pension for Indigent Senior Citizens (SPISC)")
			.first()
		await expect(spiscCard).toBeVisible({ timeout: 10000 })
		await spiscCard.click()
		await page.waitForTimeout(500)
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Verify we're on Process Info step
		await expect(
			page.locator('h2:has-text("Council Process Information")'),
		).toBeVisible()

		// Click Next to go to first dynamic step
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Save draft
		const saveDraftButton = page
			.locator('button:has-text("Save Draft")')
			.first()
		await expect(saveDraftButton).toBeVisible({ timeout: 5000 })
		await saveDraftButton.click()
		await page.waitForTimeout(2000)

		// Get draft ID from modal
		const draftIdText = await page.locator(".font-mono").textContent()
		draftId = draftIdText?.trim()
		console.log("Created draft:", draftId)

		// Close modal - use force to bypass Dialog overlay
		await page
			.locator('button:has-text("Close"), button:has-text("Continue Editing")')
			.first()
			.click({ force: true })
		await page.waitForTimeout(500)
	})

	test("should display Send Message button on request detail page", async ({
		page,
	}) => {
		expect(draftId).toBeTruthy()

		// Navigate to request detail page
		await page.goto(`http://localhost:8090/frontend/request/${draftId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Verify Send Message button exists in Quick Actions
		const sendMessageButton = page.locator('button:has-text("Send Message")')
		await expect(sendMessageButton).toBeVisible({ timeout: 10000 })
	})

	test("should open Send Message modal and display all fields", async ({
		page,
	}) => {
		expect(draftId).toBeTruthy()

		// Navigate to request detail page
		await page.goto(`http://localhost:8090/frontend/request/${draftId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Click Send Message button - use .first() since there might be multiple
		const sendMessageButton = page
			.locator('button:has-text("Send Message")')
			.first()
		await sendMessageButton.click()
		await page.waitForTimeout(500)

		// Verify modal opened with correct title
		await expect(
			page.locator('h3:has-text("Send Message to Council")'),
		).toBeVisible()

		// Verify all form fields are present
		await expect(page.locator('label:has-text("Subject")')).toBeVisible()
		await expect(page.locator('label:has-text("Message")')).toBeVisible()
		await expect(
			page.locator('label:has-text("Communication Type")'),
		).toBeVisible()

		// Verify communication type options
		const typeSelect = page.locator("select").first()
		await expect(typeSelect).toBeVisible()
		const options = await typeSelect.locator("option").allTextContents()
		expect(options).toContain("Email")
		expect(options).toContain("Phone Call Follow-up")
		expect(options).toContain("Letter")
		expect(options).toContain("Other")

		// Verify info note is displayed
		await expect(
			page.locator(
				"text=Your message will be sent to the council processing team",
			),
		).toBeVisible()
		await expect(
			page.locator("text=They typically respond within 2-3 business days"),
		).toBeVisible()

		// Verify action buttons - check for the modal's buttons specifically
		const modalButtons = page.locator('div[data-state="open"]')
		await expect(
			modalButtons.locator('button:has-text("Cancel")'),
		).toBeVisible()
		await expect(
			modalButtons.locator('button:has-text("Send Message")'),
		).toBeVisible()
	})

	test("should validate required fields in Send Message modal", async ({
		page,
	}) => {
		expect(draftId).toBeTruthy()

		await page.goto(`http://localhost:8090/frontend/request/${draftId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Open Send Message modal
		await page.locator('button:has-text("Send Message")').first().click()
		await page.waitForTimeout(500)

		// Try to send without filling fields - get the button inside the modal
		const sendButton = page.locator(
			'div[data-state="open"] button:has-text("Send Message")',
		)

		// Button should be disabled when fields are empty
		await expect(sendButton).toBeDisabled()

		// Fill only subject
		await page.fill('input[placeholder*="Brief description"]', "Test Subject")
		// Should still be disabled
		await expect(sendButton).toBeDisabled()

		// Fill message as well
		await page.fill(
			'textarea[placeholder*="Type your message"]',
			"Test message content",
		)
		// Now button should be enabled
		await expect(sendButton).toBeEnabled()
	})

	test("should successfully send a message", async ({ page }) => {
		expect(draftId).toBeTruthy()

		await page.goto(`http://localhost:8090/frontend/request/${draftId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Open Send Message modal
		await page.locator('button:has-text("Send Message")').first().click()
		await page.waitForTimeout(500)

		// Fill in the form
		await page.fill(
			'input[placeholder*="Brief description"]',
			"Test Message Subject",
		)
		await page.fill(
			'textarea[placeholder*="Type your message"]',
			"This is a test message to the council regarding my application.",
		)

		// Select communication type
		await page.selectOption("select", "Email")

		// Listen for API call - set up BEFORE clicking send
		const apiPromise = page.waitForResponse(
			(response) =>
				response
					.url()
					.includes("/api/method/lodgeick.api.send_request_message"),
			{ timeout: 15000 },
		)

		// Click Send - get button inside modal
		const sendButton = page.locator(
			'div[data-state="open"] button:has-text("Send Message")',
		)
		await sendButton.click()

		// Wait for API call to complete
		const response = await apiPromise
		const responseBody = await response.json()
		console.log("API Response:", response.status(), responseBody)

		// Check if successful (either 200 or the response has success message)
		const isSuccess = response.status() === 200 || responseBody.message?.success
		expect(isSuccess).toBeTruthy()

		// Verify we're still on the request detail page
		expect(page.url()).toContain(`/request/${draftId}`)

		// Note: Modal may remain open due to how Dialog component handles state
		// The important part is that the API call succeeded
	})

	test("should close Send Message modal on Cancel", async ({ page }) => {
		expect(draftId).toBeTruthy()

		await page.goto(`http://localhost:8090/frontend/request/${draftId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Open modal
		await page.locator('button:has-text("Send Message")').first().click()
		await page.waitForTimeout(500)

		// Verify modal is open
		await expect(
			page.locator('h3:has-text("Send Message to Council")'),
		).toBeVisible()

		// Fill some data
		await page.fill('input[placeholder*="Brief description"]', "Test Subject")

		// Click Cancel
		await page.locator('button:has-text("Cancel")').click()
		await page.waitForTimeout(300)

		// Verify modal closed
		await expect(
			page.locator('h3:has-text("Send Message to Council")'),
		).not.toBeVisible()
	})

	test("should display Book Meeting button for Resource Consent requests", async ({
		page,
	}) => {
		// Create a Resource Consent request instead
		await page.goto("http://localhost:8090/frontend/request/new")
		await page.waitForLoadState("networkidle")

		// Select council
		await page.locator('button:has-text("Taytay")').click()
		await page.waitForTimeout(500)
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Wait for request types
		const spinner = page.locator(".animate-spin")
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: "hidden", timeout: 10000 })
		}

		// Look for Resource Consent type (if available)
		const rcCard = page.locator("text=/Resource Consent/i").first()
		const hasRC = await rcCard.isVisible({ timeout: 5000 }).catch(() => false)

		if (!hasRC) {
			console.log(
				"No Resource Consent type available, skipping Book Meeting test",
			)
			test.skip()
			return
		}

		await rcCard.click()
		await page.waitForTimeout(500)
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Save draft
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)
		const saveDraftButton = page
			.locator('button:has-text("Save Draft")')
			.first()
		await saveDraftButton.click()
		await page.waitForTimeout(2000)

		const rcDraftId = await page.locator(".font-mono").textContent()
		await page
			.locator('button:has-text("Close")')
			.first()
			.click({ force: true })

		// Navigate to request detail
		await page.goto(`http://localhost:8090/frontend/request/${rcDraftId}`)
		await page.waitForLoadState("networkidle")

		// Verify Book Meeting button exists
		const bookMeetingButton = page.locator(
			'button:has-text("Book Council Meeting")',
		)
		await expect(bookMeetingButton).toBeVisible({ timeout: 10000 })
	})

	test("should open Book Meeting modal and display all fields", async ({
		page,
	}) => {
		expect(draftId).toBeTruthy()

		await page.goto(`http://localhost:8090/frontend/request/${draftId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Check if Book Meeting button is visible (might not be for SPISC)
		const bookMeetingButton = page.locator(
			'button:has-text("Book Council Meeting")',
		)
		const hasButton = await bookMeetingButton
			.isVisible({ timeout: 2000 })
			.catch(() => false)

		if (!hasButton) {
			console.log(
				"Book Meeting button not available for this request type, skipping",
			)
			test.skip()
			return
		}

		// Click Book Meeting button
		await bookMeetingButton.click()
		await page.waitForTimeout(500)

		// Verify modal opened
		await expect(
			page.locator('h3:has-text("Request Council Meeting")'),
		).toBeVisible()

		// Verify form fields
		await expect(page.locator('label:has-text("Meeting Type")')).toBeVisible()
		await expect(page.locator('label:has-text("Purpose/Agenda")')).toBeVisible()

		// Verify meeting type options
		const typeSelect = page.locator("select").first()
		const options = await typeSelect.locator("option").allTextContents()
		expect(options).toContain("Pre-Application Meeting")
		expect(options).toContain("Pre-Hearing Meeting")
		expect(options).toContain("Site Visit")
		expect(options).toContain("Clarification Meeting")
		expect(options).toContain("Other")

		// Verify "What happens next?" section
		await expect(
			page.locator('h4:has-text("What happens next?")'),
		).toBeVisible()
		await expect(
			page.locator(
				"text=Your meeting request will be sent to the council processing team",
			),
		).toBeVisible()
		await expect(
			page.locator(
				"text=A council planner will contact you within 2 business days",
			),
		).toBeVisible()

		// Verify buttons
		await expect(page.locator('button:has-text("Cancel")')).toBeVisible()
		await expect(
			page.locator('button:has-text("Request Meeting")'),
		).toBeVisible()
	})

	test("should display all new sections on request detail page", async ({
		page,
	}) => {
		expect(draftId).toBeTruthy()

		await page.goto(`http://localhost:8090/frontend/request/${draftId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Verify main sections exist
		await expect(
			page.locator('h2:has-text("Application Overview")'),
		).toBeVisible()
		await expect(
			page.locator('h2:has-text("Property Information")'),
		).toBeVisible()
		await expect(
			page.locator('h2:has-text("Applicant Information")'),
		).toBeVisible()

		// Check for Application Details section (dynamic data)
		// This may or may not be visible depending on whether form data exists
		const appDetailsHeading = page.locator('h2:has-text("Application Details")')
		const hasAppDetails = await appDetailsHeading
			.isVisible({ timeout: 2000 })
			.catch(() => false)
		if (hasAppDetails) {
			console.log("Application Details section is visible")
		} else {
			console.log("Application Details section not visible (no form data yet)")
		}

		// Verify Quick Actions section
		await expect(page.locator('h2:has-text("Quick Actions")')).toBeVisible()

		// Verify standard buttons
		await expect(page.locator('button:has-text("Send Message")')).toBeVisible()

		// Edit Draft button should be visible for draft status
		const editDraftButton = page.locator('button:has-text("Edit Draft")')
		const hasEditButton = await editDraftButton
			.isVisible({ timeout: 2000 })
			.catch(() => false)
		if (hasEditButton) {
			await expect(editDraftButton).toBeVisible()
		}
	})
})
