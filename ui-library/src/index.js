/**
 * @lodgeick/ui - Shared UI Library
 *
 * Reusable components, composables, and utilities for Lodgeick multi-app architecture.
 * This library enables code reuse across domain apps (resource_consents, social_services, etc.)
 * while maintaining configuration-driven flexibility.
 */

// API Client
export { AppApiClient } from './api/AppApiClient.js'

// Store Factories
export { createEntityStore } from './stores/createEntityStore.js'

// Components
export { default as DynamicFieldRenderer } from './components/DynamicFieldRenderer.vue'
export { default as SelectableItemPicker } from './components/SelectableItemPicker.vue'

// Composables
export { useFileUpload } from './composables/useFileUpload.ts'
export { useFormValidation } from './composables/useFormValidation.js'
export { useArrayField } from './composables/useArrayField.ts'
export { useStepNavigation } from './composables/useStepNavigation.js'
