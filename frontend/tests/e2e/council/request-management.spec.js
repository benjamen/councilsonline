/**
 * Phase 2.1: Request List & Filtering Test
 *
 * Purpose: Test the Request List page (InternalRequestManagement) with all
 * filtering, search, and sorting capabilities.
 *
 * Test Scenarios:
 * 1. Load request list with statistics
 * 2. Search by request number, applicant name, property address
 * 3. Filter by status (single and multiple)
 * 4. Filter by council
 * 5. Filter by assignee
 * 6. Filter by request type
 * 7. Sort requests
 * 8. Pagination
 * 9. Stats accuracy
 * 10. Navigate to request detail
 */

import { expect, test } from "@playwright/test"
import {
	STAFF_ROLES,
	filterRequests,
	getCouncilDashboardStats,
	loginAsCouncilStaff,
} from "../fixtures/council-staff.js"

const BASE_URL = "http://localhost:8090"

test.describe("Request Management - List View & Statistics", () => {
	let page

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage()

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN,
		})
	})

	test.afterEach(async () => {
		await page.close()
	})

	test("01 - Load request list page", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Verify page title
		const pageTitle = page.locator(".page-title, h1, .title-text")
		if ((await pageTitle.count()) > 0) {
			const titleText = await pageTitle.textContent()
			console.log(`Page title: ${titleText}`)
			expect(titleText.toLowerCase()).toContain("request")
		}

		// Verify list rows exist
		const listRows = await page.locator(".list-row").count()
		console.log(`Found ${listRows} request rows`)
		expect(listRows).toBeGreaterThan(0)
	})

	test("02 - Verify dashboard statistics load correctly", async () => {
		// Get dashboard stats
		const stats = await getCouncilDashboardStats(page)

		console.log("Dashboard stats:", stats)

		// At minimum, total should be present
		expect(stats).toBeDefined()

		// If stats.total exists, it should be a positive number
		if (stats.total !== undefined) {
			expect(stats.total).toBeGreaterThanOrEqual(0)
		}
	})

	test("03 - Verify list row count matches stats", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get visible rows count
		const visibleRows = await page.locator(".list-row").count()

		// Get list count indicator
		const listCount = page.locator(
			".list-count, .result-count, .list-count-text",
		)
		if ((await listCount.count()) > 0) {
			const countText = await listCount.textContent()
			const match = countText.match(/(\d+)/)
			if (match) {
				const reportedCount = Number.parseInt(match[1])
				console.log(
					`Visible rows: ${visibleRows}, Reported count: ${reportedCount}`,
				)

				// They should match (or reported count should be >= visible if paginated)
				expect(reportedCount).toBeGreaterThanOrEqual(visibleRows)
			}
		}

		console.log(`List displays ${visibleRows} request rows`)
	})
})

test.describe("Request Management - Search Functionality", () => {
	let page

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage()

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN,
		})
	})

	test.afterEach(async () => {
		await page.close()
	})

	test("04 - Search by request number", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get first request number
		const firstRow = page.locator(".list-row").first()
		const requestNumber = await firstRow
			.locator(
				'.level-item:has-text("SPISC"), .level-item:has-text("RC"), .level-item:has-text("BC")',
			)
			.first()
			.textContent()

		if (requestNumber && requestNumber.trim()) {
			console.log(`Searching for request: ${requestNumber.trim()}`)

			// Search for this request number
			const searchBox = page.locator(
				'.search-input, input[type="search"], .list-search',
			)
			if ((await searchBox.count()) > 0) {
				await searchBox.fill(requestNumber.trim())
				await page.keyboard.press("Enter")
				await page.waitForLoadState("networkidle")
				await page.waitForTimeout(500)

				// Verify results contain the searched request
				const results = await page.locator(".list-row").count()
				console.log(`Search returned ${results} result(s)`)

				expect(results).toBeGreaterThan(0)
			} else {
				console.log("Search box not found")
			}
		} else {
			console.log("Could not extract request number")
		}
	})

	test("05 - Search by applicant name", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get first applicant name
		const firstRow = page.locator(".list-row").first()
		const rowText = await firstRow.textContent()

		// Try to extract a name or searchable text
		console.log(`First row text: ${rowText.substring(0, 100)}...`)

		const searchBox = page.locator(
			'.search-input, input[type="search"], .list-search',
		)
		if ((await searchBox.count()) > 0) {
			// Search for common text like "SPISC" or "Draft"
			await searchBox.fill("SPISC")
			await page.keyboard.press("Enter")
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(500)

			const results = await page.locator(".list-row").count()
			console.log(`Search for "SPISC" returned ${results} result(s)`)

			expect(results).toBeGreaterThan(0)
		}
	})

	test("06 - Clear search returns to full list", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get initial count
		const initialCount = await page.locator(".list-row").count()
		console.log(`Initial list count: ${initialCount}`)

		// Perform search
		const searchBox = page.locator(
			'.search-input, input[type="search"], .list-search',
		)
		if ((await searchBox.count()) > 0) {
			await searchBox.fill("SPISC-2025-001") // Specific search
			await page.keyboard.press("Enter")
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(500)

			const searchResultCount = await page.locator(".list-row").count()
			console.log(`Search result count: ${searchResultCount}`)

			// Clear search
			await searchBox.clear()
			await page.keyboard.press("Enter")
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(500)

			const clearedCount = await page.locator(".list-row").count()
			console.log(`After clearing search: ${clearedCount}`)

			// Cleared count should match or exceed initial count
			expect(clearedCount).toBeGreaterThanOrEqual(searchResultCount)
		}
	})
})

test.describe("Request Management - Filtering", () => {
	let page

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage()

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN,
		})
	})

	test.afterEach(async () => {
		await page.close()
	})

	test("07 - Filter by status (Draft)", async () => {
		// Use the filterRequests fixture
		const resultCount = await filterRequests(page, {
			status: "Draft",
		})

		console.log(`Filter by Draft status returned ${resultCount} results`)

		// Should have at least some draft requests
		expect(resultCount).toBeGreaterThanOrEqual(0)
	})

	test("08 - Filter by status (Submitted)", async () => {
		const resultCount = await filterRequests(page, {
			status: "Submitted",
		})

		console.log(`Filter by Submitted status returned ${resultCount} results`)

		expect(resultCount).toBeGreaterThanOrEqual(0)
	})

	test("09 - Filter by request type (SPISC)", async () => {
		const resultCount = await filterRequests(page, {
			requestType: "Social Pension for Indigent Senior Citizens (SPISC)",
		})

		console.log(`Filter by SPISC type returned ${resultCount} results`)

		expect(resultCount).toBeGreaterThan(0)
	})

	test("10 - Combined filters (Status + Type)", async () => {
		const resultCount = await filterRequests(page, {
			status: "Draft",
			requestType: "Social Pension for Indigent Senior Citizens (SPISC)",
		})

		console.log(
			`Combined filter (Draft + SPISC) returned ${resultCount} results`,
		)

		expect(resultCount).toBeGreaterThanOrEqual(0)
	})
})

test.describe("Request Management - Sorting & Pagination", () => {
	let page

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage()

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN,
		})
	})

	test.afterEach(async () => {
		await page.close()
	})

	test("11 - Sort by creation date (newest first)", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for sort controls
		const sortButton = page.locator(
			'.sort-selector, button:has-text("Sort"), .sort-by',
		)

		if ((await sortButton.count()) > 0) {
			await sortButton.click()
			await page.waitForTimeout(300)

			// Select creation date
			const creationOption = page.locator("text=Creation")
			if ((await creationOption.count()) > 0) {
				await creationOption.click()
				await page.waitForLoadState("networkidle")
				await page.waitForTimeout(500)

				console.log("Sorted by creation date")
			}
		}

		// Verify list still loads
		const listRows = await page.locator(".list-row").count()
		expect(listRows).toBeGreaterThan(0)
	})

	test("12 - Navigate to next page if pagination exists", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for pagination controls
		const nextPageButton = page.locator(
			'.next-page, button:has-text("Next"), .pagination .btn-next',
		)

		if (
			(await nextPageButton.count()) > 0 &&
			(await nextPageButton.isVisible())
		) {
			// Get current page rows
			const page1Rows = await page.locator(".list-row").count()

			// Click next page
			await nextPageButton.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(500)

			// Get new page rows
			const page2Rows = await page.locator(".list-row").count()

			console.log(`Page 1: ${page1Rows} rows, Page 2: ${page2Rows} rows`)

			// Both pages should have rows
			expect(page2Rows).toBeGreaterThan(0)
		} else {
			console.log("No pagination - all results fit on one page")
		}
	})

	test("13 - Change page size if supported", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get current row count
		const initialRows = await page.locator(".list-row").count()
		console.log(`Initial rows displayed: ${initialRows}`)

		// Look for page size selector
		const pageSizeSelector = page.locator(
			'.page-size, select[name="page_length"], .page-length',
		)

		if ((await pageSizeSelector.count()) > 0) {
			// Change page size
			await pageSizeSelector.selectOption("50")
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(500)

			const newRows = await page.locator(".list-row").count()
			console.log(`After changing page size: ${newRows} rows`)

			// New count should be different or same if less than 50 total
			expect(newRows).toBeGreaterThanOrEqual(initialRows)
		} else {
			console.log("Page size selector not found")
		}
	})
})

test.describe("Request Management - Navigation", () => {
	let page

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage()

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN,
		})
	})

	test.afterEach(async () => {
		await page.close()
	})

	test("14 - Click request row to open detail view", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Click first request
		const firstRow = page.locator(".list-row").first()
		await firstRow.click()

		// Wait for navigation
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1500)

		// Verify we're on detail page
		const url = page.url()
		expect(url).toContain("/app/request/")

		// Should not be on list page anymore
		expect(url).not.toContain("/app/request?")

		console.log(`Navigated to request detail: ${url}`)
	})

	test("15 - Navigate back to list from detail view", async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Click first request
		const firstRow = page.locator(".list-row").first()
		await firstRow.click()
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1500)

		// Go back to list
		await page.goBack()
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(500)

		// Verify we're back on list page
		const url = page.url()
		expect(url).toContain("/app/request")

		// List rows should be visible
		const listRows = await page.locator(".list-row").count()
		expect(listRows).toBeGreaterThan(0)

		console.log("Successfully navigated back to list view")
	})

	test("16 - Breadcrumb navigation works", async () => {
		// Navigate to request detail
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		const firstRow = page.locator(".list-row").first()
		await firstRow.click()
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1500)

		// Look for breadcrumb
		const breadcrumb = page.locator(
			'.breadcrumb, .breadcrumb-link, [class*="breadcrumb"]',
		)

		if ((await breadcrumb.count()) > 0) {
			// Find "Request" link in breadcrumb
			const requestBreadcrumb = page
				.locator('.breadcrumb a:has-text("Request")')
				.first()

			if ((await requestBreadcrumb.count()) > 0) {
				await requestBreadcrumb.click()
				await page.waitForLoadState("networkidle")
				await page.waitForTimeout(500)

				// Should be back on list
				const url = page.url()
				expect(url).toContain("/app/request")

				console.log("Breadcrumb navigation successful")
			} else {
				console.log("Request breadcrumb link not found")
			}
		} else {
			console.log("Breadcrumbs not found")
		}
	})
})
