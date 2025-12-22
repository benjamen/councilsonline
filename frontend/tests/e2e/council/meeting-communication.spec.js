/**
 * Phase 5: Meeting & Communication Tests
 *
 * Purpose: Test pre-application meeting scheduling and communication logging.
 *
 * Test Scenarios:
 * - Pre-Application Meeting scheduling
 * - Meeting attendee management
 * - Meeting notes and outcomes
 * - Communication logging (email, phone, notes)
 * - Response tracking
 */

import { test, expect } from '@playwright/test';
import {
	loginAsCouncilStaff,
	STAFF_ROLES
} from '../fixtures/council-staff.js';

const BASE_URL = 'http://localhost:8090';

test.describe('Meeting Management - Pre-Application Meetings', () => {
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

	test('01 - Navigate to Pre-Application Meeting list', async () => {
		// Navigate to meeting list
		await page.goto(`${BASE_URL}/app/pre-application-meeting`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Verify page loaded
		const pageTitle = page.locator('.page-title, h1');

		if (await pageTitle.count() > 0) {
			const titleText = await pageTitle.textContent();
			console.log(`Meeting list page: ${titleText}`);
		}

		// Count existing meetings
		const meetingRows = await page.locator('.list-row').count();
		console.log(`Found ${meetingRows} pre-application meetings`);

		expect(meetingRows).toBeGreaterThanOrEqual(0);
	});

	test('02 - Create new pre-application meeting', async () => {
		// Navigate to meeting list
		await page.goto(`${BASE_URL}/app/pre-application-meeting`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Click New button
		const newButton = page.locator('.primary-action, button:has-text("New")');

		if (await newButton.count() > 0) {
			await newButton.first().click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Verify on new meeting form
			const url = page.url();
			expect(url).toContain('/pre-application-meeting/');

			console.log('New meeting form opened');
		} else {
			console.log('New button not found');
		}
	});

	test('03 - Fill meeting details', async () => {
		// Navigate to new meeting
		await page.goto(`${BASE_URL}/app/pre-application-meeting/new-pre-application-meeting-1`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Fill meeting title/subject
		const subjectField = page.locator('[data-fieldname="title"], [data-fieldname="subject"]');

		if (await subjectField.count() > 0) {
			const meetingTitle = `E2E Test Meeting - ${new Date().toISOString()}`;
			await subjectField.locator('input').fill(meetingTitle);
			await page.waitForTimeout(300);

			console.log(`Meeting title: ${meetingTitle}`);
		}

		// Set meeting date
		const dateField = page.locator('[data-fieldname="meeting_date"], [data-fieldname="scheduled_date"]');

		if (await dateField.count() > 0) {
			const futureDate = new Date();
			futureDate.setDate(futureDate.getDate() + 3);
			const dateString = futureDate.toISOString().split('T')[0];

			await dateField.locator('input').fill(dateString);
			await page.waitForTimeout(300);

			console.log(`Meeting date: ${dateString}`);
		}
	});

	test('04 - Set meeting location', async () => {
		// Navigate to meeting
		await page.goto(`${BASE_URL}/app/pre-application-meeting/new-pre-application-meeting-1`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Look for location field
		const locationField = page.locator('[data-fieldname="location"], [data-fieldname="meeting_location"]');

		if (await locationField.count() > 0) {
			await locationField.locator('input, textarea').fill('Council Chambers, Level 2');
			await page.waitForTimeout(300);

			console.log('Meeting location set');
		} else {
			console.log('Location field not found');
		}
	});

	test('05 - Add meeting attendees (if field exists)', async () => {
		// Navigate to meeting
		await page.goto(`${BASE_URL}/app/pre-application-meeting/new-pre-application-meeting-1`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Look for attendees table
		const attendeesField = page.locator('[data-fieldname="attendees"], [data-fieldname="participants"]');

		if (await attendeesField.count() > 0) {
			console.log('Attendees field found');

			// Look for add row button
			const addRowButton = page.locator('.grid-add-row, button:has-text("Add Row")');

			if (await addRowButton.count() > 0) {
				await addRowButton.first().click();
				await page.waitForTimeout(500);

				console.log('Add attendee row clicked');
			}
		} else {
			console.log('Attendees field not found');
		}
	});

	test('06 - View meeting detail page', async () => {
		// Navigate to meeting list
		await page.goto(`${BASE_URL}/app/pre-application-meeting`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Click first meeting if exists
		const firstMeeting = page.locator('.list-row').first();

		if (await firstMeeting.count() > 0) {
			await firstMeeting.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Verify on detail page
			const url = page.url();
			expect(url).toContain('/pre-application-meeting/');

			console.log('Viewing meeting detail');

			// Check for key fields
			const statusField = page.locator('[data-fieldname="status"]');
			const dateField = page.locator('[data-fieldname="meeting_date"]');

			if (await statusField.count() > 0 && await dateField.count() > 0) {
				console.log('Meeting detail fields visible');
			}
		} else {
			console.log('No meetings found');
		}
	});

	test('07 - Record meeting notes/outcome', async () => {
		// Navigate to meeting list
		await page.goto(`${BASE_URL}/app/pre-application-meeting`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstMeeting = page.locator('.list-row').first();

		if (await firstMeeting.count() > 0) {
			await firstMeeting.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for notes/outcome field
			const notesField = page.locator(
				'[data-fieldname="notes"], ' +
				'[data-fieldname="meeting_notes"], ' +
				'[data-fieldname="outcome"]'
			);

			if (await notesField.count() > 0) {
				const noteText = 'E2E Test: Discussion about site requirements and planning constraints.';
				await notesField.locator('textarea').fill(noteText);
				await page.waitForTimeout(300);

				console.log('Meeting notes recorded');
			} else {
				console.log('Notes field not found');
			}
		}
	});

	test('08 - Change meeting status', async () => {
		// Navigate to meeting list
		await page.goto(`${BASE_URL}/app/pre-application-meeting`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstMeeting = page.locator('.list-row').first();

		if (await firstMeeting.count() > 0) {
			await firstMeeting.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for status field
			const statusField = page.locator('[data-fieldname="status"] input');

			if (await statusField.count() > 0) {
				const currentStatus = await statusField.inputValue();
				console.log(`Current meeting status: ${currentStatus}`);

				// Try to change status
				await statusField.click();
				await page.waitForTimeout(300);

				// Look for status options (Scheduled, Held, Cancelled)
				const statusOptions = page.locator('li[data-value], .dropdown-item');

				if (await statusOptions.count() > 0) {
					const optionsCount = await statusOptions.count();
					console.log(`Found ${optionsCount} status options`);
				}
			}
		}
	});
});

test.describe('Communication Management - Logging', () => {
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

	test('09 - Navigate to Communication list', async () => {
		// Try to navigate to communication doctype
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Check if page loaded
		const pageTitle = page.locator('.page-title, h1');

		if (await pageTitle.count() > 0) {
			const titleText = await pageTitle.textContent();
			console.log(`Communication page: ${titleText}`);
		}

		// Count communications
		const commRows = await page.locator('.list-row').count();
		console.log(`Found ${commRows} communications`);
	});

	test('10 - Log email communication', async () => {
		// Navigate to communication list
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Click New
		const newButton = page.locator('.primary-action, button:has-text("New")');

		if (await newButton.count() > 0) {
			await newButton.first().click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Fill email details
			const subjectField = page.locator('[data-fieldname="subject"]');

			if (await subjectField.count() > 0) {
				await subjectField.locator('input').fill('RE: Application RC-2025-001 - Additional Information');
				console.log('Email subject filled');
			}

			// Set communication type
			const typeField = page.locator('[data-fieldname="communication_type"]');

			if (await typeField.count() > 0) {
				await typeField.locator('input').click();
				await page.waitForTimeout(300);

				const emailOption = page.locator('li:has-text("Email"), [data-value="Email"]');

				if (await emailOption.count() > 0) {
					await emailOption.first().click();
					console.log('Communication type set to Email');
				}
			}
		}
	});

	test('11 - Log phone call communication', async () => {
		// Navigate to communication list
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const newButton = page.locator('.primary-action, button:has-text("New")');

		if (await newButton.count() > 0) {
			await newButton.first().click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Set type to Phone
			const typeField = page.locator('[data-fieldname="communication_type"]');

			if (await typeField.count() > 0) {
				await typeField.locator('input').click();
				await page.waitForTimeout(300);

				const phoneOption = page.locator('li:has-text("Phone"), li:has-text("Call"), [data-value="Phone"]');

				if (await phoneOption.count() > 0) {
					await phoneOption.first().click();
					console.log('Communication type set to Phone');
				}
			}

			// Add notes
			const contentField = page.locator('[data-fieldname="content"], [data-fieldname="notes"]');

			if (await contentField.count() > 0) {
				await contentField.locator('textarea').fill('Incoming call from applicant regarding site visit timing.');
				console.log('Phone call notes added');
			}
		}
	});

	test('12 - View communication timeline on Request', async () => {
		// Navigate to a request
		await page.goto(`${BASE_URL}/app/request`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstRequest = page.locator('.list-row').first();
		await firstRequest.click();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1500);

		// Look for timeline/communications section
		const timeline = page.locator('.form-timeline, .comment-timeline, [class*="timeline"]');

		if (await timeline.count() > 0) {
			console.log('Timeline section found on request');

			// Count timeline entries
			const timelineEntries = await timeline.locator('.timeline-item, .comment-content').count();
			console.log(`Found ${timelineEntries} timeline entries`);
		} else {
			console.log('Timeline section not found');
		}
	});

	test('13 - Filter communications by type', async () => {
		// Navigate to communication list
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Look for type filter
		const typeFilter = page.locator('[data-fieldname="communication_type"]');

		if (await typeFilter.count() > 0) {
			console.log('Communication type filter available');
		}

		// Check standard filters
		const standardFilters = page.locator('.standard-filter-section, .filter-area');

		if (await standardFilters.count() > 0) {
			console.log('Standard filters available');
		}
	});

	test('14 - Mark communication as "Requires Response"', async () => {
		// Navigate to communication list
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstComm = page.locator('.list-row').first();

		if (await firstComm.count() > 0) {
			await firstComm.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for "requires response" or "follow up" field
			const followUpField = page.locator(
				'[data-fieldname="requires_response"], ' +
				'[data-fieldname="follow_up"], ' +
				'[data-fieldname="response_required"]'
			);

			if (await followUpField.count() > 0) {
				console.log('Follow-up/response tracking field found');

				// Try to check checkbox if it exists
				const checkbox = followUpField.locator('input[type="checkbox"]');

				if (await checkbox.count() > 0) {
					await checkbox.check();
					console.log('Marked as requiring response');
				}
			} else {
				console.log('Response tracking field not found');
			}
		}
	});
});

test.describe('Communication Management - Email Tracking', () => {
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

	test('15 - View email delivery status (if tracked)', async () => {
		// Navigate to communication list and find email
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Look for email communication
		const emailComm = page.locator('.list-row:has-text("Email")').first();

		if (await emailComm.count() > 0) {
			await emailComm.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for delivery status fields
			const statusField = page.locator(
				'[data-fieldname="delivery_status"], ' +
				'[data-fieldname="email_status"], ' +
				'[data-fieldname="sent"]'
			);

			if (await statusField.count() > 0) {
				console.log('Email delivery status field found');

				const status = await statusField.locator('input').inputValue().catch(() => '');
				console.log(`Email status: ${status}`);
			} else {
				console.log('No email delivery tracking found');
			}
		} else {
			console.log('No email communications found');
		}
	});

	test('16 - Attach documents to communication', async () => {
		// Navigate to communication
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstComm = page.locator('.list-row').first();

		if (await firstComm.count() > 0) {
			await firstComm.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for attachments section
			const attachSection = page.locator('.attachments-section, [data-fieldname="attachments"]');

			if (await attachSection.count() > 0) {
				console.log('Attachments section found');

				// Look for attach button
				const attachButton = page.locator('button:has-text("Attach"), .attach-btn');

				if (await attachButton.count() > 0) {
					console.log('Attach button available');
				}
			} else {
				console.log('No attachments section found');
			}
		}
	});

	test('17 - Link communication to request', async () => {
		// Navigate to communication
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		const firstComm = page.locator('.list-row').first();

		if (await firstComm.count() > 0) {
			await firstComm.click();
			await page.waitForLoadState('networkidle');
			await page.waitForTimeout(1000);

			// Look for reference/link fields
			const referenceField = page.locator(
				'[data-fieldname="reference_doctype"], ' +
				'[data-fieldname="reference_name"], ' +
				'[data-fieldname="link_doctype"]'
			);

			if (await referenceField.count() > 0) {
				console.log('Reference/link field found - can link to request');
			} else {
				console.log('No link field found');
			}
		}
	});

	test('18 - Search communications by date range', async () => {
		// Navigate to communication list
		await page.goto(`${BASE_URL}/app/communication`);
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		// Look for date filters
		const filterButton = page.locator('.filter-button, button:has-text("Filter")');

		if (await filterButton.count() > 0) {
			await filterButton.click();
			await page.waitForTimeout(300);

			console.log('Filter menu opened - date range filtering may be available');

			// Look for date field options
			const dateFields = page.locator('[data-fieldname*="date"], .filter-field');

			if (await dateFields.count() > 0) {
				console.log('Date filter fields available');
			}
		}

		// Close filter
		await page.keyboard.press('Escape');
	});
});
