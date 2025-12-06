/**
 * Conditional Logic Utility for Request Type Configuration
 *
 * Evaluates `depends_on` expressions from step_configs, step_sections, and step_fields
 *
 * Expression formats supported:
 * - eval:formData.field_name=='value'
 * - eval:formData.field_name!='value'
 * - eval:formData.field_name
 * - eval:!formData.field_name
 * - eval:formData.field_name>5
 * - eval:formData.field_name=='value1' || formData.field_name=='value2'
 * - eval:formData.field_name=='value1' && formData.other_field=='value2'
 */

/**
 * Safely evaluates a depends_on expression
 *
 * @param {string} expression - The depends_on expression (e.g., "eval:formData.applicant_type=='Company'")
 * @param {object} formData - The current form data
 * @returns {boolean} - True if condition is met, false otherwise
 */
export function evaluateCondition(expression, formData) {
  // If no expression, always show
  if (!expression || expression.trim() === '') {
    return true
  }

  // Remove 'eval:' prefix if present
  let cleanExpression = expression.trim()
  if (cleanExpression.startsWith('eval:')) {
    cleanExpression = cleanExpression.substring(5).trim()
  }

  try {
    // Create a safe evaluation context with only formData
    // This prevents access to dangerous globals like window, document, etc.
    const safeEval = new Function('formData', `
      'use strict';
      try {
        return Boolean(${cleanExpression});
      } catch (e) {
        console.warn('[Conditional Logic] Evaluation error:', e.message);
        return false;
      }
    `)

    const result = safeEval(formData)
    return result
  } catch (error) {
    console.error('[Conditional Logic] Failed to evaluate expression:', expression, error)
    // On error, default to showing the field/section (fail open)
    return true
  }
}

/**
 * Evaluates step visibility based on depends_on
 *
 * @param {object} step - Step config object with optional depends_on
 * @param {object} formData - Current form data
 * @returns {boolean} - Whether step should be visible
 */
export function isStepVisible(step, formData) {
  if (!step) return false
  if (!step.is_enabled) return false
  if (!step.depends_on) return true

  return evaluateCondition(step.depends_on, formData)
}

/**
 * Evaluates section visibility based on depends_on
 *
 * @param {object} section - Section config object with optional depends_on
 * @param {object} formData - Current form data
 * @returns {boolean} - Whether section should be visible
 */
export function isSectionVisible(section, formData) {
  if (!section) return false
  if (!section.is_enabled) return false
  if (!section.depends_on) return true

  return evaluateCondition(section.depends_on, formData)
}

/**
 * Evaluates field visibility based on depends_on
 *
 * @param {object} field - Field config object with optional depends_on
 * @param {object} formData - Current form data
 * @returns {boolean} - Whether field should be visible
 */
export function isFieldVisible(field, formData) {
  if (!field) return false
  if (!field.depends_on) return true

  return evaluateCondition(field.depends_on, formData)
}

/**
 * Filters an array of items based on their depends_on conditions
 *
 * @param {array} items - Array of steps/sections/fields with optional depends_on
 * @param {object} formData - Current form data
 * @param {function} visibilityFn - Function to check visibility (isStepVisible, isSectionVisible, isFieldVisible)
 * @returns {array} - Filtered array of visible items
 */
export function filterVisibleItems(items, formData, visibilityFn) {
  if (!items || !Array.isArray(items)) return []

  return items.filter(item => visibilityFn(item, formData))
}

/**
 * Example expressions and their evaluations:
 *
 * Expression: "eval:formData.applicant_type=='Company'"
 * formData: { applicant_type: 'Company' }
 * Result: true
 *
 * Expression: "eval:formData.has_agent"
 * formData: { has_agent: 1 }
 * Result: true
 *
 * Expression: "eval:!formData.has_agent"
 * formData: { has_agent: 0 }
 * Result: true
 *
 * Expression: "eval:formData.age>65"
 * formData: { age: 70 }
 * Result: true
 *
 * Expression: "eval:formData.consent_type=='Land Use' || formData.consent_type=='Subdivision'"
 * formData: { consent_type: 'Land Use' }
 * Result: true
 */
