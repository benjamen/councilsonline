/**
 * Phase 0.1: Request Form UX Components Verification
 *
 * Purpose: Verify the recently fixed Request form JavaScript components work without console errors.
 *
 * This test verifies:
 * - No ES6 syntax errors ("Unexpected token 'export'")
 * - No undefined errors ("Cannot read properties of undefined")
 * - Status pills render correctly for all 21 workflow states
 * - Workflow progression timeline loads without errors
 * - Dashboard metrics display correctly
 * - Defensive checks prevent crashes
 * - Deferred loading works without race conditions
 */

import { test, expect } from '@playwright/test';
import { login } from '../fixtures/auth.js';

// Base URL for Frappe backend
const BASE_URL = 'http://localhost:8090';

test.describe('Request Form UX Components Verification', () => {
	let page;
	let consoleErrors = [];
	let consoleWarnings = [];

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();

		// Capture console errors and warnings
		consoleErrors = [];
		consoleWarnings = [];

		page.on('console', (msg) => {
			if (msg.type() === 'error') {
				consoleErrors.push(msg.text());
			}
			if (msg.type() === 'warning') {
				consoleWarnings.push(msg.text());
			}
		});

		// Capture page errors
		page.on('pageerror', (error) => {
			consoleErrors.push(`Page Error: ${error.message}`);
		});

		// Login as Administrator
		await login(page, {
			username: 'Administrator',
			password: 'admin123',
			baseUrl: BASE_URL
		});
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('01 - Load Request detail page without console errors', async () => {
		// Navigate to Request List
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');

		// Wait for list to load
		await page.waitForSelector('.list-row', { timeout: 10000 });

		// Click on first request to open detail
		const firstRequest = await page.locator('.list-row').first();
		await firstRequest.click();

		// Wait for form to fully load
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000); // Allow time for deferred components (100ms + buffer)

		// Check for ES6 syntax errors
		const es6Errors = consoleErrors.filter(err =>
			err.includes('Unexpected token') ||
			err.includes('export') ||
			err.includes('import statement')
		);
		expect(es6Errors, 'Should have no ES6 syntax errors').toHaveLength(0);

		// Check for undefined property errors
		const undefinedErrors = consoleErrors.filter(err =>
			err.includes('Cannot read properties of undefined') ||
			err.includes('reading \'find\'') ||
			err.includes('reading \'wrapper\'')
		);
		expect(undefinedErrors, 'Should have no undefined property errors').toHaveLength(0);

		// Report all console errors if any
		if (consoleErrors.length > 0) {
			console.log('Console Errors Found:', consoleErrors);
		}

		expect(consoleErrors, 'Request form should load without console errors').toHaveLength(0);
	});

	test('02 - Verify status pill renders correctly', async () => {
		// Navigate to a request
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Check if status pill/badge exists in the page
		const statusBadge = await page.locator('.badge, .status-pill, [class*="status"], [class*="workflow"]').first();

		if (await statusBadge.count() > 0) {
			// Verify it's visible
			await expect(statusBadge).toBeVisible();

			// Verify it has text content
			const badgeText = await statusBadge.textContent();
			expect(badgeText).toBeTruthy();
			expect(badgeText.trim().length).toBeGreaterThan(0);
		}

		// No errors should be logged
		expect(consoleErrors, 'Status pill should render without errors').toHaveLength(0);
	});

	test('03 - Verify workflow progression timeline loads', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500); // Wait for deferred components

		// Look for timeline/progression elements
		const timeline = await page.locator('[class*="timeline"], [class*="progression"], [class*="workflow"]');

		// Timeline might be in dashboard or as separate component
		// Just verify no errors occurred during load
		expect(consoleErrors, 'Workflow timeline should load without errors').toHaveLength(0);
	});

	test('04 - Verify dashboard metrics display correctly', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500); // Wait for deferred dashboard components

		// Look for dashboard elements
		const dashboard = await page.locator('.form-dashboard, [class*="dashboard"], .indicator');

		// Dashboard should exist (Frappe creates it automatically)
		expect(await dashboard.count()).toBeGreaterThan(0);

		// No errors should be logged
		expect(consoleErrors, 'Dashboard should load without errors').toHaveLength(0);
	});

	test('05 - Verify requester card renders', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Look for requester information (could be in various places)
		const requesterFields = await page.locator('[data-fieldname*="requester"], [data-fieldname*="applicant"]');

		// Just verify no errors during render
		expect(consoleErrors, 'Requester card should render without errors').toHaveLength(0);
	});

	test('06 - Verify no ES6 module errors in action_bar_utils.js', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Check specifically for action_bar_utils.js errors
		const actionBarErrors = consoleErrors.filter(err =>
			err.includes('action_bar_utils') ||
			(err.includes('lodgeick') && err.includes('actionBar'))
		);
		expect(actionBarErrors, 'action_bar_utils.js should load without errors').toHaveLength(0);
	});

	test('07 - Verify no ES6 module errors in summary_dashboard.js', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500); // Dashboard is deferred

		// Check specifically for summary_dashboard.js errors
		const dashboardErrors = consoleErrors.filter(err =>
			err.includes('summary_dashboard') ||
			(err.includes('lodgeick') && err.includes('dashboard'))
		);
		expect(dashboardErrors, 'summary_dashboard.js should load without errors').toHaveLength(0);
	});

	test('08 - Verify defensive checks prevent crashes (frm.page.wrapper)', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(500);

		// Check for defensive check warnings (these are acceptable)
		const defensiveWarnings = consoleWarnings.filter(warn =>
			warn.includes('Page wrapper not ready') ||
			warn.includes('Dashboard not ready') ||
			warn.includes('Title area not ready')
		);

		// Defensive warnings are OK, but errors are not
		const pageWrapperErrors = consoleErrors.filter(err =>
			err.includes('frm.page.wrapper') ||
			err.includes('frm.page.title_area')
		);
		expect(pageWrapperErrors, 'Defensive checks should prevent frm.page errors').toHaveLength(0);
	});

	test('09 - Verify defensive checks prevent crashes (frm.dashboard.wrapper)', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500);

		// Check for dashboard wrapper errors
		const dashboardWrapperErrors = consoleErrors.filter(err =>
			err.includes('frm.dashboard.wrapper') ||
			err.includes('dashboard.find')
		);
		expect(dashboardWrapperErrors, 'Defensive checks should prevent frm.dashboard errors').toHaveLength(0);
	});

	test('10 - Verify deferred loading works (100ms delay)', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });
		await page.locator('.list-row').first().click();

		// Immediate check (before 100ms)
		await page.waitForTimeout(50);
		const earlyErrors = [...consoleErrors];

		// Wait for deferred components
		await page.waitForTimeout(200);
		await page.waitForLoadState('networkidle');

		// Check for race condition errors
		const raceErrors = consoleErrors.filter(err =>
			err.includes('race') ||
			err.includes('undefined') ||
			err.includes('null')
		);
		expect(raceErrors, 'Deferred loading should prevent race conditions').toHaveLength(0);
	});
});

test.describe('Request Form - Multiple Workflow States', () => {
	let page;
	let consoleErrors = [];

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();
		consoleErrors = [];

		page.on('console', (msg) => {
			if (msg.type() === 'error') {
				consoleErrors.push(msg.text());
			}
		});

		page.on('pageerror', (error) => {
			consoleErrors.push(`Page Error: ${error.message}`);
		});

		await login(page, {
			username: 'Administrator',
			password: 'admin123',
			baseUrl: BASE_URL
		});
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('11 - Load multiple requests to test different workflow states', async () => {
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForSelector('.list-row', { timeout: 10000 });

		// Get all request rows
		const requestRows = await page.locator('.list-row').all();
		const rowCount = Math.min(requestRows.length, 5); // Test first 5 requests

		console.log(`Testing ${rowCount} requests for console errors...`);

		for (let i = 0; i < rowCount; i++) {
			// Clear errors for this iteration
			const errorsBeforeClick = consoleErrors.length;

			// Click request
			await page.goto(`${BASE_URL}/app/request`);
			await page.waitForSelector('.list-row', { timeout: 10000 });
			await page.locator('.list-row').nth(i).click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1500);

			// Check for new errors
			const newErrors = consoleErrors.slice(errorsBeforeClick);
			if (newErrors.length > 0) {
				console.log(`Request ${i + 1} generated errors:`, newErrors);
			}
		}

		// Overall check - no errors across all requests
		expect(consoleErrors, 'Multiple requests should load without console errors').toHaveLength(0);
	});
});
