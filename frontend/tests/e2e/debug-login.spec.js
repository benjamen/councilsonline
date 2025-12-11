import { test, expect } from '@playwright/test'

test('debug login flow', async ({ page }) => {
	// Listen to console messages
	page.on('console', msg => console.log(`BROWSER ${msg.type()}: ${msg.text()}`))
	page.on('pageerror', error => console.log(`PAGE ERROR: ${error.message}`))

	// Navigate to frontend
	console.log('Navigating to frontend...')
	await page.goto('http://localhost:8090/frontend')
	await page.waitForLoadState('networkidle')
	await page.waitForTimeout(2000)

	// Take screenshot
	await page.screenshot({ path: '/tmp/01-initial-page.png' })
	console.log('Screenshot saved: 01-initial-page.png')

	// Check what's on the page
	const bodyText = await page.locator('body').innerText()
	console.log('Page text:', bodyText.substring(0, 500))

	// Look for various login elements
	const signInButton = page.locator('button:has-text("Sign In")')
	const logInLink = page.locator('a:has-text("Log In"), button:has-text("Log In")')
	const newAppButton = page.locator('button:has-text("New Application")')

	const hasSignIn = await signInButton.isVisible({ timeout: 2000 }).catch(() => false)
	const hasLogIn = await logInLink.isVisible({ timeout: 2000 }).catch(() => false)
	const hasNewApp = await newAppButton.isVisible({ timeout: 2000 }).catch(() => false)

	console.log('Has Sign In button:', hasSignIn)
	console.log('Has Log In link:', hasLogIn)
	console.log('Has New Application button:', hasNewApp)

	if (hasNewApp) {
		console.log('Already logged in!')
		return
	}

	if (hasSignIn) {
		console.log('Clicking Sign In button...')
		await signInButton.click()
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(1000)
		await page.screenshot({ path: '/tmp/02-after-signin-click.png' })
	} else if (hasLogIn) {
		console.log('Clicking Log In link...')
		await logInLink.click()
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(1000)
		await page.screenshot({ path: '/tmp/02-after-login-click.png' })
	}

	// Look for login form
	const emailInput = page.locator('input[type="email"], input[type="text"], input[placeholder*="email"], input[placeholder*="username"]')
	const passwordInput = page.locator('input[type="password"], input[placeholder*="password"]')
	const submitButton = page.locator('button:has-text("Sign In")')

	const hasEmail = await emailInput.isVisible({ timeout: 2000 }).catch(() => false)
	const hasPassword = await passwordInput.isVisible({ timeout: 2000 }).catch(() => false)
	const hasSubmit = await submitButton.isVisible({ timeout: 2000 }).catch(() => false)

	console.log('Has email input:', hasEmail)
	console.log('Has password input:', hasPassword)
	console.log('Has submit button:', hasSubmit)

	if (hasEmail && hasPassword) {
		console.log('Filling login form...')
		await emailInput.fill('Administrator')
		await passwordInput.fill('admin123')
		await page.screenshot({ path: '/tmp/03-form-filled.png' })

		console.log('Submitting form...')
		await submitButton.click()
		await page.waitForTimeout(5000)
		await page.screenshot({ path: '/tmp/04-after-submit.png' })

		// Check if logged in
		const stillHasNewApp = await newAppButton.isVisible({ timeout: 5000 }).catch(() => false)
		console.log('After login - Has New Application button:', stillHasNewApp)

		const currentUrl = page.url()
		console.log('Current URL:', currentUrl)

		const finalBodyText = await page.locator('body').innerText()
		console.log('Final page text:', finalBodyText.substring(0, 500))
	}
})
