import { test } from '@playwright/test'

test('Debug RequestDetail page resource loading', async ({ page }) => {
	console.log('\n=== DEBUG: RequestDetail Resource Loading ===\n')

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

	// 2. Navigate to a known request (SPISC-2025-121 from previous test)
	console.log('\nStep 2: Navigating to SPISC-2025-121...')

	// Listen to console messages from the page
	page.on('console', msg => {
		const text = msg.text()
		if (text.includes('[RequestDetail]')) {
			console.log('BROWSER LOG:', text)
		}
	})

	await page.goto('http://localhost:8090/frontend/request/SPISC-2025-121')
	await page.waitForLoadState('networkidle')
	await page.waitForTimeout(5000) // Give time for resources to load
	console.log('✓ Loaded request detail page')

	// 3. Check if meeting section is visible
	const meetingSection = page.locator('div:has(h3:has-text("Council Meeting"))')
	const isMeetingVisible = await meetingSection.isVisible({ timeout: 2000 }).catch(() => false)
	console.log('\nMeeting section visible:', isMeetingVisible)

	// 4. Take screenshot
	await page.screenshot({ path: '/tmp/request-detail-debug.png' })
	console.log('✓ Screenshot saved: /tmp/request-detail-debug.png')

	console.log('\n=== END DEBUG ===\n')
})
