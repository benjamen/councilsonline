import { defineStore } from 'pinia'
import { requestService } from '../services'

export const useRequestStore = defineStore('request', {
	state: () => ({
		// Current request being edited
		currentRequestId: null,
		requestTypeCode: null,
		requestTypeConfig: null,

		// Form state
		formData: {},
		currentStep: 0,

		// Validation
		stepValidationStatus: {}, // { 0: true, 1: false, ... }

		// UI state
		isSaving: false,
		isSubmitting: false,
		lastSaved: null,

		// Error state
		error: null
	}),

	getters: {
		isFirstStep: (state) => state.currentStep === 0,

		isLastStep: (state) => {
			const totalSteps = state.requestTypeConfig?.steps?.length || 0
			return state.currentStep === totalSteps - 1
		},

		currentStepConfig: (state) => {
			return state.requestTypeConfig?.steps?.[state.currentStep]
		},

		canNavigateNext: (state) => {
			return state.stepValidationStatus[state.currentStep] === true
		},

		completionPercentage: (state) => {
			const totalSteps = state.requestTypeConfig?.steps?.length || 0
			if (totalSteps === 0) return 0
			return Math.round(((state.currentStep + 1) / totalSteps) * 100)
		},

		hasUnsavedChanges: (state) => {
			// Check if form data exists and last saved is more than 30 seconds ago
			if (!state.lastSaved) return Object.keys(state.formData).length > 0
			const now = new Date()
			const diff = now - state.lastSaved
			return diff > 30000 // 30 seconds
		}
	},

	actions: {
		/**
		 * Initialize new request or load draft
		 */
		async initialize(requestTypeCode, draftId = null) {
			try {
				this.requestTypeCode = requestTypeCode
				this.error = null

				// Load request type config
				const configResource = requestService.getRequestTypeConfig(requestTypeCode)

				// Wait for config to load
				await new Promise((resolve) => {
					const checkLoaded = setInterval(() => {
						if (!configResource.loading) {
							clearInterval(checkLoaded)
							resolve()
						}
					}, 100)
				})

				this.requestTypeConfig = configResource.data

				if (draftId) {
					// Load existing draft
					await this.loadDraft(draftId)
				} else {
					// Initialize form, preserving existing data (like council selection)
					this.formData = { ...this.formData }
					this.currentStep = 0
				}
			} catch (error) {
				console.error('Failed to initialize request:', error)
				this.error = error.message || 'Failed to load request type'
			}
		},

		/**
		 * Load draft request
		 */
		async loadDraft(draftId) {
			try {
				const resource = requestService.getRequest(draftId)

				// Wait for load
				await new Promise((resolve) => {
					const checkLoaded = setInterval(() => {
						if (!resource.loading) {
							clearInterval(checkLoaded)
							resolve()
						}
					}, 100)
				})

				const draft = resource.data

				this.currentRequestId = draftId
				this.formData = draft.form_data || {}
				this.currentStep = draft.current_step || 0
			} catch (error) {
				console.error('Failed to load draft:', error)
				this.error = error.message || 'Failed to load draft'
			}
		},

		/**
		 * Save progress (auto-save or manual)
		 */
		async saveProgress() {
			this.isSaving = true
			this.error = null

			try {
				const result = await requestService.createDraft(
					this.formData,
					this.currentStep
				)

				if (!this.currentRequestId) {
					this.currentRequestId = result.request_id
				}

				this.lastSaved = new Date()
			} catch (error) {
				console.error('Save failed:', error)
				this.error = error.message || 'Failed to save progress'
				throw error
			} finally {
				this.isSaving = false
			}
		},

		/**
		 * Save as draft (explicit user action)
		 */
		async saveDraft() {
			return this.saveProgress()
		},

		/**
		 * Submit request
		 */
		async submitRequest() {
			this.isSubmitting = true
			this.error = null

			try {
				// Save current progress first
				if (!this.currentRequestId) {
					await this.saveProgress()
				}

				// Submit the request
				await requestService.submitRequest(this.currentRequestId)

				// Clear state
				this.reset()

				return true
			} catch (error) {
				console.error('Submit failed:', error)
				this.error = error.message || 'Failed to submit request'
				throw error
			} finally {
				this.isSubmitting = false
			}
		},

		/**
		 * Navigate to next step
		 */
		nextStep() {
			if (!this.isLastStep) {
				this.currentStep++
			}
		},

		/**
		 * Navigate to previous step
		 */
		previousStep() {
			if (!this.isFirstStep) {
				this.currentStep--
			}
		},

		/**
		 * Jump to specific step
		 */
		goToStep(stepIndex) {
			const totalSteps = this.requestTypeConfig?.steps?.length || 0
			if (stepIndex >= 0 && stepIndex < totalSteps) {
				this.currentStep = stepIndex
			}
		},

		/**
		 * Update field value
		 */
		updateField(fieldName, value) {
			this.formData[fieldName] = value
		},

		/**
		 * Update multiple fields
		 */
		updateFields(fields) {
			Object.assign(this.formData, fields)
		},

		/**
		 * Set step validation status
		 */
		setStepValidation(stepIndex, isValid) {
			this.stepValidationStatus[stepIndex] = isValid
		},

		/**
		 * Clear error
		 */
		clearError() {
			this.error = null
		},

		/**
		 * Reset store state
		 */
		reset() {
			this.currentRequestId = null
			this.requestTypeCode = null
			this.requestTypeConfig = null
			this.formData = {}
			this.currentStep = 0
			this.stepValidationStatus = {}
			this.isSaving = false
			this.isSubmitting = false
			this.lastSaved = null
			this.error = null
		}
	}
})
