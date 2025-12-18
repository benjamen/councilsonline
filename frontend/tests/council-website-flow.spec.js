import { expect, test } from "@playwright/test"

test.describe("Council Website Integration", () => {
	test("should load and display request types from council link", async ({
		page,
	}) => {
		console.log("=== Test: Council Link - Request Types Loading ===")

		// Navigate with council parameter
		await page.goto(
			"http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true",
			{
				waitUntil: "domcontentloaded",
			},
		)

		// Wait for page to stabilize
		await page.waitForTimeout(3000)

		// We should be on either council selection or request type selection
		const heading = await page.locator("h2").first().textContent()
		console.log("Current page:", heading)

		// If still on council selection, select council and proceed
		if (heading.includes("Select Council")) {
			console.log("  → Selecting Taytay council...")
			await page.click("text=Taytay")
			await page.waitForTimeout(1000)
			await page.click('button:has-text("Next")')
			await page.waitForTimeout(2000)
		}

		// Now we should be on request type selection
		await expect(page.locator("h2")).toContainText("Select Application Type", {
			timeout: 5000,
		})
		console.log("✓ On request type selection page")

		// Wait for request types to load from API
		console.log("Waiting for request types to load...")
		await page.waitForSelector(
			"text=Social Pension for Indigent Senior Citizens",
			{ timeout: 15000 },
		)
		console.log("✓ SPISC loaded")

		// Count available request types
		const requestTypeCards = page.locator(".cursor-pointer.border-2.rounded-lg")
		const count = await requestTypeCards.count()
		console.log(`✓ Found ${count} request types available`)

		// Verify specific types exist (use first() to avoid strict mode violation)
		await expect(
			page.locator("text=Social Pension for Indigent Senior Citizens").first(),
		).toBeVisible()
		await expect(
			page.locator("text=Local Senior Assistance").first(),
		).toBeVisible()
		await expect(
			page.locator("text=Burial / Medical Support").first(),
		).toBeVisible()

		expect(count).toBe(3)
		console.log("✓ All expected request types present")

		console.log("=== Test Passed ===")
	})

	test("should allow selecting and progressing with SPISC", async ({
		page,
	}) => {
		console.log("=== Test: SPISC Selection and Navigation ===")

		await page.goto(
			"http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true",
			{
				waitUntil: "domcontentloaded",
			},
		)

		await page.waitForTimeout(3000)

		// Handle council selection if needed
		const heading = await page.locator("h2").first().textContent()
		if (heading.includes("Select Council")) {
			await page.click("text=Taytay")
			await page.waitForTimeout(1000)
			await page.click('button:has-text("Next")')
			await page.waitForTimeout(2000)
		}

		// Wait for request types
		await page.waitForSelector(
			"text=Social Pension for Indigent Senior Citizens",
			{ timeout: 15000 },
		)

		// Select SPISC
		console.log("Selecting SPISC...")
		await page.click("text=Social Pension for Indigent Senior Citizens")
		await page.waitForTimeout(500)

		// Verify selection (card should have blue border)
		const selectedCard = page.locator(".border-blue-600").first()
		await expect(selectedCard).toBeVisible()
		console.log("✓ SPISC selected (blue border visible)")

		// Click Next
		console.log("Clicking Next...")
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(2000)

		// Should now be on Process Info step
		const nextHeading = await page.locator("h2").first().textContent()
		console.log("Next page:", nextHeading)

		expect(nextHeading).toContain("Process Information")
		console.log("✓ Advanced to Process Info step")

		console.log("=== Test Passed ===")
	})

	test("should handle council parameter without locked flag", async ({
		page,
	}) => {
		console.log("=== Test: Council Param Without Locked Flag ===")

		await page.goto(
			"http://localhost:8080/frontend/request/new?council=TAYTAY-PH",
			{
				waitUntil: "domcontentloaded",
			},
		)

		await page.waitForTimeout(3000)

		// With council param (no locked), should still preselect council
		const heading = await page.locator("h2").first().textContent()
		console.log("Current page:", heading)

		// Could be on council selection or request type
		if (heading.includes("Select Council")) {
			console.log("  → On council selection")
			// Council might be preselected, click Next
			await page.click('button:has-text("Next")')
			await page.waitForTimeout(2000)
		}

		// Should eventually reach request type selection
		await expect(page.locator("h2")).toContainText("Select Application Type", {
			timeout: 5000,
		})

		// Request types should load
		await page.waitForSelector(
			"text=Social Pension for Indigent Senior Citizens",
			{ timeout: 15000 },
		)
		console.log("✓ Request types loaded")

		console.log("=== Test Passed ===")
	})
})
