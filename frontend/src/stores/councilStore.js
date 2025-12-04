import { defineStore } from 'pinia'
import { call } from 'frappe-ui'

export const useCouncilStore = defineStore('council', {
  state: () => ({
    councils: [],
    selectedCouncil: null,
    preselectedFromUrl: null,
    requestTypes: [],
    loading: false,
    error: null
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
