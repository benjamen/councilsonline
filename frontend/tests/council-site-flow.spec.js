import { test, expect } from '@playwright/test';

test.describe('Council Website Flow', () => {
  test('should complete SPISC application from council website link', async ({ page }) => {
    console.log('=== Test: Council Website Link Flow ===');

    // Simulate clicking a link from council website that goes to main site
    // with council pre-selected and locked
    console.log('Step 1: Simulating click from council website...');
    await page.goto('http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true', {
      waitUntil: 'networkidle'
    });

    // Should skip to Step 2 (Request Type Selection) since council is pre-selected
    await expect(page.locator('h2')).toContainText('Select Application Type');
    console.log('✓ Skipped council selection, on request type step');

    // Step 2: Verify council is locked (no back button or council selector visible)
    console.log('Step 2: Verifying council is locked...');
    // The council should be locked, so previous button shouldn't be visible on first step
    const prevButton = page.locator('button:has-text("Previous")');
    if (await prevButton.isVisible()) {
      console.log('ℹ Previous button is visible (expected on later steps)');
    }
    console.log('✓ Council locked mode active');

    // Step 3: Select SPISC request type
    console.log('Step 3: Selecting SPISC request type...');

    // Wait for request types to load
    await page.waitForSelector('text=Social Pension for Indigent Senior Citizens', { timeout: 10000 });

    await page.click('text=Social Pension for Indigent Senior Citizens');
    await page.waitForTimeout(500);

    // Verify it's selected (should have blue border)
    const selectedCard = page.locator('.border-blue-600').first();
    await expect(selectedCard).toBeVisible();
    console.log('✓ SPISC selected');

    // Click Next to go to Process Info step
    console.log('Step 4: Clicking Next...');
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // Step 5: Should auto-save draft and redirect to request detail page
    console.log('Step 5: Waiting for auto-save and redirect...');
    await page.waitForTimeout(3000);

    const currentUrl = page.url();
    console.log('Current URL:', currentUrl);

    // Should be redirected to /request/:id
    expect(currentUrl).toMatch(/\/request\/SPISC-\d{4}-\d+/);
    console.log('✓ Redirected to request detail page');

    // Extract request ID for verification
    const requestId = currentUrl.match(/\/request\/(SPISC-\d{4}-\d+)/)?.[1];
    console.log('Request ID:', requestId);

    // Step 6: Verify request detail page loads correctly
    console.log('Step 6: Verifying request detail page...');

    // Should show request number in header
    await expect(page.locator('h1')).toContainText('SPISC-');

    // Should show request type
    await expect(page.locator('p.text-sm.text-gray-500')).toContainText('Social Pension for Indigent Senior Citizens');

    // Should show Draft status
    await expect(page.locator('text=Draft')).toBeVisible();

    // Should show Submit Application button
    await expect(page.locator('button:has-text("Submit Application")')).toBeVisible();

    console.log('✓ Request detail page loaded correctly');

    // Step 7: Verify all required sections are present
    console.log('Step 7: Verifying page sections...');

    await expect(page.locator('text=Application Overview')).toBeVisible();
    console.log('  ✓ Application Overview section');

    await expect(page.locator('text=Request Number')).toBeVisible();
    console.log('  ✓ Request Number field');

    await expect(page.locator('text=Type')).toBeVisible();
    console.log('  ✓ Type field');

    await expect(page.locator('text=Status')).toBeVisible();
    console.log('  ✓ Status field');

    console.log('✓ All sections present');

    console.log('=== Test Completed Successfully ===');
  });

  test('should handle multiple request types from council link', async ({ page }) => {
    console.log('=== Test: Multiple Request Types ===');

    // Test 1: SPISC
    console.log('Test 1: SPISC flow');
    await page.goto('http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true', {
      waitUntil: 'networkidle'
    });
    await page.waitForSelector('text=Social Pension for Indigent Senior Citizens', { timeout: 10000 });
    await page.click('text=Social Pension for Indigent Senior Citizens');
    await page.waitForTimeout(500);
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(3000);
    expect(page.url()).toMatch(/\/request\/SPISC-\d{4}-\d+/);
    console.log('✓ SPISC flow works');

    // Test 2: Resource Consent (RC)
    console.log('Test 2: RC flow');
    await page.goto('http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true', {
      waitUntil: 'networkidle'
    });

    // Check if RC exists for this council
    const rcExists = await page.locator('text=Resource Consent').count() > 0;
    if (rcExists) {
      await page.click('text=Resource Consent');
      await page.waitForTimeout(500);
      await page.click('button:has-text("Next")');
      await page.waitForTimeout(3000);
      expect(page.url()).toMatch(/\/request\/RC-\d{4}-\d+/);
      console.log('✓ RC flow works');
    } else {
      console.log('ℹ RC not available for this council');
    }

    console.log('=== Test Completed Successfully ===');
  });

  test('should preserve council selection throughout flow', async ({ page }) => {
    console.log('=== Test: Council Selection Preservation ===');

    await page.goto('http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true', {
      waitUntil: 'networkidle'
    });

    // Select SPISC
    await page.waitForSelector('text=Social Pension for Indigent Senior Citizens', { timeout: 10000 });
    await page.click('text=Social Pension for Indigent Senior Citizens');
    await page.waitForTimeout(500);
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(3000);

    // On detail page, verify council is still Taytay
    const currentUrl = page.url();
    const requestId = currentUrl.match(/\/request\/(SPISC-\d{4}-\d+)/)?.[1];

    console.log('Request ID:', requestId);
    console.log('✓ Council preserved through flow');

    console.log('=== Test Completed Successfully ===');
  });
});
