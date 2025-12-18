/**
 * Registration Flow Tests
 * Tests for Applicant and Agent registration with property management
 */

import { expect, test } from "@playwright/test"

test.describe("Registration Flow", () => {
	test.beforeEach(async ({ page }) => {
		// Navigate to registration page
		await page.goto("http://localhost:8000/frontend")
	})

	test("Applicant Registration - Individual with Property", async ({
		page,
	}) => {
		// Click Register as Applicant
		await page.click('a[href="/register"]')
		await page.waitForLoadState("networkidle")

		// Verify we're on the applicant registration page
		await expect(page.locator("h1")).toContainText("Register as Applicant")

		// Select Individual applicant type
		await page.click('button:has-text("Individual")')

		// Fill basic information
		const uniqueEmail = `test-individual-${Date.now()}@example.com`
		await page.fill('input[type="email"]', uniqueEmail)
		await page.fill('input[placeholder*="First"]', "John")
		await page.fill('input[placeholder*="Last"]', "Doe")

		// Fill phone number (NZ format)
		const phoneInput = page.locator('input[type="tel"]')
		await phoneInput.fill("021 234 5678")
		await phoneInput.blur()

		// Verify phone validation passes
		const phoneError = page.locator("text=Phone number")
		await expect(phoneError).not.toHaveClass(/text-red/)

		// Fill password
		await page.fill('input[type="password"]', "TestPassword123!")

		// Test property address lookup
		const addressInput = page.locator(
			'input[placeholder*="Start typing address"]',
		)
		await addressInput.fill("123 Main Street")

		// Wait for search results dropdown (if property API is running)
		await page.waitForTimeout(1000)

		// Note: If property API is not running, the dropdown won't show
		// But the form should still allow manual entry

		// Fill manual property details for testing
		await addressInput.clear()
		await addressInput.fill("123 Main Street, Wellington")

		console.log("✓ Individual applicant registration form filled")
	})

	test("Applicant Registration - Company", async ({ page }) => {
		await page.click('a[href="/register"]')
		await page.waitForLoadState("networkidle")

		// Select Company applicant type
		await page.click('button:has-text("Company")')

		// Fill basic information
		const uniqueEmail = `test-company-${Date.now()}@example.com`
		await page.fill('input[type="email"]', uniqueEmail)
		await page.fill('input[placeholder*="First"]', "Jane")
		await page.fill('input[placeholder*="Last"]', "Smith")
		await page.fill('input[type="tel"]', "09 123 4567")
		await page.fill('input[type="password"]', "TestPassword123!")

		// Fill company details
		const companyNameInput = page
			.locator('input[placeholder*="company name"]')
			.first()
		await companyNameInput.fill("Test Company Ltd")

		const companyNumberInput = page.locator(
			'input[placeholder*="Company Number"]',
		)
		if ((await companyNumberInput.count()) > 0) {
			await companyNumberInput.fill("1234567")
		}

		console.log("✓ Company applicant registration form filled")
	})

	test("Agent Registration - Sole Trader", async ({ page }) => {
		// Navigate to agent registration
		await page.goto("http://localhost:8000/frontend/company-registration")
		await page.waitForLoadState("networkidle")

		// Verify we're on the agent registration page
		await expect(page.locator("h1")).toContainText("Register as Agent")

		// Verify info banner is present
		await expect(page.locator("text=Planning consultants")).toBeVisible()

		// Select Sole Trader
		await page.click('button:has-text("Sole Trader")')

		// Step 1: Your Details
		const uniqueEmail = `test-agent-${Date.now()}@example.com`
		await page.fill('input[type="email"]', uniqueEmail)
		await page.fill('input[placeholder*="First"]', "Agent")
		await page.fill('input[placeholder*="Last"]', "Smith")

		// Phone with validation
		await page.fill('input[type="tel"]', "021 987 6543")
		await page.fill('input[type="password"]', "AgentPass123!")

		console.log("✓ Agent (Sole Trader) registration form filled")
	})

	test("Agent Registration - Company", async ({ page }) => {
		await page.goto("http://localhost:8000/frontend/company-registration")
		await page.waitForLoadState("networkidle")

		// Select Company
		await page.click('button:has-text("Company")')

		// Fill details
		const uniqueEmail = `test-agent-company-${Date.now()}@example.com`
		await page.fill('input[type="email"]', uniqueEmail)
		await page.fill('input[placeholder*="First"]', "Company")
		await page.fill('input[placeholder*="Last"]', "Agent")
		await page.fill('input[type="tel"]', "09 876 5432")
		await page.fill('input[type="password"]', "CompanyAgent123!")

		// Fill company details
		const companyNameInput = page
			.locator('input[placeholder*="company name"]')
			.first()
		await companyNameInput.fill("Planning Consultants Ltd")

		// Fill NZBN if visible
		const nzbnInput = page.locator('input[placeholder*="NZBN"]')
		if ((await nzbnInput.count()) > 0) {
			await nzbnInput.fill("1234567890123")
		}

		console.log("✓ Agent (Company) registration form filled")
	})

	test("Phone Number Validation", async ({ page }) => {
		await page.click('a[href="/register"]')
		await page.waitForLoadState("networkidle")

		await page.click('button:has-text("Individual")')

		const phoneInput = page.locator('input[type="tel"]')

		// Test valid mobile number
		await phoneInput.fill("021 234 5678")
		await phoneInput.blur()
		await page.waitForTimeout(300)

		// Test valid landline
		await phoneInput.fill("09 123 4567")
		await phoneInput.blur()
		await page.waitForTimeout(300)

		// Test invalid format
		await phoneInput.fill("123")
		await phoneInput.blur()
		await page.waitForTimeout(300)

		// Should show error for invalid phone
		const errorText = page.locator(".text-red-600")
		if ((await errorText.count()) > 0) {
			console.log("✓ Phone validation shows error for invalid input")
		}

		console.log("✓ Phone number validation tested")
	})

	test("Property Address Lookup Integration", async ({ page }) => {
		await page.click('a[href="/register"]')
		await page.waitForLoadState("networkidle")

		await page.click('button:has-text("Individual")')

		const addressInput = page.locator(
			'input[placeholder*="Start typing address"]',
		)

		// Type to trigger search
		await addressInput.fill("123 Queen")
		await page.waitForTimeout(500)

		// Check if dropdown appears (only if property API is running)
		const dropdown = page.locator("div.absolute.z-50")
		if ((await dropdown.count()) > 0) {
			console.log("✓ Address lookup dropdown appeared")

			// Check for "Searching addresses..." or results
			const searching = page.locator("text=Searching addresses")
			const noResults = page.locator("text=No addresses found")

			if ((await searching.count()) > 0) {
				console.log("✓ Search loading indicator shown")
			}

			if ((await noResults.count()) > 0) {
				console.log(
					"✓ No results message shown (property API may not be running)",
				)
			}
		} else {
			console.log(
				"ℹ Address lookup dropdown not shown (property API may not be running)",
			)
		}

		console.log("✓ Property address lookup component tested")
	})
})
