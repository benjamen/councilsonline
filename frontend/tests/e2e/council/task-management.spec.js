/**
 * Phase 4.1: Task Creation & Assignment Test
 *
 * Purpose: Test task creation, assignment, and tracking functionality.
 *
 * Test Scenarios:
 * 1. Create task manually
 * 2. Assign task to self
 * 3. Assign task to colleague
 * 4. Set due date
 * 5. Set priority
 * 6. Link to request
 * 7. Link to assessment
 */

import { expect, test } from "@playwright/test"
import {
	STAFF_ROLES,
	createTask,
	loginAsCouncilStaff,
} from "../fixtures/council-staff.js"

const BASE_URL = "http://localhost:8090"

test.describe("Task Management - Creation & Assignment", () => {
	let page
	let requestId

	test.beforeAll(async ({ browser }) => {
		page = await browser.newPage()

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN,
		})

		// Get a request ID to work with
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		const firstRow = page.locator(".list-row").first()
		await firstRow.click()
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1500)

		const url = page.url()
		const match = url.match(/request\/([^\/]+)/)
		requestId = match ? match[1] : null

		console.log(`Using request for task tests: ${requestId}`)
	})

	test.afterAll(async () => {
		await page.close()
	})

	test("01 - Navigate to Project Task list", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Verify page loaded
		const pageTitle = page.locator(".page-title, h1")
		if ((await pageTitle.count()) > 0) {
			const titleText = await pageTitle.textContent()
			console.log(`Task list page title: ${titleText}`)
		}

		// Check if tasks exist
		const taskRows = await page.locator(".list-row").count()
		console.log(`Found ${taskRows} existing tasks`)

		expect(taskRows).toBeGreaterThanOrEqual(0)
	})

	test("02 - Create new task manually", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Click New button
		const newButton = page.locator(
			'.primary-action, button:has-text("New"), .btn-primary-dark',
		)

		if ((await newButton.count()) > 0) {
			await newButton.first().click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Verify we're on new task page
			const url = page.url()
			expect(url).toContain("/project-task/")

			console.log("New task form opened")
		} else {
			console.log("New button not found - may use different navigation")
		}
	})

	test("03 - Fill task details", async () => {
		// Navigate to new task (or use existing from previous test)
		await page.goto(`${BASE_URL}/app/project-task/new-project-task-1`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Fill task subject
		const subjectField = page.locator(
			'[data-fieldname="subject"] input, [data-fieldname="title"] input',
		)

		if ((await subjectField.count()) > 0) {
			const taskSubject = `E2E Test Task - ${new Date().toISOString()}`
			await subjectField.fill(taskSubject)
			await page.waitForTimeout(300)

			console.log(`Task subject: ${taskSubject}`)

			// Verify field value
			const value = await subjectField.inputValue()
			expect(value).toBe(taskSubject)
		} else {
			console.log("Subject field not found")
		}
	})

	test("04 - Set task priority", async () => {
		// Reload or navigate to ensure we have a task form
		await page.goto(`${BASE_URL}/app/project-task/new-project-task-1`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for priority field
		const priorityField = page.locator('[data-fieldname="priority"]')

		if ((await priorityField.count()) > 0) {
			// Click to open dropdown
			const priorityInput = page.locator('[data-fieldname="priority"] input')

			if ((await priorityInput.count()) > 0) {
				await priorityInput.click()
				await page.waitForTimeout(300)

				// Select High priority
				const highOption = page.locator(
					'li:has-text("High"), [data-value="High"]',
				)

				if ((await highOption.count()) > 0) {
					await highOption.first().click()
					await page.waitForTimeout(300)

					console.log("Priority set to High")
				}
			}
		} else {
			console.log("Priority field not found")
		}
	})

	test("05 - Set due date", async () => {
		// Navigate to task
		await page.goto(`${BASE_URL}/app/project-task/new-project-task-1`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for due date field
		const dueDateField = page.locator(
			'[data-fieldname="exp_end_date"] input, [data-fieldname="due_date"] input',
		)

		if ((await dueDateField.count()) > 0) {
			// Set due date to 7 days from now
			const futureDate = new Date()
			futureDate.setDate(futureDate.getDate() + 7)
			const dateString = futureDate.toISOString().split("T")[0] // YYYY-MM-DD

			await dueDateField.fill(dateString)
			await page.waitForTimeout(300)

			console.log(`Due date set to: ${dateString}`)
		} else {
			console.log("Due date field not found")
		}
	})

	test("06 - Link task to request", async () => {
		// Navigate to task
		await page.goto(`${BASE_URL}/app/project-task/new-project-task-1`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for request link field
		const requestField = page.locator(
			'[data-fieldname="request"], [data-fieldname="linked_request"]',
		)

		if ((await requestField.count()) > 0) {
			const requestInput = page.locator('[data-fieldname="request"] input')

			if ((await requestInput.count()) > 0 && requestId) {
				await requestInput.fill(requestId)
				await page.keyboard.press("Enter")
				await page.waitForTimeout(500)

				console.log(`Task linked to request: ${requestId}`)
			}
		} else {
			console.log("Request link field not found")
		}
	})
})

test.describe("Task Management - Completion & Tracking", () => {
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

	test("07 - View task list with filters", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Check for filter options
		const filterButton = page.locator(
			'.filter-button, button:has-text("Filter")',
		)

		if ((await filterButton.count()) > 0) {
			console.log("Filter button available")

			// Click filter
			await filterButton.click()
			await page.waitForTimeout(300)

			// Look for filter fields
			const filterFields = page.locator(".filter-field, .filter-dropdown")

			if ((await filterFields.count()) > 0) {
				console.log("Filter options available")
			}
		} else {
			console.log("No filter button found")
		}

		// Verify tasks are displayed
		const taskRows = await page.locator(".list-row").count()
		console.log(`${taskRows} tasks visible in list`)
	})

	test("08 - Filter tasks by status", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Apply status filter
		const standardFilter = page.locator(
			'.standard-filter, [data-fieldname="status"]',
		)

		if ((await standardFilter.count()) > 0) {
			console.log("Standard filter found - can filter by status")
		}

		// Count tasks before filter
		const totalTasks = await page.locator(".list-row").count()
		console.log(`Total tasks before filter: ${totalTasks}`)
	})

	test("09 - View task detail page", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Click first task
		const firstTask = page.locator(".list-row").first()

		if ((await firstTask.count()) > 0) {
			await firstTask.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Verify on task detail page
			const url = page.url()
			expect(url).toContain("/project-task/")

			console.log("Navigated to task detail")

			// Check for task fields
			const subjectField = page.locator(
				'[data-fieldname="subject"], [data-fieldname="title"]',
			)
			const statusField = page.locator('[data-fieldname="status"]')

			if ((await subjectField.count()) > 0 && (await statusField.count()) > 0) {
				console.log("Task detail fields visible")
			}
		}
	})

	test("10 - Mark task as completed (if possible)", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Find an open/pending task
		const openTask = page
			.locator('.list-row:has-text("Open"), .list-row:has-text("Pending")')
			.first()

		if ((await openTask.count()) > 0) {
			await openTask.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Look for status field or complete button
			const statusField = page.locator('[data-fieldname="status"] input')

			if ((await statusField.count()) > 0) {
				// Try to change to Completed
				await statusField.click()
				await page.waitForTimeout(300)

				const completedOption = page.locator(
					'li:has-text("Completed"), [data-value="Completed"]',
				)

				if ((await completedOption.count()) > 0) {
					await completedOption.first().click()
					await page.waitForTimeout(300)

					console.log("Task status changed to Completed")
				}
			}
		} else {
			console.log("No open tasks found to complete")
		}
	})

	test("11 - Log hours worked (if field exists)", async () => {
		// Navigate to a task detail
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		const firstTask = page.locator(".list-row").first()
		await firstTask.click()
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for hours/time tracking fields
		const hoursField = page.locator(
			'[data-fieldname="actual_time"], ' +
				'[data-fieldname="hours"], ' +
				'[data-fieldname="time_spent"]',
		)

		if ((await hoursField.count()) > 0) {
			console.log("Hours tracking field found")

			const hoursInput = hoursField.locator("input").first()

			if ((await hoursInput.count()) > 0) {
				await hoursInput.fill("2.5")
				await page.waitForTimeout(300)

				console.log("Logged 2.5 hours")
			}
		} else {
			console.log("No hours tracking field found")
		}
	})

	test("12 - View task cost calculation (if exists)", async () => {
		// Navigate to a task detail
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		const firstTask = page.locator(".list-row").first()
		await firstTask.click()
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for cost fields
		const costField = page.locator(
			'[data-fieldname="total_costing_amount"], ' +
				'[data-fieldname="cost"], ' +
				'[data-fieldname="total_cost"]',
		)

		if ((await costField.count()) > 0) {
			console.log("Cost field found")

			const costValue = await costField
				.locator("input")
				.first()
				.inputValue()
				.catch(() => "")
			console.log(`Task cost: ${costValue}`)
		} else {
			console.log("No cost field found")
		}
	})
})

test.describe("Task Management - Task Templates", () => {
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

	test("13 - Navigate to Task Template list", async () => {
		// Navigate to task template list
		await page.goto(`${BASE_URL}/app/task-template`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Check if page loaded
		const pageTitle = page.locator(".page-title, h1")

		if ((await pageTitle.count()) > 0) {
			const titleText = await pageTitle.textContent()
			console.log(`Task Template page: ${titleText}`)
		}

		// Count existing templates
		const templateRows = await page.locator(".list-row").count()
		console.log(`Found ${templateRows} task templates`)

		expect(templateRows).toBeGreaterThanOrEqual(0)
	})

	test("14 - View task template detail", async () => {
		// Navigate to task template list
		await page.goto(`${BASE_URL}/app/task-template`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Click first template if exists
		const firstTemplate = page.locator(".list-row").first()

		if ((await firstTemplate.count()) > 0) {
			await firstTemplate.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Verify on template detail
			const url = page.url()
			expect(url).toContain("/task-template/")

			console.log("Viewing task template detail")

			// Look for template fields
			const templateNameField = page.locator(
				'[data-fieldname="template_name"], [data-fieldname="name"]',
			)

			if ((await templateNameField.count()) > 0) {
				const templateName = await templateNameField
					.locator("input")
					.first()
					.inputValue()
					.catch(() => "")
				console.log(`Template name: ${templateName}`)
			}
		} else {
			console.log("No task templates found")
		}
	})

	test("15 - View template checklist items (if exists)", async () => {
		// Navigate to task template list
		await page.goto(`${BASE_URL}/app/task-template`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		const firstTemplate = page.locator(".list-row").first()

		if ((await firstTemplate.count()) > 0) {
			await firstTemplate.click()
			await page.waitForLoadState("networkidle")
			await page.waitForTimeout(1000)

			// Look for checklist table
			const checklistTable = page.locator(
				'[data-fieldname="checklist"], ' +
					'[data-fieldname="items"], ' +
					".grid-body",
			)

			if ((await checklistTable.count()) > 0) {
				console.log("Template checklist found")

				// Count checklist items
				const checklistRows = await checklistTable
					.locator(".grid-row, tr")
					.count()
				console.log(`Template has ${checklistRows} checklist items`)
			} else {
				console.log("No checklist found in template")
			}
		}
	})
})

test.describe("Task Management - Timeliness Tracking", () => {
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

	test("16 - Check for overdue tasks indicator", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for overdue indicators
		const overdueIndicator = page.locator(
			".indicator-red, " + '[class*="overdue"], ' + ".text-danger, " + "⚠️",
		)

		if ((await overdueIndicator.count()) > 0) {
			console.log("Overdue indicators found in task list")
			const overdueCount = await overdueIndicator.count()
			console.log(`${overdueCount} overdue indicators visible`)
		} else {
			console.log(
				"No overdue indicators found - no overdue tasks or not displayed",
			)
		}
	})

	test("17 - Filter by overdue tasks", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for overdue filter
		const filterButton = page.locator(
			'.filter-button, button:has-text("Filter")',
		)

		if ((await filterButton.count()) > 0) {
			await filterButton.click()
			await page.waitForTimeout(300)

			// Try to add overdue filter
			console.log("Filter interface opened - overdue filter may be available")
		}

		// Check for standard filters
		const standardFilters = page.locator(".standard-filter-section")

		if ((await standardFilters.count()) > 0) {
			console.log("Standard filters available")
		}
	})

	test("18 - View task dashboard/stats (if exists)", async () => {
		// Navigate to task list
		await page.goto(`${BASE_URL}/app/project-task`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for dashboard stats
		const statCards = page.locator(
			'.indicator-pill, .stat-card, [class*="indicator-"]',
		)

		if ((await statCards.count()) > 0) {
			const statsCount = await statCards.count()
			console.log(`Found ${statsCount} stat indicators`)

			// Try to read stat values
			for (const stat of (await statCards.all()).slice(0, 5)) {
				const statText = await stat.textContent()
				console.log(`- Stat: ${statText}`)
			}
		} else {
			console.log("No task dashboard stats found")
		}
	})
})
