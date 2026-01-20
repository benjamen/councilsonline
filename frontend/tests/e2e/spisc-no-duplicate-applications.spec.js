/**
 * E2E Test: SPISC Application - No Duplicate Creation
 *
 * This test verifies the critical bug fix where the system was creating
 * multiple Request and SPISC Application documents (one per step) instead
 * of updating a single application.
 *
 * Bug Reference: Commit c822b40
 * Fix: Added formData.request_id to ensure backend idempotency check works
 */

import { expect, test } from "@playwright/test"

test.describe("SPISC Application - Duplicate Prevention", () => {
	let requestId = null
	const spiscApplicationId = null

	test.beforeEach(async ({ page }) => {
		// Navigate to the application
		await page.goto("http://localhost:8090/frontend/login")
		await page.waitForLoadState("networkidle")

		// Login
		await page.fill('input[name="email"], input[type="email"]', "Administrator")
		await page.fill(
			'input[name="password"], input[type="password"]',
			"admin123",
		)
		await page.click('button[type="submit"]')

		// Wait for login to complete
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Navigate to new request page with council pre-selected
		await page.goto(
			"http://localhost:8090/frontend/request/new?council=TAYTAY-PH",
		)
		await page.waitForLoadState("networkidle")
	})

	test("should create only ONE Request and ONE SPISC Application for entire form flow", async ({
		page,
	}) => {
		// Council already selected via URL parameter, skip to request type selection

		// Step 1: Select Application Type (SPISC)
		await page.waitForSelector("text=Select Application Type", {
			timeout: 10000,
		})
		const spiscCard = page
			.locator("text=Social Pension for Indigent Senior Citizens")
			.first()
		await spiscCard.click()

		// Click Next
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(1000)

		// Click "I Understand" button if present
		const understandButton = page.locator('button:has-text("I Understand")')
		if (
			await understandButton.isVisible({ timeout: 2000 }).catch(() => false)
		) {
			await understandButton.click()
			await page.waitForTimeout(2000)
		}

		// Capture request_id from network or localStorage with retries
		let requestIdFromStorage = null
		for (let i = 0; i < 5; i++) {
			requestIdFromStorage = await page.evaluate(() => {
				const store = localStorage.getItem("requestStore")
				console.log("[DEBUG] localStorage.requestStore:", store)
				if (store) {
					const parsed = JSON.parse(store)
					console.log("[DEBUG] Parsed requestStore:", parsed)
					return parsed.currentRequestId || parsed.request_id
				}
				return null
			})

			if (requestIdFromStorage) break
			console.log(`[Test] Retry ${i + 1}/5: Waiting for requestStore...`)
			await page.waitForTimeout(1000)
		}

		requestId = requestIdFromStorage
		console.log(`[Test] Request ID after Step 1: ${requestId}`)

		if (!requestId) {
			console.warn(
				"[Test] ⚠ No Request ID found in localStorage - check request creation",
			)
		}

		// Step 2: Process Info (read-only step)
		await page.waitForSelector("text=Process Information", { timeout: 10000 })
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(2000)

		// Verify request_id hasn't changed
		const requestIdAfterStep2 = await page.evaluate(() => {
			const store = localStorage.getItem("requestStore")
			if (store) {
				const parsed = JSON.parse(store)
				return parsed.currentRequestId
			}
			return null
		})

		expect(requestIdAfterStep2).toBe(requestId)
		console.log(
			`[Test] Request ID after Step 2: ${requestIdAfterStep2} (unchanged ✓)`,
		)

		// Step 3: Personal Information
		await page.waitForSelector('input[name="full_name"]', { timeout: 10000 })

		// Fill personal info
		await page.fill('input[name="full_name"]', "Test User Senior")
		await page.fill(
			'input[name="email"]',
			`test.senior.${Date.now()}@example.com`,
		)
		await page.fill('input[name="mobile_number"]', "09171234567")
		await page.fill('input[type="date"]', "1960-01-01") // Birth date for 64 year old

		// Select sex
		await page.selectOption('select[name="sex"]', "Male")

		await page.click('button:has-text("Next")')
		await page.waitForTimeout(2000)

		// Verify request_id STILL hasn't changed
		const requestIdAfterStep3 = await page.evaluate(() => {
			const store = localStorage.getItem("requestStore")
			if (store) {
				const parsed = JSON.parse(store)
				return parsed.currentRequestId
			}
			return null
		})

		expect(requestIdAfterStep3).toBe(requestId)
		console.log(
			`[Test] Request ID after Step 3: ${requestIdAfterStep3} (unchanged ✓)`,
		)

		// Step 4: Address Information
		await page.waitForSelector('input[name="street"]', { timeout: 10000 })

		// Fill address
		await page.fill('input[name="street"]', "123 Test Street")

		// Select province, municipality, barangay (if dropdowns exist)
		const provinceSelect = page.locator('select:has-text("Province")').first()
		if (await provinceSelect.isVisible()) {
			await provinceSelect.selectOption({ index: 1 })
			await page.waitForTimeout(500)
		}

		const municipalitySelect = page
			.locator('select:has-text("Municipality")')
			.first()
		if (await municipalitySelect.isVisible()) {
			await municipalitySelect.selectOption({ index: 1 })
			await page.waitForTimeout(500)
		}

		const barangaySelect = page.locator('select:has-text("Barangay")').first()
		if (await barangaySelect.isVisible()) {
			await barangaySelect.selectOption({ index: 1 })
		}

		await page.click('button:has-text("Next")')
		await page.waitForTimeout(2000)

		// Final verification: Request ID should be the same
		const requestIdFinal = await page.evaluate(() => {
			const store = localStorage.getItem("requestStore")
			if (store) {
				const parsed = JSON.parse(store)
				return parsed.currentRequestId
			}
			return null
		})

		expect(requestIdFinal).toBe(requestId)
		console.log(`[Test] Final Request ID: ${requestIdFinal} (unchanged ✓)`)

		// Now verify in the database via API that only ONE Request exists
		const response = await page.request.post(
			"http://localhost:8090/api/method/frappe.client.get_count",
			{
				data: {
					doctype: "Request",
					filters: JSON.stringify({ name: requestId }),
				},
			},
		)

		const countData = await response.json()
		console.log(`[Test] Request count in database: ${countData.message}`)
		expect(countData.message).toBe(1)

		// Verify only ONE SPISC Application exists for this request
		const spiscResponse = await page.request.post(
			"http://localhost:8090/api/method/frappe.client.get_count",
			{
				data: {
					doctype: "SPISC Application",
					filters: JSON.stringify({ request: requestId }),
				},
			},
		)

		const spiscCountData = await spiscResponse.json()
		console.log(
			`[Test] SPISC Application count for request ${requestId}: ${spiscCountData.message}`,
		)
		expect(spiscCountData.message).toBe(1)
	})

	test("should verify formData includes request_id after first save", async ({
		page,
	}) => {
		// Navigate to new request with council pre-selected
		await page.goto(
			"http://localhost:8090/frontend/request/new?council=TAYTAY-PH",
		)
		await page.waitForLoadState("networkidle")

		// Select application type (council already selected via URL)
		await page.waitForSelector("text=Select Application Type", {
			timeout: 10000,
		})
		const spiscCard = page
			.locator("text=Social Pension for Indigent Senior Citizens")
			.first()
		await spiscCard.click()
		await page.click('button:has-text("Next")')
		await page.waitForTimeout(1000)

		// Click "I Understand" button if present
		const understandButton = page.locator('button:has-text("I Understand")')
		if (
			await understandButton.isVisible({ timeout: 2000 }).catch(() => false)
		) {
			await understandButton.click()
			await page.waitForTimeout(2000)
		}

		// Check that formData now contains request_id
		const formDataHasRequestId = await page.evaluate(() => {
			const store = localStorage.getItem("requestStore")
			if (store) {
				const parsed = JSON.parse(store)
				return parsed.formData && parsed.formData.request_id !== undefined
			}
			return false
		})

		expect(formDataHasRequestId).toBe(true)
		console.log(`[Test] formData.request_id exists: ${formDataHasRequestId} ✓`)
	})
})
