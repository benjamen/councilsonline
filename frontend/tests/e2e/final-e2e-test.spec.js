import { test, expect } from '@playwright/test'

test('Complete End-to-End: Draft Save & Redirect', async ({ page }) => {
	console.log('\n=== COMPLETE END-TO-END TEST ===\n')

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

	// 2. Start new request
	console.log('\nStep 2: Starting new request...')
	await page.click('button:has-text("New Request")')
	await page.waitForLoadState('networkidle')
	console.log('✓ Clicked New Request')

	// 3. Select Taytay council
	console.log('\nStep 3: Selecting Taytay council...')
	await page.locator('button:has-text("Taytay")').click()
	await page.waitForTimeout(500)
	await page.locator('button:has-text("Next")').click()
	await page.waitForTimeout(1000)
	console.log('✓ Selected Taytay')

	// 4. Select SPISC request type
	console.log('\nStep 4: Selecting SPISC request type...')
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
	console.log('✓ Selected SPISC')

	// 5. Skip process info
	console.log('\nStep 5: Skipping process info...')
	await page.locator('button:has-text("I Understand - Continue to Application")').click()
	await page.waitForTimeout(1000)
	console.log('✓ Skipped process info')

	// 6. Save as draft and verify redirect
	console.log('\nStep 6: Saving draft...')
	const beforeUrl = page.url()
	console.log('URL before save:', beforeUrl)

	const saveDraftButton = page.locator('button:has-text("Save Draft")').first()
	await expect(saveDraftButton).toBeVisible({ timeout: 5000 })
	await saveDraftButton.click()
	await page.waitForTimeout(3000)

	const afterUrl = page.url()
	console.log('URL after save:', afterUrl)

	// 7. Verify redirect happened
	const requestIdMatch = afterUrl.match(/request\/([^\\/\\?]+)/)
	const requestId = requestIdMatch ? requestIdMatch[1] : null

	console.log('\nVerifications:')
	console.log('- Request ID extracted:', requestId)
	console.log('- Is not "new":', requestId !== 'new')
	console.log('- URL changed:', beforeUrl !== afterUrl)
	console.log('- URL contains /request/:', afterUrl.includes('/request/'))

	expect(requestId).toBeTruthy()
	expect(requestId).not.toBe('new')
	expect(beforeUrl).not.toBe(afterUrl)
	console.log('✓ REDIRECT TO REQUEST DETAIL SUCCESSFUL!')

	// 8. Verify Send Message button is visible
	console.log('\nStep 7: Checking Send Message button...')
	const sendMessageButton = page.locator('button:has-text("Send Message")')
	const hasSendMessage = await sendMessageButton.isVisible({ timeout: 5000 }).catch(() => false)

	console.log('- Send Message button visible:', hasSendMessage)
	expect(hasSendMessage).toBe(true)
	console.log('✓ SEND MESSAGE BUTTON VISIBLE!')

	// 9. Take final screenshot
	await page.screenshot({ path: '/tmp/request-detail-final.png' })
	console.log('\n✓ Screenshot saved: /tmp/request-detail-final.png')

	console.log('\n╔═══════════════════════════════════════╗')
	console.log('║  ✓ ALL END-TO-END TESTS PASSED!      ║')
	console.log('╚═══════════════════════════════════════╝\n')

	console.log('Summary of fixes verified:')
	console.log('1. ✅ Draft save redirects to /request/{id}')
	console.log('2. ✅ Request ID is correctly captured (not "new")')
	console.log('3. ✅ Send Message button is visible on request detail page')
	console.log('4. ✅ User lands on correct page after saving draft\n')
})
