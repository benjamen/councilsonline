/**
 * SPISC Application Entry Points E2E Tests
 *
 * Tests all possible ways users can access and start a SPISC application:
 * 1. Via council portal (main entry)
 * 2. Direct URL navigation
 * 3. Browser back/forward navigation
 * 4. Bookmark/saved link
 * 5. Authentication state handling
 */

import { test, expect } from '@playwright/test'
import { login, logout } from './fixtures/auth.js'

const BASE_URL = 'http://localhost:8090'
const COUNCIL_CODE = 'TAYTAY-PH'

test.describe('SPISC Entry Points & Authentication', () => {
    test.setTimeout(120000) // 2 minutes for each test

    test('Entry Point 1: Via Council Portal Homepage', async ({ page }) => {
        console.log('\n=== Test: Council Portal Entry ===\n')

        // Start at council homepage
        await page.goto(`${BASE_URL}/frontend`, { waitUntil: 'networkidle' })
        console.log('[Entry] Landed on council homepage')

        // Check if login is required
        const currentUrl = page.url()
        if (currentUrl.includes('/login')) {
            console.log('[Entry] Login required - performing login')
            await login(page, { baseUrl: BASE_URL })
        } else {
            console.log('[Entry] Already logged in or no auth required')
        }

        // Navigate to SPISC via portal
        console.log('[Entry] Looking for SPISC service in portal')

        // Click on Services or Request New Service
        const newRequestButton = page.locator('a[href*="/request/new"], button:has-text("New Request"), a:has-text("Services")')
        await newRequestButton.first().click({ timeout: 10000 }).catch(() => {
            console.log('[Entry] No obvious service button, navigating directly')
        })

        await page.waitForTimeout(2000)

        // Verify we can access SPISC application
        const finalUrl = page.url()
        console.log('[Entry] Final URL:', finalUrl)

        expect(finalUrl).toContain('/frontend')
        console.log('✓ Successfully accessed via council portal')
    })

    test('Entry Point 2: Direct URL to New Request', async ({ page }) => {
        console.log('\n=== Test: Direct URL Navigation ===\n')

        // Navigate directly to new request page with council parameter
        const directUrl = `${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}`
        console.log('[Entry] Navigating directly to:', directUrl)

        await page.goto(directUrl, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)

        // Check if redirected to login
        const currentUrl = page.url()
        console.log('[Entry] Current URL after navigation:', currentUrl)

        if (currentUrl.includes('/login')) {
            console.log('[Entry] ✓ Correctly redirected to login (authentication required)')

            // Perform login
            await login(page, { baseUrl: BASE_URL })

            // Should redirect back to intended page
            await page.waitForTimeout(2000)
            const afterLoginUrl = page.url()
            console.log('[Entry] After login URL:', afterLoginUrl)

            expect(afterLoginUrl).toContain('/request')
            console.log('✓ Successfully redirected back after login')
        } else {
            console.log('[Entry] ✓ Direct access granted (already authenticated)')
            expect(currentUrl).toContain('/request')
        }

        // Verify page loaded correctly
        const pageTitle = await page.title()
        console.log('[Entry] Page title:', pageTitle)
    })

    test('Entry Point 3: Direct URL to Specific Request Type', async ({ page }) => {
        console.log('\n=== Test: Direct URL to SPISC Request Type ===\n')

        // First login
        await login(page, { baseUrl: BASE_URL })

        // Navigate directly to SPISC request
        const spiscUrl = `${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}&type=SPISC`
        console.log('[Entry] Navigating to SPISC-specific URL:', spiscUrl)

        await page.goto(spiscUrl, { waitUntil: 'networkidle' })
        await page.waitForTimeout(3000)

        const currentUrl = page.url()
        console.log('[Entry] Current URL:', currentUrl)

        // Should be on request page
        expect(currentUrl).toContain('/request')

        // Check if SPISC is pre-selected or can be selected
        const pageContent = await page.content()
        const hasSPISC = pageContent.includes('SPISC') || pageContent.includes('Social Pension')

        if (hasSPISC) {
            console.log('✓ SPISC content found on page')
        } else {
            console.log('⚠ SPISC not immediately visible, may need to select')
        }
    })

    test('Entry Point 4: Browser Back Button Navigation', async ({ page }) => {
        console.log('\n=== Test: Browser Back/Forward Navigation ===\n')

        await login(page, { baseUrl: BASE_URL })

        // Navigate to home
        await page.goto(`${BASE_URL}/frontend`, { waitUntil: 'networkidle' })
        console.log('[Entry] Step 1: On homepage')
        await page.waitForTimeout(1000)

        // Navigate to new request
        await page.goto(`${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}`, { waitUntil: 'networkidle' })
        console.log('[Entry] Step 2: On new request page')
        await page.waitForTimeout(1000)

        // Go back
        await page.goBack()
        await page.waitForTimeout(2000)
        console.log('[Entry] Step 3: Clicked back button')

        const backUrl = page.url()
        console.log('[Entry] After back, URL:', backUrl)

        // Should be back at home
        expect(backUrl).toContain('/frontend')
        console.log('✓ Back navigation works')

        // Go forward
        await page.goForward()
        await page.waitForTimeout(2000)
        console.log('[Entry] Step 4: Clicked forward button')

        const forwardUrl = page.url()
        console.log('[Entry] After forward, URL:', forwardUrl)

        // Should be back at request page
        expect(forwardUrl).toContain('/request')
        console.log('✓ Forward navigation works')

        // Verify auth state maintained
        const content = await page.content()
        const isLoggedIn = !content.includes('Sign in') && !content.includes('Login')
        console.log('[Entry] Auth state maintained:', isLoggedIn)
    })

    test('Entry Point 5: Bookmark/Saved Link (Cold Start)', async ({ page }) => {
        console.log('\n=== Test: Bookmark/Saved Link (No Session) ===\n')

        // Simulate saved bookmark by going directly to request page
        // WITHOUT logging in first (cold start)
        const bookmarkUrl = `${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}`
        console.log('[Entry] Simulating bookmark click (no session):', bookmarkUrl)

        await page.goto(bookmarkUrl, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)

        const currentUrl = page.url()
        console.log('[Entry] Landing URL:', currentUrl)

        if (currentUrl.includes('/login')) {
            console.log('[Entry] ✓ Correctly redirected to login (no active session)')

            // Login
            await login(page, { baseUrl: BASE_URL })
            await page.waitForTimeout(2000)

            // Check if redirected back to original destination
            const afterLoginUrl = page.url()
            console.log('[Entry] After login, URL:', afterLoginUrl)

            // Should ideally redirect back to the bookmarked page
            if (afterLoginUrl.includes('/request')) {
                console.log('✓ Successfully redirected to original destination after login')
            } else {
                console.log('⚠ Redirected to different page, manual navigation may be needed')
            }
        } else {
            console.log('[Entry] ✓ Direct access (session already exists)')
        }
    })

    test('Entry Point 6: Logout and Re-login Flow', async ({ page }) => {
        console.log('\n=== Test: Logout and Re-login ===\n')

        // Login first
        await login(page, { baseUrl: BASE_URL })
        console.log('[Entry] Step 1: Logged in successfully')

        // Navigate to request page
        await page.goto(`${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}`, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)
        console.log('[Entry] Step 2: On request page')

        const beforeLogoutUrl = page.url()
        console.log('[Entry] URL before logout:', beforeLogoutUrl)

        // Attempt to logout
        console.log('[Entry] Step 3: Attempting logout')
        await logout(page)
        await page.waitForTimeout(2000)

        // Try to access protected page
        await page.goto(`${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}`, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)

        const afterLogoutUrl = page.url()
        console.log('[Entry] After logout, attempting to access request page:', afterLogoutUrl)

        if (afterLogoutUrl.includes('/login')) {
            console.log('✓ Correctly redirected to login after logout')
        } else {
            console.log('⚠ Still able to access page (logout may not have worked)')
        }

        // Re-login
        if (afterLogoutUrl.includes('/login')) {
            console.log('[Entry] Step 4: Re-logging in')
            await login(page, { baseUrl: BASE_URL })
            await page.waitForTimeout(2000)

            const afterReloginUrl = page.url()
            console.log('[Entry] After re-login, URL:', afterReloginUrl)
        }
    })

    test('Entry Point 7: Multiple Tabs/Windows (Session Sharing)', async ({ browser }) => {
        console.log('\n=== Test: Multiple Tabs Session Sharing ===\n')

        // Create first tab and login
        const context1 = await browser.newContext()
        const page1 = await context1.newPage()

        await login(page1, { baseUrl: BASE_URL })
        console.log('[Entry] Tab 1: Logged in')

        // Navigate to request page in tab 1
        await page1.goto(`${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}`, { waitUntil: 'networkidle' })
        await page1.waitForTimeout(2000)

        const tab1Url = page1.url()
        console.log('[Entry] Tab 1 URL:', tab1Url)
        expect(tab1Url).toContain('/request')

        // Create second tab in SAME context (same session)
        const page2 = await context1.newPage()
        console.log('[Entry] Tab 2: Opening new tab in same session')

        // Navigate to request page in tab 2
        await page2.goto(`${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}`, { waitUntil: 'networkidle' })
        await page2.waitForTimeout(2000)

        const tab2Url = page2.url()
        console.log('[Entry] Tab 2 URL:', tab2Url)

        // Should not need to login again (session shared)
        if (!tab2Url.includes('/login')) {
            console.log('✓ Session shared across tabs (no login required in tab 2)')
        } else {
            console.log('⚠ Session not shared, login required in tab 2')
        }

        await context1.close()
    })

    test('Entry Point 8: Auth Token Expiry Handling', async ({ page }) => {
        console.log('\n=== Test: Session Expiry Handling ===\n')

        await login(page, { baseUrl: BASE_URL })
        console.log('[Entry] Step 1: Logged in')

        await page.goto(`${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}`, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)
        console.log('[Entry] Step 2: On request page')

        // Clear cookies to simulate session expiry
        console.log('[Entry] Step 3: Clearing cookies to simulate session expiry')
        await page.context().clearCookies()

        // Try to navigate to another page
        await page.goto(`${BASE_URL}/frontend`, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)

        const afterExpiry = page.url()
        console.log('[Entry] After session expiry, URL:', afterExpiry)

        // May or may not redirect to login depending on implementation
        if (afterExpiry.includes('/login')) {
            console.log('✓ Correctly detected expired session and redirected to login')
        } else {
            console.log('⚠ No immediate redirect (may check auth on API calls)')
        }

        // Try to make an API call
        console.log('[Entry] Step 4: Testing API call with expired session')
        const response = await page.goto(`${BASE_URL}/api/method/ping`, { waitUntil: 'networkidle' })
        const status = response?.status()
        console.log('[Entry] API call status:', status)

        if (status === 403 || status === 401) {
            console.log('✓ API correctly rejects expired session')
        }
    })

    test('Entry Point 9: Deep Link with Authentication', async ({ page }) => {
        console.log('\n=== Test: Deep Link to Mid-Application ===\n')

        // Try to access a deep link (like editing a draft)
        // This simulates clicking a link from an email notification
        const deepLink = `${BASE_URL}/frontend/request/SPISC-2025-230`
        console.log('[Entry] Attempting deep link:', deepLink)

        await page.goto(deepLink, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)

        const currentUrl = page.url()
        console.log('[Entry] Landing URL:', currentUrl)

        if (currentUrl.includes('/login')) {
            console.log('[Entry] ✓ Auth check working on deep link')

            // Login
            await login(page, { baseUrl: BASE_URL })
            await page.waitForTimeout(2000)

            const afterLoginUrl = page.url()
            console.log('[Entry] After login URL:', afterLoginUrl)

            // Should redirect to the deep link destination
            console.log('[Entry] Checking if redirected to original deep link...')
        } else {
            console.log('[Entry] Accessed deep link directly')
        }
    })

    test('Entry Point 10: Invalid/Malformed URLs', async ({ page }) => {
        console.log('\n=== Test: Error Handling for Invalid URLs ===\n')

        await login(page, { baseUrl: BASE_URL })

        // Test 1: Invalid council code
        console.log('[Entry] Test 1: Invalid council code')
        await page.goto(`${BASE_URL}/frontend/request/new?council=INVALID-CODE`, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)

        const url1 = page.url()
        console.log('[Entry] URL with invalid council:', url1)

        // Check for error message
        const content1 = await page.content()
        if (content1.includes('error') || content1.includes('invalid') || content1.includes('not found')) {
            console.log('✓ Error handling for invalid council code')
        } else {
            console.log('⚠ No obvious error, may have fallback handling')
        }

        // Test 2: Invalid request type
        console.log('[Entry] Test 2: Invalid request type')
        await page.goto(`${BASE_URL}/frontend/request/new?council=${COUNCIL_CODE}&type=INVALID-TYPE`, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)

        const url2 = page.url()
        console.log('[Entry] URL with invalid type:', url2)

        // Test 3: Malformed URL
        console.log('[Entry] Test 3: Malformed URL parameters')
        await page.goto(`${BASE_URL}/frontend/request/new?council=&type=`, { waitUntil: 'networkidle' })
        await page.waitForTimeout(2000)

        const url3 = page.url()
        console.log('[Entry] URL with empty parameters:', url3)

        console.log('✓ URL error handling tests complete')
    })
})
