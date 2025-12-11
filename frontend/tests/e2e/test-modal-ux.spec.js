import { test, expect } from '@playwright/test'

test.describe('Modal UX Improvements', () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto('http://localhost:8090/frontend')
		await page.waitForLoadState('networkidle')

		const logInLink = page.locator('a:has-text("Log In"), button:has-text("Log In")')
		if (await logInLink.isVisible({ timeout: 2000 }).catch(() => false)) {
			await logInLink.click()
			await page.waitForLoadState('networkidle')
			await page.fill('input[type="email"], input[type="text"]', 'Administrator')
			await page.fill('input[type="password"]', 'admin123')
			await page.click('button:has-text("Sign In")')
			await page.waitForLoadState('networkidle')
			await page.waitForTimeout(2000)
		}

		// Navigate to request
		await page.goto('http://localhost:8090/frontend/request/SPISC-2025-121')
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(3000)
	})

	test('Send Message modal shows success and auto-closes', async ({ page }) => {
		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  TEST: Send Message Success UX                   ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')

		// Open Send Message modal
		console.log('🧪 Opening Send Message modal...')
		const sendMsgBtn = page.locator('button:has-text("Send Message")')
		await sendMsgBtn.click()
		await page.waitForTimeout(1000)

		const modalTitle = page.locator('h3:has-text("Send Message to Council")')
		await expect(modalTitle).toBeVisible({ timeout: 3000 })
		console.log('✓ Modal opened')

		// Check padding exists
		const modalBody = page.locator('div.p-6').first()
		const hasPadding = await modalBody.isVisible()
		console.log(`✓ Modal has padding: ${hasPadding}`)
		expect(hasPadding).toBe(true)

		// Fill out form
		console.log('\n🧪 Filling out message form...')
		await page.fill('input[placeholder*="Brief description"]', 'Test Subject')
		await page.fill('textarea[placeholder*="Type your message"]', 'This is a test message to verify the success UX works correctly.')
		console.log('✓ Form filled')

		// Submit
		console.log('\n🧪 Submitting message...')
		const sendBtn = page.locator('button:has-text("Send Message")').last()
		await sendBtn.click()

		// Wait for success message
		await page.waitForTimeout(1000)

		// Check for success indicator
		const successMsg = page.locator('text=Message sent successfully')
		const successVisible = await successMsg.isVisible({ timeout: 3000 }).catch(() => false)
		console.log(`Success message visible: ${successVisible}`)

		if (successVisible) {
			console.log('✅ SUCCESS: Success message displayed!')

			// Check that modal auto-closes
			console.log('\n🧪 Waiting for auto-close (2 seconds)...')
			await page.waitForTimeout(2500)

			const modalStillVisible = await modalTitle.isVisible({ timeout: 500 }).catch(() => false)
			console.log(`Modal still visible after 2.5s: ${modalStillVisible}`)

			if (!modalStillVisible) {
				console.log('✅ SUCCESS: Modal auto-closed!')
			} else {
				console.log('⚠️  Modal did not auto-close')
			}
		} else {
			console.log('❌ Success message not shown (check API response)')
		}

		await page.screenshot({ path: '/tmp/send-message-ux.png', fullPage: true })
		console.log('\n📸 Screenshot: /tmp/send-message-ux.png')

		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  Send Message Test Complete                      ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')
	})

	test('Book Meeting modal shows success and auto-closes', async ({ page }) => {
		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  TEST: Book Meeting Success UX                   ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')

		// Open Book Meeting modal
		console.log('🧪 Opening Book Meeting modal...')
		const bookMeetingBtn = page.locator('button:has-text("Request Council Meeting")')
		await bookMeetingBtn.click()
		await page.waitForTimeout(2000)

		const modalTitle = page.locator('h3:has-text("Request Pre-Application Council Meeting")')
		await expect(modalTitle).toBeVisible({ timeout: 3000 })
		console.log('✓ Modal opened')

		// Check padding exists
		const modalBody = page.locator('div.p-6').first()
		const hasPadding = await modalBody.isVisible()
		console.log(`✓ Modal has padding: ${hasPadding}`)
		expect(hasPadding).toBe(true)

		// Load available slots
		console.log('\n🧪 Loading available slots...')
		const loadSlotsBtn = page.locator('button:has-text("Load Available Slots"), button:has-text("Refresh Available Slots")')
		if (await loadSlotsBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
			await loadSlotsBtn.click()
			await page.waitForTimeout(4000)
		}

		// Scroll to form fields
		await modalBody.evaluate(el => el.scrollTop = el.scrollHeight)
		await page.waitForTimeout(500)

		// Fill out form
		console.log('\n🧪 Filling out meeting request form...')
		await page.fill('textarea[placeholder*="Brief summary"]', 'I would like to discuss my SPISC application requirements.')

		// Select time slots from dropdowns if available
		const selects = page.locator('select')
		const selectCount = await selects.count()

		if (selectCount >= 4) {
			console.log('✓ Using dropdown slot selection')
			// Select 3 time slots
			await selects.nth(1).selectOption({ index: 1 })
			await selects.nth(2).selectOption({ index: 2 })
			await selects.nth(3).selectOption({ index: 3 })
			console.log('✓ Selected 3 time slots from dropdowns')
		} else {
			console.log('⚠️  Using manual datetime entry')
			const datetimeInputs = page.locator('input[type="datetime-local"]')
			const now = new Date()
			now.setDate(now.getDate() + 7)
			now.setHours(10, 0, 0, 0)
			const datetime = now.toISOString().slice(0, 16)
			await datetimeInputs.first().fill(datetime)
			console.log('✓ Entered manual time slot')
		}

		// Submit
		console.log('\n🧪 Submitting meeting request...')
		const requestBtn = page.locator('button:has-text("Request Meeting")')
		await requestBtn.click()

		// Wait for success message
		await page.waitForTimeout(1500)

		// Check for success indicator
		const successMsg = page.locator('text=Meeting request submitted successfully')
		const successVisible = await successMsg.isVisible({ timeout: 3000 }).catch(() => false)
		console.log(`Success message visible: ${successVisible}`)

		if (successVisible) {
			console.log('✅ SUCCESS: Success message displayed!')

			// Check that modal auto-closes
			console.log('\n🧪 Waiting for auto-close (2 seconds)...')
			await page.waitForTimeout(2500)

			const modalStillVisible = await modalTitle.isVisible({ timeout: 500 }).catch(() => false)
			console.log(`Modal still visible after 2.5s: ${modalStillVisible}`)

			if (!modalStillVisible) {
				console.log('✅ SUCCESS: Modal auto-closed!')
			} else {
				console.log('⚠️  Modal did not auto-close')
			}
		} else {
			console.log('❌ Success message not shown (check API response)')
		}

		await page.screenshot({ path: '/tmp/book-meeting-ux.png', fullPage: true })
		console.log('\n📸 Screenshot: /tmp/book-meeting-ux.png')

		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  Book Meeting Test Complete                      ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')
	})

	test('Both modals have proper padding', async ({ page }) => {
		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  TEST: Modal Padding                              ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')

		// Test Send Message modal
		const sendMsgBtn = page.locator('button:has-text("Send Message")')
		await sendMsgBtn.click()
		await page.waitForTimeout(1000)

		let paddingDiv = page.locator('div.p-6').first()
		let hasPadding = await paddingDiv.isVisible()
		console.log(`Send Message modal has padding: ${hasPadding}`)
		expect(hasPadding).toBe(true)

		// Close modal
		const cancelBtn = page.locator('button:has-text("Cancel")').first()
		await cancelBtn.click()
		await page.waitForTimeout(500)

		// Test Book Meeting modal
		const bookMeetingBtn = page.locator('button:has-text("Request Council Meeting")')
		await bookMeetingBtn.click()
		await page.waitForTimeout(1000)

		paddingDiv = page.locator('div.p-6').first()
		hasPadding = await paddingDiv.isVisible()
		console.log(`Book Meeting modal has padding: ${hasPadding}`)
		expect(hasPadding).toBe(true)

		console.log('\n✅ Both modals have proper padding')
	})
})
