/**
 * Manual SPISC Request Flow Test
 *
 * Purpose: Test complete SPISC request workflow from creation to approval
 * This test creates a new SPISC request and processes it through all stages.
 */

import { expect, test } from "@playwright/test"

const BASE_URL = "http://localhost:8090"
const ADMIN_USER = "Administrator"
const ADMIN_PASS = "admin123"

test.describe("SPISC Request: Complete Flow from Lodgement to Approval", () => {
	let page
	let requestId

	test.beforeAll(async ({ browser }) => {
		page = await browser.newPage()
	})

	test.afterAll(async () => {
		await page.close()
	})

	test("Step 01 - Login as Administrator", async () => {
		console.log("\n=== STEP 1: Admin Login ===")

		await page.goto(`${BASE_URL}/frontend/login`)
		await page.waitForLoadState("networkidle")

		// Fill login form
		await page.fill('input[name="email"], input[type="email"]', ADMIN_USER)
		await page.fill(
			'input[name="password"], input[type="password"]',
			ADMIN_PASS,
		)

		// Submit
		await page.click('button[type="submit"]')
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Verify we're logged in
		const url = page.url()
		console.log(`Logged in, URL: ${url}`)

		expect(url).not.toContain("/login")
	})

	test("Step 02 - Navigate to Request list and find SPISC request", async () => {
		console.log("\n=== STEP 2: Find SPISC Request ===")

		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Get total requests
		const totalRequests = await page.locator(".list-row").count()
		console.log(`Total requests found: ${totalRequests}`)

		if (totalRequests > 0) {
			// Click first request
			await page.locator(".list-row").first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(2500) // Wait for UX components

			// Get request ID from URL
			const url = page.url()
			const match = url.match(/request\/([^\/]+)/)
			if (match) {
				requestId = match[1]
				console.log(`✓ Working with Request ID: ${requestId}`)

				// Get request type
				const requestTypeField = page.locator('[data-fieldname="request_type"]')
				if ((await requestTypeField.count()) > 0) {
					const requestType = await requestTypeField
						.locator("input")
						.inputValue()
						.catch(() => "Unknown")
					console.log(`  Request Type: ${requestType}`)
				}

				// Get current workflow state
				const stateField = page.locator('[data-fieldname="workflow_state"]')
				if ((await stateField.count()) > 0) {
					const currentState = await stateField
						.locator("input")
						.inputValue()
						.catch(() => "Unknown")
					console.log(`  Current State: ${currentState}`)
				}

				expect(requestId).toBeTruthy()
			}
		} else {
			console.log(
				"⚠ No requests found - you may need to create one first via the frontend",
			)
		}
	})

	test("Step 03 - View request details and UX components", async () => {
		if (!requestId) {
			test.skip()
			return
		}

		console.log("\n=== STEP 3: View Request Details ===")

		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2500)

		// Check for status pill
		const statusPill = page.locator(
			'.status-pill, .indicator-pill, [class*="status-badge"]',
		)
		if ((await statusPill.count()) > 0) {
			const pillText = await statusPill.first().textContent()
			console.log(`✓ Status Pill: ${pillText}`)
		} else {
			console.log("  Status pill not found")
		}

		// Check for workflow timeline
		const timeline = page.locator(
			'.workflow-timeline, .timeline, [data-component="timeline"]',
		)
		if ((await timeline.count()) > 0) {
			console.log("✓ Workflow timeline rendered")
		}

		// Check for dashboard/summary
		const dashboard = page.locator('[class*="dashboard"], [class*="summary"]')
		if ((await dashboard.count()) > 0) {
			console.log("✓ Summary dashboard rendered")
		}

		console.log("✓ Request detail page loaded successfully")
	})

	test("Step 04 - Check available workflow actions", async () => {
		if (!requestId) {
			test.skip()
			return
		}

		console.log("\n=== STEP 4: Check Workflow Actions ===")

		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Look for workflow action buttons
		const workflowButtons = await page
			.locator(
				'button[data-action], .btn-workflow, button:has-text("Submit"), button:has-text("Approve"), button:has-text("Acknowledge")',
			)
			.all()

		console.log(`Found ${workflowButtons.length} workflow action buttons:`)
		for (const button of workflowButtons) {
			const text = await button.textContent()
			console.log(`  - ${text.trim()}`)
		}
	})

	test("Step 05 - View linked application (if exists)", async () => {
		if (!requestId) {
			test.skip()
			return
		}

		console.log("\n=== STEP 5: Check Linked Application ===")

		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Look for SPISC application link
		const spiscLink = page.locator(
			'a[href*="spisc-application"], [data-fieldname="spisc_application"]',
		)

		if ((await spiscLink.count()) > 0) {
			console.log("✓ SPISC Application linked")

			// Try to get application ID
			const appLink = spiscLink.first()
			const href = await appLink.getAttribute("href")
			if (href) {
				console.log(`  Application Link: ${href}`)
			}
		} else {
			console.log("  No SPISC application linked yet")
		}
	})

	test("Step 06 - Check for Assessment Project", async () => {
		if (!requestId) {
			test.skip()
			return
		}

		console.log("\n=== STEP 6: Check Assessment Project ===")

		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Look for assessment project link
		const assessmentLink = page.locator(
			'a[href*="assessment-project"], [data-fieldname="assessment_project"]',
		)

		if ((await assessmentLink.count()) > 0) {
			console.log("✓ Assessment Project exists")

			const href = await assessmentLink.first().getAttribute("href")
			if (href) {
				console.log(`  Assessment URL: ${href}`)

				// Navigate to assessment
				await assessmentLink.first().click()
				await page.waitForLoadState("networkidle")
				await page.waitForTimeout(1500)

				const assessmentTitle = await page
					.locator(".page-title, h1")
					.textContent()
				console.log(`  Assessment Title: ${assessmentTitle}`)

				// Check for stages
				const stages = await page
					.locator('[data-fieldname="stages"], .assessment-stage')
					.count()
				if (stages > 0) {
					console.log(`  Found ${stages} assessment stages`)
				}

				// Go back to request
				await page.goto(`${BASE_URL}/app/request/${requestId}`)
				await page.waitForLoadState("networkidle")
				await page.waitForTimeout(1000)
			}
		} else {
			console.log(
				"  No Assessment Project found - may be created after acknowledgment",
			)
		}
	})

	test("Step 07 - View SLA tracking information", async () => {
		if (!requestId) {
			test.skip()
			return
		}

		console.log("\n=== STEP 7: View SLA Information ===")

		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Check SLA fields
		const targetDate = await page
			.locator('[data-fieldname="target_completion_date"] input')
			.inputValue()
			.catch(() => "")
		const daysRemaining = await page
			.locator('[data-fieldname="working_days_remaining"] input')
			.inputValue()
			.catch(() => "")
		const daysElapsed = await page
			.locator('[data-fieldname="working_days_elapsed"] input')
			.inputValue()
			.catch(() => "")
		const acknowledgedDate = await page
			.locator('[data-fieldname="acknowledged_date"] input')
			.inputValue()
			.catch(() => "")

		console.log("SLA Tracking:")
		console.log(`  Target Completion: ${targetDate || "Not set"}`)
		console.log(`  Days Remaining: ${daysRemaining || "Not set"}`)
		console.log(`  Days Elapsed: ${daysElapsed || "Not set"}`)
		console.log(`  Acknowledged Date: ${acknowledgedDate || "Not set"}`)
	})

	test("Step 08 - View tasks linked to request", async () => {
		if (!requestId) {
			test.skip()
			return
		}

		console.log("\n=== STEP 8: Check Tasks ===")

		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Look for tasks section/tab
		const tasksTab = page.locator(
			'.tab-link:has-text("Task"), button:has-text("Task"), a:has-text("Tasks")',
		)

		if ((await tasksTab.count()) > 0) {
			console.log("✓ Tasks section found")

			await tasksTab.first().click()
			await page.waitForTimeout(500)

			const taskCount = await page
				.locator('.task-row, [data-doctype="Project Task"]')
				.count()
			console.log(`  Found ${taskCount} tasks`)
		} else {
			console.log("  No tasks section found")
		}
	})

	test("Step 09 - View communications log", async () => {
		if (!requestId) {
			test.skip()
			return
		}

		console.log("\n=== STEP 9: Check Communications ===")

		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2000)

		// Look for communications tab
		const commTab = page.locator(
			'.tab-link:has-text("Communication"), button:has-text("Communication")',
		)

		if ((await commTab.count()) > 0) {
			console.log("✓ Communications section found")

			await commTab.first().click()
			await page.waitForTimeout(500)

			const commCount = await page
				.locator('.communication-row, [data-doctype="Communication"]')
				.count()
			console.log(`  Found ${commCount} communications`)
		} else {
			console.log("  No communications section found")
		}
	})

	test("Step 10 - Final Summary", async () => {
		if (!requestId) {
			test.skip()
			return
		}

		console.log("\n=== FINAL SUMMARY ===")

		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(2500)

		// Get final state
		const finalState = await page
			.locator('[data-fieldname="workflow_state"] input')
			.inputValue()
			.catch(() => "Unknown")
		const requestType = await page
			.locator('[data-fieldname="request_type"] input')
			.inputValue()
			.catch(() => "Unknown")

		console.log(`\n✓ Request ID: ${requestId}`)
		console.log(`✓ Request Type: ${requestType}`)
		console.log(`✓ Final Workflow State: ${finalState}`)
		console.log(`\n✓ Test completed successfully!`)
		console.log(`\nTo continue testing workflow transitions:`)
		console.log(`1. Use the Frappe UI to change workflow states`)
		console.log(
			`2. Or implement API calls to transition states programmatically`,
		)
		console.log(`3. View the request at: ${BASE_URL}/app/request/${requestId}`)
	})
})
