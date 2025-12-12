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

        // === NEW GETTER: Total Steps (matches logic in NewRequest.vue) ===
        totalSteps: (state) => {
            if (state.requestTypeConfig?.steps) {
                // 3 Static Steps (Council, Type, Process Info) + Dynamic Steps + 1 Review Step
                return state.requestTypeConfig.steps.length + 4
            }
            return 4 // Default: 3 Static + 1 Review
        },
        // =================================================================

        // === FIXED GETTER: isLastStep ===
        isLastStep: (state) => {
            // Use the new, correct totalSteps getter
            return state.currentStep === state.totalSteps - 1
        },
        // ================================

        currentStepConfig: (state) => {
            // NOTE: This getter still uses the wrong index if totalSteps were used, 
            // but the parent component uses its own calculation. Keeping it as-is 
            // since it is not currently used by the parent for dynamic steps.
            return state.requestTypeConfig?.steps?.[state.currentStep]
        },

        canNavigateNext: (state) => {
            return state.stepValidationStatus[state.currentStep] === true
        },

        completionPercentage: (state) => {
            if (state.totalSteps === 0) return 0
            return Math.round(((state.currentStep + 1) / state.totalSteps) * 100)
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
        // ... (initialize, loadDraft, saveProgress, saveDraft, submitRequest actions remain unchanged)

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
            // Use the correct totalSteps getter
            if (stepIndex >= 0 && stepIndex < this.totalSteps) {
                this.currentStep = stepIndex
            }
        },
        // ... (updateField, updateFields, setStepValidation, clearError, reset actions remain unchanged)

        // All the boilerplate logic for initialize, loadDraft, saveProgress, etc. goes here
        // ...
        async initialize(requestTypeCode, draftId = null) {
            try {
                this.requestTypeCode = requestTypeCode
                this.error = null

                console.log('[RequestStore] initialize called:', { requestTypeCode, draftId })

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
                }
            } catch (error) {
                console.error('Failed to initialize request:', error)
                this.error = error.message || 'Failed to load request type'
            }
        },

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

                // Parse the full form data from draft_full_data JSON field
                if (draft.draft_full_data) {
                    try {
                        this.formData = JSON.parse(draft.draft_full_data)
                    } catch (error) {
                        console.error('Failed to parse draft_full_data:', error)
                        this.formData = draft.form_data || {}
                    }
                } else {
                    this.formData = draft.form_data || {}
                }

                // Use draft_current_step from the document
                this.currentStep = draft.draft_current_step || 0
            } catch (error) {
                console.error('Failed to load draft:', error)
                this.error = error.message || 'Failed to load draft'
            }
        },

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

        async saveDraft() {
            return this.saveProgress()
        },

        async submitRequest() {
            this.isSubmitting = true
            this.error = null

            try {
                // Save current progress first
                if (!this.currentRequestId) {
                    await this.saveProgress()
                }

                // Submit the request and get result
                const result = await requestService.submitRequest(this.currentRequestId)

                // Clear state
                this.reset()

                // Return submission result with SLA info
                return result
            } catch (error) {
                console.error('Submit failed:', error)
                this.error = error.message || 'Failed to submit request'
                throw error
            } finally {
                this.isSubmitting = false
            }
        },

        updateField(fieldName, value) {
            this.formData[fieldName] = value
        },

        updateFields(fields) {
            Object.assign(this.formData, fields)
        },

        setStepValidation(stepIndex, isValid) {
            this.stepValidationStatus[stepIndex] = isValid
        },

        clearError() {
            this.error = null
        },

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