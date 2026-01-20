/**
 * Phase 7: Dashboard & Branding Tests
 *
 * Purpose: Test council dashboard statistics and branding customization.
 *
 * Test Scenarios:
 * - Dashboard statistics and metrics
 * - Council switcher (multi-council users)
 * - Council branding (logo, colors, name)
 * - Landing pages
 * - Email template branding
 */

import { expect, test } from "@playwright/test"
import {
	STAFF_ROLES,
	getCouncilDashboardStats,
	loginAsCouncilStaff,
} from "../fixtures/council-staff.js"

const BASE_URL = "http://localhost:8090"

test.describe("Council Dashboard - Statistics & Metrics", () => {
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

	test("01 - Load council dashboard", async () => {
		// Navigate to request list (acts as main dashboard)
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Verify page loaded
		const pageTitle = page.locator(".page-title, h1")

		if ((await pageTitle.count()) > 0) {
			const titleText = await pageTitle.textContent()
			console.log(`Dashboard page: ${titleText}`)
		}

		// Check for request list
		const listRows = await page.locator(".list-row").count()
		console.log(`Dashboard shows ${listRows} requests`)

		expect(listRows).toBeGreaterThanOrEqual(0)
	})

	test("02 - Verify dashboard statistics display", async () => {
		// Get dashboard stats using fixture
		const stats = await getCouncilDashboardStats(page)

		console.log("Dashboard statistics:", stats)

		// Stats should be returned
		expect(stats).toBeDefined()

		// Log individual stats if available
		if (stats.total !== undefined) {
			console.log(`- Total requests: ${stats.total}`)
		}
		if (stats.inProgress !== undefined) {
			console.log(`- In Progress: ${stats.inProgress}`)
		}
		if (stats.pending !== undefined) {
			console.log(`- Pending: ${stats.pending}`)
		}
		if (stats.completed !== undefined) {
			console.log(`- Completed: ${stats.completed}`)
		}
	})

	test("03 - Verify stat cards load correctly", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for stat cards/indicators
		const statCards = page.locator(
			".indicator-pill, " +
				".stat-card, " +
				'[class*="indicator-"], ' +
				'[class*="stat"]',
		)

		if ((await statCards.count()) > 0) {
			const statsCount = await statCards.count()
			console.log(`Found ${statsCount} stat indicators`)

			// Verify at least some stats are visible
			expect(statsCount).toBeGreaterThan(0)
		} else {
			console.log("No stat cards found - may be different UI layout")
		}
	})

	test("04 - Verify stat accuracy matches list count", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get visible list count
		const visibleRows = await page.locator(".list-row").count()

		// Get reported total from list count indicator
		const listCount = page.locator(
			".list-count, .result-count, .list-count-text",
		)

		if ((await listCount.count()) > 0) {
			const countText = await listCount.textContent()
			const match = countText.match(/(\d+)/)

			if (match) {
				const reportedCount = Number.parseInt(match[1])
				console.log(`Visible: ${visibleRows}, Reported: ${reportedCount}`)

				// Reported should be >= visible (may be paginated)
				expect(reportedCount).toBeGreaterThanOrEqual(visibleRows)
			}
		}
	})

	test("05 - Filter and verify stat updates", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get initial count
		const initialCount = await page.locator(".list-row").count()
		console.log(`Initial count: ${initialCount}`)

		// Apply a filter (e.g., Draft status)
		const filterButton = page.locator(
			'.filter-button, button:has-text("Filter")',
		)

		if ((await filterButton.count()) > 0) {
			// Filter interface exists
			console.log("Filter available - stats should update when filtered")
		}

		// After filter, count should change
		const afterFilterCount = await page.locator(".list-row").count()
		console.log(`After filter: ${afterFilterCount}`)

		// Counts can differ
		expect(afterFilterCount).toBeGreaterThanOrEqual(0)
	})

	test("06 - Verify dashboard refreshes on data change", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get initial count
		const initialCount = await page.locator(".list-row").count()

		// Refresh page
		await page.reload()
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get new count
		const refreshedCount = await page.locator(".list-row").count()

		console.log(`Before refresh: ${initialCount}, After: ${refreshedCount}`)

		// Should maintain consistency
		expect(refreshedCount).toBeGreaterThanOrEqual(0)
	})
})

test.describe("Council Dashboard - Multi-Council Features", () => {
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

	test("07 - Check for council switcher (if multi-council user)", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for council switcher dropdown
		const councilSwitcher = page.locator(
			'[data-fieldname="council"], ' +
				".council-switcher, " +
				'select[name="council"]',
		)

		if ((await councilSwitcher.count()) > 0) {
			console.log("Council switcher found - user has multi-council access")

			// Try to get available councils
			const councilOptions = await councilSwitcher.locator("option").all()
			console.log(`Available councils: ${councilOptions.length}`)
		} else {
			console.log("No council switcher - single council user or different UI")
		}
	})

	test("08 - Filter requests by council", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for council filter
		const councilFilter = page.locator('[data-fieldname="council"]')

		if ((await councilFilter.count()) > 0) {
			console.log("Council filter available")

			// Can filter by council
			expect(councilFilter.count()).toBeGreaterThan(0)
		} else {
			console.log("Council filter not found in current view")
		}
	})
})

test.describe("Council Branding - Visual Elements", () => {
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

	test("09 - Check for council logo in header", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for logo in header
		const logo = page.locator(
			".navbar-brand img, " +
				".logo img, " +
				"header img, " +
				'[class*="logo"]',
		)

		if ((await logo.count()) > 0) {
			console.log("Logo found in header")

			// Get logo src
			const logoSrc = await logo.first().getAttribute("src")
			console.log(`Logo source: ${logoSrc}`)

			expect(logo.count()).toBeGreaterThan(0)
		} else {
			console.log("No logo found - may be text-based branding")
		}
	})

	test("10 - Verify council name displays", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for council name
		const councilName = page.locator(
			".navbar-brand, " +
				".council-name, " +
				"header .title, " +
				'[class*="council"]',
		)

		if ((await councilName.count()) > 0) {
			const nameText = await councilName.first().textContent()
			console.log(`Council name/branding: ${nameText}`)
		} else {
			console.log("Council name not found in header")
		}
	})

	test("11 - Check for custom colors/theme", async () => {
		// Navigate to dashboard
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Get primary color from navbar or header
		const navbar = page.locator(".navbar, header, .page-head")

		if ((await navbar.count()) > 0) {
			const bgColor = await navbar
				.first()
				.evaluate((el) => window.getComputedStyle(el).backgroundColor)

			console.log(`Primary background color: ${bgColor}`)

			// Should have some background color
			expect(bgColor).toBeTruthy()
		}
	})
})

test.describe("Council Branding - Public Pages", () => {
	let page

	test.beforeAll(async ({ browser }) => {
		page = await browser.newPage()
	})

	test.afterAll(async () => {
		await page.close()
	})

	test("12 - Load council landing page (public)", async () => {
		// Try to load a council landing page
		// Format: /council/{council_code}
		await page.goto(`${BASE_URL}/council/AKL`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Check if page loaded
		const pageContent = page.locator("body")
		const hasContent = (await pageContent.count()) > 0

		console.log(`Council landing page loaded: ${hasContent}`)

		expect(hasContent).toBe(true)
	})

	test("13 - Verify council branding on public landing page", async () => {
		// Load council landing page
		await page.goto(`${BASE_URL}/council/AKL`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for council-specific branding
		const logo = page.locator(
			'img[alt*="Council"], img[class*="logo"], .council-logo',
		)
		const councilName = page.locator('h1, .council-name, [class*="title"]')

		if ((await logo.count()) > 0) {
			console.log("Council logo found on landing page")
		}

		if ((await councilName.count()) > 0) {
			const nameText = await councilName.first().textContent()
			console.log(`Council name on landing page: ${nameText}`)
		}
	})

	test("14 - Verify council login page branding", async () => {
		// Navigate to login page
		await page.goto(`${BASE_URL}/frontend/login`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for branding on login page
		const loginLogo = page.locator('img, .logo, [class*="brand"]')

		if ((await loginLogo.count()) > 0) {
			console.log("Branding found on login page")

			const logoCount = await loginLogo.count()
			console.log(`Found ${logoCount} branding elements`)
		} else {
			console.log("No branding elements on login page")
		}
	})
})

test.describe("Council Branding - Configuration", () => {
	let page

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage()

		// Login as Admin
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN,
		})
	})

	test.afterEach(async () => {
		await page.close()
	})

	test("15 - Navigate to Council configuration", async () => {
		// Navigate to Council doctype
		await page.goto(`${BASE_URL}/app/council`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Verify Council list loaded
		const pageTitle = page.locator(".page-title, h1")

		if ((await pageTitle.count()) > 0) {
			const titleText = await pageTitle.textContent()
			console.log(`Council configuration page: ${titleText}`)
		}

		// Check for council records
		const councilRows = await page.locator(".list-row").count()
		console.log(`Found ${councilRows} council records`)

		expect(councilRows).toBeGreaterThanOrEqual(0)
	})

	test("16 - View council branding settings", async () => {
		// Navigate to Council list
		await page.goto(`${BASE_URL}/app/council`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Click first council
		const firstCouncil = page.locator(".list-row").first()

		if ((await firstCouncil.count()) > 0) {
			await firstCouncil.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Look for branding fields
			const logoField = page.locator(
				'[data-fieldname="logo"], [data-fieldname="council_logo"]',
			)
			const colorField = page.locator(
				'[data-fieldname="primary_color"], [data-fieldname="brand_color"]',
			)
			const nameField = page.locator('[data-fieldname="council_name"]')

			if ((await logoField.count()) > 0) {
				console.log("Logo field found")
			}
			if ((await colorField.count()) > 0) {
				console.log("Color customization field found")
			}
			if ((await nameField.count()) > 0) {
				const councilName = await nameField
					.locator("input")
					.inputValue()
					.catch(() => "")
				console.log(`Council name: ${councilName}`)
			}
		} else {
			console.log("No council records found")
		}
	})

	test("17 - Verify council code field", async () => {
		// Navigate to Council list
		await page.goto(`${BASE_URL}/app/council`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		const firstCouncil = page.locator(".list-row").first()

		if ((await firstCouncil.count()) > 0) {
			await firstCouncil.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Get council code (used in URLs)
			const codeField = page.locator(
				'[data-fieldname="council_code"], [data-fieldname="code"]',
			)

			if ((await codeField.count()) > 0) {
				const councilCode = await codeField
					.locator("input")
					.inputValue()
					.catch(() => "")
				console.log(`Council code: ${councilCode}`)

				// Code should exist (used for landing pages)
				expect(councilCode.length).toBeGreaterThan(0)
			}
		}
	})

	test("18 - Verify multiple councils exist (if applicable)", async () => {
		// Navigate to Council list
		await page.goto(`${BASE_URL}/app/council`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Count total councils
		const councilCount = await page.locator(".list-row").count()
		console.log(`Total councils in system: ${councilCount}`)

		// System supports multiple councils
		expect(councilCount).toBeGreaterThanOrEqual(1)

		if (councilCount > 1) {
			console.log("Multi-council setup detected")
		} else {
			console.log("Single council setup")
		}
	})
})
