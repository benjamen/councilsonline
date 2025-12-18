import { expect, test } from "@playwright/test"

test.describe("Main Site SPISC Flow", () => {
	test("should complete SPISC application from main site", async ({ page }) => {
		console.log("=== Test: Main Site SPISC Flow ===")

		// Step 1: Navigate to main site
		console.log("Step 1: Navigating to main site /frontend/request/new...")
		await page.goto("http://localhost:8080/frontend/request/new", {
			waitUntil: "networkidle",
		})

		// Should be on Step 1 (Council Selection) since no council param
		await expect(page.locator("h2")).toContainText("Select Council")
		console.log("✓ On council selection step")

		// Step 2: Select Taytay council
		console.log("Step 2: Selecting Taytay council...")
		await page.click("text=Taytay Municipal Council")
		await page.waitForTimeout(500)

		// Click Next to go to request type selection
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(1000)

		// Should now be on Step 2 (Request Type Selection)
		await expect(page.locator("h2")).toContainText("Select Application Type")
		console.log("✓ On request type selection step")

		// Step 3: Select SPISC request type
		console.log("Step 3: Selecting SPISC request type...")
		await page.click("text=Social Pension for Indigent Senior Citizens")
		await page.waitForTimeout(500)

		// Click Next to go to Process Info step
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(2000)

		// Step 4: Should auto-save and redirect to request detail page
		console.log("Step 4: Waiting for auto-save and redirect...")
		await page.waitForTimeout(3000)

		const currentUrl = page.url()
		console.log("Current URL:", currentUrl)

		// Should be redirected to /request/:id
		expect(currentUrl).toMatch(/\/request\/SPISC-\d{4}-\d+/)
		console.log("✓ Redirected to request detail page")

		// Step 5: Verify request detail page elements
		console.log("Step 5: Verifying request detail page...")

		// Should show request number
		await expect(page.locator("h1")).toContainText("SPISC-")

		// Should show request type
		await expect(
			page.locator("text=Social Pension for Indigent Senior Citizens"),
		).toBeVisible()

		// Should show status badge (Draft)
		await expect(page.locator("text=Draft")).toBeVisible()

		// Should show Submit Application button
		await expect(
			page.locator('button:has-text("Submit Application")'),
		).toBeVisible()

		console.log("✓ Request detail page loaded correctly")

		// Step 6: Verify application overview section
		console.log("Step 6: Verifying application overview...")
		await expect(page.locator("text=Application Overview")).toBeVisible()
		await expect(page.locator("text=Request Number")).toBeVisible()
		await expect(page.locator("text=Status")).toBeVisible()

		console.log("✓ Application overview section present")

		console.log("=== Test Completed Successfully ===")
	})

	test("should handle back navigation correctly", async ({ page }) => {
		console.log("=== Test: Back Navigation ===")

		// Start at new request page with council selected
		console.log("Step 1: Starting with council pre-selected...")
		await page.goto(
			"http://localhost:8080/frontend/request/new?council=TAYTAY-PH",
			{ waitUntil: "networkidle" },
		)

		// Should skip to Step 2 (Request Type)
		await expect(page.locator("h2")).toContainText("Select Application Type")
		console.log("✓ Skipped to request type selection")

		// Select SPISC
		console.log("Step 2: Selecting SPISC...")
		await page.click("text=Social Pension for Indigent Senior Citizens")
		await page.waitForTimeout(500)

		// Click Next
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(2000)

		// Should redirect to detail page
		const currentUrl = page.url()
		expect(currentUrl).toMatch(/\/request\/SPISC-\d{4}-\d+/)
		console.log("✓ Redirected to detail page:", currentUrl)

		// Click back button
		console.log("Step 3: Clicking back button...")
		await page.click('button:has([d*="M10 19l-7-7"])') // SVG back arrow
		await page.waitForTimeout(1000)

		// Should go back to previous page
		const backUrl = page.url()
		console.log("Back URL:", backUrl)

		console.log("=== Test Completed Successfully ===")
	})
})
