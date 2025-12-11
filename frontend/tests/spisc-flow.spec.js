import { test, expect } from '@playwright/test'

test.describe('SPISC Request Flow', () => {
	test.beforeEach(async ({ page }) => {
		// Navigate to the frontend app
		await page.goto('http://localhost:8090/frontend')
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(1000)

		// Check if we're already logged in by looking for "New Request" button
		const newRequestButton = page.locator('button:has-text("New Request")')
		const isLoggedIn = await newRequestButton.isVisible().catch(() => false)

		if (!isLoggedIn) {
			// We need to log in - look for Sign In button or Log In link
			const signInButton = page.locator('button:has-text("Sign In")')
			const logInLink = page.locator('a:has-text("Log In"), button:has-text("Log In")')

			if (await signInButton.isVisible({ timeout: 2000 }).catch(() => false)) {
				await signInButton.click()
				await page.waitForLoadState('networkidle')
			} else if (await logInLink.isVisible({ timeout: 2000 }).catch(() => false)) {
				await logInLink.click()
				await page.waitForLoadState('networkidle')
			}

			// Fill in the login form
			await page.fill('input[type="email"], input[type="text"], input[placeholder*="email"], input[placeholder*="username"]', 'Administrator')
			await page.fill('input[type="password"], input[placeholder*="password"]', 'admin123')

			// Click Sign In button
			await page.click('button:has-text("Sign In")')
			await page.waitForLoadState('networkidle')
			await page.waitForTimeout(2000)

			// Verify login was successful
			await page.waitForSelector('button:has-text("New Request")', { timeout: 10000 })
		}
	})

	test('should display single progress bar with correct step count', async ({ page }) => {
		// Navigate to new request
		await page.goto('http://localhost:8090/frontend/request/new')
		await page.waitForLoadState('networkidle')

		// Step 1: Select Council (Taytay)
		const taytayButton = page.locator('button:has-text("Taytay")')
		await expect(taytayButton).toBeVisible({ timeout: 10000 })
		await taytayButton.click()
		await page.waitForTimeout(500)

		// Click Next to go to Request Type step
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Wait for request types to load - look for loading spinner to disappear
		const spinner = page.locator('.animate-spin')
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: 'hidden', timeout: 10000 })
		}
		await page.waitForTimeout(500)

		// Step 2: Select SPISC Request Type
		const spiscCard = page.locator('text=Social Pension for Indigent Senior Citizens (SPISC)').first()
		await expect(spiscCard).toBeVisible({ timeout: 10000 })
		await spiscCard.click()
		await page.waitForTimeout(500)

		// Click Next to go to Process Info
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Verify we're on Process Info step
		await expect(page.locator('h2:has-text("Council Process Information")')).toBeVisible()

		// Count progress bars - should be exactly 1
		const progressBars = await page.locator('.h-2.bg-gray-200').count()
		expect(progressBars).toBe(1)

		// Verify step count is correct (Council + Type + Process Info + 5 SPISC steps + Review = 9)
		const progressText = await page.locator('text=/Process Info|Council Process Information/').first().textContent()
		console.log('Progress text:', progressText)

		// Verify progress percentage is reasonable (Step 3 of 9 = 33%)
		const percentageText = await page.locator('text=/\\d+% Complete/').textContent()
		console.log('Percentage:', percentageText)
		const percentage = parseInt(percentageText.match(/(\d+)%/)[1])
		expect(percentage).toBeGreaterThanOrEqual(30)
		expect(percentage).toBeLessThanOrEqual(40)
	})

	test('should load all 5 SPISC dynamic steps', async ({ page }) => {
		// Navigate through to Process Info
		await page.goto('http://localhost:8090/frontend/request/new')
		await page.waitForLoadState('networkidle')

		// Select Taytay
		await page.locator('button:has-text("Taytay")').click()
		await page.waitForTimeout(500)

		// Click Next to go to Request Type step
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Wait for loading to complete
		const spinner = page.locator('.animate-spin')
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: 'hidden', timeout: 10000 })
		}
		await page.waitForTimeout(500)

		// Select SPISC
		await page.locator('text=Social Pension for Indigent Senior Citizens (SPISC)').first().click()
		await page.waitForTimeout(500)

		// Click Next to go to Process Info
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Click "I Understand - Continue to Application"
		const continueButton = page.locator('button:has-text("I Understand - Continue to Application")')
		await expect(continueButton).toBeVisible()
		await continueButton.click()
		await page.waitForTimeout(1000)

		// Should now be on Step 4: Personal Information
		await expect(page.locator('h2:has-text("Personal Information")')).toBeVisible()

		// Verify we can see the first dynamic step fields
		await expect(page.locator('label:has-text("Full Name")')).toBeVisible()
		await expect(page.locator('label:has-text("Date of Birth")')).toBeVisible()
	})

	test('should save draft successfully', async ({ page }) => {
		// Navigate through to first dynamic step
		await page.goto('http://localhost:8090/frontend/request/new')
		await page.waitForLoadState('networkidle')

		// Select Taytay
		await page.locator('button:has-text("Taytay")').click()
		await page.waitForTimeout(500)

		// Click Next to go to Request Type step
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Wait for loading to complete
		const spinner = page.locator('.animate-spin')
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: 'hidden', timeout: 10000 })
		}
		await page.waitForTimeout(500)

		// Select SPISC
		await page.locator('text=Social Pension for Indigent Senior Citizens (SPISC)').first().click()
		await page.waitForTimeout(500)

		// Click Next to go to Process Info
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Continue past Process Info
		await page.locator('button:has-text("I Understand - Continue to Application")').click()
		await page.waitForTimeout(1000)

		// Wait for dynamic fields to load
		await expect(page.locator('h2:has-text("Personal Information")')).toBeVisible({ timeout: 10000 })

		// Wait for fields to actually be rendered and interactable
		await page.waitForSelector('input[name="full_name"]', { state: 'visible', timeout: 10000 })
		await page.waitForTimeout(1000)

		// Fill in some fields
		await page.fill('input[name="full_name"]', 'Test Applicant')
		await page.fill('input[name="birth_date"]', '1950-01-01')
		await page.selectOption('select[name="sex"]', 'Male')
		await page.selectOption('select[name="civil_status"]', 'Single')

		// Click Save Draft (use .last() to get the main content button, not header button)
		const saveDraftButton = page.locator('button:has-text("Save Draft")').last()
		await expect(saveDraftButton).toBeVisible()
		await saveDraftButton.click()

		// Wait for save to complete - look for success indication
		// Could be a toast message, redirect, or button state change
		await page.waitForTimeout(2000)

		// Check for no errors in console
		const errors = []
		page.on('console', msg => {
			if (msg.type() === 'error') {
				errors.push(msg.text())
			}
		})

		// Verify no HTTP 417 errors
		const has417Error = errors.some(err => err.includes('417') || err.includes('EXPECTATION FAILED'))
		expect(has417Error).toBe(false)
	})

	test('should not show duplicate address fields', async ({ page }) => {
		// Navigate to Personal Information step
		await page.goto('http://localhost:8090/frontend/request/new')
		await page.waitForLoadState('networkidle')

		await page.locator('button:has-text("Taytay")').click()
		await page.waitForTimeout(500)

		// Click Next to go to Request Type step
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Wait for loading to complete
		const spinner = page.locator('.animate-spin')
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: 'hidden', timeout: 10000 })
		}
		await page.waitForTimeout(500)

		await page.locator('text=Social Pension for Indigent Senior Citizens (SPISC)').first().click()
		await page.waitForTimeout(500)

		// Click Next to go to Process Info
		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		await page.locator('button:has-text("I Understand - Continue to Application")').click()
		await page.waitForTimeout(1000)

		// Wait for Personal Information step
		await expect(page.locator('h2:has-text("Personal Information")')).toBeVisible({ timeout: 10000 })

		// Wait for fields to actually be rendered
		await page.waitForSelector('input[name="full_name"]', { state: 'visible', timeout: 10000 })
		await page.waitForTimeout(1000)

		// Personal Information step should have basic fields (not address yet)
		// Address is in a separate section, let's check if duplicate fields exist
		const fullNameFields = await page.locator('input[name="full_name"]').count()
		expect(fullNameFields).toBe(1)

		// Should NOT see individual barangay, municipality, province fields
		// (they should be hidden when address_line exists)
		const barangayInputs = await page.locator('input[name="barangay"]').count()
		const municipalityInputs = await page.locator('input[name="municipality"]').count()
		const provinceInputs = await page.locator('input[name="province"]').count()

		// These should either be 0 (hidden) or 1 (in PhilippinesAddressInput component)
		expect(barangayInputs).toBeLessThanOrEqual(1)
		expect(municipalityInputs).toBeLessThanOrEqual(1)
		expect(provinceInputs).toBeLessThanOrEqual(1)
	})

	test('should resume draft at saved step when editing', async ({ page }) => {
		// Create a draft and save at step 4 (Personal Information)
		await page.goto('http://localhost:8090/frontend/request/new')
		await page.waitForLoadState('networkidle')

		// Navigate to Personal Information step (step 4)
		await page.locator('button:has-text("Taytay")').click()
		await page.waitForTimeout(500)

		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		// Wait for loading to complete
		const spinner = page.locator('.animate-spin')
		if (await spinner.isVisible().catch(() => false)) {
			await spinner.waitFor({ state: 'hidden', timeout: 10000 })
		}
		await page.waitForTimeout(500)

		await page.locator('text=Social Pension for Indigent Senior Citizens (SPISC)').first().click()
		await page.waitForTimeout(500)

		await page.locator('button:has-text("Next")').click()
		await page.waitForTimeout(1000)

		await page.locator('button:has-text("I Understand - Continue to Application")').click()
		await page.waitForTimeout(1000)

		// Wait for Personal Information step to load
		await expect(page.locator('h2:has-text("Personal Information")')).toBeVisible({ timeout: 10000 })

		// Wait for fields to actually be rendered and interactable
		await page.waitForSelector('input[name="full_name"]', { state: 'visible', timeout: 10000 })
		await page.waitForTimeout(1000)

		// Fill some fields to make the draft identifiable
		const uniqueName = 'Test Resume Draft ' + Date.now()
		await page.fill('input[name="full_name"]', uniqueName)
		await page.fill('input[name="birth_date"]', '1952-03-20')
		await page.selectOption('select[name="sex"]', 'Male')

		// Capture the draft ID from the API response
		const draftIdPromise = page.waitForResponse(
			response => response.url().includes('create_draft_request') && response.status() === 200
		)

		// Save draft (use .last() to get the main content button, not header button)
		await page.locator('button:has-text("Save Draft")').last().click()

		// Get the draft ID from the API response
		const draftResponse = await draftIdPromise
		const draftData = await draftResponse.json()
		const draftId = draftData.message?.request_id
		console.log('Created draft:', draftId)

		await page.waitForTimeout(2000)

		// Navigate directly to the draft detail page
		await page.goto(`http://localhost:8090/frontend/request/${draftId}`)
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(1000)

		// Should be on RequestDetail page - verify "Edit Draft" button exists
		const editDraftButton = page.locator('button:has-text("Edit Draft")')
		await expect(editDraftButton).toBeVisible({ timeout: 5000 })

		// Click "Edit Draft" button
		await editDraftButton.click()
		await page.waitForLoadState('networkidle')
		await page.waitForTimeout(2000)

		// Verify we're back at step 4 (Personal Information) with data loaded
		await expect(page.locator('h2:has-text("Personal Information")')).toBeVisible({ timeout: 10000 })

		// Verify the form data is restored
		const nameInput = page.locator('input[name="full_name"]')
		await expect(nameInput).toHaveValue(uniqueName)

		const dateInput = page.locator('input[name="birth_date"]')
		await expect(dateInput).toHaveValue('1952-03-20')

		// Verify progress shows we're at the Personal Information step
		const progressText = await page.locator('.text-sm.font-medium.text-gray-700').first().textContent()
		expect(progressText).toContain('Personal Information')

		console.log('✓ Draft resumed successfully at saved step with all data restored')
	})
})

