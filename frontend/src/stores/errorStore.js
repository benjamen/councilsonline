import { defineStore } from "pinia"

export const useErrorStore = defineStore("error", {
	state: () => ({
		errors: [], // Array of error objects
		globalError: null, // Critical error
	}),

	getters: {
		hasErrors: (state) => state.errors.length > 0,
		latestError: (state) => state.errors[state.errors.length - 1],
		errorCount: (state) => state.errors.length,
	},

	actions: {
		/**
		 * Add error to the store
		 * @param {Object|String} error - Error object or message
		 */
		addError(error) {
			const errorObj = {
				id: Date.now() + Math.random(),
				message:
					typeof error === "string" ? error : error.message || error.toString(),
				timestamp: new Date(),
				type: error.type || "error",
				context: error.context || null,
			}

			this.errors.push(errorObj)

			// Auto-clear error after 10 seconds unless it's critical
			if (errorObj.type !== "critical") {
				setTimeout(() => {
					this.clearError(errorObj.id)
				}, 10000)
			}
		},

		/**
		 * Set global/critical error
		 * @param {Object|String} error - Error object or message
		 */
		setGlobalError(error) {
			this.globalError =
				typeof error === "string"
					? { message: error, timestamp: new Date() }
					: { ...error, timestamp: new Date() }
		},

		/**
		 * Clear specific error by ID
		 * @param {Number} errorId - Error ID
		 */
		clearError(errorId) {
			this.errors = this.errors.filter((e) => e.id !== errorId)
		},

		/**
		 * Clear all errors
		 */
		clearAllErrors() {
			this.errors = []
			this.globalError = null
		},

		/**
		 * Clear global error
		 */
		clearGlobalError() {
			this.globalError = null
		},
	},
})
