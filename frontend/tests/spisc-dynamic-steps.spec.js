import { test, expect } from '@playwright/test';

test.describe('SPISC Dynamic Steps - Council Link Flow', () => {
  test('CRITICAL: should show all 5 SPISC dynamic steps from council link', async ({ page, context }) => {
    console.log('=== CRITICAL TEST: All Dynamic Steps Must Appear ===');

    // Clear all caches before starting test
    await context.clearCookies();
    await page.goto('about:blank');

    // Step 0: Navigate with council link (pre-selected and locked)
    console.log('Step 0: Navigating with council link...');
    await page.goto('http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true', {
      waitUntil: 'networkidle'
    });

    // Force a hard reload to bypass all caches
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);

    // Step 1: Request Type Selection
    console.log('Step 1: Selecting SPISC request type...');
    await page.waitForSelector('text=Social Pension for Indigent Senior Citizens', { timeout: 15000 });
    await page.click('text=Social Pension for Indigent Senior Citizens');
    await page.waitForTimeout(500);

    // Verify selection
    const selectedCard = page.locator('.border-blue-600').first();
    await expect(selectedCard).toBeVisible();
    console.log('✓ SPISC selected');

    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // Step 2: Process Info
    console.log('Step 2: Process Information...');
    await expect(page.locator('h2')).toContainText('Process Information');
    console.log('✓ On Process Info step');

    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // CRITICAL CHECK: Step 3 - Personal Information (FIRST DYNAMIC STEP)
    console.log('Step 3: CRITICAL - Verifying Personal Information step...');
    await expect(page.locator('h2')).toContainText('Personal Information', { timeout: 10000 });
    console.log('✅ DYNAMIC STEP 1: Personal Information - PASSED');

    // Verify some fields exist
    const personalInfoFields = page.locator('input, select, textarea').count();
    console.log(`  Found ${await personalInfoFields} form fields`);

    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // CRITICAL CHECK: Step 4 - Household Information (SECOND DYNAMIC STEP)
    console.log('Step 4: CRITICAL - Verifying Household Information step...');
    await expect(page.locator('h2')).toContainText('Household Information', { timeout: 10000 });
    console.log('✅ DYNAMIC STEP 2: Household Information - PASSED');

    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // CRITICAL CHECK: Step 5 - Identity Verification (THIRD DYNAMIC STEP)
    console.log('Step 5: CRITICAL - Verifying Identity Verification step...');
    await expect(page.locator('h2')).toContainText('Identity Verification', { timeout: 10000 });
    console.log('✅ DYNAMIC STEP 3: Identity Verification - PASSED');

    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // CRITICAL CHECK: Step 6 - Supporting Documents (FOURTH DYNAMIC STEP)
    console.log('Step 6: CRITICAL - Verifying Supporting Documents step...');
    await expect(page.locator('h2')).toContainText('Supporting Documents', { timeout: 10000 });
    console.log('✅ DYNAMIC STEP 4: Supporting Documents - PASSED');

    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // CRITICAL CHECK: Step 7 - Declaration (FIFTH DYNAMIC STEP)
    console.log('Step 7: CRITICAL - Verifying Declaration step...');
    await expect(page.locator('h2')).toContainText('Declaration', { timeout: 10000 });
    console.log('✅ DYNAMIC STEP 5: Declaration - PASSED');

    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // Step 8: Review (Final Step)
    console.log('Step 8: Verifying Review step...');
    await expect(page.locator('h2')).toContainText('Review', { timeout: 10000 });
    console.log('✓ On Review step');

    console.log('');
    console.log('════════════════════════════════════════════');
    console.log('✅ ✅ ✅ ALL 5 DYNAMIC STEPS PASSED ✅ ✅ ✅');
    console.log('════════════════════════════════════════════');
    console.log('');
  });

  test('should allow navigation back through dynamic steps', async ({ page, context }) => {
    console.log('=== TEST: Backward Navigation ===');

    // Clear all caches before starting test
    await context.clearCookies();
    await page.goto('about:blank');

    // Get to a dynamic step (simplified flow)
    await page.goto('http://localhost:8080/frontend/request/new?council=TAYTAY-PH&locked=true', {
      waitUntil: 'networkidle'
    });

    // Force a hard reload to bypass all caches
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);

    await page.waitForSelector('text=Social Pension for Indigent Senior Citizens', { timeout: 15000 });
    await page.click('text=Social Pension for Indigent Senior Citizens');
    await page.waitForTimeout(500);
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // Process Info
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(2000);

    // Should be on Personal Information
    await expect(page.locator('h2')).toContainText('Personal Information');

    // Click Previous
    await page.click('button:has-text("Previous")');
    await page.waitForTimeout(2000);

    // Should go back to Process Info
    await expect(page.locator('h2')).toContainText('Process Information');
    console.log('✓ Backward navigation works');
  });
});
