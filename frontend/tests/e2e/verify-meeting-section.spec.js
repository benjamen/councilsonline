import { test, expect } from '@playwright/test'

test('Verify Council Meeting section is visible', async ({ page }) => {
	console.log('\n=== VERIFY: Council Meeting Section ===\n')

	// 1. Login
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

	// 2. Navigate to request
	await page.goto('http://localhost:8090/frontend/request/SPISC-2025-121')
	await page.waitForLoadState('networkidle')
	await page.waitForTimeout(3000) // Wait for resource to load
	console.log('✓ Loaded request detail page')

	// 3. Check for Council Meeting h2
	const councilMeetingH2 = page.locator('h2:has-text("Council Meeting")')
	const h2Visible = await councilMeetingH2.isVisible({ timeout: 5000 }).catch(() => false)
	console.log('Council Meeting h2 visible:', h2Visible)

	if (h2Visible) {
		console.log('✓ SUCCESS: Council Meeting section is visible!')

		// Check for Book Meeting button
		const bookMeetingBtn = page.locator('button:has-text("Book Meeting")')
		const btnVisible = await bookMeetingBtn.isVisible({ timeout: 2000 }).catch(() => false)
		console.log('Book Meeting button visible:', btnVisible)
	}

	// 4. Take screenshot
	await page.screenshot({ path: '/tmp/meeting-section-verified.png', fullPage: true })
	console.log('✓ Screenshot saved')

	// Expect h2 to be visible
	expect(h2Visible).toBe(true)

	console.log('\n✓ VERIFICATION COMPLETE!\n')
})
