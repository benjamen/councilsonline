/**
 * Request flow fixtures for E2E tests
 * Provides reusable functions for navigating request forms
 */

/**
 * Select a council on the new request page
 * @param {Page} page - Playwright page object
 * @param {string} councilName - Council name to select (e.g., 'TayTay Council')
 */
export async function selectCouncil(page, councilName) {
    console.log(`[RequestFlow] Selecting council: ${councilName}`)

    const councilButton = page.locator(`text=${councilName}`).first()
    await councilButton.click()

    console.log(`[RequestFlow] Clicked ${councilName}`)
}

/**
 * Select a request type
 * @param {Page} page - Playwright page object
 * @param {string} requestTypeName - Request type name or pattern (e.g., 'SPISC' or 'Social Pension')
 */
export async function selectRequestType(page, requestTypeName) {
    console.log(`[RequestFlow] Selecting request type: ${requestTypeName}`)

    // Try to find the request type card/button
    const requestTypeButton = page.locator(`text=/${requestTypeName}/i`).first()
    await requestTypeButton.click()

    console.log(`[RequestFlow] Clicked request type containing: ${requestTypeName}`)
}

/**
 * Click the "I Understand - Continue to Application" button
 * @param {Page} page - Playwright page object
 */
export async function clickUnderstandButton(page) {
    console.log('[RequestFlow] Clicking "I Understand" button')

    const understandButton = page.locator('button:has-text("I Understand")').first()
    await understandButton.click()

    console.log('[RequestFlow] Clicked "I Understand" button')
    await page.waitForTimeout(2000)
}

/**
 * Click the Next button to proceed to next step
 * @param {Page} page - Playwright page object
 */
export async function clickNext(page) {
    console.log('[RequestFlow] Clicking Next button')

    const nextButton = page.locator('button:has-text("Next")').first()
    await nextButton.click()

    console.log('[RequestFlow] Clicked Next button')
    await page.waitForTimeout(2000)
}

/**
 * Upload a file using the file input
 * @param {Page} page - Playwright page object
 * @param {string} filePath - Path to file to upload
 * @param {number} inputIndex - Index of file input if multiple exist (default: 0)
 */
export async function uploadFile(page, filePath, inputIndex = 0) {
    console.log(`[RequestFlow] Uploading file: ${filePath}`)

    const fileInputs = page.locator('input[type="file"]')
    const count = await fileInputs.count()

    console.log(`[RequestFlow] Found ${count} file input(s)`)

    if (count === 0) {
        throw new Error('No file input found on page')
    }

    const fileInput = fileInputs.nth(inputIndex)
    await fileInput.setInputFiles(filePath)

    console.log(`[RequestFlow] File uploaded to input ${inputIndex}`)

    // Wait for upload to process
    await page.waitForTimeout(2000)
}

/**
 * Fill a form field by label
 * @param {Page} page - Playwright page object
 * @param {string} label - Field label text
 * @param {string} value - Value to fill
 */
export async function fillFieldByLabel(page, label, value) {
    console.log(`[RequestFlow] Filling field "${label}" with value: ${value}`)

    // Try to find the input by associated label
    const input = page.locator(`input:below(:text("${label}"))`).first()
    await input.fill(value)

    console.log(`[RequestFlow] Filled "${label}"`)
}

/**
 * Navigate to new request page for a specific council
 * @param {Page} page - Playwright page object
 * @param {string} councilCode - Council code (e.g., 'TAYTAY-PH')
 * @param {string} baseUrl - Base URL (default: 'http://localhost:8080')
 */
export async function navigateToNewRequest(page, councilCode, baseUrl = 'http://localhost:8080') {
    const url = `${baseUrl}/frontend/request/new?council=${councilCode}`
    console.log(`[RequestFlow] Navigating to: ${url}`)

    await page.goto(url, { waitUntil: 'networkidle' })
    await page.waitForTimeout(2000)

    console.log('[RequestFlow] New request page loaded')
}

/**
 * Complete full SPISC application flow up to the form
 * @param {Page} page - Playwright page object
 * @param {Object} options - Options
 * @param {string} options.councilCode - Council code (default: 'TAYTAY-PH')
 * @param {string} options.baseUrl - Base URL (default: 'http://localhost:8080')
 */
export async function startSPISCApplication(page, options = {}) {
    const {
        councilCode = 'TAYTAY-PH',
        baseUrl = 'http://localhost:8080'
    } = options

    console.log('[RequestFlow] Starting SPISC application flow')

    // Navigate to new request page
    await navigateToNewRequest(page, councilCode, baseUrl)

    // Council is pre-selected via URL, so go straight to selecting request type
    await selectRequestType(page, 'SPISC')

    // Click Next to go to "About This Application" page
    await clickNext(page)

    // Click "I Understand - Continue to Application"
    await clickUnderstandButton(page)

    console.log('[RequestFlow] SPISC application flow complete, now on form page')
}
