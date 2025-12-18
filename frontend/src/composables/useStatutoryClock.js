import { createResource } from "frappe-ui"
import { computed, ref, watch } from "vue"

/**
 * Composable for managing statutory clock data
 *
 * For Resource Consent requests, fetches clock data from Resource Consent Application.
 * For other request types (Building Consent, etc.), will fetch from their respective applications.
 * Falls back to Request fields for backward compatibility during migration.
 *
 * @param {Object} request - The request resource from frappe-ui
 * @returns {Object} Statutory clock data and methods
 */
export function useStatutoryClock(request) {
	// Fetch Resource Consent Application if this is a Resource Consent
	const consentApplication = createResource({
		url: "frappe.client.get_list",
		params: {
			doctype: "Resource Consent Application",
			filters: { request: request.data?.name },
			fields: [
				"name",
				"statutory_clock_started",
				"statutory_clock_stopped",
				"working_days_elapsed",
				"working_days_remaining",
			],
			limit: 1,
		},
		auto: false,
	})

	// Auto-fetch when request data is available
	watch(
		() => request.data,
		(newData) => {
			if (
				newData &&
				newData.request_category === "Resource Consent" &&
				newData.name
			) {
				consentApplication.reload()
			}
		},
		{ immediate: true },
	)

	/**
	 * Get statutory clock data from the appropriate source
	 */
	const clockData = computed(() => {
		// For Resource Consent, prefer RC Application data
		if (request.data?.request_category === "Resource Consent") {
			const rcApp = consentApplication.data?.[0]
			if (rcApp) {
				return {
					statutory_clock_started: rcApp.statutory_clock_started,
					statutory_clock_stopped: rcApp.statutory_clock_stopped,
					working_days_elapsed: rcApp.working_days_elapsed || 0,
					working_days_remaining: rcApp.working_days_remaining || 0,
					source: "Resource Consent Application",
				}
			}
		}

		// Fallback to Request fields (deprecated, for backward compatibility)
		return {
			statutory_clock_started: request.data?.statutory_clock_started,
			statutory_clock_stopped: request.data?.statutory_clock_stopped,
			working_days_elapsed: request.data?.working_days_elapsed || 0,
			working_days_remaining: request.data?.working_days_remaining || 0,
			source: "Request (deprecated)",
		}
	})

	/**
	 * Calculate progress percentage for visual indicators
	 */
	const progressPercent = computed(() => {
		const elapsed = clockData.value.working_days_elapsed
		const total = request.data?.statutory_timeframe || 20
		return Math.min((elapsed / total) * 100, 100)
	})

	/**
	 * Check if clock is currently running
	 */
	const isClockRunning = computed(() => {
		return (
			clockData.value.statutory_clock_started &&
			!clockData.value.statutory_clock_stopped
		)
	})

	/**
	 * Check if request is overdue
	 */
	const isOverdue = computed(() => {
		return (
			clockData.value.working_days_remaining < 0 || request.data?.is_overdue
		)
	})

	return {
		clockData,
		progressPercent,
		isClockRunning,
		isOverdue,
		loading: computed(() => consentApplication.loading),
	}
}
