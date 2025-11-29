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

    // Step 8: Proposal Details (Resource Consent only)
    if (step === 8 && isResourceConsent.value) {
      const hasBriefDescription = !!formData.value.brief_description?.trim()
      const hasDetailedDescription = !!formData.value.detailed_description?.trim()
      // Detailed breakdown (proposal_details) is optional
      return hasBriefDescription && hasDetailedDescription
    }

    // Step 9: Site & Environment (Resource Consent only)
    if (step === 9 && isResourceConsent.value) {
      return !!formData.value.site_description?.trim() &&
        !!formData.value.current_use?.trim()
    }

    // Step 10: NES & Hazards (Resource Consent only)
    if (step === 10 && isResourceConsent.value) {
      return true // Optional step
    }

    // Step 11: AEE (Resource Consent only)
    if (step === 11 && isResourceConsent.value) {
      return !!formData.value.aee_effects_description?.trim() &&
        !!formData.value.aee_mitigation_measures?.trim() &&
        !!formData.value.aee_alternatives_considered?.trim()
    }

    // Step 12: Plan Assessment (Resource Consent only)
    if (step === 12 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 13: Affected Parties (Resource Consent only)
    if (step === 13 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 14: Specialist Reports (Resource Consent only)
    if (step === 14 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 15: Proposed Conditions (Resource Consent only)
    if (step === 15 && isResourceConsent.value) {
      return true // Optional
    }

    // Step 16: Declarations (Resource Consent only)
    if (step === 16 && isResourceConsent.value) {
      return formData.value.declaration_rma_compliance &&
        formData.value.declaration_public_information &&
        formData.value.declaration_authorized
    }

    // Step 17: Review
    if (step === 17) {
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
        hasConsentTypes && hasBriefDescription && hasDetailedDescription &&
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
