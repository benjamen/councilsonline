import { test as setup } from "@playwright/test"

const authFile = "playwright/.auth/user.json"

setup("authenticate", async ({ page, context }) => {
	// Go directly to the Frappe desk login page
	await page.goto("http://localhost:8000/login")

	// Fill in credentials
	await page.fill("#login_email", "Administrator")
	await page.fill("#login_password", "admin")

	// Click login
	await page.click('button[type="submit"]')

	// Wait for successful login
	await page.waitForURL("http://localhost:8000/app**", { timeout: 10000 })

	// Save signed-in state
	await context.storageState({ path: authFile })
})
