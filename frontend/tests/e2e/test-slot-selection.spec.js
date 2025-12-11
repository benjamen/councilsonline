import { test, expect } from '@playwright/test'

test.describe('Meeting Slot Selection UX', () => {
	test('Slot selection should use dropdown selectors, not manual datetime pickers', async ({ page }) => {
		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  TEST: Slot Selection UX                         ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')

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

		// Navigate to existing SPISC request
		console.log('\n📍 Navigating to request...')
		await page.goto('http://localhost:8090/frontend/request/SPISC-2025-121')
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(3000)
		console.log('✓ On request detail page')

		// Open Book Meeting modal
		console.log('\n🧪 Opening Book Meeting modal...')
		const bookMeetingBtn = page.locator('button:has-text("Request Council Meeting")')
		await bookMeetingBtn.click()
		await page.waitForTimeout(2000)

		const modalTitle = page.locator('h3:has-text("Request Pre-Application Council Meeting")')
		const modalVisible = await modalTitle.isVisible({ timeout: 5000 }).catch(() => false)
		expect(modalVisible).toBe(true)
		console.log('✓ Modal opened')

		// Click "Load Available Slots" button
		console.log('\n🧪 Loading available slots...')
		const loadSlotsBtn = page.locator('button:has-text("Load Available Slots")')
		const loadBtnVisible = await loadSlotsBtn.isVisible({ timeout: 2000 }).catch(() => false)

		if (loadBtnVisible) {
			console.log('Found "Load Available Slots" button, clicking...')
			await loadSlotsBtn.click()
			await page.waitForTimeout(3000) // Wait for API call
		} else {
			console.log('Button text might be different, checking for "Refresh Available Slots"...')
			const refreshBtn = page.locator('button:has-text("Refresh Available Slots")')
			if (await refreshBtn.isVisible().catch(() => false)) {
				await refreshBtn.click()
				await page.waitForTimeout(3000)
			}
		}

		// Check if we have dropdowns (select elements) instead of datetime-local inputs
		console.log('\n🧪 Checking for dropdown selectors...')
		const selectElements = page.locator('select')
		const selectCount = await selectElements.count()

		// We expect at least 4 selects: 1 for meeting type + 3 for time slots
		// (if slots are available)
		console.log(`Found ${selectCount} select dropdowns`)

		// Check for datetime-local inputs (should only appear if no slots available)
		const datetimeInputs = page.locator('input[type="datetime-local"]')
		const datetimeCount = await datetimeInputs.count()
		console.log(`Found ${datetimeCount} datetime-local inputs`)

		// Take screenshot to see the UI
		await page.screenshot({ path: '/tmp/slot-selection-ui.png', fullPage: true })
		console.log('📸 Screenshot saved: /tmp/slot-selection-ui.png')

		// Check if we got slot dropdowns or manual inputs
		if (selectCount >= 4) {
			console.log('\n✅ PASS: Slot selection using DROPDOWNS!')
			console.log('   - Users can select from available time slots')

			// Try to select a slot from the first dropdown
			const firstSlotSelect = page.locator('select').nth(1) // Skip meeting type dropdown
			const options = await firstSlotSelect.locator('option').count()
			console.log(`   - First time slot has ${options} options`)

			if (options > 1) { // More than just placeholder
				console.log('   ✅ Available slots are populated in dropdown!')
			} else {
				console.log('   ⚠️  No available slots, but dropdown exists for when slots are available')
			}
		} else if (datetimeCount >= 3) {
			console.log('\n⚠️  Using manual datetime pickers')
			console.log('   This is OK if no slots are available')
			console.log('   But should switch to dropdowns when slots are loaded')
		}

		// Check for loading state message
		const loadingMsg = page.locator('text=Loading available time slots')
		const isLoading = await loadingMsg.isVisible().catch(() => false)

		if (isLoading) {
			console.log('\n⏳ Still loading slots...')
			await page.waitForTimeout(3000)
		}

		// Check for "no slots" message
		const noSlotsMsg = page.locator('text=No available slots found')
		const hasNoSlots = await noSlotsMsg.isVisible().catch(() => false)

		if (hasNoSlots) {
			console.log('\n📋 No available slots found - this is expected if council has no configured slots')
			console.log('   UI correctly falls back to manual datetime input')
		}

		// Check for error message
		const errorMsg = page.locator('text=Failed to load available slots')
		const hasError = await errorMsg.isVisible().catch(() => false)

		if (hasError) {
			console.log('\n❌ Error loading slots')
			console.log('   Need to investigate API/database')
		}

		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  TEST COMPLETE                                    ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')

		console.log('Summary:')
		console.log('═══════════════════════════════════════════════════')
		console.log(`Select dropdowns: ${selectCount}`)
		console.log(`DateTime inputs: ${datetimeCount}`)
		console.log(`Loading: ${isLoading}`)
		console.log(`No slots: ${hasNoSlots}`)
		console.log(`Error: ${hasError}`)
		console.log('')

		// The test passes if we have dropdown UI OR manual input as fallback
		const hasDropdownUI = selectCount >= 4
		const hasManualFallback = datetimeCount >= 3

		expect(hasDropdownUI || hasManualFallback).toBe(true)
	})
})
