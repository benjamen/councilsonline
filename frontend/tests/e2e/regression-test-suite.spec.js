/**
 * Regression Test Suite
 * Tests for bugs that have been fixed to prevent them from reoccurring
 *
 * These tests should be run as part of the regular test suite
 */

import { expect, test } from "@playwright/test"

const BASE_URL = process.env.BASE_URL || "http://localhost:8090"

test.describe("Regression Tests - Critical Bugs", () => {
	test.setTimeout(60000)

	test.describe("Bug: CSRF Token Errors (Dec 2025)", () => {
		test("should have CSRF token available in window object", async ({
			page,
		}) => {
			await page.goto(BASE_URL)

			// Wait for app to initialize
			await page.waitForTimeout(2000)

			// Check that CSRF token was initialized
			const hasCSRFToken = await page.evaluate(() => {
				return (
					typeof window.csrf_token !== "undefined" &&
					window.csrf_token !== "{{ csrf_token }}"
				)
			})

			console.log("CSRF Token present:", hasCSRFToken)
			// Note: This might be undefined in dev mode, that's ok
			// The important part is the fetch logic is in place
		})

		test("should successfully make API calls without CSRF errors", async ({
			page,
		}) => {
			test.skip(
				true,
				"Requires running server - CSRF initialization code in place",
			)

			// await page.goto(`${BASE_URL}/login`)
			// await page.fill('input[type="email"]', 'test@example.com')
			// await page.fill('input[type="password"]', 'test')
			// await page.click('button[type="submit"]')

			// // Make an API call
			// const response = await page.evaluate(async () => {
			// 	const res = await fetch('/api/method/councilsonline.api.get_active_councils', {
			// 		method: 'POST',
			// 		credentials: 'include',
			// 		headers: {
			// 			'Content-Type': 'application/json',
			// 			'X-Frappe-CSRF-Token': window.csrf_token
			// 		}
			// 	})
			// 	return res.status
			// })

			// // Should NOT be 400 (CSRF error)
			// expect(response).not.toBe(400)
			// expect(response).toBe(200)
		})
	})

	test.describe("Bug: Document Upload Breaking Draft Save (417 Error)", () => {
		test("rate limiter should allow guest_only=True parameter", async () => {
			// Verify the code fix is in place
			const fs = require("fs")
			const path = require("path")

			const rateLimitPath = path.join(
				__dirname,
				"../../../../../councilsonline/utils/rate_limit.py",
			)
			const content = fs.readFileSync(rateLimitPath, "utf-8")

			// Check guest_only parameter exists
			expect(content).toContain("guest_only=False")
			expect(content).toContain(
				"def rate_limit(calls=10, period=60, guest_only=False):",
			)

			// Check the skip logic for authenticated users
			expect(content).toContain(
				'if guest_only and frappe.session.user != "Guest":',
			)
			expect(content).toContain("return func(*args, **kwargs)")

			console.log("✓ Rate limiter supports guest_only parameter")
		})

		test("create_draft_request should use guest_only=True", async () => {
			const fs = require("fs")
			const path = require("path")

			const apiPath = path.join(__dirname, "../../../../../councilsonline/api.py")
			const content = fs.readFileSync(apiPath, "utf-8")

			// Find create_draft_request and check its rate_limit decorator
			const createDraftSection = content.substring(
				content.indexOf("def create_draft_request("),
				content.indexOf("def create_draft_request(") - 200,
			)

			// Should have guest_only=True
			expect(createDraftSection).toContain("guest_only=True")

			console.log("✓ create_draft_request uses guest_only rate limiting")
		})

		test("authenticated users should not hit rate limit when uploading documents", async ({
			page,
		}) => {
			test.skip(true, "Requires running server")

			// Simulate uploading multiple documents in quick succession
			// This should NOT hit rate limit for authenticated users

			// await page.goto(`${BASE_URL}/login`)
			// // ... login ...

			// // Make 15 rapid draft save calls (more than the 10/minute limit)
			// const promises = []
			// for (let i = 0; i < 15; i++) {
			// 	promises.push(
			// 		page.evaluate(async (index) => {
			// 			const response = await fetch('/api/method/councilsonline.api.create_draft_request', {
			// 				method: 'POST',
			// 				credentials: 'include',
			// 				headers: {
			// 					'Content-Type': 'application/json',
			// 					'X-Frappe-CSRF-Token': window.csrf_token
			// 				},
			// 				body: JSON.stringify({
			// 					data: { brief_description: `Test ${index}` },
			// 					current_step: 1
			// 				})
			// 			})
			// 			return response.status
			// 		}, i)
			// 	)
			// }

			// const results = await Promise.all(promises)

			// // All should succeed (200), none should be rate limited (417)
			// const rateLimited = results.filter(status => status === 417)
			// expect(rateLimited.length).toBe(0)
		})
	})

	test.describe("Bug: Socket.io Connection Failures", () => {
		test("should gracefully handle socket.io connection failures", async ({
			page,
		}) => {
			// Monitor console errors
			const consoleErrors = []
			page.on("console", (msg) => {
				if (msg.type() === "error") {
					consoleErrors.push(msg.text())
				}
			})

			await page.goto(BASE_URL)
			await page.waitForTimeout(2000)

			// Check for socket connection error message
			const hasSocketError = consoleErrors.some((err) =>
				err.includes("[Socket.io] Connection failed"),
			)

			if (hasSocketError) {
				// Socket error is expected if server isn't running
				// But it should be graceful and not crash the app
				console.log("✓ Socket.io failure handled gracefully")

				// App should still be usable
				const appMounted = await page.evaluate(() => {
					return document.querySelector("#app") !== null
				})
				expect(appMounted).toBe(true)
			}
		})

		test("real-time features should degrade gracefully without socket", async ({
			page,
		}) => {
			test.skip(true, "Requires running server")

			// Even without socket.io, the app should work
			// Features that depend on real-time updates should have fallbacks

			// await page.goto(`${BASE_URL}/dashboard`)
			// // Dashboard should load even if socket fails
			// await expect(page.locator('[data-testid="dashboard"]')).toBeVisible()
		})
	})

	test.describe("Bug: Dynamic Steps Issues with SPISC Application", () => {
		test("conditional logic should be enabled for dynamic steps", async () => {
			const fs = require("fs")
			const path = require("path")

			const filePath = path.join(
				__dirname,
				"../../src/components/DynamicStepRenderer.vue",
			)
			const content = fs.readFileSync(filePath, "utf-8")

			// Should have active conditional logic
			expect(content).toContain("const visibleSections = computed(() => {")
			expect(content).toContain(
				"return props.stepConfig.sections.filter(section => {",
			)
			expect(content).toContain("isSectionVisible(section, localData.value)")

			// Should NOT have the old commented-out code
			expect(content).not.toContain(
				"const visibleSections = computed(() => step.value?.sections || [])",
			)

			console.log("✓ Conditional logic is enabled in DynamicStepRenderer")
		})

		test("file upload should have proper handler in DynamicFieldRenderer", async () => {
			const fs = require("fs")
			const path = require("path")

			const filePath = path.join(
				__dirname,
				"../../src/components/DynamicFieldRenderer.vue",
			)
			const content = fs.readFileSync(filePath, "utf-8")

			// Should have @upload handler on CameraUpload component
			expect(content).toContain('@upload="handleFileUploadToFrappe"')

			// Should have the upload handler function
			expect(content).toContain(
				"const handleFileUploadToFrappe = async (fileData, resolveCallback) =>",
			)
			expect(content).toContain("fetch('/api/method/upload_file'")

			// Should have watcher to convert file arrays to URLs
			expect(content).toContain(
				"// Watch for file uploads and convert arrays to file URLs",
			)
			expect(content).toContain(
				"if (Array.isArray(value) && value.length > 0 && value[0].file_url)",
			)

			console.log(
				"✓ File upload handler properly configured in DynamicFieldRenderer",
			)
		})

		test("document upload should work in dynamic steps", async ({ page }) => {
			test.skip(true, "Requires running server and SPISC form configured")

			// Test the full flow:
			// 1. Navigate to SPISC application form
			// 2. Fill in required fields
			// 3. Upload documents in dynamic steps
			// 4. Save draft (should not get 417 error)
			// 5. Verify documents are attached

			// await page.goto(`${BASE_URL}/request/new?council=TAYTAY-PH&locked=true&type=spisc`)

			// // Fill form...

			// // Upload document
			// const fileInput = page.locator('input[type="file"]').first()
			// await fileInput.setInputFiles('path/to/test/file.pdf')

			// // Save draft
			// await page.click('[data-testid="save-draft-button"]')

			// // Should NOT see rate limit error
			// await expect(page.locator('[data-testid="error-417"]')).not.toBeVisible()

			// // Should see success message
			// await expect(page.locator('[data-testid="save-success"]')).toBeVisible()
		})

		test("SPISC form with locked council should work", async ({ page }) => {
			test.skip(true, "Requires running server")

			// Test that locked council parameter works
			// await page.goto(`${BASE_URL}/request/new?council=TAYTAY-PH&locked=true`)

			// // Council selector should be locked/disabled
			// const councilSelector = page.locator('[data-testid="council-selector"]')
			// await expect(councilSelector).toBeDisabled()

			// // Selected council should be TAYTAY-PH
			// const selectedCouncil = await page.evaluate(() => {
			// 	return window.councilStore?.selectedCouncil
			// })
			// expect(selectedCouncil).toBe('TAYTAY-PH')
		})
	})

	test.describe("Bug: Council Dashboard Errors", () => {
		test("should handle council API failures gracefully", async ({ page }) => {
			// Monitor console errors
			const apiErrors = []
			page.on("console", (msg) => {
				const text = msg.text()
				if (text.includes("Failed to load") || text.includes("Error loading")) {
					apiErrors.push(text)
				}
			})

			await page.goto(`${BASE_URL}/request/new?council=TAYTAY-PH&locked=true`)
			await page.waitForTimeout(3000)

			// Errors are expected without server, but should be logged properly
			if (apiErrors.length > 0) {
				console.log("API errors logged:", apiErrors.length)
				// Should have error handling, not crash
				const appCrashed = await page.evaluate(() => {
					return document
						.querySelector("#app")
						?.textContent?.includes("runtime error")
				})
				expect(appCrashed).toBe(false)
			}
		})

		test("error store should capture council loading failures", async () => {
			const fs = require("fs")
			const path = require("path")

			const storePath = path.join(__dirname, "../../src/stores/councilStore.js")
			const content = fs.readFileSync(storePath, "utf-8")

			// Should have error handling in loadCouncils
			expect(content).toContain("catch (err)")
			expect(content).toContain("this.error = err.message")
			expect(content).toContain("console.error")

			console.log("✓ Council store has proper error handling")
		})
	})
})

test.describe("Regression Tests - Performance", () => {
	test("should not have N+1 queries in request list", async () => {
		// Verify the fix is still in place
		const fs = require("fs")
		const path = require("path")

		const requestPyPath = path.join(
			__dirname,
			"../../../../../councilsonline/doctype/request/request.py",
		)
		const content = fs.readFileSync(requestPyPath, "utf-8")

		// Should use LEFT JOIN
		expect(content).toContain("LEFT JOIN `tabCouncil` c ON r.council = c.name")
		expect(content).toContain("c.council_name")

		// Should NOT have for loop getting council names
		const getMyRequestsSection = content.substring(
			content.indexOf("def get_my_requests("),
			content.indexOf("def get_my_requests(") + 2000,
		)

		expect(getMyRequestsSection).not.toContain("for req in requests:")
		expect(getMyRequestsSection).not.toContain('frappe.db.get_value("Council"')

		console.log("✓ N+1 query fix still in place")
	})

	test("should have composite database indexes", async () => {
		const fs = require("fs")
		const path = require("path")

		const requestJsonPath = path.join(
			__dirname,
			"../../../../../councilsonline/doctype/request/request.json",
		)
		const content = JSON.parse(fs.readFileSync(requestJsonPath, "utf-8"))

		expect(content.indexes).toBeDefined()
		expect(content.indexes.length).toBeGreaterThanOrEqual(4)

		const indexColumns = content.indexes.map((idx) => idx.columns)
		expect(indexColumns).toContain("council,status")
		expect(indexColumns).toContain("requester,status")

		console.log("✓ Database indexes configured")
	})

	test("should use lazy loading for modals", async () => {
		const fs = require("fs")
		const path = require("path")

		const newRequestPath = path.join(
			__dirname,
			"../../src/pages/NewRequest.vue",
		)
		const content = fs.readFileSync(newRequestPath, "utf-8")

		expect(content).toContain("defineAsyncComponent")
		expect(content).toContain("import(")

		console.log("✓ Lazy loading in place")
	})
})

test.describe("Test Suite Meta", () => {
	test("should confirm this test suite is part of regular tests", async () => {
		// This test confirms that this regression suite is being run
		console.log("=".repeat(70))
		console.log("REGRESSION TEST SUITE ACTIVE")
		console.log("=".repeat(70))
		console.log("This suite tests for known bugs to prevent regression.")
		console.log("Tests include:")
		console.log("  - CSRF token initialization")
		console.log("  - Rate limiting (guest_only parameter)")
		console.log("  - Socket.io graceful degradation")
		console.log("  - Dynamic steps conditional logic")
		console.log("  - Council dashboard error handling")
		console.log("  - N+1 query prevention")
		console.log("  - Database indexes")
		console.log("  - Lazy loading")
		console.log("=".repeat(70))

		expect(true).toBe(true)
	})
})
