import { defineStore } from 'pinia'
import { call } from 'frappe-ui'

export const useCouncilStore = defineStore('council', {
  state: () => ({
    councils: [],
    selectedCouncil: null,
    preselectedFromUrl: null,
    requestTypes: [],
    loading: false,
    error: null,
    lockedCouncil: null,       // NEW: Locked council from session
    isCouncilLocked: false     // NEW: Lock state
  }),

  getters: {
    activeCouncils: (state) => state.councils.filter(c => c.is_active),

    selectedCouncilData: (state) => {
      if (!state.selectedCouncil) return null
      return state.councils.find(c => c.council_code === state.selectedCouncil)
    },

    hasCouncilSelected: (state) => !!state.selectedCouncil,

    availableRequestTypes: (state) => state.requestTypes
  },

  actions: {
    async loadCouncils() {
      this.loading = true
      this.error = null

      try {
        const response = await call('lodgeick.api.get_active_councils')
        this.councils = response || []

        // If there's a preselected council from URL, set it
        if (this.preselectedFromUrl && !this.selectedCouncil) {
          const council = this.councils.find(
            c => c.council_code === this.preselectedFromUrl
          )
          if (council) {
            this.selectedCouncil = council.council_code
          }
        }
      } catch (err) {
        this.error = err.message || 'Failed to load councils'
        console.error('Error loading councils:', err)
      } finally {
        this.loading = false
      }
    },

    async loadCouncilByCode(councilCode) {
      this.loading = true
      this.error = null

      try {
        const response = await call('lodgeick.api.get_council_by_code', {
          council_code: councilCode
        })

        if (response) {
          // Add to councils array if not already there
          const exists = this.councils.find(c => c.council_code === councilCode)
          if (!exists) {
            this.councils.push(response)
          }

          // Set as selected if license is valid
          if (response.is_license_valid) {
            this.selectedCouncil = councilCode
          }

          return response
        }
        return null
      } catch (err) {
        this.error = err.message || 'Failed to load council'
        console.error('Error loading council:', err)
        return null
      } finally {
        this.loading = false
      }
    },

    async loadRequestTypesForCouncil(councilCode) {
      if (!councilCode) {
        this.requestTypes = []
        return
      }

      this.loading = true
      this.error = null

      try {
        const response = await call('lodgeick.api.get_request_types_for_council', {
          council_code: councilCode
        })
        this.requestTypes = response || []
      } catch (err) {
        this.error = err.message || 'Failed to load request types'
        console.error('Error loading request types:', err)
        this.requestTypes = []
      } finally {
        this.loading = false
      }
    },

    setCouncil(councilCode) {
      // Prevent changing council if locked
      if (this.isCouncilLocked && councilCode !== this.lockedCouncil) {
        console.warn('Cannot change council - council is locked:', this.lockedCouncil)
        return false
      }

      this.selectedCouncil = councilCode

      // Store in localStorage for persistence
      if (councilCode) {
        localStorage.setItem('selected_council', councilCode)

        // Load request types for this council
        this.loadRequestTypesForCouncil(councilCode)
      } else {
        localStorage.removeItem('selected_council')
        this.requestTypes = []
      }

      return true
    },

    setPreselectedFromUrl(councilCode) {
      this.preselectedFromUrl = councilCode

      // Store in localStorage
      if (councilCode) {
        localStorage.setItem('preselected_council', councilCode)
      }
    },

    clearPreselection() {
      this.preselectedFromUrl = null
      localStorage.removeItem('preselected_council')
    },

    async setUserDefaultCouncil(councilCode) {
      try {
        await call('lodgeick.api.set_user_default_council', {
          council_code: councilCode
        })

        // Update local selection
        this.setCouncil(councilCode)

        return true
      } catch (err) {
        this.error = err.message || 'Failed to set default council'
        console.error('Error setting default council:', err)
        return false
      }
    },

    async getUserCouncils() {
      try {
        const response = await call('lodgeick.api.get_user_councils')
        return response || { default_council: null, associated_councils: [] }
      } catch (err) {
        console.error('Error getting user councils:', err)
        return { default_council: null, associated_councils: [] }
      }
    },

    restoreFromLocalStorage() {
      // Check for preselected council from previous session
      const preselected = localStorage.getItem('preselected_council')
      if (preselected) {
        this.preselectedFromUrl = preselected
      }

      // Check for last selected council
      const selected = localStorage.getItem('selected_council')
      if (selected) {
        this.selectedCouncil = selected
      }
    },

    clearError() {
      this.error = null
    },

    async loadLockedCouncil() {
      // Check if council is locked in session
      try {
        const response = await call('lodgeick.api.get_locked_council')

        if (response?.is_locked) {
          this.lockedCouncil = response.council_code
          this.isCouncilLocked = true
          this.selectedCouncil = response.council_code

          // Load request types for locked council
          await this.loadRequestTypesForCouncil(response.council_code)

          return response
        } else {
          // Only clear the lock if we don't already have one in memory
          // This preserves the lock when navigating within the same session
          if (!this.isCouncilLocked) {
            this.lockedCouncil = null
            this.isCouncilLocked = false
          } else {
            console.log('[councilStore] Redis has no lock, but preserving in-memory lock:', this.lockedCouncil)
          }
        }
      } catch (error) {
        console.error('Failed to load locked council:', error)
        // Only clear on error if we don't have an in-memory lock
        if (!this.isCouncilLocked) {
          this.lockedCouncil = null
          this.isCouncilLocked = false
        }
      }

      return null
    },

    async setLockedCouncil(councilCode) {
      // Set council as locked in backend session
      try {
        const response = await call('lodgeick.api.set_locked_council', {
          council_code: councilCode
        })

        if (response?.success) {
          this.lockedCouncil = councilCode
          this.isCouncilLocked = true
          this.selectedCouncil = councilCode

          // Load request types
          await this.loadRequestTypesForCouncil(councilCode)

          return true
        }
      } catch (error) {
        console.error('Failed to lock council:', error)
        return false
      }

      return false
    },

    async clearLockedCouncil() {
      // Clear locked council (admin override only)
      try {
        await call('lodgeick.api.clear_locked_council')

        this.lockedCouncil = null
        this.isCouncilLocked = false
        this.selectedCouncil = null
      } catch (error) {
        console.error('Failed to clear locked council:', error)
      }
    },

    async shouldRedirectToCouncilDashboard(councilCode) {
      // Check if user should be redirected to council-specific dashboard
      try {
        const response = await call('lodgeick.api.should_redirect_to_council_dashboard', {
          council_code: councilCode
        })
        return response?.should_redirect || false
      } catch (error) {
        console.error('Failed to check redirect settings:', error)
        return false
      }
    },

    async getCouncilSettings(councilCode) {
      // Get council portal and website settings
      try {
        const response = await call('lodgeick.api.get_council_settings', {
          council_code: councilCode
        })
        return response
      } catch (error) {
        console.error('Failed to get council settings:', error)
        return null
      }
    },

    setPreferredCouncil(councilCode) {
      // Set as preferred council (softer than locked)
      this.selectedCouncil = councilCode
      localStorage.setItem('preferred_council', councilCode)
    },

    reset() {
      this.selectedCouncil = null
      this.preselectedFromUrl = null
      this.requestTypes = []
      this.error = null
      localStorage.removeItem('selected_council')
      localStorage.removeItem('preselected_council')
    }
  }
})
