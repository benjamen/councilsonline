import { test, expect } from '@playwright/test'

test('Final Verification: All Features Working', async ({ page }) => {
	console.log('\n=== FINAL VERIFICATION TEST ===\n')

	// 1. Login
	console.log('Step 1: Logging in...')
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

	// 2. Create a new draft request
	console.log('\nStep 2: Creating new SPISC request...')
	await page.click('button:has-text("New Application"), a:has-text("New Application")')
	await page.waitForLoadState('networkidle')

	// Select Taytay
	await page.locator('button:has-text("Taytay")').click()
	await page.waitForTimeout(500)
	await page.locator('button:has-text("Next")').click()
	await page.waitForTimeout(1000)

	// Select SPISC
	const spinner = page.locator('.animate-spin')
	if (await spinner.isVisible().catch(() => false)) {
		await spinner.waitFor({ state: 'hidden', timeout: 10000 })
	}

	const spiscCard = page.locator('text=Social Pension for Indigent Senior Citizens (SPISC)').first()
	await expect(spiscCard).toBeVisible({ timeout: 10000 })
	await spiscCard.click()
	await page.waitForTimeout(500)
	await page.locator('button:has-text("Next")').click()
	await page.waitForTimeout(1000)

	// Skip process info
	await page.locator('button:has-text("I Understand - Continue to Application")').click()
	await page.waitForTimeout(1000)
	console.log('✓ At application step')

	// Save draft
	console.log('\nStep 3: Saving draft...')
	const beforeUrl = page.url()
	const saveDraftButton = page.locator('button:has-text("Save Draft")').first()
	await expect(saveDraftButton).toBeVisible({ timeout: 5000 })
	await saveDraftButton.click()
	await page.waitForTimeout(3000)

	const afterUrl = page.url()
	const requestIdMatch = afterUrl.match(/request\/([^\\/\\?]+)/)
	const requestId = requestIdMatch ? requestIdMatch[1] : null

	expect(requestId).toBeTruthy()
	expect(requestId).not.toBe('new')
	expect(beforeUrl).not.toBe(afterUrl)
	console.log(`✓ Redirected to /request/${requestId}`)

	// Wait for page to fully load with all resources
	await page.waitForTimeout(3000)

	// 3. Verify Send Message button
	console.log('\nStep 4: Checking Send Message button...')
	const sendMessageButton = page.locator('button:has-text("Send Message")')
	const hasSendMessage = await sendMessageButton.isVisible({ timeout: 5000 }).catch(() => false)
	expect(hasSendMessage).toBe(true)
	console.log('✓ Send Message button is visible')

	// 4. Verify Council Meeting section
	console.log('\nStep 5: Checking Council Meeting section...')
	const councilMeetingH2 = page.locator('h2:has-text("Council Meeting")')
	const hasMeetingSection = await councilMeetingH2.isVisible({ timeout: 5000 }).catch(() => false)
	expect(hasMeetingSection).toBe(true)
	console.log('✓ Council Meeting section is visible')

	// 5. Verify Request Council Meeting button
	const requestMeetingBtn = page.locator('button:has-text("Request Council Meeting")')
	const hasRequestMeetingBtn = await requestMeetingBtn.isVisible({ timeout: 5000 }).catch(() => false)
	expect(hasRequestMeetingBtn).toBe(true)
	console.log('✓ Request Council Meeting button is visible')

	// 6. Take screenshot
	await page.screenshot({ path: '/tmp/final-verification.png', fullPage: true })
	console.log('\n✓ Screenshot saved: /tmp/final-verification.png')

	console.log('\n╔═══════════════════════════════════════════════════╗')
	console.log('║  ✅ ALL FEATURES VERIFIED WORKING!              ║')
	console.log('╚═══════════════════════════════════════════════════╝\n')

	console.log('Summary of verified features:')
	console.log('1. ✅ Draft save redirects to /request/{id}')
	console.log('2. ✅ Send Message button visible on detail page')
	console.log('3. ✅ Council Meeting section visible on detail page')
	console.log('4. ✅ Request Council Meeting button visible')
	console.log('5. ✅ Request type config loaded successfully\n')
})
