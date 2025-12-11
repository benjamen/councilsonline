import { test, expect } from '@playwright/test';

test.describe('Council Website Flow', () => {
  test('should complete SPISC application from council link', async ({ page }) => {
    // Enable console logging to see the error
    page.on('console', msg => {
      console.log(`[Browser ${msg.type()}]`, msg.text());
    });

    page.on('pageerror', error => {
      console.log(`[Page Error] ${error.message}`);
    });

    // Navigate to council site first to simulate council referral
    console.log('Step 1: Navigating to council website...');
    await page.goto('http://localhost:8090/?council=TAYTAY-PH', { waitUntil: 'networkidle' });

    // Wait a moment for any scripts to load
    await page.waitForTimeout(2000);

    // Click on a link that goes to main site with council pre-selected
    // This simulates clicking from council website
    console.log('Step 2: Looking for council link to main site...');

    // Let's manually navigate with council param like a council site would
    await page.goto('http://localhost:8080/new-request?council=TAYTAY-PH&locked=true', { waitUntil: 'networkidle' });

    console.log('Step 3: Verifying council is pre-selected...');
    await page.waitForTimeout(1000);

    // Check if we're on step 2 (request type selection)
    const heading = await page.textContent('h2');
    console.log('Current heading:', heading);

    // Select SPISC
    console.log('Step 4: Selecting SPISC request type...');
    await page.click('text=Social Pension for Indigent Senior Citizens');

    await page.waitForTimeout(1000);

    // Click Next
    console.log('Step 5: Clicking Next to Process Info step...');
    await page.click('button:has-text("Next")');

    await page.waitForTimeout(2000);

    // Check for console errors
    console.log('Step 6: Checking current URL and state...');
    const currentUrl = page.url();
    console.log('Current URL:', currentUrl);

    // Wait to see if redirect happens
    await page.waitForTimeout(3000);

    const finalUrl = page.url();
    console.log('Final URL:', finalUrl);

    // Check if we got redirected to request detail page
    expect(finalUrl).toContain('/request/');
  });
});
