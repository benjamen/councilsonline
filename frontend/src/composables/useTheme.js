/**
 * Theme Composable
 * Manages dynamic theming based on Council branding settings.
 * Updates CSS variables at runtime when council data loads.
 */

import { computed, watch, onMounted } from 'vue'
import { useSiteCouncilStore } from '@/stores/siteCouncil'

/**
 * Converts a hex color to RGB values
 * @param {string} hex - Hex color code (e.g., "#2563EB")
 * @returns {object} - { r, g, b }
 */
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null
}

/**
 * Darkens a hex color by a percentage
 * @param {string} hex - Hex color code
 * @param {number} percent - Percentage to darken (0-100)
 * @returns {string} - Darkened hex color
 */
function darkenColor(hex, percent) {
  const rgb = hexToRgb(hex)
  if (!rgb) return hex

  const factor = 1 - (percent / 100)
  const r = Math.round(rgb.r * factor)
  const g = Math.round(rgb.g * factor)
  const b = Math.round(rgb.b * factor)

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

/**
 * Lightens a hex color by mixing with white
 * @param {string} hex - Hex color code
 * @param {number} percent - Percentage to lighten (0-100)
 * @returns {string} - Lightened hex color
 */
function lightenColor(hex, percent) {
  const rgb = hexToRgb(hex)
  if (!rgb) return hex

  const factor = percent / 100
  const r = Math.round(rgb.r + (255 - rgb.r) * factor)
  const g = Math.round(rgb.g + (255 - rgb.g) * factor)
  const b = Math.round(rgb.b + (255 - rgb.b) * factor)

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

/**
 * Applies CSS variables to the document root
 * @param {object} branding - Branding object from council
 */
function applyCssVariables(branding) {
  const root = document.documentElement

  if (branding.primaryColor) {
    root.style.setProperty('--color-primary', branding.primaryColor)
    root.style.setProperty('--color-primary-hover', darkenColor(branding.primaryColor, 15))
    root.style.setProperty('--color-primary-light', lightenColor(branding.primaryColor, 85))
    root.style.setProperty('--color-primary-dark', darkenColor(branding.primaryColor, 25))
  }

  if (branding.secondaryColor) {
    root.style.setProperty('--color-secondary', branding.secondaryColor)
    root.style.setProperty('--color-secondary-hover', darkenColor(branding.secondaryColor, 15))
    root.style.setProperty('--color-secondary-light', lightenColor(branding.secondaryColor, 85))
  }

  if (branding.accentColor) {
    root.style.setProperty('--color-accent', branding.accentColor)
    root.style.setProperty('--color-accent-hover', darkenColor(branding.accentColor, 15))
    root.style.setProperty('--color-accent-light', lightenColor(branding.accentColor, 85))
  }
}

/**
 * Updates the document favicon
 * @param {string} faviconUrl - URL to the favicon image
 */
function updateFavicon(faviconUrl) {
  if (!faviconUrl) return

  let link = document.querySelector("link[rel~='icon']")
  if (!link) {
    link = document.createElement('link')
    link.rel = 'icon'
    document.head.appendChild(link)
  }
  link.href = faviconUrl
}

/**
 * Updates the document title
 * @param {string} appName - Application name
 */
function updateDocumentTitle(appName) {
  if (appName) {
    // Only update if we're on a generic page, not overriding specific titles
    const currentTitle = document.title
    if (currentTitle === 'Lodgeick' || currentTitle === 'Loading...') {
      document.title = appName
    }
  }
}

/**
 * Main theme composable
 * Call this in App.vue to initialize theming
 */
export function useTheme() {
  const councilStore = useSiteCouncilStore()

  // Computed branding object with all theme values
  const branding = computed(() => councilStore.branding)

  // Computed values for easy template access
  const appName = computed(() => branding.value.appName || branding.value.councilName || 'CouncilsOnline')
  const tagline = computed(() => branding.value.tagline || '')
  const logo = computed(() => branding.value.logo || null)
  const primaryColor = computed(() => branding.value.primaryColor)
  const secondaryColor = computed(() => branding.value.secondaryColor)
  const accentColor = computed(() => branding.value.accentColor)
  const favicon = computed(() => branding.value.favicon || null)

  // Watch for branding changes and apply CSS variables
  watch(branding, (newBranding) => {
    if (newBranding) {
      applyCssVariables(newBranding)
      updateFavicon(newBranding.favicon)
      updateDocumentTitle(newBranding.appName || newBranding.councilName)
    }
  }, { immediate: true, deep: true })

  // Initialize on mount
  async function initTheme() {
    try {
      await councilStore.loadCouncil()
      if (councilStore.branding) {
        applyCssVariables(councilStore.branding)
        updateFavicon(councilStore.branding.favicon)
        updateDocumentTitle(councilStore.branding.appName || councilStore.branding.councilName)
      }
    } catch (error) {
      console.warn('Failed to load council branding:', error)
      // Use defaults - CSS variables will keep initial values
    }
  }

  return {
    // State
    branding,
    appName,
    tagline,
    logo,
    primaryColor,
    secondaryColor,
    accentColor,
    favicon,

    // Methods
    initTheme,
    applyCssVariables,

    // Store access
    councilStore,
    isLoading: computed(() => councilStore.isLoading),
    council: computed(() => councilStore.council)
  }
}

export default useTheme
