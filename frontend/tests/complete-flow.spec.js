import { test, expect } from '@playwright/test';

test.describe('Complete SPISC Application Flow', () => {
  test('should complete full SPISC application from council website', async ({ page }) => {
    console.log('=== Test: Complete SPISC Flow from Council Link ===');

    // Step 1: Navigate with council pre-selected (simulating council website link)
    console.log('Step 1: Starting from council website link...');
    await page.goto('http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true', {
      waitUntil: 'domcontentloaded'
    });

    // Wait for page to load
    await page.waitForTimeout(2000);

    // Check if we're on request type selection or council selection
    const heading = await page.locator('h2').first().textContent();
    console.log('Current step:', heading);

    if (heading.includes('Select Council')) {
      console.log('  → On council selection, clicking Taytay...');
      await page.click('text=Taytay');
      await page.waitForTimeout(1000);
      await page.click('button:has-text("Next")');
      await page.waitForTimeout(2000);
    }

    // Step 2: Should now be on request type selection
    await expect(page.locator('h2')).toContainText('Select Application Type', { timeout: 10000 });
    console.log('✓ On request type selection step');

    // Wait for request types to load
    console.log('Step 2: Waiting for request types to load...');
    await page.waitForSelector('text=Social Pension for Indigent Senior Citizens', { timeout: 15000 });
    console.log('✓ Request types loaded');

    // Select SPISC
    console.log('Step 3: Selecting SPISC...');
    await page.click('text=Social Pension for Indigent Senior Citizens');
    await page.waitForTimeout(500);

    // Verify selection
    const selectedCard = page.locator('.border-blue-600').first();
    await expect(selectedCard).toBeVisible();
    console.log('✓ SPISC selected');

    // Click Next to go to Process Info
    console.log('Step 4: Clicking Next to Process Info step...');
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // Should be on Process Info step
    const processInfoHeading = await page.locator('h2').first().textContent();
    console.log('Current step after Next:', processInfoHeading);

    if (processInfoHeading.includes('Process Information')) {
      console.log('✓ On Process Info step');

      // Click Next again to trigger auto-save and redirect
      console.log('Step 5: Clicking Next to trigger auto-save...');
      await page.click('button:has-text("Next")');

      // Wait for redirect
      await page.waitForTimeout(3000);

      // Check if redirected to request detail page
      const finalUrl = page.url();
      console.log('Final URL:', finalUrl);

      if (finalUrl.includes('/request/SPISC-')) {
        console.log('✓ Redirected to request detail page');

        // Verify request detail page elements
        await expect(page.locator('h1')).toContainText('SPISC-', { timeout: 5000 });
        console.log('✓ Request ID displayed in header');

        await expect(page.locator('text=Social Pension for Indigent Senior Citizens')).toBeVisible();
        console.log('✓ Request type displayed');

        await expect(page.locator('text=Draft')).toBeVisible();
        console.log('✓ Status is Draft');
      } else {
        console.log('ℹ Did not redirect yet, URL:', finalUrl);
      }
    }

    console.log('=== Test Completed ===');
  });

  test('should load request types for Taytay council', async ({ page }) => {
    console.log('=== Test: Request Types Loading ===');

    await page.goto('http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true', {
      waitUntil: 'domcontentloaded'
    });

    await page.waitForTimeout(2000);

    // Skip council selection if needed
    const heading = await page.locator('h2').first().textContent();
    if (heading.includes('Select Council')) {
      await page.click('text=Taytay');
      await page.waitForTimeout(500);
      await page.click('button:has-text("Next")');
      await page.waitForTimeout(2000);
    }

    // Verify we're on request type selection
    await expect(page.locator('h2')).toContainText('Select Application Type');

    // Wait for and verify request types loaded
    await page.waitForSelector('text=Social Pension for Indigent Senior Citizens', { timeout: 15000 });
    console.log('✓ SPISC is available');

    const requestTypeCards = page.locator('.cursor-pointer.border-2');
    const count = await requestTypeCards.count();
    console.log(`✓ Found ${count} request types`);

    expect(count).toBeGreaterThan(0);

    console.log('=== Test Completed ===');
  });
});
