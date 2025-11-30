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

    // Step 4: Applicant Details
    if (step === 4) {
      const hasApplicantName = !!formData.value.applicant_name?.trim()
      const hasApplicantEmail = !!formData.value.applicant_email?.trim()
      const hasApplicantPhone = !!formData.value.applicant_phone?.trim()
      const hasApplicantType = !!formData.value.applicant_type

      const ownerInfoValid = !formData.value.applicant_is_not_owner ||
        (formData.value.applicant_is_not_owner && !!formData.value.owner_name?.trim())

      return hasApplicantName && hasApplicantEmail && hasApplicantPhone &&
        hasApplicantType && ownerInfoValid
    }

    // Step 5: Property Details
    if (step === 5) {
      return !!formData.value.property_address?.trim()
    }

    // Step 6: Delivery & Payment
    if (step === 6) {
      const hasDeliveryPref = !!formData.value.delivery_preference
      const hasInvoiceTo = !!formData.value.invoice_to

      const invoiceDetailsValid = formData.value.invoice_to !== 'Other' ||
        (!!formData.value.invoice_name?.trim() && !!formData.value.invoice_email?.trim())

      const depositValid = !formData.value.transfer_deposit_required ||
        !!formData.value.transfer_deposit_consent_number?.trim()

      return hasDeliveryPref && hasInvoiceTo && invoiceDetailsValid && depositValid
    }

    // Step 7: Consent Type (Resource Consent only)
    if (step === 7 && isResourceConsent.value) {
      // Activity status is now optional - can proceed with just consent types
      return formData.value.consent_types?.length > 0
    }

    // Step 8: Consent Details (Resource Consent only) - NEW STEP
    if (step === 8 && isResourceConsent.value) {
      // Duration validation - each consent type must have duration specified
      const consentTypes = formData.value.consent_types || []
      const hasDurations = consentTypes.every(ct => {
        const durationData = formData.value.consent_type_durations?.find(d => d.consent_type === ct.consent_type)
        if (!durationData) return false
        return durationData.duration_unlimited || (durationData.duration_years && durationData.duration_years > 0)
      })

      // Consent notice validation (Subdivision only)
      const consentNoticeValid = !hasSubdivision(formData.value) ||
        !formData.value.consent_notice_required ||
        !!formData.value.consent_notice_details?.trim()

      return hasDurations && consentNoticeValid
    }

    // Step 9: Proposal Details (was Step 8)
    if (step === 9 && isResourceConsent.value) {
      const hasBriefDescription = !!formData.value.brief_description?.trim()
      const hasDetailedDescription = !!formData.value.detailed_description?.trim()
      // Detailed breakdown (proposal_details) is optional
      return hasBriefDescription && hasDetailedDescription
    }

    // Step 10: Site & Environment (was Step 9)
    if (step === 10 && isResourceConsent.value) {
      return !!formData.value.site_description?.trim() &&
        !!formData.value.current_use?.trim()
    }

    // Step 11: NES & Hazards (was Step 10) - with natural hazards validation for LUC/SC
    if (step === 11 && isResourceConsent.value) {
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

    // Step 12: AEE (was Step 11)
    if (step === 12 && isResourceConsent.value) {
      return !!formData.value.aee_effects_description?.trim() &&
        !!formData.value.aee_mitigation_measures?.trim() &&
        !!formData.value.aee_alternatives_considered?.trim()
    }

    // Step 13: Plan Assessment (was Step 12)
    if (step === 13 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 14: Affected Parties (was Step 13)
    if (step === 14 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 15: Specialist Reports (was Step 14)
    if (step === 15 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 16: Proposed Conditions (was Step 15)
    if (step === 16 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 17: Declarations (was Step 16)
    if (step === 17 && isResourceConsent.value) {
      return formData.value.declaration_rma_compliance &&
        formData.value.declaration_public_information &&
        formData.value.declaration_authorized
    }

    // Step 18: Review (was Step 17)
    if (step === 18) {
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
