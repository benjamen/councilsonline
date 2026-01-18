/**
 * SPISC Pickup Scheduling E2E Tests
 *
 * Tests the pickup appointment scheduling feature for Cash Pickup payment method
 */
import { test, expect } from "@playwright/test"

const BASE_URL = "http://localhost:8090"

test.describe("SPISC Pickup Scheduling", () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto(`${BASE_URL}/login`)
		await page.waitForLoadState("networkidle")

		// Check if already logged in
		const currentUrl = page.url()
		if (currentUrl.includes("/login")) {
			await page.fill('input[name="email"], input[type="email"]', "admin")
			await page.fill('input[name="password"], input[type="password"]', "admin")
			await page.click('button[type="submit"]')
			await page.waitForURL(/\/(dashboard|home)/, { timeout: 10000 })
		}
	})

	test("Scheduling API returns available slots", async ({ page }) => {
		// Test the scheduling API directly
		const response = await page.evaluate(async () => {
			const res = await fetch("/api/method/lodgeick.api.scheduling.get_available_slots", {
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

		expect(response.message?.success).toBe(true)
		expect(response.message?.slots).toBeDefined()
		expect(response.message?.slots.length).toBeGreaterThan(0)
		expect(response.message?.config).toBeDefined()
		expect(response.message?.config.team_code).toBe("PAYMENTS")

		console.log(`Found ${response.message.slots.length} available slots`)
		console.log(`Team: ${response.message.config.team_name}`)
		console.log(`Duration: ${response.message.config.duration_minutes} minutes`)
		console.log(`Locations: ${response.message.config.locations.join(", ")}`)
	})

	test("Team config API returns correct configuration", async ({ page }) => {
		const response = await page.evaluate(async () => {
			const res = await fetch("/api/method/lodgeick.api.scheduling.get_team_config", {
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

		expect(response.message?.success).toBe(true)
		expect(response.message?.config).toBeDefined()

		const config = response.message.config
		expect(config.team_code).toBe("PAYMENTS")
		expect(config.team_name).toBe("Payments Team")
		expect(config.duration_minutes).toBe(15)
		expect(config.available_durations).toContain(15)
		expect(config.available_durations).toContain(30)
		expect(config.locations).toContain("Municipal Treasury Office")
		expect(config.locations).toContain("Barangay Hall")
		expect(config.locations).toContain("OSCA Office")
	})

	test("Can book an appointment slot", async ({ page }) => {
		// First get available slots
		const slotsResponse = await page.evaluate(async () => {
			const res = await fetch("/api/method/lodgeick.api.scheduling.get_available_slots", {
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

		// Book the first available slot
		const slot = slots[0]
		const bookResponse = await page.evaluate(
			async ({ slot }) => {
				const res = await fetch("/api/method/lodgeick.api.scheduling.book_appointment", {
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
						purpose: "E2E Test Appointment",
					}),
				})
				return res.json()
			},
			{ slot },
		)

		expect(bookResponse.message?.success).toBe(true)
		expect(bookResponse.message?.appointment_id).toBeDefined()
		expect(bookResponse.message?.status).toBe("Scheduled")

		console.log(`Booked appointment: ${bookResponse.message.appointment_id}`)
		console.log(`Status: ${bookResponse.message.status}`)
		console.log(`Location: ${bookResponse.message.location}`)
	})

	test("Booked slot is no longer available", async ({ page }) => {
		// Get current available slots
		const slotsResponse1 = await page.evaluate(async () => {
			const res = await fetch("/api/method/lodgeick.api.scheduling.get_available_slots", {
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

		const initialCount = slotsResponse1.message.slots.length

		// Book the first slot
		const slot = slotsResponse1.message.slots[0]
		await page.evaluate(
			async ({ slot }) => {
				const res = await fetch("/api/method/lodgeick.api.scheduling.book_appointment", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"X-Frappe-CSRF-Token": window.csrf_token,
					},
					body: JSON.stringify({
						team_code: "PAYMENTS",
						scheduled_start: slot.start,
						scheduled_end: slot.end,
						appointment_type: "Cash Pickup Test",
						location: "Barangay Hall",
					}),
				})
				return res.json()
			},
			{ slot },
		)

		// Get slots again
		const slotsResponse2 = await page.evaluate(async () => {
			const res = await fetch("/api/method/lodgeick.api.scheduling.get_available_slots", {
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

		// The booked slot should no longer be in the available slots
		const bookedSlotStillAvailable = slotsResponse2.message.slots.some((s) => s.start === slot.start)
		expect(bookedSlotStillAvailable).toBe(false)

		console.log(`Initial slots: ${initialCount}`)
		console.log(`After booking: ${slotsResponse2.message.slots.length}`)
	})
})
