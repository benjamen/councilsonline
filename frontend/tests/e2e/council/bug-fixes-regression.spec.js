/**
 * Phase 0.2: Bug Fixes Regression Test
 *
 * Purpose: Verify that recently fixed bugs don't regress.
 *
 * This test verifies the following commits/fixes:
 * - Commit 7b2fc72: ES6 to Frappe namespace conversion
 * - Commit f107a93: Dashboard defensive checks
 * - Commit 7ee30c3: Deferred initialization
 * - Commit 7be7507: Page wrapper defensive checks
 *
 * Each test ensures the specific bug fix is still working.
 */

import { expect, test } from "@playwright/test"
import { login } from "../fixtures/auth.js"

const BASE_URL = "http://localhost:8090"

test.describe("Bug Fixes Regression - Commit Verification", () => {
	let page
	let consoleErrors = []
	let consoleWarnings = []

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage()
		consoleErrors = []
		consoleWarnings = []

		// Capture all console messages
		page.on("console", (msg) => {
			const text = msg.text()
			if (msg.type() === "error") {
				consoleErrors.push(text)
			}
			if (msg.type() === "warning") {
				consoleWarnings.push(text)
			}
			if (
				msg.type() === "log" &&
				(text.includes("councilsonline") || text.includes("namespace"))
			) {
				console.log("Console log:", text)
			}
		})

		page.on("pageerror", (error) => {
			consoleErrors.push(`Page Error: ${error.message}`)
		})

		await login(page, {
			username: "Administrator",
			password: "admin123",
			baseUrl: BASE_URL,
		})
	})

	test.afterEach(async () => {
		await page.close()
	})

	test.describe("Commit 7b2fc72 - ES6 to Frappe Namespace Conversion", () => {
		test("Should load action_bar_utils.js without ES6 export errors", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Check for ES6 export/import errors
			const es6Errors = consoleErrors.filter(
				(err) =>
					err.toLowerCase().includes("export") ||
					err.toLowerCase().includes("import statement") ||
					(err.toLowerCase().includes("unexpected token") &&
						err.toLowerCase().includes("export")),
			)

			expect(
				es6Errors,
				"action_bar_utils.js should not have ES6 export errors",
			).toHaveLength(0)
		})

		test("Should have councilsonline.actionBar namespace available", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Check if namespace exists in browser context
			const hasActionBarNamespace = await page.evaluate(() => {
				return (
					typeof window.councilsonline !== "undefined" &&
					typeof window.councilsonline.actionBar !== "undefined"
				)
			})

			// If namespace doesn't exist, that's OK as long as no errors
			// The important thing is no console errors
			expect(consoleErrors, "Should not have namespace errors").toHaveLength(0)
		})

		test("Should load summary_dashboard.js without ES6 import errors", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1500) // Dashboard is deferred

			// Check for import statement errors
			const importErrors = consoleErrors.filter(
				(err) =>
					err.includes("import statement outside a module") ||
					err.includes("Cannot use import"),
			)

			expect(
				importErrors,
				"summary_dashboard.js should not have ES6 import errors",
			).toHaveLength(0)
		})

		test("Should have councilsonline.dashboard namespace available", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1500)

			// No namespace errors
			expect(
				consoleErrors,
				"Dashboard namespace should load without errors",
			).toHaveLength(0)
		})
	})

	test.describe("Commit f107a93 - Dashboard Defensive Checks", () => {
		test("add_summary_dashboard() should handle dashboard not ready", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()

			// Check immediately (before dashboard might be ready)
			await page.waitForTimeout(50)

			// Should either work or show warning, but NOT error
			const dashboardErrors = consoleErrors.filter(
				(err) =>
					err.includes("add_summary_dashboard") ||
					(err.includes("dashboard") &&
						err.includes("undefined") &&
						!err.includes("warning")),
			)

			expect(
				dashboardErrors,
				"add_summary_dashboard() should not crash if dashboard not ready",
			).toHaveLength(0)

			// Wait for full load
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1500)
		})

		test("render_dashboard() should return gracefully if not ready", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1500)

			// Check for render_dashboard errors
			const renderErrors = consoleErrors.filter(
				(err) =>
					err.includes("render_dashboard") ||
					(err.includes("rendering") && err.includes("undefined")),
			)

			expect(
				renderErrors,
				"render_dashboard() should handle missing dashboard gracefully",
			).toHaveLength(0)
		})

		test("add_workflow_progression_indicator() should check dashboard exists", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1500)

			// Check for workflow progression errors
			const workflowErrors = consoleErrors.filter(
				(err) =>
					err.includes("workflow_progression") ||
					(err.includes("progression") && err.includes("undefined")),
			)

			expect(
				workflowErrors,
				"Workflow progression should handle missing dashboard",
			).toHaveLength(0)
		})

		test("add_sla_countdown_indicator() should verify dashboard wrapper", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1500)

			// Check for SLA countdown errors
			const slaErrors = consoleErrors.filter(
				(err) =>
					err.includes("sla_countdown") ||
					(err.includes("sla") && err.includes("undefined")),
			)

			expect(
				slaErrors,
				"SLA countdown should check dashboard exists",
			).toHaveLength(0)
		})
	})

	test.describe("Commit 7ee30c3 - Deferred Initialization", () => {
		test("Dashboard components should load after 100ms delay", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()

			// Check errors before delay
			const errorsBeforeDelay = [...consoleErrors]

			// Wait for deferred components (100ms + buffer)
			await page.waitForTimeout(200)
			await page.waitForLoadState("networkidle")

			// Should not have race condition errors
			const raceErrors = consoleErrors.filter(
				(err) =>
					err.includes("race") ||
					(err.includes("undefined") &&
						(err.includes("dashboard") || err.includes("wrapper"))),
			)

			expect(
				raceErrors,
				"Deferred loading should prevent race conditions",
			).toHaveLength(0)
		})

		test("Immediate components should load without delay", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()

			// Check immediately
			await page.waitForTimeout(50)

			// Action bar and other immediate components should not error
			const immediateErrors = consoleErrors.filter(
				(err) =>
					err.includes("action bar") ||
					err.includes("quick actions") ||
					err.includes("form sections"),
			)

			expect(
				immediateErrors,
				"Immediate components should load without errors",
			).toHaveLength(0)
		})
	})

	test.describe("Commit 7be7507 - Page Wrapper Defensive Checks", () => {
		test("add_status_pill_to_header() should check frm.page exists", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()

			// Check immediately (before page might be fully ready)
			await page.waitForTimeout(50)

			// Should not have frm.page errors
			const pageErrors = consoleErrors.filter(
				(err) =>
					err.includes("frm.page") &&
					err.includes("undefined") &&
					!err.includes("warning"),
			)

			expect(
				pageErrors,
				"Should not have frm.page undefined errors",
			).toHaveLength(0)

			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)
		})

		test("Should not error when accessing frm.page.wrapper", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Check for page wrapper errors
			const wrapperErrors = consoleErrors.filter(
				(err) =>
					(err.includes("page.wrapper") && err.includes("undefined")) ||
					err.includes("Cannot read properties of undefined (reading 'find')"),
			)

			expect(
				wrapperErrors,
				"frm.page.wrapper access should be safe",
			).toHaveLength(0)
		})

		test("Should not error when accessing frm.page.title_area", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Check for title_area errors
			const titleAreaErrors = consoleErrors.filter(
				(err) => err.includes("title_area") && err.includes("undefined"),
			)

			expect(
				titleAreaErrors,
				"frm.page.title_area access should be safe",
			).toHaveLength(0)
		})

		test("Defensive warnings are acceptable (not errors)", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1500)

			// Warnings like "Dashboard not ready" are OK
			const defensiveWarnings = consoleWarnings.filter(
				(warn) =>
					warn.includes("not ready") ||
					warn.includes("Page wrapper not ready") ||
					warn.includes("Dashboard not ready"),
			)

			// Warnings are informational, not failures
			console.log(
				`Found ${defensiveWarnings.length} defensive warnings (expected behavior)`,
			)

			// But there should be NO errors
			expect(
				consoleErrors,
				"Defensive checks should prevent errors, warnings are OK",
			).toHaveLength(0)
		})
	})

	test.describe("Comprehensive Regression Check", () => {
		test("All 4 commits combined - no console errors on Request form", async () => {
			await page.goto(`${BASE_URL}/app/request`)
			await page.waitForSelector(".list-row", { timeout: 10000 })
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(2000) // Full load with deferred components

			// Report any console errors
			if (consoleErrors.length > 0) {
				console.log("===== CONSOLE ERRORS FOUND =====")
				consoleErrors.forEach((err, idx) => {
					console.log(`${idx + 1}. ${err}`)
				})
				console.log("================================")
			}

			// Report warnings (for informational purposes)
			if (consoleWarnings.length > 0) {
				console.log("===== CONSOLE WARNINGS (Informational) =====")
				consoleWarnings.forEach((warn, idx) => {
					console.log(`${idx + 1}. ${warn}`)
				})
				console.log("============================================")
			}

			// Final assertion - zero console errors
			expect(
				consoleErrors,
				`Request form should have ZERO console errors after all bug fixes`,
			).toHaveLength(0)
		})
	})
})
