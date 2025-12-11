import { test, expect } from '@playwright/test'

test.describe('Meeting Banner Verification', () => {
	test('Meeting banner shows on NewRequest page and modal works', async ({ page }) => {
		console.log('\n=== MANUAL TEST: Navigate to application step directly ===\n')

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

		// Navigate directly to an existing draft in progress
		console.log('\nNavigating to request/new with council and type pre-selected...')
		await page.goto('http://localhost:8090/frontend/request/new?council=TAYTAY-PH&requestType=SPISC')
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(3000) // Wait for request type config to load
		console.log('✓ On new request page')

		// Check current step
		const currentUrl = page.url()
		console.log('Current URL:', currentUrl)

		// Look for meeting banner (should appear after step 3)
		console.log('\nLooking for meeting banner...')
		const meetingBanner = page.locator('h3:has-text("Pre-Application Meeting Available")')

		// If we're on an earlier step, navigate forward
		let stepCount = 0
		while (!(await meetingBanner.isVisible().catch(() => false)) && stepCount < 5) {
			console.log(`Step ${stepCount}: Meeting banner not visible yet, clicking Next...`)
			const nextBtn = page.locator('button:has-text("Next")')
			if (await nextBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
				await nextBtn.click()
				await page.waitForTimeout(1500)
				stepCount++
			} else {
				// Try continue button for process info
				const continueBtn = page.locator('button:has-text("I Understand - Continue to Application")')
				if (await continueBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
					await continueBtn.click()
					await page.waitForTimeout(1500)
					stepCount++
				} else {
					break
				}
			}
		}

		// Now check for banner
		const bannerVisible = await meetingBanner.isVisible({ timeout: 5000 }).catch(() => false)
		console.log('Meeting banner visible:', bannerVisible)

		if (bannerVisible) {
			console.log('✓ Meeting banner found!')

			// Click the button
			console.log('\nClicking Request Council Meeting button...')
			const requestBtn = page.locator('button:has-text("Request Council Meeting")')

			// Listen for errors
			const consoleErrors = []
			page.on('console', msg => {
				if (msg.type() === 'error') {
					consoleErrors.push(msg.text())
				}
			})

			await requestBtn.click()
			await page.waitForTimeout(2000)

			// Check for circular JSON errors
			const hasCircularJSONError = consoleErrors.some(err =>
				err.includes('Converting circular structure to JSON')
			)
			console.log('Has circular JSON error:', hasCircularJSONError)
			expect(hasCircularJSONError).toBe(false)
			console.log('✓ No circular JSON errors!')

			// Verify modal
			const modalTitle = page.locator('h3:has-text("Request Pre-Application Council Meeting")')
			const modalVisible = await modalTitle.isVisible({ timeout: 5000 }).catch(() => false)
			console.log('Modal visible:', modalVisible)
			expect(modalVisible).toBe(true)
			console.log('✓ Modal opened successfully!')

			await page.screenshot({ path: '/tmp/meeting-modal-open.png' })
			console.log('✓ Screenshot saved\n')
		} else {
			console.log('⚠ Meeting banner not found (might be on wrong step or request type)')
			await page.screenshot({ path: '/tmp/meeting-banner-not-found.png' })
			console.log('Screenshot saved for debugging\n')
		}

		expect(bannerVisible).toBe(true)
	})

	test('Both fixes verified on RequestDetail page', async ({ page }) => {
		console.log('\n=== VERIFICATION: Both Bugs Fixed ===\n')

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

		// Go to request detail
		await page.goto('http://localhost:8090/frontend/request/SPISC-2025-121')
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(3000)
		console.log('✓ On request detail page')

		// Bug Fix #1: Council Meeting section should be visible (requestTypeConfig loads correctly)
		console.log('\nFix #1: Checking Council Meeting section...')
		const meetingSection = page.locator('h2:has-text("Council Meeting")')
		const sectionVisible = await meetingSection.isVisible({ timeout: 5000 }).catch(() => false)
		console.log('Council Meeting section visible:', sectionVisible)
		expect(sectionVisible).toBe(true)
		console.log('✅ FIX #1 VERIFIED: RequestDetail circular JSON bug fixed!')

		// Bug Fix #2: Modal should open without errors
		console.log('\nFix #2: Testing modal opens without circular JSON errors...')
		const requestBtn = page.locator('button:has-text("Request Council Meeting")')
		const btnVisible = await requestBtn.isVisible({ timeout: 2000 }).catch(() => false)
		expect(btnVisible).toBe(true)

		// Listen for console errors
		const consoleErrors = []
		page.on('console', msg => {
			if (msg.type() === 'error') {
				consoleErrors.push(msg.text())
			}
		})

		await requestBtn.click()
		await page.waitForTimeout(2000)

		const hasCircularJSONError = consoleErrors.some(err =>
			err.includes('Converting circular structure to JSON')
		)
		console.log('Has circular JSON error:', hasCircularJSONError)
		expect(hasCircularJSONError).toBe(false)
		console.log('✅ FIX #2 VERIFIED: BookMeetingModal circular JSON bug fixed!')

		// Verify modal opened
		const modalTitle = page.locator('h3:has-text("Request Pre-Application Council Meeting")')
		const modalVisible = await modalTitle.isVisible({ timeout: 5000 }).catch(() => false)
		expect(modalVisible).toBe(true)
		console.log('✅ Modal works perfectly!')

		console.log('\n╔═══════════════════════════════════════════════════╗')
		console.log('║  ✅ BOTH CRITICAL BUGS FIXED AND VERIFIED!       ║')
		console.log('╚═══════════════════════════════════════════════════╝\n')
	})
})
