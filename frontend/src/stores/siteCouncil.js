/**
 * Site Council Store (Single-Tenant)
 *
 * Simplified store for single-tenant architecture where Council is a Single DocType.
 * Replaces the complex multi-tenant councilStore.js.
 */

import { call } from "frappe-ui"
import { defineStore } from "pinia"

export const useSiteCouncilStore = defineStore("siteCouncil", {
	state: () => ({
		council: null,
		requestTypes: [],
		loading: false,
		error: null,
		lastFetched: null, // Cache timestamp
	}),

	getters: {
		/**
		 * Get council data (always available since it's a Single DocType)
		 */
		councilData: (state) => state.council,

		/**
		 * Check if council data is loaded
		 */
		isLoaded: (state) => !!state.council,

		/**
		 * Get available request types for this site's council
		 */
		availableRequestTypes: (state) => state.requestTypes,

		/**
		 * Get council branding/theme colors
		 */
		branding: (state) => ({
			// Colors
			primaryColor: state.council?.primary_color || "#2563EB",
			secondaryColor: state.council?.secondary_color || "#1E40AF",
			accentColor: state.council?.accent_color || "#059669",
			// Identity
			appName: state.council?.app_name || null,
			councilName: state.council?.council_name || "Council",
			tagline: state.council?.tagline || null,
			// Assets
			logo: state.council?.logo || null,
			favicon: state.council?.favicon || null,
			// Landing Page - Hero
			heroTitle: state.council?.hero_title || null,
			heroSubtitle: state.council?.hero_subtitle || null,
			heroDescription: state.council?.hero_description || null,
			heroImage: state.council?.hero_image || null,
			ctaPrimaryText: state.council?.cta_primary_text || "Get Started",
			ctaSecondaryText: state.council?.cta_secondary_text || "Learn More",
			// Landing Page - Features
			feature1Title: state.council?.feature_1_title || null,
			feature1Description: state.council?.feature_1_description || null,
			feature2Title: state.council?.feature_2_title || null,
			feature2Description: state.council?.feature_2_description || null,
			feature3Title: state.council?.feature_3_title || null,
			feature3Description: state.council?.feature_3_description || null,
			feature4Title: state.council?.feature_4_title || null,
			feature4Description: state.council?.feature_4_description || null,
			// Footer Content
			footerTagline: state.council?.footer_tagline || null,
			supportEmail: state.council?.support_email || null,
			supportPhone: state.council?.support_phone || null,
			footerAddress: state.council?.footer_address || null,
			// Contact (existing)
			website: state.council?.website || null,
			contactEmail: state.council?.contact_email || null,
			contactPhone: state.council?.contact_phone || null,
		}),

		/**
		 * Get meeting configuration
		 */
		meetingConfig: (state) => ({
			defaultDuration: state.council?.default_meeting_duration || 60,
			availableDurations: state.council?.available_meeting_durations
				?.split(",")
				.map((d) => Number.parseInt(d.trim())) || [30, 60, 90],
			bufferTime: state.council?.meeting_buffer_time || 15,
		}),
	},

	actions: {
		/**
		 * Load council data from server
		 * @param {boolean} forceRefresh - Skip cache and fetch fresh data
		 */
		async loadCouncil(forceRefresh = false) {
			// Cache for 5 minutes
			const CACHE_DURATION = 5 * 60 * 1000
			const now = Date.now()

			// Return cached data if available and not expired
			if (!forceRefresh && this.council && this.lastFetched) {
				const cacheAge = now - this.lastFetched
				if (cacheAge < CACHE_DURATION) {
					console.log("[siteCouncil] Using cached council data")
					return
				}
			}

			this.loading = true
			this.error = null

			try {
				console.log("[siteCouncil] Fetching council data...")

				// Get council data (Single DocType)
				this.council = await call("lodgeick.api.get_council")

				// Get enabled request types
				this.requestTypes = await call("lodgeick.api.get_request_types")

				this.lastFetched = now

				console.log(`[siteCouncil] Loaded: ${this.council.council_name}`)
				console.log(`[siteCouncil] Request Types: ${this.requestTypes.length}`)
			} catch (err) {
				console.error("[siteCouncil] Failed to load council data:", err)
				this.error = err.message || "Failed to load council data"
				throw err
			} finally {
				this.loading = false
			}
		},

		/**
		 * Reload council data (force refresh)
		 */
		async reload() {
			return this.loadCouncil(true)
		},

		/**
		 * Clear cached data
		 */
		clearCache() {
			this.council = null
			this.requestTypes = []
			this.lastFetched = null
			console.log("[siteCouncil] Cache cleared")
		},
	},
})
