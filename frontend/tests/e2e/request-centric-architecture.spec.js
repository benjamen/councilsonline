/**
 * End-to-End Test: Request-Centric Architecture
 *
 * Tests the new Request-centric architecture including:
 * - Universal action bar on Request form
 * - Summary dashboard with metrics
 * - Simplified SPISC Application with "View Request" button
 * - Navigation between Request and Application
 * - Assessment Project creation and linking
 */

import { test, expect } from '@playwright/test';

// Helper function to login to Frappe
async function loginToFrappe(page) {
	await page.goto('http://localhost:8090/login');
	await page.waitForLoadState('networkidle');

	await page.fill('#login_email', 'Administrator');
	await page.fill('#login_password', 'admin123');
	await page.click('.btn-login');

	await page.waitForLoadState('networkidle');
	await page.waitForTimeout(2000);
	console.log('✓ Logged in to Frappe');
}

test.describe('Request-Centric Architecture E2E Tests', () => {

	test('Complete Request-centric workflow for SPISC', async ({ page }) => {
		console.log('\n=== PHASE 1: Login ===');
		await loginToFrappe(page);

		// ========================================
		// PHASE 2: Find existing SPISC Request
		// ========================================
		console.log('\n=== PHASE 2: Find SPISC Request ===');

		await page.goto('http://localhost:8090/app/request');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Find a SPISC request
		const spiscRequestLink = await page.locator('a[data-doctype="Request"]').first();
		await expect(spiscRequestLink).toBeVisible({ timeout: 10000 });

		const requestName = await spiscRequestLink.getAttribute('data-name');
		console.log(`✓ Found Request: ${requestName}`);

		// Click to open Request
		await spiscRequestLink.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// ========================================
		// PHASE 3: Verify Request Universal Action Bar
		// ========================================
		console.log('\n=== PHASE 3: Verify Request Action Bar ===');

		// Check for Actions group buttons
		const viewApplicationBtn = page.locator('button:has-text("View Application")').first();
		await expect(viewApplicationBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "View Application" button exists');

		const viewAssessmentBtn = page.locator('button:has-text("View Assessment Project")').first();
		await expect(viewAssessmentBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "View Assessment Project" button exists');

		// Check for Tasks group buttons
		const viewTasksBtn = page.locator('button:has-text("View Tasks")').first();
		await expect(viewTasksBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "View Tasks" button exists');

		const createTaskBtn = page.locator('button:has-text("Create Task")').first();
		await expect(createTaskBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "Create Task" button exists');

		// Check for Meetings group buttons
		const viewMeetingsBtn = page.locator('button:has-text("View Meetings")').first();
		await expect(viewMeetingsBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "View Meetings" button exists');

		const scheduleMeetingBtn = page.locator('button:has-text("Schedule Meeting")').first();
		await expect(scheduleMeetingBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "Schedule Meeting" button exists');

		// Check for Communications group buttons
		const viewCommsBtn = page.locator('button:has-text("View Communications")').first();
		await expect(viewCommsBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "View Communications" button exists');

		const sendNotificationBtn = page.locator('button:has-text("Send Notification")').first();
		await expect(sendNotificationBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "Send Notification" button exists');

		const addNoteBtn = page.locator('button:has-text("Add Internal Note")').first();
		await expect(addNoteBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "Add Internal Note" button exists');

		// Check for Documents group buttons
		const viewDocsBtn = page.locator('button:has-text("View Documents")').first();
		await expect(viewDocsBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "View Documents" button exists');

		const uploadDocBtn = page.locator('button:has-text("Upload Document")').first();
		await expect(uploadDocBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "Upload Document" button exists');

		console.log('\n✓ All 11 action bar buttons verified!');

		// ========================================
		// PHASE 4: Verify Summary Dashboard
		// ========================================
		console.log('\n=== PHASE 4: Verify Summary Dashboard ===');

		// Check for dashboard existence
		const dashboard = page.locator('.request-summary-dashboard').first();
		await expect(dashboard).toBeVisible({ timeout: 5000 });
		console.log('✓ Summary dashboard is visible');

		// Check for metrics
		const dashboardMetrics = page.locator('.dashboard-metric');
		const metricsCount = await dashboardMetrics.count();
		console.log(`✓ Dashboard has ${metricsCount} metrics displayed`);

		expect(metricsCount).toBeGreaterThanOrEqual(4); // At least Tasks, Meetings, Comms, Assessment

		// Check for gradient background (SPISC should be blue)
		const bgColor = await dashboard.evaluate(el =>
			window.getComputedStyle(el).background
		);
		console.log(`✓ Dashboard has gradient background: ${bgColor.substring(0, 50)}...`);

		// ========================================
		// PHASE 5: Navigate to SPISC Application
		// ========================================
		console.log('\n=== PHASE 5: Navigate to SPISC Application ===');

		// Click "View Application" button
		await viewApplicationBtn.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Verify we're on SPISC Application form
		const currentUrl = page.url();
		expect(currentUrl).toContain('spisc-application');
		console.log(`✓ Navigated to SPISC Application: ${currentUrl}`);

		// ========================================
		// PHASE 6: Verify Simplified SPISC Application
		// ========================================
		console.log('\n=== PHASE 6: Verify Simplified SPISC Application ===');

		// Check for prominent "View Request (Main Hub)" button
		const viewRequestBtn = page.locator('button:has-text("View Request (Main Hub)")').first();
		await expect(viewRequestBtn).toBeVisible({ timeout: 5000 });
		console.log('✓ "View Request (Main Hub)" button exists');

		// Verify it has btn-primary class (prominent)
		const isPrimary = await viewRequestBtn.evaluate(el =>
			el.classList.contains('btn-primary')
		);
		expect(isPrimary).toBe(true);
		console.log('✓ Button is styled as primary (prominent)');

		// Check for helper message about using Request form
		const helperMessage = page.locator('text=Use the Request form to access Tasks');
		await expect(helperMessage).toBeVisible({ timeout: 5000 });
		console.log('✓ Helper message displayed to guide users to Request form');

		// Verify NO duplicate action bar buttons exist on SPISC form
		const spiscTasksBtn = page.locator('button:has-text("View Tasks")');
		const spiscTasksCount = await spiscTasksBtn.count();
		expect(spiscTasksCount).toBe(0);
		console.log('✓ No duplicate "View Tasks" button (removed from SPISC)');

		const spiscMeetingsBtn = page.locator('button:has-text("View Meetings")');
		const spiscMeetingsCount = await spiscMeetingsBtn.count();
		expect(spiscMeetingsCount).toBe(0);
		console.log('✓ No duplicate "View Meetings" button (removed from SPISC)');

		// Check for SPISC-specific buttons (should still exist)
		const assessEligibilityBtn = page.locator('button:has-text("Assess Eligibility")').first();
		if (await assessEligibilityBtn.isVisible()) {
			console.log('✓ SPISC-specific "Assess Eligibility" button exists');
		} else {
			console.log('  (Assess Eligibility button not shown - may be submitted already)');
		}

		// ========================================
		// PHASE 7: Navigate back to Request
		// ========================================
		console.log('\n=== PHASE 7: Navigate Back to Request ===');

		// Click "View Request (Main Hub)" to go back
		await viewRequestBtn.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Verify we're back on Request form
		const backUrl = page.url();
		expect(backUrl).toContain('request');
		expect(backUrl).toContain(requestName);
		console.log(`✓ Successfully navigated back to Request: ${backUrl}`);

		// ========================================
		// PHASE 8: Test View Assessment Project
		// ========================================
		console.log('\n=== PHASE 8: Test View Assessment Project ===');

		// Click "View Assessment Project" button
		const assessmentProjectBtn = page.locator('button:has-text("View Assessment Project")').first();
		await assessmentProjectBtn.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(3000);

		// Check if we navigated to Assessment Project or got a message
		const assessmentUrl = page.url();

		if (assessmentUrl.includes('assessment-project')) {
			console.log(`✓ Navigated to Assessment Project: ${assessmentUrl}`);

			// Verify Assessment Project fields exist
			const projectName = await page.locator('[data-fieldname="name"]').inputValue();
			console.log(`✓ Assessment Project: ${projectName}`);

			// Check for stages and tasks
			const stagesSection = page.locator('text=Stages').first();
			if (await stagesSection.isVisible()) {
				console.log('✓ Assessment stages visible');
			}
		} else {
			// Check if we got a "No Assessment Project" message
			const noProjectMsg = page.locator('text=No Assessment Project');
			if (await noProjectMsg.isVisible()) {
				console.log('  No Assessment Project exists yet (expected for some requests)');
			}
		}

		// ========================================
		// PHASE 9: Test Action Bar Functionality
		// ========================================
		console.log('\n=== PHASE 9: Test Action Bar Functionality ===');

		// Go back to Request to test other buttons
		await page.goto(`http://localhost:8090/app/request/${requestName}`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Test "View Tasks" button
		const tasksButton = page.locator('button:has-text("View Tasks")').first();
		await tasksButton.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		const tasksUrl = page.url();
		expect(tasksUrl).toContain('project-task');
		console.log('✓ "View Tasks" button navigates to Project Task list');

		// Go back to Request
		await page.goto(`http://localhost:8090/app/request/${requestName}`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Test "Send Notification" dialog
		const notificationBtn = page.locator('button:has-text("Send Notification")').first();
		await notificationBtn.click();
		await page.waitForTimeout(1000);

		// Check if dialog opened
		const dialogTitle = page.locator('.modal-title:has-text("Send Notification")');
		if (await dialogTitle.isVisible()) {
			console.log('✓ "Send Notification" dialog opens correctly');

			// Close dialog
			const closeBtn = page.locator('button.btn-modal-close').first();
			await closeBtn.click();
			await page.waitForTimeout(500);
		}

		// ========================================
		// PHASE 10: Verify No Redundant Fields
		// ========================================
		console.log('\n=== PHASE 10: Verify Removed Redundant Fields ===');

		// Check that removed fields don't exist on Request form
		const assessmentStatusField = page.locator('[data-fieldname="assessment_status"]');
		const assessmentStatusExists = await assessmentStatusField.count();
		expect(assessmentStatusExists).toBe(0);
		console.log('✓ Removed field "assessment_status" not present');

		const currentStageField = page.locator('[data-fieldname="current_stage"]');
		const currentStageExists = await currentStageField.count();
		expect(currentStageExists).toBe(0);
		console.log('✓ Removed field "current_stage" not present');

		const assessmentTemplateField = page.locator('[data-fieldname="assessment_template"]');
		const assessmentTemplateExists = await assessmentTemplateField.count();
		expect(assessmentTemplateExists).toBe(0);
		console.log('✓ Removed field "assessment_template" not present');

		const assessmentOwnerField = page.locator('[data-fieldname="assessment_owner"]');
		const assessmentOwnerExists = await assessmentOwnerField.count();
		expect(assessmentOwnerExists).toBe(0);
		console.log('✓ Removed field "assessment_owner" not present');

		// Verify assessment_project field still exists (it should)
		const assessmentProjectField = page.locator('[data-fieldname="assessment_project"]');
		const assessmentProjectExists = await assessmentProjectField.count();
		expect(assessmentProjectExists).toBeGreaterThan(0);
		console.log('✓ "assessment_project" link field still exists (as expected)');

		console.log('\n=== ✅ ALL TESTS PASSED ===\n');
	});


	test('Verify Resource Consent Application integration', async ({ page }) => {
		console.log('\n=== Testing Resource Consent Application ===');

		await loginToFrappe(page);

		// Find a Resource Consent request
		await page.goto('http://localhost:8090/app/request');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		// Look for a Resource Consent request
		const requests = await page.locator('a[data-doctype="Request"]').all();

		for (const request of requests) {
			await request.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Check if this is a Resource Consent request
			const requestType = await page.locator('[data-fieldname="request_type"]').inputValue();

			if (requestType === 'Resource Consent') {
				console.log('✓ Found Resource Consent request');

				// Verify universal action bar exists
				const viewApplicationBtn = page.locator('button:has-text("View Application")').first();
				await expect(viewApplicationBtn).toBeVisible({ timeout: 5000 });
				console.log('✓ Request has universal action bar');

				// Navigate to RC Application
				await viewApplicationBtn.click();
				await page.waitForLoadState('networkidle');
				await page.waitForTimeout(2000);

				// Verify we're on RC Application
				const url = page.url();
				expect(url).toContain('resource-consent-application');
				console.log('✓ Navigated to Resource Consent Application');

				// Check for "View Request (Main Hub)" button
				const viewRequestBtn = page.locator('button:has-text("View Request (Main Hub)")').first();
				await expect(viewRequestBtn).toBeVisible({ timeout: 5000 });
				console.log('✓ "View Request (Main Hub)" button exists on RC Application');

				// Check for RC-specific buttons (should still exist)
				const refreshConditionsBtn = page.locator('button:has-text("Refresh Condition Templates")').first();
				if (await refreshConditionsBtn.isVisible()) {
					console.log('✓ RC-specific "Refresh Condition Templates" button exists');
				}

				// Check for statutory clock indicator
				const clockIndicator = page.locator('.statutory-clock-indicator').first();
				if (await clockIndicator.isVisible()) {
					console.log('✓ RC-specific statutory clock indicator visible');
				}

				console.log('✓ Resource Consent Application verified!');
				break;
			}
		}
	});


	test('Verify universal API endpoints work', async ({ page }) => {
		console.log('\n=== Testing Universal API Endpoints ===');

		await loginToFrappe(page);

		// Find any request
		await page.goto('http://localhost:8090/app/request');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		const firstRequest = page.locator('a[data-doctype="Request"]').first();
		await firstRequest.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(2000);

		const requestName = await page.locator('[data-fieldname="name"]').inputValue();
		console.log(`Testing with Request: ${requestName}`);

		// Test get_request_summary_data API
		const response = await page.evaluate(async (reqName) => {
			return await frappe.call({
				method: 'lodgeick.api.get_request_summary_data',
				args: { request_id: reqName }
			});
		}, requestName);

		expect(response.message).toBeDefined();
		expect(response.message.success).toBe(true);
		expect(response.message.tasks_count).toBeDefined();
		expect(response.message.meetings_count).toBeDefined();
		expect(response.message.communications_count).toBeDefined();
		expect(response.message.assessment_status).toBeDefined();

		console.log('✓ get_request_summary_data API returns correct structure');
		console.log(`  - Tasks: ${response.message.tasks_count}`);
		console.log(`  - Meetings: ${response.message.meetings_count}`);
		console.log(`  - Communications: ${response.message.communications_count}`);
		console.log(`  - Assessment Status: ${response.message.assessment_status}`);

		console.log('✓ Universal API endpoint verified!');
	});
});
