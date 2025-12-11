import { test, expect } from '@playwright/test'

test.describe('Meeting Slot API Investigation', () => {
	test('Click Refresh Available Slots and check API response', async ({ page }) => {
		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  TEST: Slot API Investigation                    ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')

		// Capture network requests
		const apiCalls = []
		page.on('request', request => {
			if (request.url().includes('get_available_meeting_slots')) {
				console.log('📤 API Request:', request.url())
				console.log('   Method:', request.method())
				console.log('   Post Data:', request.postData())
				apiCalls.push({
					url: request.url(),
					method: request.method(),
					postData: request.postData()
				})
			}
		})

		page.on('response', async response => {
			if (response.url().includes('get_available_meeting_slots')) {
				console.log('📥 API Response:', response.url())
				console.log('   Status:', response.status())
				try {
					const body = await response.json()
					console.log('   Body:', JSON.stringify(body, null, 2))
				} catch (e) {
					console.log('   Body: (not JSON)')
				}
			}
		})

		// Capture console errors
		const consoleErrors = []
		page.on('console', msg => {
			if (msg.type() === 'error') {
				consoleErrors.push(msg.text())
				console.log('🔴 Console Error:', msg.text())
			}
		})

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
		console.log('✓ Logged in')

		// Navigate to request
		await page.goto('http://localhost:8090/frontend/request/SPISC-2025-121')
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(3000)

		// Open modal
		const bookMeetingBtn = page.locator('button:has-text("Request Council Meeting")')
		await bookMeetingBtn.click()
		await page.waitForTimeout(2000)

		// Click "Refresh Available Slots" button
		console.log('\n🧪 Clicking "Refresh Available Slots" button...')
		const refreshBtn = page.locator('button:has-text("Refresh Available Slots"), button:has-text("Load Available Slots")')
		const btnVisible = await refreshBtn.isVisible({ timeout: 3000 }).catch(() => false)

		if (btnVisible) {
			console.log('✓ Button found, clicking...')
			await refreshBtn.click()
			console.log('✓ Button clicked, waiting for API response...')
			await page.waitForTimeout(5000) // Give time for API call
		} else {
			console.log('❌ Button not found!')
		}

		// Check for loading state
		await page.waitForTimeout(1000)
		const loadingIndicator = page.locator('text=Loading available time slots')
		const isLoading = await loadingIndicator.isVisible().catch(() => false)
		console.log('\nLoading indicator visible:', isLoading)

		// Check for error message
		const errorMsg = page.locator('text=Failed to load available slots')
		const hasError = await errorMsg.isVisible().catch(() => false)
		console.log('Error message visible:', hasError)

		// Check for no slots message
		const noSlotsMsg = page.locator('text=No available slots found')
		const hasNoSlots = await noSlotsMsg.isVisible().catch(() => false)
		console.log('No slots message visible:', hasNoSlots)

		// Check for dropdowns
		const selects = page.locator('select')
		const selectCount = await selects.count()
		console.log('Number of select elements:', selectCount)

		// Check for datetime inputs
		const datetimeInputs = page.locator('input[type="datetime-local"]')
		const datetimeCount = await datetimeInputs.count()
		console.log('Number of datetime inputs:', datetimeCount)

		// Take screenshot
		await page.screenshot({ path: '/tmp/slot-api-test.png', fullPage: true })
		console.log('\n📸 Screenshot saved: /tmp/slot-api-test.png')

		// Summary
		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  API CALL SUMMARY                                 ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')
		console.log(`API calls made: ${apiCalls.length}`)
		console.log(`Console errors: ${consoleErrors.length}`)
		console.log(`Select dropdowns: ${selectCount}`)
		console.log(`DateTime inputs: ${datetimeCount}`)
		console.log(`Loading: ${isLoading}`)
		console.log(`Error: ${hasError}`)
		console.log(`No slots: ${hasNoSlots}`)
		console.log('')
	})
})
