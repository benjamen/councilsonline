import { computed } from 'vue'

/**
 * Composable for form validation logic in NewRequest
 * @param {Object} formData - The form data ref
 * @param {Object} currentStep - The current step ref
 * @param {Object} isResourceConsent - Computed for resource consent check
 * @returns {Object} Validation functions and computed properties
 */
export function useFormValidation(formData, currentStep, isResourceConsent) {
  /**
   * Helper function to check if Subdivision consent is selected
   */
  const hasSubdivision = (formData) => {
    return formData.consent_types?.some(ct => ct.consent_type === 'Subdivision') || false
  }

  /**
   * Check if user can proceed from current step
   */
  const canProceed = () => {
    const step = currentStep.value

    // Step 1: Council Selection
    if (step === 1) {
      return !!formData.value.council
    }

    // Step 2: Request Type
    if (step === 2) {
      return !!formData.value.request_type
    }

    // Step 3: Process Info (no validation, just informational)
    if (step === 3) {
      return true
    }

    // Step 4: Applicant Details & Delivery/Payment (merged)
    if (step === 4) {
      const hasApplicantName = !!formData.value.applicant_name?.trim()
      const hasApplicantEmail = !!formData.value.applicant_email?.trim()
      const hasApplicantPhone = !!formData.value.applicant_phone?.trim()
      const hasApplicantType = !!formData.value.applicant_type

      const ownerInfoValid = !formData.value.applicant_is_not_owner ||
        (formData.value.applicant_is_not_owner && !!formData.value.owner_name?.trim())

      // Delivery & Payment validation (merged into Step 4)
      const hasInvoiceTo = !!formData.value.invoice_to

      const invoiceDetailsValid = formData.value.invoice_to !== 'Other' ||
        (!!formData.value.invoice_name?.trim() && !!formData.value.invoice_email?.trim())

      const depositValid = !formData.value.transfer_deposit_required ||
        !!formData.value.transfer_deposit_consent_number?.trim()

      return hasApplicantName && hasApplicantEmail && hasApplicantPhone &&
        hasApplicantType && ownerInfoValid && hasInvoiceTo && invoiceDetailsValid && depositValid
    }

    // Step 5: Property Details
    if (step === 5) {
      return !!formData.value.property_address?.trim()
    }

    // Step 6: Consent Information (merged: Type + Details + Proposal) (Resource Consent only)
    if (step === 6 && isResourceConsent.value) {
      // Consent types must be selected
      const hasConsentTypes = formData.value.consent_types?.length > 0
      console.log('Step 6 Validation - hasConsentTypes:', hasConsentTypes, formData.value.consent_types)
      if (!hasConsentTypes) return false

      // Duration validation - each consent type must have duration specified
      const consentTypes = formData.value.consent_types || []
      const hasDurations = consentTypes.every(ct => {
        const durationData = formData.value.consent_type_durations?.find(d => d.consent_type === ct.consent_type)
        console.log('Duration check for', ct.consent_type, ':', durationData)
        if (!durationData) return false
        return durationData.duration_unlimited || (durationData.duration_years && durationData.duration_years > 0)
      })
      console.log('Step 6 Validation - hasDurations:', hasDurations)

      // Consent notice validation (Subdivision only)
      const consentNoticeValid = !hasSubdivision(formData.value) ||
        !formData.value.consent_notice_required ||
        !!formData.value.consent_notice_details?.trim()
      console.log('Step 6 Validation - consentNoticeValid:', consentNoticeValid)

      // Proposal descriptions are required
      const hasBriefDescription = !!formData.value.brief_description?.trim()
      const hasDetailedDescription = !!formData.value.detailed_description?.trim()
      console.log('Step 6 Validation - hasBriefDescription:', hasBriefDescription, 'hasDetailedDescription:', hasDetailedDescription)
      console.log('Brief:', formData.value.brief_description, 'Detailed:', formData.value.detailed_description)

      const result = hasDurations && consentNoticeValid && hasBriefDescription && hasDetailedDescription
      console.log('Step 6 Validation - FINAL RESULT:', result)
      return result
    }

    // Step 7: Site & Environment
    if (step === 7 && isResourceConsent.value) {
      return !!formData.value.site_description?.trim() &&
        !!formData.value.current_use?.trim()
    }

    // Step 8: NES & Hazards - with natural hazards validation for LUC/SC
    if (step === 8 && isResourceConsent.value) {
      const requiresHazards = formData.value.consent_types?.some(ct =>
        ct.consent_type === 'Land Use' || ct.consent_type === 'Subdivision'
      )

      if (requiresHazards) {
        // Either have hazards identified OR explicitly confirm no hazards
        const hasHazards = formData.value.natural_hazards && formData.value.natural_hazards.length > 0
        const confirmedNoHazards = formData.value.no_natural_hazards_confirmed

        if (!hasHazards && !confirmedNoHazards) {
          return false // Must either identify hazards or confirm there are none
        }
      }

      return true // Optional for other consent types
    }

    // Step 9: AEE
    if (step === 9 && isResourceConsent.value) {
      return !!formData.value.aee_effects_description?.trim() &&
        !!formData.value.aee_mitigation_measures?.trim() &&
        !!formData.value.aee_alternatives_considered?.trim()
    }

    // Step 10: Plan Assessment
    if (step === 10 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 11: Affected Parties
    if (step === 11 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 12: Specialist Reports
    if (step === 12 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 13: Proposed Conditions
    if (step === 13 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 14: Declarations
    if (step === 14 && isResourceConsent.value) {
      return formData.value.declaration_rma_compliance &&
        formData.value.declaration_public_information &&
        formData.value.declaration_authorized
    }

    // Review step - always last (step number computed dynamically)
    const isReviewStep = !isResourceConsent.value && step === 6 || isResourceConsent.value && step === 15
    if (isReviewStep) {
      return true
    }

    return false
  }

  /**
   * Check if form can be submitted
   */
  const canSubmit = computed(() => {
    // Must have completed all required fields
    const hasCouncil = !!formData.value.council
    const hasRequestType = !!formData.value.request_type
    const hasApplicantDetails = !!formData.value.applicant_name &&
      !!formData.value.applicant_email &&
      !!formData.value.applicant_phone &&
      !!formData.value.applicant_type
    const hasPropertyAddress = !!formData.value.property_address
    const hasDeliveryPreference = !!formData.value.delivery_preference
    const hasInvoiceTo = !!formData.value.invoice_to

    // Resource Consent specific validations
    if (isResourceConsent.value) {
      const hasConsentTypes = formData.value.consent_types?.length > 0

      // Duration validation - per consent type
      const consentTypes = formData.value.consent_types || []
      const hasDurations = consentTypes.every(ct => {
        const durationData = formData.value.consent_type_durations?.find(d => d.consent_type === ct.consent_type)
        if (!durationData) return false
        return durationData.duration_unlimited || (durationData.duration_years && durationData.duration_years > 0)
      })

      // Natural hazards validation for LUC/SC
      const requiresHazards = formData.value.consent_types?.some(ct =>
        ct.consent_type === 'Land Use' || ct.consent_type === 'Subdivision'
      )
      const hazardsValid = !requiresHazards ||
        (formData.value.natural_hazards && formData.value.natural_hazards.length > 0) ||
        formData.value.no_natural_hazards_confirmed

      // Activity status is optional - council can determine this
      const hasBriefDescription = !!formData.value.brief_description?.trim()
      const hasDetailedDescription = !!formData.value.detailed_description?.trim()
      const hasSiteDescription = !!formData.value.site_description
      const hasCurrentUse = !!formData.value.current_use
      const hasAEE = !!formData.value.aee_effects_description &&
        !!formData.value.aee_mitigation_measures &&
        !!formData.value.aee_alternatives_considered
      const hasDeclarations = formData.value.declaration_rma_compliance &&
        formData.value.declaration_public_information &&
        formData.value.declaration_authorized

      return hasCouncil && hasRequestType && hasApplicantDetails &&
        hasPropertyAddress && hasDeliveryPreference && hasInvoiceTo &&
        hasConsentTypes && hasDurations && hazardsValid &&
        hasBriefDescription && hasDetailedDescription &&
        hasSiteDescription && hasCurrentUse && hasAEE && hasDeclarations
    }

    // Non-Resource Consent validations
    return hasCouncil && hasRequestType && hasApplicantDetails &&
      hasPropertyAddress && hasDeliveryPreference && hasInvoiceTo
  })

  return {
    canProceed,
    canSubmit
  }
}
