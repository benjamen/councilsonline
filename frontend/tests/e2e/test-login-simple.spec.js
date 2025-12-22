import { test, expect } from '@playwright/test';

test('Simple login test', async ({ page }) => {
  console.log('Navigating to login page...');
  await page.goto('http://localhost:8090/frontend/login');

  // Wait for page to load
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);

  console.log('Current URL:', page.url());
  console.log('Page title:', await page.title());

  // Take a screenshot
  await page.screenshot({ path: '/tmp/login-page.png', fullPage: true });
  console.log('Screenshot saved to /tmp/login-page.png');

  // Try to find input fields
  const inputs = await page.locator('input').count();
  console.log('Number of input fields found:', inputs);

  // Find text/email input
  const emailInput = page.locator('input[type="text"], input[type="email"], input[name="usr"]').first();
  const emailVisible = await emailInput.isVisible().catch(() => false);
  console.log('Email input visible:', emailVisible);

  if (emailVisible) {
    await emailInput.fill('Administrator');
    console.log('Filled email field');
  }

  // Find password input
  const passwordInput = page.locator('input[type="password"], input[name="pwd"]').first();
  const passwordVisible = await passwordInput.isVisible().catch(() => false);
  console.log('Password input visible:', passwordVisible);

  if (passwordVisible) {
    await passwordInput.fill('admin123');
    console.log('Filled password field');
  }

  // Find submit button
  const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first();
  const buttonVisible = await submitButton.isVisible().catch(() => false);
  console.log('Submit button visible:', buttonVisible);

  if (buttonVisible) {
    await submitButton.click();
    console.log('Clicked login button');

    // Wait for navigation
    await page.waitForTimeout(5000);
    console.log('After login URL:', page.url());

    // Check if login succeeded
    if (!page.url().includes('/login')) {
      console.log('✓ LOGIN SUCCESSFUL');
    } else {
      console.log('✗ Login failed - still on login page');
      await page.screenshot({ path: '/tmp/login-failed.png', fullPage: true });
    }
  }

  // Keep browser open for inspection
  await page.waitForTimeout(10000);
});
