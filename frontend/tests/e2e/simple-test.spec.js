import { test } from '@playwright/test'

test('Simple check what is on dashboard', async ({ page }) => {
	await page.goto('http://localhost:8090/frontend')
	await page.waitForLoadState('networkidle')

	// Login
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

	const currentUrl = page.url()
	console.log('After login URL:', currentUrl)

	// Get all button text
	const allButtons = await page.locator('button, a').all()
	console.log('\nAll clickable elements:')
	for (const btn of allButtons.slice(0, 20)) {
		const text = await btn.innerText().catch(() => '')
		if (text && text.trim()) {
			console.log('  -', text.trim())
		}
	}

	await page.screenshot({ path: '/tmp/dashboard-after-login.png' })
	console.log('\nScreenshot saved to /tmp/dashboard-after-login.png')
})
