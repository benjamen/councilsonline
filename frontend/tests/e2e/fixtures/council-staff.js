/**
 * Council Staff Test Fixtures
 *
 * Reusable utilities for council staff operations in E2E tests.
 * Provides functions for user management, authentication, request operations,
 * and workflow transitions.
 */

import { login } from "./auth.js"

const BASE_URL = process.env.BASE_URL || "http://localhost:8090"

/**
 * Council staff role types
 */
export const STAFF_ROLES = {
	PLANNER: "Planner",
	MANAGER: "Council Manager",
	ADMIN: "Administrator",
	INSPECTOR: "Building Inspector",
}

/**
 * Create a council staff user for testing
 *
 * @param {Object} page - Playwright page object
 * @param {Object} options - User creation options
 * @param {string} options.role - Staff role (Planner, Manager, Admin, Inspector)
 * @param {string} options.email - User email (optional, auto-generated if not provided)
 * @param {string} options.firstName - First name (optional)
 * @param {string} options.lastName - Last name (optional)
 * @param {string} options.council - Council code (optional, defaults to 'AKL')
 * @returns {Object} Created user details { email, password, fullName, role }
 */
export async function createCouncilStaffer(page, options = {}) {
	const {
		role = STAFF_ROLES.PLANNER,
		email = `test.${role.toLowerCase().replace(" ", ".")}@council.test`,
		firstName = "Test",
		lastName = role,
		council = "AKL",
	} = options

	console.log(`[CouncilStaff] Creating ${role} user: ${email}`)

	// Login as Administrator to create users
	await login(page, {
		username: "Administrator",
		password: "admin123",
		baseUrl: BASE_URL,
	})

	// Navigate to User List
	await page.goto(`${BASE_URL}/app/user`)
	await page.waitForLoadState("networkidle")

	// Click New User button
	await page.click(".primary-action")
	await page.waitForLoadState("networkidle")

	// Fill user details
	await page.fill('input[data-fieldname="email"]', email)
	await page.fill('input[data-fieldname="first_name"]', firstName)
	await page.fill('input[data-fieldname="last_name"]', lastName)

	// Add role
	await page.click('[data-fieldname="roles"] .grid-add-row')
	await page.waitForTimeout(500)
	await page.fill('[data-fieldname="role"] input', role)
	await page.keyboard.press("Enter")

	// Set password
	const password = "test123"
	await page.fill('input[data-fieldname="new_password"]', password)

	// Save user
	await page.click(".primary-action")
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	const fullName = `${firstName} ${lastName}`
	console.log(`[CouncilStaff] Created user: ${fullName} (${role})`)

	return {
		email,
		password,
		fullName,
		role,
		council,
	}
}

/**
 * Login as council staff with specific role
 *
 * @param {Object} page - Playwright page object
 * @param {Object} options - Login options
 * @param {string} options.role - Staff role (uses pre-created test users)
 * @param {string} options.email - User email (optional, uses default test user if not provided)
 * @param {string} options.password - Password (optional, defaults to 'admin123' for Administrator)
 * @returns {boolean} Login success
 */
export async function loginAsCouncilStaff(page, options = {}) {
	const { role = STAFF_ROLES.PLANNER, email = null, password = null } = options

	// Default credentials based on role
	let username
	let pwd

	if (role === STAFF_ROLES.ADMIN || role === "Administrator") {
		username = email || "Administrator"
		pwd = password || "admin123"
	} else {
		// For other roles, use test user pattern
		username =
			email || `test.${role.toLowerCase().replace(" ", ".")}@council.test`
		pwd = password || "test123"
	}

	console.log(`[CouncilStaff] Logging in as ${role}: ${username}`)

	return await login(page, {
		username: username,
		password: pwd,
		baseUrl: BASE_URL,
	})
}

/**
 * Assign a request to a staff member
 *
 * @param {Object} page - Playwright page object
 * @param {string} requestId - Request ID or name
 * @param {string} staffEmail - Staff member email to assign to
 * @returns {boolean} Assignment success
 */
export async function assignRequestToStaff(page, requestId, staffEmail) {
	console.log(`[CouncilStaff] Assigning request ${requestId} to ${staffEmail}`)

	// Navigate to request
	await page.goto(`${BASE_URL}/app/request/${requestId}`)
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	// Find and fill the assigned_to field
	const assignedToField = page.locator('input[data-fieldname="assigned_to"]')
	await assignedToField.click()
	await assignedToField.fill(staffEmail)
	await page.keyboard.press("Enter")
	await page.waitForTimeout(500)

	// Save the request
	await page.click(".primary-action")
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	console.log(`[CouncilStaff] Request assigned successfully`)
	return true
}

/**
 * Change request workflow status
 *
 * @param {Object} page - Playwright page object
 * @param {string} requestId - Request ID or name
 * @param {string} newStatus - New workflow status
 * @param {string} reason - Reason for status change (optional)
 * @returns {boolean} Status change success
 */
export async function changeRequestStatus(
	page,
	requestId,
	newStatus,
	reason = "",
) {
	console.log(
		`[CouncilStaff] Changing request ${requestId} status to: ${newStatus}`,
	)

	// Navigate to request
	await page.goto(`${BASE_URL}/app/request/${requestId}`)
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1500) // Wait for dashboard/UX components

	// Look for workflow state button or field
	const workflowStateField = page.locator(
		'input[data-fieldname="workflow_state"]',
	)

	if ((await workflowStateField.count()) > 0) {
		// Change via workflow_state field
		await workflowStateField.click()
		await workflowStateField.fill(newStatus)
		await page.keyboard.press("Enter")
		await page.waitForTimeout(500)
	} else {
		// Look for workflow action buttons
		const workflowButton = page.locator(`button:has-text("${newStatus}")`)
		if ((await workflowButton.count()) > 0) {
			await workflowButton.click()
			await page.waitForTimeout(500)
		} else {
			console.warn(
				`[CouncilStaff] Could not find workflow control for status: ${newStatus}`,
			)
			return false
		}
	}

	// If reason dialog appears, fill it
	if (reason) {
		const reasonField = page.locator(
			'textarea[data-fieldname="reason"], input[placeholder*="reason"]',
		)
		if ((await reasonField.count()) > 0) {
			await reasonField.fill(reason)
			await page.click('button.btn-primary:has-text("Submit")')
			await page.waitForTimeout(500)
		}
	}

	// Save the request
	await page.click(".primary-action")
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	console.log(`[CouncilStaff] Status changed successfully to: ${newStatus}`)
	return true
}

/**
 * Get council dashboard statistics
 *
 * @param {Object} page - Playwright page object
 * @returns {Object} Dashboard stats { total, inProgress, pending, completed, rfi, new }
 */
export async function getCouncilDashboardStats(page) {
	console.log(`[CouncilStaff] Fetching council dashboard stats`)

	// Navigate to council dashboard or request list
	await page.goto(`${BASE_URL}/app/request`)
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	const stats = {}

	// Try to extract stats from indicator cards or list stats
	const indicators = await page
		.locator('.indicator, .stat-card, [class*="stat"]')
		.all()

	for (const indicator of indicators) {
		const text = await indicator.textContent()

		// Parse different stat formats
		if (text.includes("Total")) {
			const match = text.match(/(\d+)/)
			if (match) stats.total = Number.parseInt(match[1])
		}
		if (text.includes("In Progress") || text.includes("Processing")) {
			const match = text.match(/(\d+)/)
			if (match) stats.inProgress = Number.parseInt(match[1])
		}
		if (text.includes("Pending")) {
			const match = text.match(/(\d+)/)
			if (match) stats.pending = Number.parseInt(match[1])
		}
		if (text.includes("Completed")) {
			const match = text.match(/(\d+)/)
			if (match) stats.completed = Number.parseInt(match[1])
		}
		if (text.includes("RFI")) {
			const match = text.match(/(\d+)/)
			if (match) stats.rfi = Number.parseInt(match[1])
		}
		if (text.includes("New")) {
			const match = text.match(/(\d+)/)
			if (match) stats.new = Number.parseInt(match[1])
		}
	}

	// Fallback: get count from list
	if (!stats.total) {
		const listCount = page.locator(".list-count, .result-count")
		if ((await listCount.count()) > 0) {
			const countText = await listCount.textContent()
			const match = countText.match(/(\d+)/)
			if (match) stats.total = Number.parseInt(match[1])
		}
	}

	console.log(`[CouncilStaff] Dashboard stats:`, stats)
	return stats
}

/**
 * Filter requests with various criteria
 *
 * @param {Object} page - Playwright page object
 * @param {Object} filters - Filter criteria
 * @param {string} filters.status - Filter by status (e.g., "Processing", "Pending Decision")
 * @param {string} filters.requestType - Filter by request type (e.g., "RC", "BC", "SPISC")
 * @param {string} filters.assignedTo - Filter by assigned staff
 * @param {string} filters.search - Search text (applicant name, property address, etc.)
 * @param {string} filters.council - Filter by council code
 * @returns {number} Number of filtered results
 */
export async function filterRequests(page, filters = {}) {
	console.log(`[CouncilStaff] Applying filters:`, filters)

	// Ensure we're on the request list page
	const currentUrl = page.url()
	if (!currentUrl.includes("/app/request")) {
		await page.goto(`${BASE_URL}/app/request`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)
	}

	// Apply search filter
	if (filters.search) {
		const searchBox = page.locator(
			'.search-input, input[type="search"], .list-search',
		)
		await searchBox.fill(filters.search)
		await page.keyboard.press("Enter")
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(500)
	}

	// Apply status filter
	if (filters.status) {
		// Look for filter button or dropdown
		const filterButton = page.locator(
			'.filter-button, button:has-text("Filter")',
		)
		if ((await filterButton.count()) > 0) {
			await filterButton.click()
			await page.waitForTimeout(300)

			// Select status field
			await page.click("text=Status")
			await page.waitForTimeout(200)

			// Enter status value
			await page.fill(".filter-value input", filters.status)
			await page.keyboard.press("Enter")
			await page.waitForTimeout(500)
		}
	}

	// Apply request type filter
	if (filters.requestType) {
		const filterButton = page.locator(
			'.filter-button, button:has-text("Filter")',
		)
		if ((await filterButton.count()) > 0) {
			await filterButton.click()
			await page.waitForTimeout(300)

			await page.click("text=Request Type")
			await page.waitForTimeout(200)

			await page.fill(".filter-value input", filters.requestType)
			await page.keyboard.press("Enter")
			await page.waitForTimeout(500)
		}
	}

	// Apply assigned to filter
	if (filters.assignedTo) {
		const filterButton = page.locator(
			'.filter-button, button:has-text("Filter")',
		)
		if ((await filterButton.count()) > 0) {
			await filterButton.click()
			await page.waitForTimeout(300)

			await page.click("text=Assigned To")
			await page.waitForTimeout(200)

			await page.fill(".filter-value input", filters.assignedTo)
			await page.keyboard.press("Enter")
			await page.waitForTimeout(500)
		}
	}

	// Wait for filter results
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1000)

	// Get result count
	const listRows = await page.locator(".list-row").count()

	console.log(`[CouncilStaff] Filter applied, ${listRows} results found`)
	return listRows
}

/**
 * Create a task for a request
 *
 * @param {Object} page - Playwright page object
 * @param {string} requestId - Request ID
 * @param {Object} taskData - Task data
 * @param {string} taskData.subject - Task subject/title
 * @param {string} taskData.description - Task description
 * @param {string} taskData.assignedTo - Assigned staff email
 * @param {string} taskData.dueDate - Due date (YYYY-MM-DD)
 * @param {string} taskData.priority - Priority (Low/Medium/High)
 * @returns {string} Created task ID
 */
export async function createTask(page, requestId, taskData = {}) {
	const {
		subject = "Test Task",
		description = "Task created by E2E test",
		assignedTo = null,
		dueDate = null,
		priority = "Medium",
	} = taskData

	console.log(
		`[CouncilStaff] Creating task for request ${requestId}: ${subject}`,
	)

	// Navigate to request
	await page.goto(`${BASE_URL}/app/request/${requestId}`)
	await page.waitForLoadState("networkidle")
	await page.waitForTimeout(1500)

	// Look for "Add Task" button or similar
	const addTaskButton = page.locator(
		'button:has-text("Add Task"), button:has-text("New Task")',
	)

	if ((await addTaskButton.count()) > 0) {
		await addTaskButton.click()
		await page.waitForTimeout(500)

		// Fill task form
		await page.fill('input[data-fieldname="subject"]', subject)

		if (description) {
			await page.fill('textarea[data-fieldname="description"]', description)
		}

		if (assignedTo) {
			await page.fill('input[data-fieldname="assigned_to"]', assignedTo)
			await page.keyboard.press("Enter")
			await page.waitForTimeout(300)
		}

		if (dueDate) {
			await page.fill('input[data-fieldname="due_date"]', dueDate)
		}

		if (priority) {
			await page.click(`input[data-fieldname="priority"]`)
			await page.click(`li:has-text("${priority}")`)
		}

		// Save task
		await page.click(
			'button.btn-primary:has-text("Save"), button.primary-action',
		)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		console.log(`[CouncilStaff] Task created successfully`)

		// Get task ID from URL
		const url = page.url()
		const taskIdMatch = url.match(/project-task\/([^\/]+)/)
		return taskIdMatch ? taskIdMatch[1] : null
	}

	console.warn(`[CouncilStaff] Could not find Add Task button`)
	return null
}

/**
 * Wait for assessment project to be created
 *
 * @param {Object} page - Playwright page object
 * @param {string} requestId - Request ID
 * @param {number} timeout - Max wait time in ms (default 10000)
 * @returns {boolean} Assessment project found
 */
export async function waitForAssessmentProject(
	page,
	requestId,
	timeout = 10000,
) {
	console.log(
		`[CouncilStaff] Waiting for assessment project for request ${requestId}`,
	)

	const startTime = Date.now()

	while (Date.now() - startTime < timeout) {
		await page.goto(`${BASE_URL}/app/request/${requestId}`)
		await page.waitForLoadState("networkidle")
		await page.waitForTimeout(1000)

		// Look for assessment project link or section
		const assessmentLink = page.locator(
			'a[href*="assessment-project"], [data-fieldname="assessment_project"]',
		)

		if ((await assessmentLink.count()) > 0) {
			console.log(`[CouncilStaff] Assessment project found`)
			return true
		}

		await page.waitForTimeout(1000)
	}

	console.warn(`[CouncilStaff] Assessment project not found after ${timeout}ms`)
	return false
}
