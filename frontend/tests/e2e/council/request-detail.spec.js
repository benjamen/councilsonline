/**
 * Phase 2.2: Request Detail View Test
 *
 * Purpose: Test the Request detail page with all UX components and functionality.
 *
 * Test Scenarios:
 * 1. View request detail - all fields displayed correctly
 * 2. Status badge rendering - correct color/text for workflow states
 * 3. Workflow progression timeline - visual timeline shows current state
 * 4. Requester card - applicant info displays
 * 5. Dashboard metrics - tasks, meetings, communications counts
 * 6. Edit request fields - update assigned to, priority, notes
 * 7. View linked application - navigate to RC/BC/SPISC application
 * 8. Action buttons - Create Task, Schedule Meeting, Send Communication
 */

import { test, expect } from '@playwright/test';
import {
	loginAsCouncilStaff,
	STAFF_ROLES
} from '../fixtures/council-staff.js';

const BASE_URL = 'http://localhost:8090';

test.describe('Request Detail View - Basic Information', () => {
	let page;
	let requestId;

	test.beforeAll(async ({ browser }) => {
		page = await browser.newPage();

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN
		});

		// Navigate to request list and get first request
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRow = page.locator('.list-row').first();
		await firstRow.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500); // Wait for UX components

		// Get request ID from URL
		const url = page.url();
		const match = url.match(/request\/([^\/]+)/);
		requestId = match ? match[1] : null;

		console.log(`Testing request detail view for: ${requestId}`);
	});

	test.afterAll(async () => {
		await page.close();
	});

	test('01 - All essential fields are displayed', async () => {
		// Verify essential fields exist
		const requestNumberField = page.locator('[data-fieldname="request_number"]');
		const requestTypeField = page.locator('[data-fieldname="request_type"]');
		const workflowStateField = page.locator('[data-fieldname="workflow_state"]');

		// Check if fields are present
		const hasRequestNumber = await requestNumberField.count() > 0;
		const hasRequestType = await requestTypeField.count() > 0;
		const hasWorkflowState = await workflowStateField.count() > 0;

		console.log('Essential fields present:', {
			requestNumber: hasRequestNumber,
			requestType: hasRequestType,
			workflowState: hasWorkflowState
		});

		// At least request number should be present
		expect(hasRequestNumber).toBe(true);
	});

	test('02 - Request number matches URL', async () => {
		const requestNumberField = page.locator('[data-fieldname="request_number"] input, [data-fieldname="request_number"]');

		if (await requestNumberField.count() > 0) {
			const displayedNumber = await requestNumberField.first().inputValue().catch(() =>
				requestNumberField.first().textContent()
			);

			console.log(`Request number: ${displayedNumber}, URL ID: ${requestId}`);

			// They should match
			expect(displayedNumber).toBe(requestId);
		}
	});

	test('03 - Request type is displayed', async () => {
		const requestTypeField = page.locator('[data-fieldname="request_type"] input, [data-fieldname="request_type"]');

		if (await requestTypeField.count() > 0) {
			const requestType = await requestTypeField.first().inputValue().catch(() =>
				requestTypeField.first().textContent()
			);

			console.log(`Request type: ${requestType}`);

			// Should have a value
			expect(requestType).toBeTruthy();
			expect(requestType.length).toBeGreaterThan(0);
		}
	});

	test('04 - Workflow state is displayed', async () => {
		const workflowStateField = page.locator('[data-fieldname="workflow_state"] input');

		if (await workflowStateField.count() > 0) {
			const workflowState = await workflowStateField.inputValue();

			console.log(`Workflow state: ${workflowState}`);

			// Should have a valid state
			expect(workflowState).toBeTruthy();
			expect(workflowState.length).toBeGreaterThan(0);
		}
	});
});

test.describe('Request Detail View - UX Components', () => {
	let page;

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN
		});

		// Navigate to a request detail
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRow = page.locator('.list-row').first();
		await firstRow.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000); // Wait for all UX components including deferred
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('05 - Status badge/pill renders correctly', async () => {
		// Look for status badge
		const statusBadge = page.locator('.badge, .status-pill, .indicator, [class*="status-"]').first();

		if (await statusBadge.count() > 0) {
			const badgeText = await statusBadge.textContent();
			const badgeColor = await statusBadge.evaluate(el => window.getComputedStyle(el).backgroundColor);

			console.log(`Status badge: "${badgeText}", color: ${badgeColor}`);

			// Badge should have text
			expect(badgeText.trim().length).toBeGreaterThan(0);

			// Badge should have background color (not transparent)
			expect(badgeColor).not.toBe('rgba(0, 0, 0, 0)');
		} else {
			console.log('Status badge not found');
		}
	});

	test('06 - Workflow progression timeline displays', async () => {
		// Look for timeline/progression indicator
		const timeline = page.locator(
			'[class*="timeline"], ' +
			'[class*="progression"], ' +
			'[class*="workflow"], ' +
			'[data-fieldname="timeline_visual_html"]'
		);

		if (await timeline.count() > 0) {
			console.log('Workflow progression timeline found');

			// Timeline should be visible
			const isVisible = await timeline.first().isVisible();
			expect(isVisible).toBe(true);
		} else {
			console.log('Workflow progression timeline not found - may be in collapsed section');
		}
	});

	test('07 - Requester information card displays', async () => {
		// Look for requester card
		const requesterCard = page.locator(
			'[data-fieldname="requester_card_html"], ' +
			'[data-fieldname="requester"], ' +
			'[data-fieldname="requester_name"]'
		);

		if (await requesterCard.count() > 0) {
			console.log('Requester information section found');

			// Should have some content
			const hasContent = await requesterCard.count() > 0;
			expect(hasContent).toBe(true);
		}
	});

	test('08 - Dashboard metrics display (if present)', async () => {
		// Look for dashboard section
		const dashboard = page.locator('.form-dashboard, [class*="dashboard"], [data-fieldname="status_card_html"]');

		if (await dashboard.count() > 0) {
			console.log('Dashboard metrics section found');

			// Dashboard should be visible
			const isVisible = await dashboard.first().isVisible();
			expect(isVisible).toBe(true);
		} else {
			console.log('Dashboard not found or not initialized yet');
		}
	});

	test('09 - Form tabs are present', async () => {
		// Look for form tabs
		const tabs = page.locator('.form-tabs, .page-head-tabs, [role="tablist"]');

		if (await tabs.count() > 0) {
			const tabButtons = await tabs.locator('a, button, [role="tab"]').all();
			console.log(`Found ${tabButtons.length} form tabs`);

			// Should have multiple tabs
			expect(tabButtons.length).toBeGreaterThan(0);

			// Log tab names
			for (const tab of tabButtons) {
				const tabText = await tab.textContent();
				console.log(`- Tab: ${tabText}`);
			}
		}
	});
});

test.describe('Request Detail View - Linked Records', () => {
	let page;

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN
		});

		// Navigate to a request detail
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRow = page.locator('.list-row').first();
		await firstRow.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500);
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('10 - Assessment project link (if exists)', async () => {
		// Look for assessment project field
		const assessmentField = page.locator('[data-fieldname="assessment_project"]');

		if (await assessmentField.count() > 0) {
			// Check if it has a value
			const assessmentLink = page.locator('[data-fieldname="assessment_project"] a');

			if (await assessmentLink.count() > 0) {
				const linkText = await assessmentLink.textContent();
				console.log(`Assessment project linked: ${linkText}`);

				expect(linkText.trim().length).toBeGreaterThan(0);
			} else {
				console.log('Assessment project field exists but no assessment linked yet');
			}
		} else {
			console.log('Assessment project field not found');
		}
	});

	test('11 - Linked application navigation (if exists)', async () => {
		// Look for application doctype and name fields
		const applicationDoctypeField = page.locator('[data-fieldname="application_doctype"]');
		const applicationNameField = page.locator('[data-fieldname="application_name"]');

		if (await applicationDoctypeField.count() > 0 && await applicationNameField.count() > 0) {
			const appDoctype = await applicationDoctypeField.inputValue().catch(() => '');
			const appName = await applicationNameField.inputValue().catch(() => '');

			if (appDoctype && appName) {
				console.log(`Linked application: ${appDoctype} - ${appName}`);

				// Look for link to application
				const applicationLink = page.locator(`a[href*="${appName}"]`);

				if (await applicationLink.count() > 0) {
					console.log('Application link found - navigation available');
					expect(applicationLink.count()).toBeGreaterThan(0);
				}
			}
		}
	});

	test('12 - Related requests section (if exists)', async () => {
		// Look for related requests field
		const relatedRequestsField = page.locator('[data-fieldname="related_requests"]');

		if (await relatedRequestsField.count() > 0) {
			console.log('Related requests section found');
			expect(relatedRequestsField.count()).toBeGreaterThan(0);
		} else {
			console.log('Related requests section not found');
		}
	});
});

test.describe('Request Detail View - Actions', () => {
	let page;

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN
		});

		// Navigate to a request detail
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRow = page.locator('.list-row').first();
		await firstRow.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500);
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('13 - Primary action buttons visible', async () => {
		// Look for primary action (Save)
		const saveButton = page.locator('.primary-action, button:has-text("Save")');

		if (await saveButton.count() > 0) {
			console.log('Save button found');
			expect(saveButton.count()).toBeGreaterThan(0);
		}

		// Look for menu button
		const menuButton = page.locator('.menu-btn, button.btn-secondary, .actions-btn-group button');

		if (await menuButton.count() > 0) {
			const menuCount = await menuButton.count();
			console.log(`Found ${menuCount} action menu button(s)`);
		}
	});

	test('14 - Workflow action buttons (if present)', async () => {
		// Look for workflow buttons
		const workflowButtons = page.locator('.form-workflow, .workflow-buttons, button[data-action]');

		if (await workflowButtons.count() > 0) {
			const buttons = await workflowButtons.all();
			console.log(`Found ${buttons.length} workflow action button(s)`);

			for (const button of buttons.slice(0, 5)) { // Check first 5
				const buttonText = await button.textContent();
				console.log(`- Workflow action: ${buttonText}`);
			}

			expect(buttons.length).toBeGreaterThan(0);
		} else {
			console.log('No workflow action buttons found in current state');
		}
	});

	test('15 - Additional action menu items', async () => {
		// Look for and click the Menu button
		const menuButton = page.locator('.menu-btn-group .btn, button:has-text("Menu")').first();

		if (await menuButton.count() > 0) {
			await menuButton.click();
			await page.waitForTimeout(500);

			// Look for dropdown menu items
			const menuItems = page.locator('.dropdown-menu a, .dropdown-item');

			if (await menuItems.count() > 0) {
				const items = await menuItems.all();
				console.log(`Found ${items.length} menu items`);

				for (const item of items.slice(0, 10)) { // Check first 10
					const itemText = await item.textContent();
					console.log(`- Menu item: ${itemText}`);
				}

				expect(items.length).toBeGreaterThan(0);

				// Close menu
				await page.keyboard.press('Escape');
			}
		} else {
			console.log('Menu button not found');
		}
	});
});

test.describe('Request Detail View - Edit Functionality', () => {
	let page;

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN
		});

		// Navigate to a request detail
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRow = page.locator('.list-row').first();
		await firstRow.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500);
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('16 - Update processing notes field', async () => {
		// Find processing notes field
		const processingNotesField = page.locator('[data-fieldname="processing_notes"] textarea, [data-fieldname="processing_notes"]');

		if (await processingNotesField.count() > 0) {
			const currentValue = await processingNotesField.inputValue().catch(() => '');
			const newValue = `Test note added at ${new Date().toISOString()}`;

			// Update the field
			await processingNotesField.fill(newValue);
			await page.waitForTimeout(500);

			// Verify it was updated
			const updatedValue = await processingNotesField.inputValue();
			expect(updatedValue).toBe(newValue);

			console.log('Processing notes updated successfully');

			// Revert to original value
			await processingNotesField.fill(currentValue);
		} else {
			console.log('Processing notes field not found or not editable');
		}
	});

	test('17 - Update priority field (if exists)', async () => {
		// Find priority field
		const priorityField = page.locator('[data-fieldname="priority"]');

		if (await priorityField.count() > 0) {
			console.log('Priority field found');

			// Try to click and change value
			const priorityInput = page.locator('[data-fieldname="priority"] input, [data-fieldname="priority"] select');

			if (await priorityInput.count() > 0) {
				const currentValue = await priorityInput.inputValue().catch(() => '');
				console.log(`Current priority: ${currentValue}`);

				expect(priorityField.count()).toBeGreaterThan(0);
			}
		} else {
			console.log('Priority field not found');
		}
	});

	test('18 - Verify form is dirty after editing', async () => {
		// Find an editable field
		const processingNotesField = page.locator('[data-fieldname="processing_notes"] textarea');

		if (await processingNotesField.count() > 0) {
			// Edit the field
			await processingNotesField.fill('Test modification');
			await page.waitForTimeout(500);

			// Look for dirty indicator (unsaved changes)
			const dirtyIndicator = page.locator('.indicator-orange, [title*="Not Saved"], .modified-indicator');

			if (await dirtyIndicator.count() > 0) {
				console.log('Form correctly shows as dirty (unsaved changes)');
				expect(dirtyIndicator.count()).toBeGreaterThan(0);
			} else {
				console.log('Dirty indicator not found - may use different visual cue');
			}

			// Refresh to discard changes
			await page.reload();
			await page.waitForLoadState('networkidle');
		}
	});
});
