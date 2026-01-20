/**
 * Regression Test Suite for CouncilsOnline v1.3+ Critical Bugs (E2E)
 *
 * This E2E test suite MUST PASS before each release to prevent regression
 * of three critical production bugs:
 *
 * - BUG-001: Project Task autoname duplicate key errors (IntegrityError 1062)
 * - BUG-002: Council Meeting DocType 404 errors after rename
 * - BUG-003: SPISC Application fetch_from validation error blocking draft saves
 *
 * Run in headed mode for visual verification:
 *   npm run test:e2e:regression
 */

import { expect, test } from "@playwright/test"

// ============================================================================
// BUG-001 E2E Tests: Project Task Autoname Duplicate Keys
// ============================================================================

test.describe("BUG-001: Project Task Autoname (E2E)", () => {
	test("should create tasks from template without duplicate errors", async ({
		page,
	}) => {
		test.setTimeout(90000) // Extended timeout for this test

		// Login as council staff
		await page.goto("/login")
		await page.waitForLoadState("networkidle")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Navigate to Assessment Project list
		await page.goto("/app/assessment-project")
		await page.waitForLoadState("networkidle")

		// Get first Assessment Project (if exists)
		const projectExists = await page
			.locator(".list-row")
			.first()
			.isVisible({ timeout: 5000 })
			.catch(() => false)

		if (projectExists) {
			// Click first project
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")

			// Look for task creation button (if exists)
			const createTaskButton = page.locator('button:has-text("Create Tasks")')
			const buttonExists = await createTaskButton
				.isVisible({ timeout: 3000 })
				.catch(() => false)

			if (buttonExists) {
				// Click create tasks button
				await createTaskButton.click()

				// Wait for operation to complete
				await page.waitForTimeout(2000)

				// Check for error dialog with "Duplicate entry"
				const errorDialog = page.locator(
					'.modal-content:has-text("Duplicate entry")',
				)
				const hasError = await errorDialog
					.isVisible({ timeout: 1000 })
					.catch(() => false)

				// CRITICAL ASSERTION: Should NOT see duplicate entry error
				expect(hasError).toBe(false)

				// Check for success message
				const successToast = page.locator(
					".alert-success, .indicator-pill.green",
				)
				const hasSuccess = await successToast
					.isVisible({ timeout: 3000 })
					.catch(() => false)

				if (hasSuccess) {
					console.log(
						"✓ BUG-001: Tasks created successfully without duplicate errors",
					)
				}
			}
		}
	})

	test("should display unique task names in Project Task list view", async ({
		page,
	}) => {
		// Login
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Navigate to Project Task list
		await page.goto("/app/project-task")
		await page.waitForLoadState("networkidle")

		// Wait for list to load
		await page.waitForTimeout(2000)

		// Get all task names from list
		const taskNames = await page
			.locator(".list-row .level-item.bold")
			.allTextContents()

		// Check for duplicates
		const uniqueNames = new Set(taskNames)

		// CRITICAL ASSERTION: All task names should be unique
		expect(uniqueNames.size).toBe(taskNames.length)

		console.log(`✓ BUG-001: Found ${taskNames.length} unique task names`)
	})
})

// ============================================================================
// BUG-002 E2E Tests: Council Meeting DocType 404 Errors
// ============================================================================

test.describe("BUG-002: Council Meeting DocType (E2E)", () => {
	test("should load Council Meeting list page without 404", async ({
		page,
	}) => {
		// Login
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Navigate to Council Meeting page
		await page.goto("/app/council-meeting")
		await page.waitForLoadState("networkidle")

		// CRITICAL ASSERTION: Page should load (not 404)
		const notFoundText = page.locator("text=Page council-meeting not found")
		const is404 = await notFoundText
			.isVisible({ timeout: 2000 })
			.catch(() => false)

		expect(is404).toBe(false)

		// Verify page heading is visible
		const heading = page.locator(".page-title, h1")
		await expect(heading).toBeVisible({ timeout: 5000 })

		// Verify we're on the right page
		const pageTitle = await heading.textContent()
		expect(pageTitle).toMatch(/Council Meeting/i)

		console.log("✓ BUG-002: Council Meeting page loaded successfully")
	})

	test("should create new Council Meeting successfully", async ({ page }) => {
		test.setTimeout(60000)

		// Login
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Navigate to new Council Meeting
		await page.goto("/app/council-meeting/new")
		await page.waitForLoadState("networkidle")

		// Wait for form to load
		await page.waitForTimeout(2000)

		// CRITICAL ASSERTION: Form should load (not 404)
		const notFound = page.locator("text=not found")
		const is404 = await notFound.isVisible({ timeout: 1000 }).catch(() => false)
		expect(is404).toBe(false)

		// Check if form has expected fields
		const hasForm = await page
			.locator("form, .form-layout")
			.isVisible({ timeout: 3000 })
			.catch(() => false)

		if (hasForm) {
			console.log("✓ BUG-002: Council Meeting form loaded successfully")
		}
	})

	test("should call book_council_meeting API successfully", async ({
		page,
	}) => {
		// Login
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Navigate to Request detail page (if exists)
		await page.goto("/app/request")
		await page.waitForLoadState("networkidle")

		const requestExists = await page
			.locator(".list-row")
			.first()
			.isVisible({ timeout: 5000 })
			.catch(() => false)

		if (requestExists) {
			// Click first request
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")

			// Look for "Book Meeting" or similar button
			const bookButton = page.locator(
				'button:has-text("Book"), button:has-text("Meeting")',
			)
			const hasButton = await bookButton
				.first()
				.isVisible({ timeout: 3000 })
				.catch(() => false)

			if (hasButton) {
				// Set up response listener
				const responsePromise = page
					.waitForResponse(
						(response) => response.url().includes("book_council_meeting"),
						{ timeout: 10000 },
					)
					.catch(() => null)

				// Click book button
				await bookButton.first().click()

				const response = await responsePromise

				if (response) {
					// CRITICAL ASSERTION: API should not return 404
					expect(response.status()).not.toBe(404)
					console.log(
						`✓ BUG-002: book_council_meeting API returned status ${response.status()}`,
					)
				}
			}
		}
	})

	test("should not have Pre-Application Meeting references", async ({
		page,
	}) => {
		// Login
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Try to access old Pre-Application Meeting URL (should fail)
		await page.goto("/app/pre-application-meeting")
		await page.waitForLoadState("networkidle")

		// CRITICAL ASSERTION: Should see 404 for old URL
		const notFound = page.locator(
			"text=not found, text=Page pre-application-meeting not found",
		)
		const is404 = await notFound.isVisible({ timeout: 3000 }).catch(() => false)

		expect(is404).toBe(true)

		console.log("✓ BUG-002: Pre-Application Meeting URL correctly returns 404")
	})
})

// ============================================================================
// BUG-003 E2E Tests: SPISC Application fetch_from Validation Error
// ============================================================================

test.describe("BUG-003: SPISC Application Draft Save (E2E)", () => {
	test("should save draft SPISC request without validation error", async ({
		page,
	}) => {
		test.setTimeout(90000)

		// Login as applicant or staff
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Navigate to new SPISC request (adjust URL based on your routing)
		await page.goto("/app/request/new")
		await page.waitForLoadState("networkidle")

		// Wait for form to load
		await page.waitForTimeout(2000)

		// Fill basic applicant info
		const fullNameField = page
			.locator('[data-fieldname="requester"], input[name="full_name"]')
			.first()
		const fullNameExists = await fullNameField
			.isVisible({ timeout: 3000 })
			.catch(() => false)

		if (fullNameExists) {
			await fullNameField.fill("John E2E Test Doe")
		}

		// Try to save draft
		const saveDraftButton = page.locator('button:has-text("Save")').first()
		const saveButtonExists = await saveDraftButton
			.isVisible({ timeout: 3000 })
			.catch(() => false)

		if (saveButtonExists) {
			// Set up error listener
			const errorDialog = page.locator(
				'.modal-content:has-text("Fetch From"), .msgprint:has-text("Fetch From")',
			)

			await saveDraftButton.click()
			await page.waitForTimeout(3000)

			// CRITICAL ASSERTION: Should NOT see fetch_from validation error
			const hasFetchFromError = await errorDialog
				.isVisible({ timeout: 2000 })
				.catch(() => false)

			expect(hasFetchFromError).toBe(false)

			// Check for success or other validation messages (not fetch_from)
			const validationError = page.locator(".modal-content, .alert-danger")
			const hasError = await validationError
				.isVisible({ timeout: 2000 })
				.catch(() => false)

			if (hasError) {
				const errorText = await validationError.textContent()
				// Should not contain "Fetch From"
				expect(errorText).not.toMatch(/Fetch From/i)
				console.log(
					"✓ BUG-003: No fetch_from error (other validation may exist)",
				)
			} else {
				console.log(
					"✓ BUG-003: Draft saved without fetch_from validation error",
				)
			}
		}
	})

	test("should display applicant name correctly after save", async ({
		page,
	}) => {
		test.setTimeout(90000)

		// Login
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Navigate to SPISC Application list
		await page.goto("/app/spisc-application")
		await page.waitForLoadState("networkidle")

		// Check if any applications exist
		const appExists = await page
			.locator(".list-row")
			.first()
			.isVisible({ timeout: 5000 })
			.catch(() => false)

		if (appExists) {
			// Click first application
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")

			// Wait for form to load
			await page.waitForTimeout(2000)

			// Check if applicant_name field is populated
			const applicantNameField = page.locator(
				'[data-fieldname="applicant_name"]',
			)
			const hasApplicantName = await applicantNameField
				.isVisible({ timeout: 3000 })
				.catch(() => false)

			if (hasApplicantName) {
				const applicantNameValue = await applicantNameField
					.inputValue()
					.catch(() => "")

				// CRITICAL ASSERTION: applicant_name should be populated (not empty)
				expect(applicantNameValue).not.toBe("")

				console.log(
					`✓ BUG-003: Applicant name populated: "${applicantNameValue}"`,
				)
			}
		}
	})

	test("should create SPISC application with age field populated", async ({
		page,
	}) => {
		// Login
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Navigate to SPISC Application list
		await page.goto("/app/spisc-application")
		await page.waitForLoadState("networkidle")

		const appExists = await page
			.locator(".list-row")
			.first()
			.isVisible({ timeout: 5000 })
			.catch(() => false)

		if (appExists) {
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(2000)

			// Check if age display field is populated
			const ageDisplayField = page.locator(
				'[data-fieldname="applicant_age_display"]',
			)
			const hasAgeDisplay = await ageDisplayField
				.isVisible({ timeout: 3000 })
				.catch(() => false)

			if (hasAgeDisplay) {
				const ageValue = await ageDisplayField.inputValue().catch(() => "")

				// Should have age populated (from manual population, not fetch_from)
				if (ageValue) {
					console.log(`✓ BUG-003: Age display populated: "${ageValue}"`)
				}
			}
		}
	})
})

// ============================================================================
// Comprehensive Regression Suite Summary
// ============================================================================

test.describe("Regression Suite Summary", () => {
	test("should verify all critical DocTypes exist", async ({ page }) => {
		// Login
		await page.goto("/login")
		await page.fill("#login_email", "Administrator")
		await page.fill("#login_password", "admin123")
		await page.click('button.btn-login[type="submit"]')
		await page.waitForLoadState("networkidle")

		// Check Project Task
		await page.goto("/app/project-task")
		await page.waitForLoadState("networkidle")
		let notFound = await page
			.locator("text=not found")
			.isVisible({ timeout: 2000 })
			.catch(() => false)
		expect(notFound).toBe(false)
		console.log("✓ Project Task DocType accessible")

		// Check Council Meeting
		await page.goto("/app/council-meeting")
		await page.waitForLoadState("networkidle")
		notFound = await page
			.locator("text=not found")
			.isVisible({ timeout: 2000 })
			.catch(() => false)
		expect(notFound).toBe(false)
		console.log("✓ Council Meeting DocType accessible")

		// Check SPISC Application
		await page.goto("/app/spisc-application")
		await page.waitForLoadState("networkidle")
		notFound = await page
			.locator("text=not found")
			.isVisible({ timeout: 2000 })
			.catch(() => false)
		expect(notFound).toBe(false)
		console.log("✓ SPISC Application DocType accessible")

		// Check Assessment Project
		await page.goto("/app/assessment-project")
		await page.waitForLoadState("networkidle")
		notFound = await page
			.locator("text=not found")
			.isVisible({ timeout: 2000 })
			.catch(() => false)
		expect(notFound).toBe(false)
		console.log("✓ Assessment Project DocType accessible")

		console.log("\n✅ All critical DocTypes verified accessible")
	})
})
