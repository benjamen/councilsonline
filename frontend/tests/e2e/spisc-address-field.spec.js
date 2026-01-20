/**
 * SPISC Address Field Saving Test
 *
 * Verifies that the Street/House Number field from PhilippinesAddressInput
 * saves correctly to the backend SPISC Application's address_line field.
 */

import { expect, test } from "@playwright/test"
import { login } from "./fixtures/auth.js"
import { startSPISCApplication } from "./fixtures/request-flow.js"

const BASE_URL = "http://localhost:8090"
const BACKEND_URL = "http://localhost:8090"

test.describe("SPISC Address Field Saving", () => {
	test.setTimeout(120000) // 2 minutes

	test("Verify address_line saves correctly to backend", async ({ page }) => {
		console.log("\n=== Test: Address Field Saving ===\n")

		// Login
		await login(page, { baseUrl: BASE_URL })
		console.log("[Test] Logged in successfully")

		// Start SPISC application
		await startSPISCApplication(page, {
			councilCode: "TAYTAY-PH",
			baseUrl: BASE_URL,
		})
		console.log("[Test] Started SPISC application")

		// Wait for form to be ready
		await page.waitForTimeout(2000)

		// Fill personal info with specific address
		const testAddress = "456 Test Street, Unit 7B"
		const testName = "Address Test User"
		const testDOB = "1960-05-20"

		console.log("[Test] Filling personal information...")

		// 1. Full Name
		const nameInput = await page.locator('input[type="text"]').first()
		await nameInput.fill(testName)
		console.log(`  ✓ Name: ${testName}`)

		// 2. Date of Birth
		const dateInput = await page.locator('input[type="date"]').first()
		await dateInput.fill(testDOB)
		console.log(`  ✓ DOB: ${testDOB}`)

		// 3. Sex - First dropdown
		const allSelects = await page.locator("select").all()
		await allSelects[0].selectOption({ label: "Male" })
		console.log("  ✓ Sex: Male")

		// 4. Civil Status - Second dropdown
		await allSelects[1].selectOption({ label: "Single" })
		console.log("  ✓ Civil Status: Single")

		// 5. Mobile Number
		const textInputs = await page.locator('input[type="text"]').all()
		for (let i = 1; i < textInputs.length; i++) {
			const value = await textInputs[i].inputValue()
			if (!value || value === "") {
				await textInputs[i].fill("9171234567")
				await textInputs[i].blur()
				console.log("  ✓ Mobile: 9171234567")
				break
			}
		}

		await page.waitForTimeout(1000)

		// 6-8. Province, Municipality, Barangay (cascading dropdowns)
		console.log("[Test] Filling address dropdowns...")

		const currentSelects = await page.locator("select").all()
		if (currentSelects.length > 2) {
			await currentSelects[2].selectOption({ index: 1 }) // Province
			console.log("  ✓ Province selected")
			await page.waitForTimeout(800)
		}

		const updatedSelects = await page.locator("select").all()
		if (updatedSelects.length > 3) {
			await updatedSelects[3].selectOption({ index: 1 }) // Municipality
			console.log("  ✓ Municipality selected")
			await page.waitForTimeout(800)
		}

		const finalSelects = await page.locator("select").all()
		if (finalSelects.length > 4) {
			await finalSelects[4].selectOption({ index: 1 }) // Barangay
			console.log("  ✓ Barangay selected")
			await page.waitForTimeout(500)
		}

		// 9. Street / House Number - THIS IS THE CRITICAL FIELD WE'RE TESTING
		console.log(`[Test] Filling street address: "${testAddress}"`)

		const allTextInputs = await page.locator('input[type="text"]').all()
		let addressFilled = false

		// Try to find the street input by placeholder
		const streetInput = page
			.locator(
				'input[placeholder*="Street"], input[placeholder*="street"], input[placeholder*="House"]',
			)
			.first()
		if ((await streetInput.count()) > 0) {
			await streetInput.fill(testAddress)
			await streetInput.blur()
			console.log("  ✓ Found street input by placeholder")
			addressFilled = true
		} else {
			// Fallback: fill the last empty text input
			for (let i = allTextInputs.length - 1; i >= 0; i--) {
				const value = await allTextInputs[i].inputValue()
				if (!value || value === "") {
					await allTextInputs[i].fill(testAddress)
					await allTextInputs[i].blur()
					console.log("  ✓ Filled street address in last empty input")
					addressFilled = true
					break
				}
			}
		}

		if (!addressFilled) {
			console.log("  ⚠ WARNING: Could not find street address input!")
		}

		await page.waitForTimeout(1000)

		// Click Next to save the step
		console.log("[Test] Clicking Next to save step...")
		const nextButton = page.locator('button:has-text("Next")').first()
		await nextButton.click()
		await page.waitForTimeout(3000)

		console.log(
			"[Test] Step 1 saved, attempting to retrieve data from backend...",
		)

		// CRITICAL: Get the draft ID to query the backend
		// Try multiple methods to get the draft ID
		let draftId = null

		// Method 1: From localStorage
		draftId = await page.evaluate(() => {
			return (
				window.localStorage.getItem("current_draft_id") ||
				window.localStorage.getItem("current_spisc_draft") ||
				window.localStorage.getItem("draft_id")
			)
		})

		// Method 2: From URL if it changed
		if (!draftId) {
			const currentUrl = page.url()
			const match = currentUrl.match(/SPISC%20Application\/([^/?]+)/)
			if (match) {
				draftId = decodeURIComponent(match[1])
			}
		}

		// Method 3: From Pinia store
		if (!draftId) {
			draftId = await page.evaluate(() => {
				const state = window.__PINIA__?.state
				if (state) {
					for (const key in state.value) {
						if (state.value[key].currentDraft) {
							return state.value[key].currentDraft.name
						}
					}
				}
				return null
			})
		}

		console.log("[Test] Draft ID:", draftId || "NOT FOUND")

		if (!draftId) {
			// If we can't get the draft ID, try to get it from the latest created SPISC Application
			console.log(
				"[Test] Attempting to find latest SPISC Application via API...",
			)

			const listResponse = await page.goto(
				`${BACKEND_URL}/api/resource/SPISC Application?fields=["name","creation","full_name"]&limit_page_length=1&order_by=creation desc`,
			)
			const listData = await listResponse.json()

			if (listData.data && listData.data.length > 0) {
				draftId = listData.data[0].name
				console.log("[Test] Found latest draft:", draftId)
			}
		}

		expect(draftId).toBeTruthy()
		console.log(`[Test] ✓ Got draft ID: ${draftId}`)

		// Query backend to verify field saved
		console.log("[Test] Querying backend for SPISC Application data...")

		const response = await page.goto(
			`${BACKEND_URL}/api/resource/SPISC Application/${draftId}`,
		)
		const data = await response.json()

		console.log("\n=== BACKEND DATA RETRIEVED ===")
		console.log("  Full Name:", data.data.full_name)
		console.log("  Address Line:", data.data.address_line || "(empty)")
		console.log("  Barangay:", data.data.barangay || "(empty)")
		console.log("  Municipality:", data.data.municipality || "(empty)")
		console.log("  Province:", data.data.province || "(empty)")
		console.log("==============================\n")

		// ASSERTIONS - THE CORE TEST
		console.log("[Test] Running assertions...")

		// Assert: address_line should exist
		expect(data.data.address_line).toBeTruthy()
		console.log("  ✓ address_line field has a value")

		// Assert: address_line should contain our test address
		expect(data.data.address_line).toContain(testAddress)
		console.log(`  ✓ address_line contains: "${testAddress}"`)

		// Assert: barangay should exist
		expect(data.data.barangay).toBeTruthy()
		console.log("  ✓ barangay field has a value")

		// Assert: municipality should exist
		expect(data.data.municipality).toBeTruthy()
		console.log("  ✓ municipality field has a value")

		// Assert: province should exist
		expect(data.data.province).toBeTruthy()
		console.log("  ✓ province field has a value")

		console.log("\n=== ✅ ALL ASSERTIONS PASSED ===")
		console.log("Street/House Number field is saving correctly to backend!")
		console.log(`Saved value: "${data.data.address_line}"`)
		console.log("===============================\n")
	})
})
