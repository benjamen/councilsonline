/**
 * SPISC Test Helper Functions
 *
 * Reusable utilities for SPISC application E2E testing
 */

const BASE_URL = 'http://localhost:8090';

/**
 * Find the latest submitted SPISC application
 * @param {Page} page - Playwright page object
 * @returns {Promise<string>} - SPISC application ID (e.g., "SPISC-2025-244")
 */
export async function findLatestSPISCApplication(page) {
	console.log('[SPISC Helper] Finding latest SPISC application...');
	await page.goto(`${BASE_URL}/app/spisc-application`);
	await page.waitForLoadState('networkidle');
	await page.waitForTimeout(3000); // Increased wait for list to load

	// Try multiple selectors for list rows
	let firstRow = null;
	let spiscId = null;

	// Try 1: Standard list row container
	const listRows = page.locator('.list-row-container, .list-row, [data-doctype="SPISC Application"]');
	const count = await listRows.count();
	console.log(`[SPISC Helper] Found ${count} list rows with primary selector`);

	if (count > 0) {
		firstRow = listRows.first();
		const rowText = await firstRow.textContent();
		console.log(`[SPISC Helper] First row text: ${rowText.substring(0, 100)}...`);
		const match = rowText.match(/SPISC-2025-\d+/);
		if (match) {
			spiscId = match[0];
			console.log(`[SPISC Helper] Found SPISC Application: ${spiscId}`);
			return spiscId;
		}
	}

	// Try 2: Check if list is empty due to filters
	console.log('[SPISC Helper] Checking if list has filters applied...');
	const clearFilters = page.locator('button:has-text("Clear Filters"), .clear-filters');
	if (await clearFilters.count() > 0) {
		console.log('[SPISC Helper] Clearing filters...');
		await clearFilters.first().click();
		await page.waitForTimeout(2000);

		const rowsAfterClear = page.locator('.list-row-container, .list-row');
		const newCount = await rowsAfterClear.count();
		console.log(`[SPISC Helper] After clearing filters: ${newCount} rows`);

		if (newCount > 0) {
			const rowText = await rowsAfterClear.first().textContent();
			const match = rowText.match(/SPISC-2025-\d+/);
			if (match) {
				spiscId = match[0];
				console.log(`[SPISC Helper] Found SPISC Application after clearing filters: ${spiscId}`);
				return spiscId;
			}
		}
	}

	// Try 3: Check page content for any SPISC IDs
	console.log('[SPISC Helper] Searching page content for SPISC IDs...');
	const pageContent = await page.content();
	const allMatches = pageContent.match(/SPISC-2025-\d+/g);
	if (allMatches && allMatches.length > 0) {
		// Get the highest number (most recent)
		const sorted = allMatches.sort().reverse();
		spiscId = sorted[0];
		console.log(`[SPISC Helper] Found SPISC ID in page content: ${spiscId}`);
		return spiscId;
	}

	// If still nothing found, log more debugging info
	console.log('[SPISC Helper] No SPISC applications found. Debugging info:');
	console.log(`  - Current URL: ${page.url()}`);
	console.log(`  - Page title: ${await page.title()}`);

	// Check for "No data" message
	const noData = page.locator('.no-result, .empty-state, :has-text("No SPISC Application found")');
	if (await noData.count() > 0) {
		console.log('  - List shows "No data" message');
	}

	throw new Error('No SPISC applications found in list');
}

/**
 * Open a SPISC application by ID
 * @param {Page} page - Playwright page object
 * @param {string} spiscId - SPISC application ID
 */
export async function openSPISCApplication(page, spiscId) {
	console.log(`Opening SPISC Application: ${spiscId}`);
	await page.goto(`${BASE_URL}/app/spisc-application/${encodeURIComponent(spiscId)}`);
	await page.waitForLoadState('networkidle');
	await page.waitForTimeout(2000);
}

/**
 * Get the Request ID linked to a SPISC application
 * @param {Page} page - Playwright page object (must be on SPISC Application page)
 * @returns {Promise<string>} - Request ID
 */
export async function getLinkedRequestId(page) {
	const requestField = page.locator('input[data-fieldname="request"]').first();
	const requestId = await requestField.inputValue();
	console.log(`Linked Request ID: ${requestId}`);
	return requestId;
}

/**
 * Navigate to linked Request from SPISC Application
 * @param {Page} page - Playwright page object
 * @param {string} requestId - Request ID
 */
export async function navigateToRequest(page, requestId) {
	console.log(`Navigating to Request: ${requestId}`);
	await page.goto(`${BASE_URL}/app/request/${encodeURIComponent(requestId)}`);
	await page.waitForLoadState('networkidle');
	await page.waitForTimeout(2000);
}

/**
 * Get current workflow state of a request
 * @param {Page} page - Playwright page object (must be on Request page)
 * @returns {Promise<string>} - Current workflow state
 */
export async function getCurrentWorkflowState(page) {
	await page.waitForLoadState('networkidle');
	let state = null;

	// Try 1: workflow_state field input
	try {
		const workflowField = page.locator('[data-fieldname="workflow_state"] input, [data-fieldname="workflow_state"] .control-value').first();
		if (await workflowField.isVisible({ timeout: 2000 })) {
			state = await workflowField.inputValue().catch(async () => {
				// If not an input, try textContent
				return await workflowField.textContent();
			});
		}
	} catch (e) {
		// Continue to next attempt
	}

	// Try 2: status field as fallback
	if (!state || state === '') {
		try {
			const statusField = page.locator('[data-fieldname="status"] input, [data-fieldname="status"] .control-value').first();
			if (await statusField.isVisible({ timeout: 2000 })) {
				state = await statusField.inputValue().catch(async () => {
					return await statusField.textContent();
				});
			}
		} catch (e) {
			// Continue to next attempt
		}
	}

	// Try 3: Check indicator/badge
	if (!state || state === '') {
		try {
			const indicator = page.locator('.indicator-pill, .badge, .status-indicator').first();
			if (await indicator.isVisible({ timeout: 2000 })) {
				state = await indicator.textContent();
			}
		} catch (e) {
			// Continue
		}
	}

	// Clean up state value
	if (state) {
		state = state.trim();
	}

	console.log(`Current Workflow State: ${state || 'Unknown'}`);
	return state || 'Unknown';
}

/**
 * Change workflow state using Actions menu
 * @param {Page} page - Playwright page object (must be on Request page)
 * @param {string} targetState - Target workflow state (e.g., "Acknowledged", "Processing")
 * @returns {Promise<boolean>} - Success status
 */
export async function changeWorkflowState(page, targetState) {
	console.log(`Attempting to change workflow state to: ${targetState}`);

	try {
		// Click Actions button
		const actionsButton = page.locator('button:has-text("Actions")').first();
		if (await actionsButton.isVisible({ timeout: 5000 })) {
			await actionsButton.click();
			await page.waitForTimeout(1000);

			// Look for target state action
			const stateAction = page.locator(`.dropdown-menu.show a:has-text("${targetState}")`).first();
			if (await stateAction.isVisible({ timeout: 2000 })) {
				await stateAction.click();
				await page.waitForTimeout(1000);

				// Handle confirmation dialog if appears
				const confirmButton = page.locator('button.btn-primary:has-text("Yes"), button:has-text("Confirm")').first();
				if (await confirmButton.isVisible({ timeout: 2000 })) {
					await confirmButton.click();
				}

				await page.waitForTimeout(2000);
				console.log(`✓ Workflow state changed to: ${targetState}`);
				return true;
			}
		}

		console.log(`⚠ Workflow action "${targetState}" not available`);
		return false;
	} catch (error) {
		console.error(`Error changing workflow state:`, error.message);
		return false;
	}
}

/**
 * Wait for Assessment Project to be created (polls for up to timeout)
 * @param {Page} page - Playwright page object (must be on Request page)
 * @param {number} timeout - Maximum wait time in ms (default 15000)
 * @returns {Promise<string|null>} - Assessment Project ID or null if not found
 */
export async function waitForAssessmentProject(page, timeout = 15000) {
	console.log('Waiting for Assessment Project creation...');
	const startTime = Date.now();

	while (Date.now() - startTime < timeout) {
		await page.reload();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const assessmentField = page.locator('[data-fieldname="assessment_project"] input').first();
		if (await assessmentField.isVisible()) {
			const assessmentId = await assessmentField.inputValue().catch(() => '');
			if (assessmentId && assessmentId.length > 0) {
				console.log(`✓ Assessment Project created: ${assessmentId}`);
				return assessmentId;
			}
		}

		await page.waitForTimeout(2000);
	}

	console.log('⚠ Assessment Project not created within timeout');
	return null;
}

/**
 * Navigate to Assessment Project
 * @param {Page} page - Playwright page object
 * @param {string} assessmentId - Assessment Project ID
 */
export async function navigateToAssessmentProject(page, assessmentId) {
	console.log(`Navigating to Assessment Project: ${assessmentId}`);
	await page.goto(`${BASE_URL}/app/assessment-project/${encodeURIComponent(assessmentId)}`);
	await page.waitForLoadState('networkidle');
	await page.waitForTimeout(2000);
}

/**
 * Get count of assessment stages
 * @param {Page} page - Playwright page object (must be on Assessment Project page)
 * @returns {Promise<number>} - Number of stages
 */
export async function getAssessmentStageCount(page) {
	// Click on Stages tab if it exists
	const stagesTab = page.locator('a:has-text("Stages"), button:has-text("Stages")').first();
	if (await stagesTab.isVisible({ timeout: 2000 })) {
		await stagesTab.click();
		await page.waitForTimeout(1000);
	}

	const stageRows = await page.locator('[data-fieldname="stages"] .grid-row').count();
	console.log(`Assessment has ${stageRows} stages`);
	return stageRows;
}

/**
 * Create tasks from template on Assessment Project
 * @param {Page} page - Playwright page object (must be on Assessment Project page)
 * @returns {Promise<boolean>} - Success status
 */
export async function createTasksFromTemplate(page) {
	console.log('Creating tasks from template...');

	try {
		// Look for "Create Tasks" button in menu or page
		const createTasksButton = page.locator('button:has-text("Create Tasks")').first();

		if (await createTasksButton.isVisible({ timeout: 5000 })) {
			await createTasksButton.click();
			await page.waitForTimeout(3000); // Wait for task creation

			console.log('✓ Tasks created from template');
			return true;
		}

		console.log('⚠ Create Tasks button not found');
		return false;
	} catch (error) {
		console.error(`Error creating tasks:`, error.message);
		return false;
	}
}

/**
 * Get count of Project Tasks linked to a request
 * @param {Page} page - Playwright page object
 * @param {string} requestId - Request ID
 * @returns {Promise<number>} - Number of tasks
 */
export async function getTaskCountForRequest(page, requestId) {
	await page.goto(`${BASE_URL}/app/project-task?request=${encodeURIComponent(requestId)}`);
	await page.waitForLoadState('networkidle');
	await page.waitForTimeout(2000);

	const taskCount = await page.locator('.list-row-container').count();
	console.log(`Found ${taskCount} tasks for request ${requestId}`);
	return taskCount;
}

/**
 * Execute a project task (assign, record time, mark complete)
 * @param {Page} page - Playwright page object
 * @param {string} taskId - Project Task ID
 * @param {number} hoursWorked - Hours to record (default 1.5)
 * @param {string} assignee - User to assign to (default 'Administrator')
 * @returns {Promise<boolean>} - Success status
 */
export async function executeSPISCTask(page, taskId, hoursWorked = 1.5, assignee = 'Administrator') {
	console.log(`Executing task: ${taskId}`);

	try {
		// Navigate to task
		await page.goto(`${BASE_URL}/app/project-task/${encodeURIComponent(taskId)}`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Assign to user if not already assigned
		const assignedToField = page.locator('[data-fieldname="assigned_to"] input').first();
		const currentAssignee = await assignedToField.inputValue().catch(() => '');

		if (!currentAssignee) {
			await assignedToField.fill(assignee);
			await page.waitForTimeout(500);
			await page.keyboard.press('Enter');
			await page.waitForTimeout(1000);
			console.log(`  ✓ Assigned to: ${assignee}`);
		}

		// Record actual time
		const actualTimeField = page.locator('[data-fieldname="actual_time"] input').first();
		const isReadonly = await actualTimeField.getAttribute('readonly');

		if (!isReadonly) {
			await actualTimeField.fill(hoursWorked.toString());
			console.log(`  ✓ Recorded ${hoursWorked} hours`);
		}

		// Set status to Completed
		const statusField = page.locator('[data-fieldname="status"]').first();
		const statusInput = statusField.locator('input, select').first();

		if (await statusInput.isVisible()) {
			const tagName = await statusInput.evaluate(el => el.tagName.toLowerCase());

			if (tagName === 'select') {
				await statusInput.selectOption('Completed');
			} else {
				await statusInput.click();
				await page.waitForTimeout(500);
				const completedOption = page.locator('.awesomplete li:has-text("Completed")').first();
				if (await completedOption.isVisible({ timeout: 2000 })) {
					await completedOption.click();
				}
			}
			console.log(`  ✓ Status set to Completed`);
		}

		// Set progress to 100%
		const progressField = page.locator('[data-fieldname="progress"] input').first();
		if (await progressField.isVisible()) {
			await progressField.fill('100');
			console.log(`  ✓ Progress set to 100%`);
		}

		// Save
		const saveButton = page.locator('button.primary-action:has-text("Save")').first();
		await saveButton.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		console.log(`✓ Task ${taskId} completed`);
		return true;

	} catch (error) {
		console.error(`Error executing task ${taskId}:`, error.message);
		return false;
	}
}

/**
 * Fill eligibility assessment on SPISC Application
 * @param {Page} page - Playwright page object (must be on SPISC Application page)
 * @param {string} status - "Eligible" or "Not Eligible"
 * @param {string} notes - Assessment notes
 * @returns {Promise<boolean>} - Success status
 */
export async function fillEligibilityAssessment(page, status, notes) {
	console.log(`Filling eligibility assessment: ${status}`);

	try {
		// Scroll to assessment section
		await page.evaluate(() => {
			const section = document.querySelector('[data-fieldname="eligibility_status"]');
			if (section) section.scrollIntoView({ behavior: 'smooth' });
		});
		await page.waitForTimeout(1000);

		// Fill eligibility status
		const eligibilityField = page.locator('[data-fieldname="eligibility_status"]').first();
		if (await eligibilityField.isVisible()) {
			const selectInput = eligibilityField.locator('select, input').first();
			const tagName = await selectInput.evaluate(el => el.tagName.toLowerCase());

			if (tagName === 'select') {
				await selectInput.selectOption(status);
			} else {
				await selectInput.fill(status);
				await page.waitForTimeout(500);
				await page.keyboard.press('Enter');
			}
			console.log(`  ✓ Eligibility status: ${status}`);
		}

		// Fill eligibility notes
		const notesField = page.locator('[data-fieldname="eligibility_notes"]').first();
		if (await notesField.isVisible()) {
			await notesField.fill(notes);
			console.log(`  ✓ Added eligibility notes`);
		}

		// Save
		const saveButton = page.locator('button.primary-action:has-text("Save")').first();
		await saveButton.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		console.log(`✓ Eligibility assessment saved`);
		return true;

	} catch (error) {
		console.error(`Error filling eligibility assessment:`, error.message);
		return false;
	}
}

/**
 * Verify status history contains a transition
 * @param {Page} page - Playwright page object (must be on Request page)
 * @param {string} fromStatus - Previous status
 * @param {string} toStatus - New status
 * @returns {Promise<boolean>} - True if transition found in history
 */
export async function verifyStatusHistoryTransition(page, fromStatus, toStatus) {
	console.log(`Verifying status history: ${fromStatus} → ${toStatus}`);

	// Click on status history tab if it exists
	const historyTab = page.locator('a:has-text("Status History"), button:has-text("History")').first();
	if (await historyTab.isVisible({ timeout: 2000 })) {
		await historyTab.click();
		await page.waitForTimeout(1000);
	}

	// Look for history table rows
	const historyRows = page.locator('[data-fieldname="status_history"] .grid-row');
	const rowCount = await historyRows.count();

	for (let i = 0; i < rowCount; i++) {
		const row = historyRows.nth(i);
		const rowText = await row.textContent();

		if (rowText.includes(fromStatus) && rowText.includes(toStatus)) {
			console.log(`  ✓ Found transition in history`);
			return true;
		}
	}

	console.log(`  ⚠ Transition not found in history`);
	return false;
}

/**
 * Create a Request for Information (RFI)
 * @param {Page} page - Playwright page object
 * @param {string} requestId - Request ID
 * @param {Array<string>} questions - Array of RFI questions
 * @returns {Promise<string|null>} - RFI ID or null if failed
 */
export async function createRFI(page, requestId, questions = ['Please provide additional documents']) {
	console.log(`Creating RFI for request: ${requestId}`);

	// Validate requestId
	if (!requestId || requestId === '' || requestId === 'null' || requestId === 'undefined') {
		console.error('Cannot create RFI: requestId is invalid or undefined');
		return null;
	}

	try {
		// Navigate to RFI list
		await page.goto(`${BASE_URL}/app/request-for-information/new`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Link to request
		const requestField = page.locator('[data-fieldname="request"] input').first();
		await requestField.fill(requestId);
		await page.waitForTimeout(500);
		await page.keyboard.press('Enter');
		await page.waitForTimeout(1000);

		// Add questions (if child table exists)
		for (const question of questions) {
			// This is simplified - actual implementation may vary
			const addRowButton = page.locator('[data-fieldname="questions"] .grid-add-row').first();
			if (await addRowButton.isVisible({ timeout: 2000 })) {
				await addRowButton.click();
				await page.waitForTimeout(500);

				const questionField = page.locator('[data-fieldname="question"] textarea, [data-fieldname="question"] input').last();
				await questionField.fill(question);
			}
		}

		// Save
		const saveButton = page.locator('button.primary-action:has-text("Save")').first();
		await saveButton.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Get RFI ID from URL
		const url = page.url();
		const match = url.match(/request-for-information\/([^\/]+)/);
		const rfiId = match ? match[1] : null;

		console.log(`✓ RFI created: ${rfiId}`);
		return rfiId;

	} catch (error) {
		console.error(`Error creating RFI:`, error.message);
		return null;
	}
}

export default {
	findLatestSPISCApplication,
	openSPISCApplication,
	getLinkedRequestId,
	navigateToRequest,
	getCurrentWorkflowState,
	changeWorkflowState,
	waitForAssessmentProject,
	navigateToAssessmentProject,
	getAssessmentStageCount,
	createTasksFromTemplate,
	getTaskCountForRequest,
	executeSPISCTask,
	fillEligibilityAssessment,
	verifyStatusHistoryTransition,
	createRFI
};
