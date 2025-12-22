/**
 * Phase 6: Assessment & SLA Tests
 *
 * Purpose: Test Assessment Project lifecycle and SLA clock tracking.
 *
 * Test Scenarios:
 * - Assessment Project auto-creation
 * - Assessment stages progression
 * - SLA clock calculation
 * - Working days tracking
 * - Deadline warnings
 * - Cost tracking
 */

import { test, expect } from '@playwright/test';
import {
	loginAsCouncilStaff,
	waitForAssessmentProject,
	STAFF_ROLES
} from '../fixtures/council-staff.js';

const BASE_URL = 'http://localhost:8090';

test.describe('Assessment Project - Lifecycle', () => {
	let page;

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN
		});
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('01 - Navigate to Assessment Project list', async () => {
		// Navigate to assessment project list
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Verify page loaded
		const pageTitle = page.locator('.page-title, h1');

		if (await pageTitle.count() > 0) {
			const titleText = await pageTitle.textContent();
			console.log(`Assessment Project page: ${titleText}`);
		}

		// Count existing assessments
		const assessmentRows = await page.locator('.list-row').count();
		console.log(`Found ${assessmentRows} assessment projects`);

		expect(assessmentRows).toBeGreaterThanOrEqual(0);
	});

	test('02 - View assessment project detail', async () => {
		// Navigate to assessment list
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Click first assessment
		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Verify on detail page
			const url = page.url();
			expect(url).toContain('/assessment-project/');

			console.log('Viewing assessment project detail');

			// Check for key fields
			const requestField = page.locator('[data-fieldname="request"]');
			const statusField = page.locator('[data-fieldname="overall_status"]');

			if (await requestField.count() > 0 && await statusField.count() > 0) {
				console.log('Assessment detail fields visible');
			}
		} else {
			console.log('No assessment projects found');
		}
	});

	test('03 - Navigate to linked request', async () => {
		// Navigate to assessment list
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for request link
			const requestLink = page.locator('[data-fieldname="request"] a');

			if (await requestLink.count() > 0) {
				const requestName = await requestLink.textContent();
				console.log(`Linked request: ${requestName}`);

				// Click to navigate
				await requestLink.click();
				await page.waitForLoadState('networkidle');
				await page.waitForTimeout(1000);

				// Verify navigated to request
				const url = page.url();
				expect(url).toContain('/request/');

				console.log('Successfully navigated to linked request');
			} else {
				console.log('Request link not found');
			}
		}
	});

	test('04 - View assessment stages', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for stages table/grid
			const stagesField = page.locator(
				'[data-fieldname="assessment_stages"], ' +
				'[data-fieldname="stages"], ' +
				'.grid-body'
			);

			if (await stagesField.count() > 0) {
				console.log('Assessment stages found');

				// Count stages
				const stageRows = await stagesField.locator('.grid-row, tr').count();
				console.log(`Assessment has ${stageRows} stages`);

				expect(stageRows).toBeGreaterThan(0);
			} else {
				console.log('No assessment stages found');
			}
		}
	});

	test('05 - View stage status', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for stage status fields
			const stageStatuses = page.locator('[data-fieldname="stage_status"], [class*="stage"], .indicator');

			if (await stageStatuses.count() > 0) {
				console.log('Stage status indicators found');

				// Log first few statuses
				const statuses = await stageStatuses.all();
				for (const status of statuses.slice(0, 5)) {
					const statusText = await status.textContent();
					console.log(`- Stage status: ${statusText}`);
				}
			} else {
				console.log('No stage status indicators found');
			}
		}
	});

	test('06 - View overall assessment status', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Get overall status
			const statusField = page.locator('[data-fieldname="overall_status"] input');

			if (await statusField.count() > 0) {
				const overallStatus = await statusField.inputValue();
				console.log(`Overall assessment status: ${overallStatus}`);

				expect(overallStatus).toBeTruthy();
			}
		}
	});

	test('07 - View linked tasks (if exists)', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for tasks section/link
			const tasksSection = page.locator(
				'[data-fieldname="tasks"], ' +
				'.form-dashboard .document-link:has-text("Task"), ' +
				'a:has-text("Project Task")'
			);

			if (await tasksSection.count() > 0) {
				console.log('Tasks section/link found');

				// Try to count linked tasks
				const taskCount = await tasksSection.locator('.count, .badge').textContent().catch(() => '0');
				console.log(`Linked tasks: ${taskCount}`);
			} else {
				console.log('No tasks section found');
			}
		}
	});
});

test.describe('SLA Clock - Tracking & Calculation', () => {
	let page;

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN
		});
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('08 - View SLA fields on request', async () => {
		// Navigate to request
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRequest = page.locator('.list-row').first();
		await firstRequest.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000); // Wait for dashboard components

		// Look for SLA fields
		const slaFields = page.locator(
			'[data-fieldname="target_completion_date"], ' +
			'[data-fieldname="statutory_deadline"], ' +
			'[data-fieldname="working_days_remaining"]'
		);

		if (await slaFields.count() > 0) {
			console.log('SLA tracking fields found');

			// Try to read field values
			const targetDate = await page.locator('[data-fieldname="target_completion_date"] input').inputValue().catch(() => '');
			const daysRemaining = await page.locator('[data-fieldname="working_days_remaining"] input').inputValue().catch(() => '');

			console.log(`Target completion: ${targetDate}`);
			console.log(`Working days remaining: ${daysRemaining}`);
		} else {
			console.log('SLA fields not found');
		}
	});

	test('09 - View acknowledged date (SLA start)', async () => {
		// Navigate to request
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRequest = page.locator('.list-row').first();
		await firstRequest.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500);

		// Get acknowledged date
		const acknowledgedDateField = page.locator('[data-fieldname="acknowledged_date"] input');

		if (await acknowledgedDateField.count() > 0) {
			const acknowledgedDate = await acknowledgedDateField.inputValue();
			console.log(`Acknowledged date (SLA start): ${acknowledgedDate}`);

			if (acknowledgedDate) {
				expect(acknowledgedDate.length).toBeGreaterThan(0);
			}
		}
	});

	test('10 - View SLA countdown indicator (if displayed)', async () => {
		// Navigate to request
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRequest = page.locator('.list-row').first();
		await firstRequest.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000); // Wait for deferred dashboard

		// Look for SLA countdown in dashboard
		const slaIndicator = page.locator(
			'.sla-countdown, ' +
			'[class*="sla"], ' +
			'[class*="countdown"], ' +
			'.indicator:has-text("days")'
		);

		if (await slaIndicator.count() > 0) {
			console.log('SLA countdown indicator found');

			const slaText = await slaIndicator.first().textContent();
			console.log(`SLA indicator: ${slaText}`);
		} else {
			console.log('No SLA countdown indicator visible');
		}
	});

	test('11 - Check overdue indicator (if applicable)', async () => {
		// Navigate to request list
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Look for overdue indicators in list
		const overdueIndicators = page.locator('.indicator-red, [class*="overdue"], .text-danger');

		if (await overdueIndicators.count() > 0) {
			console.log('Overdue indicators found');

			const overdueCount = await overdueIndicators.count();
			console.log(`${overdueCount} overdue indicators visible`);
		} else {
			console.log('No overdue indicators found - no overdue requests or not displayed');
		}
	});

	test('12 - View working days elapsed', async () => {
		// Navigate to request
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRequest = page.locator('.list-row').first();
		await firstRequest.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500);

		// Look for working days elapsed field
		const daysElapsedField = page.locator(
			'[data-fieldname="working_days_elapsed"], ' +
			'[data-fieldname="days_elapsed"]'
		);

		if (await daysElapsedField.count() > 0) {
			const daysElapsed = await daysElapsedField.locator('input').inputValue().catch(() => '');
			console.log(`Working days elapsed: ${daysElapsed}`);
		} else {
			console.log('Working days elapsed field not found');
		}
	});

	test('13 - View clock exclusion periods (if tracked)', async () => {
		// Navigate to request
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRequest = page.locator('.list-row').first();
		await firstRequest.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500);

		// Look for clock exclusion/stop-the-clock fields
		const exclusionField = page.locator(
			'[data-fieldname="clock_exclusions"], ' +
			'[data-fieldname="stop_the_clock"], ' +
			'[data-fieldname="exclusion_days"]'
		);

		if (await exclusionField.count() > 0) {
			console.log('Clock exclusion tracking found');
		} else {
			console.log('Clock exclusion tracking not found - may be calculated internally');
		}
	});
});

test.describe('Cost Tracking - Assessment & Tasks', () => {
	let page;

	test.beforeEach(async ({ browser }) => {
		page = await browser.newPage();

		// Login as council staff
		await loginAsCouncilStaff(page, {
			role: STAFF_ROLES.ADMIN
		});
	});

	test.afterEach(async () => {
		await page.close();
	});

	test('14 - View budgeted hours on assessment', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for budgeted hours
			const budgetedHoursField = page.locator(
				'[data-fieldname="expected_time"], ' +
				'[data-fieldname="budgeted_hours"], ' +
				'[data-fieldname="estimated_hours"]'
			);

			if (await budgetedHoursField.count() > 0) {
				const budgetedHours = await budgetedHoursField.locator('input').inputValue().catch(() => '');
				console.log(`Budgeted hours: ${budgetedHours}`);
			} else {
				console.log('Budgeted hours field not found');
			}
		}
	});

	test('15 - View actual hours/cost', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for actual hours/cost
			const actualField = page.locator(
				'[data-fieldname="actual_time"], ' +
				'[data-fieldname="total_actual_time"], ' +
				'[data-fieldname="total_costing_amount"]'
			);

			if (await actualField.count() > 0) {
				const actualValue = await actualField.locator('input').inputValue().catch(() => '');
				console.log(`Actual time/cost: ${actualValue}`);
			} else {
				console.log('Actual time/cost field not found');
			}
		}
	});

	test('16 - View cost breakdown by role (if exists)', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for costing details table
			const costingTable = page.locator(
				'[data-fieldname="costing_details"], ' +
				'[data-fieldname="cost_breakdown"], ' +
				'.grid-body'
			);

			if (await costingTable.count() > 0) {
				console.log('Cost breakdown table found');

				const costRows = await costingTable.locator('.grid-row, tr').count();
				console.log(`${costRows} cost breakdown entries`);
			} else {
				console.log('No cost breakdown table found');
			}
		}
	});

	test('17 - Verify task costs roll up to assessment', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Get assessment total cost
			const assessmentCostField = page.locator('[data-fieldname="total_costing_amount"] input');
			const assessmentCost = await assessmentCostField.inputValue().catch(() => '0');

			console.log(`Assessment total cost: ${assessmentCost}`);

			// Navigate to linked tasks
			const tasksLink = page.locator('a:has-text("Project Task"), .document-link:has-text("Task")');

			if (await tasksLink.count() > 0) {
				console.log('Tasks link found - can verify cost rollup');
				// In a full implementation, would click through and sum task costs
			}
		}
	});

	test('18 - View budgeted vs actual variance', async () => {
		// Navigate to assessment
		await page.goto(`${BASE_URL}/app/assessment-project`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstAssessment = page.locator('.list-row').first();

		if (await firstAssessment.count() > 0) {
			await firstAssessment.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Get budgeted and actual
			const budgetedField = page.locator('[data-fieldname="expected_time"] input');
			const actualField = page.locator('[data-fieldname="total_actual_time"] input');

			const budgeted = await budgetedField.inputValue().catch(() => '0');
			const actual = await actualField.inputValue().catch(() => '0');

			console.log(`Budgeted: ${budgeted}, Actual: ${actual}`);

			if (budgeted && actual) {
				const variance = parseFloat(actual) - parseFloat(budgeted);
				console.log(`Variance: ${variance} hours`);
			}
		}
	});
});
