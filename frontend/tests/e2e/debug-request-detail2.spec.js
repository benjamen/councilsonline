import { test, expect } from '@playwright/test'

test('Debug RequestDetail page - Check meeting section after resource loads', async ({ page }) => {
	console.log('\n=== DEBUG: RequestDetail Meeting Section ===\n')

	// 1. Login
	console.log('Step 1: Login...')
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

	// 2. Navigate to a known request
	console.log('\nStep 2: Navigating to SPISC-2025-121...')

	// Listen to console messages from the page
	let resourceLoaded = false
	page.on('console', msg => {
		const text = msg.text()
		if (text.includes('[RequestDetail] v-if condition: true')) {
			resourceLoaded = true
			console.log('BROWSER LOG: Resource loaded and v-if is true')
		}
	})

	await page.goto('http://localhost:8090/frontend/request/SPISC-2025-121')
	await page.waitForLoadState('networkidle')

	// Wait for the resource to load (detected by console log)
	console.log('Waiting for resource to load...')
	let waitCount = 0
	while (!resourceLoaded && waitCount < 20) {
		await page.waitForTimeout(500)
		waitCount++
	}

	if (resourceLoaded) {
		console.log('✓ Resource loaded successfully')
	} else {
		console.log('⚠ Timeout waiting for resource')
	}

	// Give Vue a moment to update the DOM after data changes
	await page.waitForTimeout(1000)

	// 3. Check if meeting section is visible
	const meetingSection = page.locator('div:has(h2:has-text("Council Meeting"))')
	const isMeetingVisible = await meetingSection.isVisible({ timeout: 2000 }).catch(() => false)
	console.log('\nMeeting section visible:', isMeetingVisible)

	// 4. If not visible, check what's on the page
	if (!isMeetingVisible) {
		const allH2 = await page.locator('h2').allTextContents()
		console.log('All h2 elements on page:', allH2)

		// Check if the div exists but is not visible
		const meetingDivCount = await page.locator('div:has(h2:has-text("Council Meeting"))').count()
		console.log('Council Meeting div count:', meetingDivCount)
	}

	// 5. Take screenshot
	await page.screenshot({ path: '/tmp/request-detail-debug2.png', fullPage: true })
	console.log('✓ Screenshot saved: /tmp/request-detail-debug2.png')

	// 6. Expect the section to be visible
	expect(isMeetingVisible).toBe(true)

	console.log('\n=== END DEBUG ===\n')
})
