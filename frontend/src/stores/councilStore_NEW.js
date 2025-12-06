/**
 * councilStore_NEW.js
 *
 * REFACTORED VERSION using createEntityStore factory from @lodgeick/ui
 *
 * BEFORE (councilStore.js): 193 lines of repetitive Pinia store code
 * AFTER (this file): 13 lines of configuration
 *
 * This demonstrates:
 * - 93% less code (193 lines → 13 lines)
 * - No hardcoded API calls
 * - All standard CRUD operations included automatically
 * - Easy to adapt when Council moves to platform_core app
 * - Same pattern works for ANY entity (Household, Request Type, etc.)
 *
 * To use this store instead of the old one:
 * 1. Import: import { useCouncilStoreNew } from '@/stores/councilStore_NEW'
 * 2. Use in component: const councilStore = useCouncilStoreNew()
 * 3. Load councils: await councilStore.loadItems()
 * 4. Access items: councilStore.items
 * 5. Select council: councilStore.selectItem(council)
 */

import { createEntityStore } from '@lodgeick/ui'

export const useCouncilStoreNew = createEntityStore('council-new', {
  appName: 'lodgeick', // When we migrate to multi-app, change to 'platform_core'
  doctype: 'Council',
  filters: { is_active: 1 },
  fields: [
    'name',
    'council_code',
    'council_name',
    'logo',
    'primary_color',
    'website',
    'contact_email',
    'council_region',
    'is_license_valid'
  ],
  displayField: 'council_name',
  orderBy: 'council_name asc'
})

/**
 * COMPARISON
 *
 * Old councilStore.js (193 lines):
 * --------------------------------
 * - Manual state definition (councils, selectedCouncil, loading, error)
 * - Manual getter implementations (activeCouncils, selectedCouncilData)
 * - Manual action implementations (loadCouncils, loadCouncilByCode, etc.)
 * - Custom localStorage logic
 * - Hardcoded API calls: call('lodgeick.api.get_active_councils')
 * - Request type management mixed in
 * - URL preselection logic
 *
 * New councilStore_NEW.js (13 lines):
 * ------------------------------------
 * - All state automatically provided (items, selected, loading, error, currentFilters)
 * - All getters automatically provided (selectedDisplay, selectedName, hasItems, itemCount)
 * - All actions automatically provided:
 *   - loadItems(), reload(), selectItem(), selectByName(), clearSelection()
 *   - updateFilters(), resetFilters(), fetchItem(), saveItem(), deleteItem()
 *   - getCount()
 * - Generic API client (works with any app)
 * - Single responsibility (councils only)
 *
 * USAGE COMPARISON
 *
 * Old:
 * ----
 * const councilStore = useCouncilStore()
 * await councilStore.loadCouncils()
 * const councils = councilStore.activeCouncils
 * councilStore.setCouncil(councilCode)
 *
 * New:
 * ----
 * const councilStore = useCouncilStoreNew()
 * await councilStore.loadItems() // or loadItems({ council_region: 'North Island' })
 * const councils = councilStore.items
 * councilStore.selectByName(councilCode)
 *
 * MIGRATION TO MULTI-APP
 *
 * When Council moves to platform_core app, only change ONE line:
 *   appName: 'lodgeick' → appName: 'platform_core'
 *
 * Everything else stays the same!
 */

/**
 * EXAMPLE: Creating stores for other entities using the same pattern
 */

// Household store (for social_services app)
export const useHouseholdStore = createEntityStore('household', {
  appName: 'social_services', // Future app
  doctype: 'Household Record',
  filters: { is_active: 1 },
  fields: ['name', 'head_of_household_name', 'barangay', 'member_count', 'status'],
  displayField: 'head_of_household_name'
})

// Request Type store (for lodgement_requests app)
export const useRequestTypeStore = createEntityStore('request-type', {
  appName: 'lodgement_requests', // Future app
  doctype: 'Request Type',
  filters: { is_active: 1 },
  fields: ['name', 'request_type_name', 'category', 'description', 'base_fee'],
  displayField: 'request_type_name',
  orderBy: 'request_type_name asc'
})

// Organization store (for platform_core app)
export const useOrganizationStore = createEntityStore('organization', {
  appName: 'platform_core', // Future app
  doctype: 'Organization',
  filters: { is_active: 1 },
  fields: ['name', 'organization_name', 'organization_type', 'contact_email'],
  displayField: 'organization_name'
})

/**
 * ADVANCED USAGE EXAMPLES
 */

// Example 1: Filter by region
// const councilStore = useCouncilStoreNew()
// await councilStore.loadItems({ council_region: 'North Island' })

// Example 2: Search and select
// const councilStore = useCouncilStoreNew()
// await councilStore.loadItems()
// const auckland = councilStore.findBy('council_code', 'AKL')
// councilStore.selectItem(auckland)

// Example 3: Update and save
// const councilStore = useCouncilStoreNew()
// const council = await councilStore.fetchItem('COUNCIL-001')
// await councilStore.saveItem({
//   ...council,
//   contact_email: 'updated@example.com'
// })

// Example 4: Get count
// const councilStore = useCouncilStoreNew()
// const activeCount = await councilStore.getCount() // Uses current filters
