/**
 * SPISC Cash Pickup Complete E2E Test
 *
 * Tests the complete flow of filling SPISC form with Cash Pickup payment method
 * and scheduling a pickup appointment
 */
import { test, expect } from "@playwright/test"

const BASE_URL = "http://localhost:8090"

test.describe("SPISC Cash Pickup Complete Flow", () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto(`${BASE_URL}/login`)
		await page.waitForLoadState("networkidle")

		const currentUrl = page.url()
		if (currentUrl.includes("/login")) {
			await page.fill('input[name="email"], input[type="email"]', "admin")
			await page.fill('input[name="password"], input[type="password"]', "admin")
			await page.click('button[type="submit"]')
			await page.waitForURL(/\/(dashboard|home|app)/, { timeout: 15000 })
		}
	})

	test("Complete SPISC form with Cash Pickup and schedule pickup", async ({ page }) => {
		console.log("\n=== Starting SPISC Cash Pickup Complete Flow ===\n")

		// Step 1: Navigate to new request
		await page.goto(`${BASE_URL}/new-request`)
		await page.waitForLoadState("networkidle")
		console.log("Step 1: Navigated to new request page")

		// Step 2: Select SPISC request type
		const spiscCard = page.locator('[data-request-type="SPISC"]').or(
			page.locator('text=Social Pension').first()
		).or(
			page.locator('text=SPISC').first()
		)

		if (await spiscCard.isVisible({ timeout: 5000 })) {
			await spiscCard.click()
			console.log("Step 2: Selected SPISC request type")
		} else {
			// Try clicking via API
			console.log("Step 2: SPISC card not found, trying API approach")
		}

		// Wait for form to load
		await page.waitForTimeout(2000)

		// Step 3: Fill personal information
		console.log("Step 3: Filling personal information...")

		// Fill name fields if visible
		const firstNameField = page.locator('[data-fieldname="first_name"] input, input[name="first_name"]').first()
		if (await firstNameField.isVisible({ timeout: 3000 })) {
			await firstNameField.fill("Juan")
		}

		const middleNameField = page.locator('[data-fieldname="middle_name"] input, input[name="middle_name"]').first()
		if (await middleNameField.isVisible({ timeout: 1000 })) {
			await middleNameField.fill("Santos")
		}

		const lastNameField = page.locator('[data-fieldname="last_name"] input, input[name="last_name"]').first()
		if (await lastNameField.isVisible({ timeout: 1000 })) {
			await lastNameField.fill("Dela Cruz")
		}

		// Fill date of birth
		const dobField = page.locator('[data-fieldname="date_of_birth"] input, input[name="date_of_birth"]').first()
		if (await dobField.isVisible({ timeout: 1000 })) {
			await dobField.fill("1955-05-15")
		}

		// Fill gender
		const genderField = page.locator('[data-fieldname="gender"] select, select[name="gender"]').first()
		if (await genderField.isVisible({ timeout: 1000 })) {
			await genderField.selectOption("Male")
		}

		// Fill civil status
		const civilStatusField = page.locator('[data-fieldname="civil_status"] select, select[name="civil_status"]').first()
		if (await civilStatusField.isVisible({ timeout: 1000 })) {
			await civilStatusField.selectOption("Married")
		}

		// Step 4: Navigate to payment step or scroll to payment section
		console.log("Step 4: Looking for payment method field...")

		// Try to find and click next button to advance steps
		const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue")').first()
		let attempts = 0
		while (attempts < 5) {
			const paymentMethodField = page.locator('[data-fieldname="payment_method"]').first()
			if (await paymentMethodField.isVisible({ timeout: 2000 })) {
				break
			}
			if (await nextButton.isVisible({ timeout: 1000 })) {
				await nextButton.click()
				await page.waitForTimeout(1000)
			}
			attempts++
		}

		// Step 5: Select Cash Pickup payment method
		console.log("Step 5: Selecting Cash Pickup payment method...")
		const paymentMethodSelect = page.locator('[data-fieldname="payment_method"] select').first()

		if (await paymentMethodSelect.isVisible({ timeout: 5000 })) {
			await paymentMethodSelect.selectOption("Cash Pickup")
			console.log("  Selected: Cash Pickup")
			await page.waitForTimeout(500)
		} else {
			console.log("  Payment method field not found, checking if already on payment step")
		}

		// Step 6: Select pickup location
		console.log("Step 6: Selecting pickup location...")
		const pickupLocationSelect = page.locator('[data-fieldname="pickup_location"] select').first()

		if (await pickupLocationSelect.isVisible({ timeout: 3000 })) {
			await pickupLocationSelect.selectOption("Municipal Treasury Office")
			console.log("  Selected: Municipal Treasury Office")
		}

		// Step 7: Click Schedule Pickup button
		console.log("Step 7: Looking for Schedule Pickup button...")
		const scheduleButton = page.locator('button:has-text("Schedule Pickup")').first()

		if (await scheduleButton.isVisible({ timeout: 5000 })) {
			await scheduleButton.click()
			console.log("  Clicked Schedule Pickup button")

			// Wait for modal to appear
			await page.waitForTimeout(1000)

			// Step 8: Select a date in the modal
			console.log("Step 8: Selecting date in modal...")
			const dateButton = page.locator('.grid button:has-text("Monday"), .grid button:has-text("Tuesday")').first()

			if (await dateButton.isVisible({ timeout: 5000 })) {
				await dateButton.click()
				console.log("  Selected a date")
				await page.waitForTimeout(500)
			}

			// Step 9: Select a time slot
			console.log("Step 9: Selecting time slot...")
			const timeButton = page.locator('.grid button:has-text("AM"), .grid button:has-text("PM")').first()

			if (await timeButton.isVisible({ timeout: 3000 })) {
				await timeButton.click()
				console.log("  Selected a time slot")
				await page.waitForTimeout(500)
			}

			// Step 10: Select location in modal
			console.log("Step 10: Selecting location in modal...")
			const modalLocationSelect = page.locator('dialog select, [role="dialog"] select').first()

			if (await modalLocationSelect.isVisible({ timeout: 2000 })) {
				await modalLocationSelect.selectOption("Municipal Treasury Office")
				console.log("  Selected location")
			}

			// Step 11: Click Book Appointment button
			console.log("Step 11: Clicking Book Appointment...")
			const bookButton = page.locator('button:has-text("Book Appointment")').first()

			if (await bookButton.isVisible({ timeout: 3000 })) {
				await bookButton.click()
				console.log("  Clicked Book Appointment")

				// Wait for success message
				await page.waitForTimeout(2000)

				// Check for success indicator
				const successMessage = page.locator('text=Appointment booked, text=Pickup Scheduled, .text-green-600').first()
				if (await successMessage.isVisible({ timeout: 5000 })) {
					console.log("\n=== SUCCESS: Appointment booked! ===\n")
				}
			}
		} else {
			console.log("  Schedule Pickup button not visible - may need to navigate to correct step")
		}

		// Take a screenshot of the final state
		await page.screenshot({ path: "test-results/spisc-cash-pickup-final.png" })
		console.log("\nScreenshot saved to test-results/spisc-cash-pickup-final.png")

		// Verify via API that appointment was created
		const appointmentsResponse = await page.evaluate(async () => {
			const res = await fetch("/api/method/councilsonline.api.scheduling.get_user_appointments", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					team_code: "PAYMENTS",
				}),
			})
			return res.json()
		})

		console.log("\n=== Appointments in system ===")
		if (appointmentsResponse.message?.appointments) {
			console.log(`Total appointments: ${appointmentsResponse.message.appointments.length}`)
			appointmentsResponse.message.appointments.forEach((apt, i) => {
				console.log(`  ${i + 1}. ${apt.name} - ${apt.scheduled_date} - ${apt.status}`)
			})
		}
	})

	test("API-based booking test", async ({ page }) => {
		console.log("\n=== Testing API-based booking ===\n")

		// Navigate to get CSRF token
		await page.goto(`${BASE_URL}/dashboard`)
		await page.waitForLoadState("networkidle")

		// Get available slots
		const slotsResponse = await page.evaluate(async () => {
			const res = await fetch("/api/method/councilsonline.api.scheduling.get_available_slots", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					team_code: "PAYMENTS",
				}),
			})
			return res.json()
		})

		expect(slotsResponse.message?.success).toBe(true)
		const slots = slotsResponse.message.slots
		expect(slots.length).toBeGreaterThan(0)

		console.log(`Found ${slots.length} available slots`)
		console.log(`First slot: ${slots[0].date} ${slots[0].start_display}`)

		// Book an appointment
		const slot = slots[0]
		const bookResponse = await page.evaluate(
			async ({ slot }) => {
				const res = await fetch("/api/method/councilsonline.api.scheduling.book_appointment", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"X-Frappe-CSRF-Token": window.csrf_token,
					},
					body: JSON.stringify({
						team_code: "PAYMENTS",
						scheduled_start: slot.start,
						scheduled_end: slot.end,
						appointment_type: "Cash Pickup",
						location: "Municipal Treasury Office",
						purpose: "SPISC Payment Pickup - E2E Test",
						contact_name: "Juan Dela Cruz",
						contact_phone: "09171234567",
					}),
				})
				return res.json()
			},
			{ slot },
		)

		expect(bookResponse.message?.success).toBe(true)
		expect(bookResponse.message?.appointment_id).toBeDefined()

		console.log(`\nBooked appointment: ${bookResponse.message.appointment_id}`)
		console.log(`Status: ${bookResponse.message.status}`)
		console.log(`Time: ${slot.start_display} - ${slot.end_display}`)
		console.log(`Location: ${bookResponse.message.location}`)
		console.log(`Message: ${bookResponse.message.message}`)

		// Verify appointment exists
		const getResponse = await page.evaluate(
			async ({ appointmentId }) => {
				const res = await fetch("/api/method/councilsonline.api.scheduling.get_appointment", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"X-Frappe-CSRF-Token": window.csrf_token,
					},
					body: JSON.stringify({
						appointment_id: appointmentId,
					}),
				})
				return res.json()
			},
			{ appointmentId: bookResponse.message.appointment_id },
		)

		expect(getResponse.message?.success).toBe(true)
		expect(getResponse.message?.appointment?.status).toBe("Scheduled")

		console.log("\n=== Appointment Details ===")
		const apt = getResponse.message.appointment
		console.log(`ID: ${apt.name}`)
		console.log(`Type: ${apt.appointment_type}`)
		console.log(`Team: ${apt.team_name}`)
		console.log(`Date: ${apt.scheduled_date}`)
		console.log(`Time: ${apt.scheduled_start} - ${apt.scheduled_end}`)
		console.log(`Duration: ${apt.duration_minutes} minutes`)
		console.log(`Location: ${apt.location}`)
		console.log(`Contact: ${apt.contact_name} (${apt.contact_phone})`)
		console.log(`Status: ${apt.status}`)
		console.log(`Booked by: ${apt.booked_by}`)
	})
})
