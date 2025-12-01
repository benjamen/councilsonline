import { test } from '@playwright/test'

test('Navigate to Step 3', async ({ page }) => {
  await page.goto('http://localhost:8090/frontend')
  await page.waitForTimeout(2000)

  // Should already be logged in from previous test
  console.log('Clicking New Request...')
  await page.click('button:has-text("New Request")')
  await page.waitForTimeout(2000)

  // Step 1
  console.log('Step 1...')
  await page.screenshot({ path: 'test-results/s1.png' })
  const councils = await page.locator('button, div').all()
  for (const c of councils) {
    const txt = await c.textContent().catch(() => '')
    if (txt.includes('Council') && txt.length < 50 && txt.length > 5) {
      console.log('Clicking:', txt.trim())
      await c.click()
      break
    }
  }
  await page.waitForTimeout(1000)
  await page.click('button:has-text("Next")')
  await page.waitForTimeout(2000)

  // Step 2
  console.log('Step 2...')
  await page.screenshot({ path: 'test-results/s2.png' })
  await page.locator('text=Building Consent - Residential New Build').first().click()
  await page.waitForTimeout(1000)
  await page.click('button:has-text("Next")')
  await page.waitForTimeout(3000)

  // Step 3
  console.log('Step 3 - checking page...')
  await page.screenshot({ path: 'test-results/s3.png' })
  
  const url = page.url()
  console.log('URL:', url)
  
  const h2s = await page.locator('h2').allTextContents()
  const btns = await page.locator('button').allTextContents()
  console.log('H2s:', h2s)
  console.log('Buttons:', btns)
  
  const nextBtn = page.locator('button:has-text("Next")')
  const visible = await nextBtn.isVisible().catch(() => false)
  const enabled = await nextBtn.isEnabled().catch(() => false)
  console.log('Next - Visible:', visible, 'Enabled:', enabled)
  
  if (visible && enabled) {
    console.log('Clicking Next on Step 3...')
    await nextBtn.click()
    await page.waitForTimeout(2000)
    await page.screenshot({ path: 'test-results/s4.png' })
    const h2_s4 = await page.locator('h2').first().textContent()
    console.log('Step 4 heading:', h2_s4)
  } else {
    console.log('FAILED: Next button not clickable!')
  }
})
