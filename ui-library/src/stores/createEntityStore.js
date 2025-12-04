import { defineStore } from 'pinia'
import { AppApiClient } from '../api/AppApiClient.js'

/**
 * Factory function to create reusable entity stores
 *
 * This eliminates the need to write repetitive store code for each entity type.
 * Instead of creating individual stores for Council, Household Record, etc.,
 * you can use this factory to generate them with configuration.
 *
 * @param {string} id - Unique store ID
 * @param {Object} config - Store configuration
 * @param {string} config.appName - Frappe app name (e.g., 'platform_core')
 * @param {string} config.doctype - DocType name (e.g., 'Council')
 * @param {Object} [config.filters] - Default filters to apply when loading
 * @param {string[]} [config.fields] - Fields to fetch
 * @param {string} [config.displayField] - Field to use for display (default: 'name')
 * @param {string} [config.orderBy] - Order by clause (e.g., 'council_name asc')
 * @returns {Function} Pinia store
 *
 * @example
 * // In resource_consents app - create a council store
 * export const useCouncilStore = createEntityStore('council', {
 *   appName: 'platform_core',
 *   doctype: 'Council',
 *   filters: { is_active: 1 },
 *   fields: ['name', 'council_name', 'primary_color', 'logo'],
 *   displayField: 'council_name',
 *   orderBy: 'council_name asc'
 * })
 *
 * @example
 * // In social_services app - create a household store
 * export const useHouseholdStore = createEntityStore('household', {
 *   appName: 'social_services',
 *   doctype: 'Household Record',
 *   filters: { is_active: 1 },
 *   fields: ['name', 'head_of_household_name', 'barangay', 'member_count'],
 *   displayField: 'head_of_household_name'
 * })
 */
export function createEntityStore(id, config) {
  const {
    appName,
    doctype,
    filters = {},
    fields = ['name'],
    displayField = 'name',
    orderBy = null
  } = config

  return defineStore(id, {
    state: () => ({
      /** @type {any[]} */
      items: [],
      /** @type {any|null} */
      selected: null,
      /** @type {boolean} */
      loading: false,
      /** @type {string|null} */
      error: null,
      /** @type {Object} */
      currentFilters: { ...filters }
    }),

    getters: {
      /**
       * Get the display value for the currently selected item
       * @returns {string}
       */
      selectedDisplay() {
        if (!this.selected) return ''
        return this.selected[displayField] || this.selected.name || ''
      },

      /**
       * Get the name of the currently selected item
       * @returns {string|null}
       */
      selectedName() {
        return this.selected?.name || null
      },

      /**
       * Check if any items are loaded
       * @returns {boolean}
       */
      hasItems() {
        return this.items.length > 0
      },

      /**
       * Get count of loaded items
       * @returns {number}
       */
      itemCount() {
        return this.items.length
      },

      /**
       * Find an item by its name field
       * @returns {Function}
       */
      findByName() {
        return (name) => this.items.find(item => item.name === name)
      },

      /**
       * Find an item by a specific field value
       * @returns {Function}
       */
      findBy() {
        return (field, value) => this.items.find(item => item[field] === value)
      }
    },

    actions: {
      /**
       * Load items from the server
       * @param {Object} additionalFilters - Additional filters to merge with defaults
       * @returns {Promise<void>}
       */
      async loadItems(additionalFilters = {}) {
        this.loading = true
        this.error = null

        try {
          const api = new AppApiClient(appName)
          const mergedFilters = { ...this.currentFilters, ...additionalFilters }

          const options = {}
          if (orderBy) {
            options.order_by = orderBy
          }

          this.items = await api.getList(doctype, mergedFilters, fields, options)
        } catch (error) {
          this.error = error.message || 'Failed to load items'
          console.error(`Error loading ${doctype}:`, error)
          throw error
        } finally {
          this.loading = false
        }
      },

      /**
       * Reload items with current filters
       * @returns {Promise<void>}
       */
      async reload() {
        await this.loadItems()
      },

      /**
       * Select an item
       * @param {any} item - Item to select
       */
      selectItem(item) {
        this.selected = item
      },

      /**
       * Select an item by its name
       * @param {string} name - Item name
       */
      selectByName(name) {
        const item = this.findByName(name)
        if (item) {
          this.selected = item
        }
      },

      /**
       * Clear the current selection
       */
      clearSelection() {
        this.selected = null
      },

      /**
       * Update the filters and reload
       * @param {Object} newFilters - New filter object
       * @returns {Promise<void>}
       */
      async updateFilters(newFilters) {
        this.currentFilters = { ...filters, ...newFilters }
        await this.loadItems()
      },

      /**
       * Reset filters to defaults and reload
       * @returns {Promise<void>}
       */
      async resetFilters() {
        this.currentFilters = { ...filters }
        await this.loadItems()
      },

      /**
       * Get a single item by name from the server
       * @param {string} name - Document name
       * @returns {Promise<any>}
       */
      async fetchItem(name) {
        const api = new AppApiClient(appName)
        return await api.get(doctype, name)
      },

      /**
       * Save an item (create or update)
       * @param {Object} data - Item data
       * @returns {Promise<any>}
       */
      async saveItem(data) {
        const api = new AppApiClient(appName)
        const saved = await api.save(doctype, data)

        // Update items list if the saved item matches current filters
        const existingIndex = this.items.findIndex(item => item.name === saved.name)
        if (existingIndex >= 0) {
          // Update existing item
          this.items[existingIndex] = { ...this.items[existingIndex], ...saved }
        } else {
          // Reload to get the new item if it matches filters
          await this.reload()
        }

        return saved
      },

      /**
       * Delete an item
       * @param {string} name - Document name
       * @returns {Promise<void>}
       */
      async deleteItem(name) {
        const api = new AppApiClient(appName)
        await api.delete(doctype, name)

        // Remove from local items
        this.items = this.items.filter(item => item.name !== name)

        // Clear selection if deleted item was selected
        if (this.selected?.name === name) {
          this.clearSelection()
        }
      },

      /**
       * Get count of items matching current filters
       * @returns {Promise<number>}
       */
      async getCount() {
        const api = new AppApiClient(appName)
        return await api.getCount(doctype, this.currentFilters)
      }
    }
  })
}
