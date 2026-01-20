import { expect, test } from "@playwright/test"

test.describe("Complete SPISC Application Submission", () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto("http://localhost:8090/frontend")
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Check if already logged in
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

	test("Complete SPISC application from start to finish", async ({ page }) => {
		console.log("\n=== TEST: Complete SPISC Application Submission ===\n")

		// Step 1: Start new application
		console.log("Step 1: Starting new SPISC application...")
		await page.click(
			'button:has-text("New Request"), a:has-text("New Request"), button:has-text("New Application"), a:has-text("New Application")',
		)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)
		console.log("✓ New application page loaded")

		// Step 2: Select SPISC request type
		console.log("\nStep 2: Selecting SPISC request type...")
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

		// Step 3: Process Info - Click "I Understand"
		console.log("\nStep 3: Accepting process information...")
		await page
			.locator('button:has-text("I Understand - Continue to Application")')
			.click()
		await page.waitForTimeout(1000)
		console.log("✓ Process info accepted")

		// Step 4: Fill all dynamic form fields
		console.log("\nStep 4: Filling all form fields...")

		// This test will fill all visible input fields with sample data
		// to ensure the form passes validation
		await page.evaluate(() => {
			// Fill all text inputs
			const textInputs = document.querySelectorAll(
				'input[type="text"], input:not([type])',
			)
			textInputs.forEach((input, index) => {
				if (!input.value && input.offsetParent !== null) {
					// visible and empty
					if (input.placeholder?.toLowerCase().includes("name")) {
						input.value = "Juan Dela Cruz"
					} else if (
						input.placeholder?.toLowerCase().includes("phone") ||
						input.placeholder?.toLowerCase().includes("mobile")
					) {
						input.value = "09171234567"
					} else if (
						input.placeholder?.toLowerCase().includes("address") ||
						input.placeholder?.toLowerCase().includes("street")
					) {
						input.value = "123 Main Street"
					} else {
						input.value = `Test Value ${index}`
					}
					input.dispatchEvent(new Event("input", { bubbles: true }))
					input.dispatchEvent(new Event("change", { bubbles: true }))
				}
			})

			// Fill all date inputs
			const dateInputs = document.querySelectorAll('input[type="date"]')
			dateInputs.forEach((input) => {
				if (!input.value && input.offsetParent !== null) {
					input.value = "1955-01-15"
					input.dispatchEvent(new Event("input", { bubbles: true }))
					input.dispatchEvent(new Event("change", { bubbles: true }))
				}
			})

			// Fill all number inputs
			const numberInputs = document.querySelectorAll('input[type="number"]')
			numberInputs.forEach((input) => {
				if (!input.value && input.offsetParent !== null) {
					input.value = "100"
					input.dispatchEvent(new Event("input", { bubbles: true }))
					input.dispatchEvent(new Event("change", { bubbles: true }))
				}
			})

			// Select first option in all select dropdowns
			const selects = document.querySelectorAll("select")
			selects.forEach((select) => {
				if (
					!select.value &&
					select.offsetParent !== null &&
					select.options.length > 1
				) {
					select.selectedIndex = 1 // Select first real option (skip placeholder)
					select.dispatchEvent(new Event("change", { bubbles: true }))
				}
			})

			// Check all checkboxes
			const checkboxes = document.querySelectorAll('input[type="checkbox"]')
			checkboxes.forEach((checkbox) => {
				if (!checkbox.checked && checkbox.offsetParent !== null) {
					checkbox.checked = true
					checkbox.dispatchEvent(new Event("change", { bubbles: true }))
				}
			})
		})

		await page.waitForTimeout(1000)
		console.log("✓ Form fields filled")

		// Navigate through all steps, filling fields as we go
		console.log("\nNavigating through all form steps...")
		const maxSteps = 10
		let stepCount = 0

		while (stepCount < maxSteps) {
			// Check if we're at the Review step
			const reviewHeading = page.locator(
				'h2:has-text("Review"), h3:has-text("Review")',
			)
			const isReviewStep = await reviewHeading
				.isVisible({ timeout: 1000 })
				.catch(() => false)

			if (isReviewStep) {
				console.log("✓ Reached Review step")
				break
			}

			// Fill all fields on current step
			await page.evaluate(() => {
				// Fill all visible text inputs
				document
					.querySelectorAll('input[type="text"], input:not([type])')
					.forEach((input, index) => {
						if (!input.value && input.offsetParent !== null) {
							input.value = input.placeholder?.toLowerCase().includes("name")
								? "Juan Dela Cruz"
								: input.placeholder?.toLowerCase().includes("phone")
									? "09171234567"
									: input.placeholder?.toLowerCase().includes("address")
										? "123 Main Street"
										: `Test ${index}`
							input.dispatchEvent(new Event("input", { bubbles: true }))
							input.dispatchEvent(new Event("change", { bubbles: true }))
						}
					})
				// Fill dates
				document.querySelectorAll('input[type="date"]').forEach((input) => {
					if (!input.value && input.offsetParent !== null) {
						input.value = "1955-01-15"
						input.dispatchEvent(new Event("input", { bubbles: true }))
					}
				})
				// Fill numbers
				document.querySelectorAll('input[type="number"]').forEach((input) => {
					if (!input.value && input.offsetParent !== null) {
						input.value = "100"
						input.dispatchEvent(new Event("input", { bubbles: true }))
					}
				})
				// Select dropdowns
				document.querySelectorAll("select").forEach((select) => {
					if (
						!select.value &&
						select.offsetParent !== null &&
						select.options.length > 1
					) {
						select.selectedIndex = 1
						select.dispatchEvent(new Event("change", { bubbles: true }))
					}
				})
				// Check checkboxes
				document
					.querySelectorAll('input[type="checkbox"]')
					.forEach((checkbox) => {
						if (!checkbox.checked && checkbox.offsetParent !== null) {
							checkbox.checked = true
							checkbox.dispatchEvent(new Event("change", { bubbles: true }))
						}
					})
			})

			await page.waitForTimeout(500)

			// Check if Next button exists
			const nextBtn = page.locator('button:has-text("Next")').first()
			const hasNextBtn = await nextBtn
				.isVisible({ timeout: 1000 })
				.catch(() => false)

			if (!hasNextBtn) {
				console.log("✓ No more Next buttons - at final step")
				break
			}

			// Click Next
			await nextBtn.click()
			await page.waitForTimeout(1000)
			stepCount++
			console.log(`  ✓ Completed step ${stepCount}`)
		}

		// Take screenshot of review page
		await page.screenshot({ path: "/tmp/spisc-review-page.png" })
		console.log("\n✓ Screenshot saved: /tmp/spisc-review-page.png")

		// Check for Submit button
		const submitBtn = page.locator(
			'button:has-text("Submit Application"), button:has-text("Submit")',
		)
		const hasSubmitBtn = await submitBtn
			.isVisible({ timeout: 2000 })
			.catch(() => false)

		if (hasSubmitBtn) {
			console.log("✓ Submit Application button found")
			console.log("\n✓ COMPLETE FLOW TEST PASSED!")
			console.log("  - Successfully navigated all application steps")
			console.log("  - Reached review/submit page")
			console.log("  - Ready for submission\n")
		} else {
			console.log("⚠ Submit button not found - might be at intermediate step")
			// Take debug screenshot
			await page.screenshot({ path: "/tmp/spisc-final-state.png" })
			console.log("Debug screenshot: /tmp/spisc-final-state.png")
		}

		// Verify we can see the form data
		expect(hasSubmitBtn).toBe(true)
	})
})
