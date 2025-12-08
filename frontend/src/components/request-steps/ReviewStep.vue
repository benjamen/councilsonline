<template>
  <div class="px-4 sm:px-0">
    <h2 class="text-xl sm:text-2xl font-bold text-gray-900 mb-2">Review & Submit</h2>
    <p class="text-sm sm:text-base text-gray-600 mb-6 sm:mb-8">Review your application details before submitting</p>

    <div class="space-y-4 sm:space-y-6">
      <!-- Application Summary -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-0">
          <div>
            <h3 class="text-base sm:text-lg font-semibold text-blue-900">{{ requestTypeName }}</h3>
            <p class="text-xs sm:text-sm text-blue-700 mt-1">{{ councilName }}</p>
          </div>
          <div class="sm:text-right">
            <div class="text-xs sm:text-sm text-blue-600 font-medium">Application Fee</div>
            <div class="text-xl sm:text-2xl font-bold text-blue-900">{{ applicationFee }}</div>
          </div>
        </div>
      </div>

      <!-- Applicant Details -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900 text-sm sm:text-base">Applicant Details</h3>
        </div>
        <div class="p-4 sm:p-6 space-y-3">
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <span class="text-sm text-gray-500">Name:</span>
              <p class="font-medium">{{ modelValue.requester_name || 'Not provided' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Email:</span>
              <p class="font-medium">{{ modelValue.requester_email || 'Not provided' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Phone:</span>
              <p class="font-medium">{{ modelValue.requester_phone || 'Not provided' }}</p>
            </div>
            <div v-if="modelValue.applicant_company">
              <span class="text-sm text-gray-500">Company:</span>
              <p class="font-medium">{{ modelValue.applicant_company }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Property Details (only show if request type has property information) -->
      <div v-if="hasPropertyDetails" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900 text-sm sm:text-base">Property Details</h3>
        </div>
        <div class="p-4 sm:p-6">
          <div v-if="modelValue.property_address" class="space-y-2">
            <div>
              <span class="text-sm text-gray-500">Address:</span>
              <p class="font-medium">{{ modelValue.property_address }}</p>
            </div>
            <div v-if="modelValue.legal_description">
              <span class="text-sm text-gray-500">Legal Description:</span>
              <p class="font-medium">{{ modelValue.legal_description }}</p>
            </div>
          </div>
          <p v-else class="text-gray-500">No property selected</p>
        </div>
      </div>

      <!-- Delivery Preference (only show if request type collects payment) -->
      <div v-if="requestTypeDetails?.collect_payment" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900 text-sm sm:text-base">Delivery & Payment</h3>
        </div>
        <div class="p-4 sm:p-6 space-y-3">
          <div>
            <span class="text-sm text-gray-500">Delivery Preference:</span>
            <p class="font-medium">{{ modelValue.delivery_preference || 'Not selected' }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Invoice To:</span>
            <p class="font-medium">{{ modelValue.invoice_to || 'Not specified' }}</p>
          </div>
        </div>
      </div>

      <!-- Dynamic Review Sections (for configured request types) -->
      <template v-if="usesConfigurableSteps && reviewSections.length > 0">
        <div
          v-for="step in reviewSections"
          :key="step.step_code"
          class="bg-white border border-gray-200 rounded-lg overflow-hidden"
        >
          <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900 text-sm sm:text-base">{{ step.step_title }}</h3>
          </div>
          <div class="p-4 sm:p-6 space-y-4">
            <div
              v-for="section in step.sections.filter(s => s.show_on_review)"
              :key="section.section_code"
            >
              <h4 v-if="section.section_title" class="text-sm font-medium text-gray-700 mb-2">
                {{ section.section_title }}
              </h4>
              <div class="grid md:grid-cols-2 gap-4">
                <div
                  v-for="field in section.fields.filter(f => f.show_on_review)"
                  :key="field.field_name"
                >
                  <span class="text-sm text-gray-500">{{ field.review_label || field.field_label }}:</span>
                  <p class="font-medium">{{ formatFieldValue(field, modelValue[field.field_name]) }}</p>
                </div>
              </div>
            </div>
            <p v-if="!hasReviewContent(step)" class="text-gray-500 text-sm">
              No information to display for review
            </p>
          </div>
        </div>
      </template>

      <!-- Resource Consent Specific Details -->
      <template v-if="isResourceConsent">
        <!-- Consent Types -->
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900 text-sm sm:text-base">Consent Types & Activity Status</h3>
          </div>
          <div class="p-4 sm:p-6">
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-500">Consent Types:</span>
                <div class="mt-2 flex flex-wrap gap-2">
                  <span
                    v-if="modelValue.consent_type_land_use"
                    class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                  >
                    Land Use Consent
                  </span>
                  <span
                    v-if="modelValue.consent_type_subdivision"
                    class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                  >
                    Subdivision Consent
                  </span>
                  <span
                    v-if="modelValue.consent_type_discharge"
                    class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
                  >
                    Discharge Permit
                  </span>
                  <span
                    v-if="modelValue.consent_type_water"
                    class="px-3 py-1 bg-cyan-100 text-cyan-800 rounded-full text-sm font-medium"
                  >
                    Water Permit
                  </span>
                  <span
                    v-if="modelValue.consent_type_coastal"
                    class="px-3 py-1 bg-teal-100 text-teal-800 rounded-full text-sm font-medium"
                  >
                    Coastal Permit
                  </span>
                  <span v-if="!hasAnyConsentType" class="text-gray-500">
                    None selected
                  </span>
                </div>
              </div>
              <div>
                <span class="text-sm text-gray-500">Activity Status:</span>
                <div class="mt-1 inline-flex items-center">
                  <span
                    class="px-3 py-1 rounded-full text-sm font-medium"
                    :class="activityStatusClass"
                  >
                    {{ modelValue.activity_status_type || 'Not specified' }}
                  </span>
                </div>
              </div>
              <div v-if="modelValue.activity_title">
                <span class="text-sm text-gray-500">Activity Title:</span>
                <p class="font-medium break-words">{{ modelValue.activity_title }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Natural Hazards -->
        <div v-if="hasNaturalHazards" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900 text-sm sm:text-base">Natural Hazards</h3>
          </div>
          <div class="p-4 sm:p-6">
            <div class="flex flex-wrap gap-2">
              <span
                v-if="modelValue.hazard_flooding"
                class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium inline-flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707" />
                </svg>
                Flood Hazard
              </span>
              <span
                v-if="modelValue.hazard_earthquake"
                class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium inline-flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Earthquake/Fault Line
              </span>
              <span
                v-if="modelValue.hazard_landslip"
                class="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium inline-flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
                Landslip/Slope Instability
              </span>
              <span
                v-if="modelValue.hazard_coastal"
                class="px-3 py-1 bg-cyan-100 text-cyan-800 rounded-full text-sm font-medium inline-flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5" />
                </svg>
                Coastal Hazard
              </span>
            </div>
          </div>
        </div>

        <!-- Consultation & Affected Parties -->
        <div v-if="hasConsultation" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900 text-sm sm:text-base">Consultation & Affected Parties</h3>
          </div>
          <div class="p-4 sm:p-6">
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-500">Consultation Undertaken:</span>
                <p class="font-medium">{{ modelValue.consultation_undertaken || 'Not specified' }}</p>
              </div>
              <div v-if="modelValue.consultation_summary">
                <span class="text-sm text-gray-500">Consultation Summary:</span>
                <p class="text-sm mt-1 line-clamp-3">{{ modelValue.consultation_summary }}</p>
              </div>
              <div v-if="modelValue.affected_parties_details">
                <span class="text-sm text-gray-500">Affected Parties:</span>
                <p class="text-sm mt-1 line-clamp-3">{{ stripHtml(modelValue.affected_parties_details) }}</p>
              </div>
              <div class="flex items-center gap-2">
                <svg
                  class="w-5 h-5"
                  :class="modelValue.written_approvals_obtained ? 'text-green-600' : 'text-gray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span :class="modelValue.written_approvals_obtained ? 'text-gray-900' : 'text-gray-500'">
                  Written Approvals {{ modelValue.written_approvals_obtained ? 'Obtained' : 'Not Obtained' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- AEE Summary -->
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900 text-sm sm:text-base">Assessment of Environmental Effects</h3>
          </div>
          <div class="p-4 sm:p-6">
            <div class="space-y-4">
              <div v-if="modelValue.activity_description">
                <span class="text-sm text-gray-500">Activity Description:</span>
                <div class="text-sm mt-1 line-clamp-3" v-html="modelValue.activity_description"></div>
              </div>
              <div v-if="modelValue.aee_full_assessment">
                <span class="text-sm text-gray-500">Full Assessment:</span>
                <div class="text-sm mt-1 line-clamp-3" v-html="modelValue.aee_full_assessment"></div>
              </div>
              <div v-if="modelValue.positive_effects_description">
                <span class="text-sm text-gray-500">Positive Effects:</span>
                <p class="text-sm mt-1 line-clamp-3">{{ modelValue.positive_effects_description }}</p>
              </div>
              <div v-if="modelValue.effects_visual_amenity || modelValue.effects_traffic_parking || modelValue.effects_noise">
                <span class="text-sm text-gray-500">Adverse Effects Summary:</span>
                <ul class="text-sm mt-1 space-y-1 list-disc list-inside">
                  <li v-if="modelValue.effects_visual_amenity">Visual/Amenity: {{ truncate(modelValue.effects_visual_amenity, 50) }}</li>
                  <li v-if="modelValue.effects_traffic_parking">Traffic/Parking: {{ truncate(modelValue.effects_traffic_parking, 50) }}</li>
                  <li v-if="modelValue.effects_noise">Noise: {{ truncate(modelValue.effects_noise, 50) }}</li>
                </ul>
              </div>
              <div v-if="modelValue.mitigation_measures">
                <span class="text-sm text-gray-500">Mitigation Measures:</span>
                <div class="text-sm mt-1 line-clamp-3" v-html="modelValue.mitigation_measures"></div>
              </div>
              <p v-if="!hasAEEContent" class="text-gray-500 text-sm">
                AEE not yet completed
              </p>
            </div>
          </div>
        </div>

        <!-- Statutory Declarations -->
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900 text-sm sm:text-base">Statutory Declarations</h3>
          </div>
          <div class="p-4 sm:p-6">
            <div class="space-y-2">
              <div class="flex items-start gap-2">
                <svg
                  class="w-5 h-5 flex-shrink-0 mt-0.5"
                  :class="(modelValue.declaration_accuracy || modelValue.declaration_rma_compliance) ? 'text-green-600' : 'text-gray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm" :class="(modelValue.declaration_accuracy || modelValue.declaration_rma_compliance) ? 'text-gray-900' : 'text-gray-500'">
                  Declaration of Accuracy & RMA Compliance
                </span>
              </div>
              <div class="flex items-start gap-2">
                <svg
                  class="w-5 h-5 flex-shrink-0 mt-0.5"
                  :class="(modelValue.declaration_authority || modelValue.declaration_authorized) ? 'text-green-600' : 'text-gray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm" :class="(modelValue.declaration_authority || modelValue.declaration_authorized) ? 'text-gray-900' : 'text-gray-500'">
                  Declaration of Authority to Apply
                </span>
              </div>
              <div class="flex items-start gap-2">
                <svg
                  class="w-5 h-5 flex-shrink-0 mt-0.5"
                  :class="(modelValue.declaration_acknowledgment || modelValue.declaration_public_information) ? 'text-green-600' : 'text-gray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm" :class="(modelValue.declaration_acknowledgment || modelValue.declaration_public_information) ? 'text-gray-900' : 'text-gray-500'">
                  Public Information & Privacy Acknowledgment
                </span>
              </div>
              <div v-if="modelValue.requester_signature" class="mt-4 pt-4 border-t border-gray-200">
                <span class="text-sm text-gray-500">Signed by:</span>
                <p class="font-medium">{{ modelValue.requester_signature }}</p>
                <p v-if="modelValue.signature_date" class="text-sm text-gray-500">
                  Date: {{ formatSignatureDate(modelValue.signature_date) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Important Notice -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 sm:p-6">
        <div class="flex items-start gap-2 sm:gap-3">
          <svg class="w-5 h-5 sm:w-6 sm:h-6 text-yellow-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h4 class="font-semibold text-yellow-900 text-sm sm:text-base">Before You Submit</h4>
            <ul class="mt-2 text-xs sm:text-sm text-yellow-800 space-y-1 list-disc list-inside">
              <li>Review all information carefully for accuracy and completeness</li>
              <li>Ensure all required fields are completed</li>
              <li>For Resource Consent applications, verify all statutory declarations are confirmed</li>
              <li>Once submitted, you cannot edit the application (you may need to withdraw and resubmit)</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Completeness Check -->
      <div v-if="!isComplete" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <div class="flex items-start gap-2 sm:gap-3">
          <svg class="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-red-900 text-xs sm:text-sm">Application Incomplete</h5>
            <p class="text-red-800 text-xs sm:text-sm mt-1">
              Please complete all required sections before submitting. Use the Previous button to go back and fill in missing information.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  councilName: {
    type: String,
    default: 'Council'
  },
  requestTypeName: {
    type: String,
    default: 'Application'
  },
  applicationFee: {
    type: String,
    default: 'TBD'
  },
  isResourceConsent: {
    type: Boolean,
    default: false
  },
  stepConfigs: {
    type: Array,
    default: () => []
  },
  usesConfigurableSteps: {
    type: Boolean,
    default: false
  },
  requestTypeDetails: {
    type: Object,
    default: null
  }
})

// Filter steps that should show on review
const reviewSections = computed(() => {
  if (!props.usesConfigurableSteps || !props.stepConfigs) {
    return []
  }

  return props.stepConfigs.filter(step => step.show_on_review)
})

// Check if property details should be displayed
const hasPropertyDetails = computed(() => {
  // Always show for resource consent
  if (props.isResourceConsent) {
    return true
  }

  // Check if property data actually exists in the request
  return !!(props.modelValue.property || props.modelValue.property_address)
})

// Check if a step has any content to show on review
const hasReviewContent = (step) => {
  if (!step.sections) return false

  for (const section of step.sections) {
    if (!section.show_on_review) continue

    for (const field of section.fields) {
      if (field.show_on_review && props.modelValue[field.field_name]) {
        return true
      }
    }
  }

  return false
}

// Format field value for display
const formatFieldValue = (field, value) => {
  if (value === undefined || value === null || value === '') {
    return 'Not provided'
  }

  // Check field type
  if (field.field_type === 'Check') {
    return value ? 'Yes' : 'No'
  }

  if (field.field_type === 'Date' && value) {
    // Format date nicely
    try {
      return new Date(value).toLocaleDateString('en-NZ', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch (e) {
      return value
    }
  }

  if (field.field_type === 'Currency' && value) {
    return `₱${Number(value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  if (field.field_type === 'Select') {
    return value
  }

  if (field.field_type === 'Attach' || field.field_type === 'Attach Image') {
    return value ? '✓ File attached' : 'Not provided'
  }

  return value
}

// RC-specific computed properties
const hasAnyConsentType = computed(() => {
  return !!(
    props.modelValue.consent_type_land_use ||
    props.modelValue.consent_type_subdivision ||
    props.modelValue.consent_type_discharge ||
    props.modelValue.consent_type_water ||
    props.modelValue.consent_type_coastal
  )
})

const activityStatusClass = computed(() => {
  const status = props.modelValue.activity_status_type
  if (status === 'Permitted') return 'bg-green-100 text-green-800'
  if (status === 'Controlled') return 'bg-blue-100 text-blue-800'
  if (status === 'Restricted Discretionary') return 'bg-yellow-100 text-yellow-800'
  if (status === 'Discretionary') return 'bg-orange-100 text-orange-800'
  if (status === 'Non-Complying') return 'bg-red-100 text-red-800'
  if (status === 'Prohibited') return 'bg-gray-800 text-white'
  return 'bg-gray-100 text-gray-800'
})

const hasNaturalHazards = computed(() => {
  return !!(
    props.modelValue.hazard_flooding ||
    props.modelValue.hazard_earthquake ||
    props.modelValue.hazard_landslip ||
    props.modelValue.hazard_coastal
  )
})

const hasConsultation = computed(() => {
  return !!(
    props.modelValue.consultation_undertaken ||
    props.modelValue.consultation_summary ||
    props.modelValue.affected_parties_details ||
    props.modelValue.written_approvals_obtained
  )
})

const hasAEEContent = computed(() => {
  return !!(
    props.modelValue.activity_description ||
    props.modelValue.aee_full_assessment ||
    props.modelValue.positive_effects_description ||
    props.modelValue.effects_visual_amenity ||
    props.modelValue.effects_traffic_parking ||
    props.modelValue.effects_noise ||
    props.modelValue.mitigation_measures ||
    // Legacy fields
    props.modelValue.aee_activity_description ||
    props.modelValue.aee_existing_environment ||
    props.modelValue.assessment_of_effects ||
    props.modelValue.aee_document
  )
})

// Helper functions
const stripHtml = (html) => {
  if (!html) return ''
  const tmp = document.createElement('div')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

const truncate = (text, maxLength) => {
  if (!text) return ''
  const clean = stripHtml(text)
  if (clean.length <= maxLength) return clean
  return clean.substring(0, maxLength) + '...'
}

const formatSignatureDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('en-NZ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch (e) {
    return dateStr
  }
}

const isComplete = computed(() => {
  // Basic required fields
  const hasBasicInfo = !!(
    props.modelValue.council &&
    props.modelValue.request_type &&
    props.modelValue.requester_name &&
    props.modelValue.requester_email &&
    props.modelValue.property_address &&
    props.modelValue.delivery_preference
  )

  // If RC, check additional requirements
  if (props.isResourceConsent) {
    const hasRCRequirements = !!(
      hasAnyConsentType.value &&
      props.modelValue.activity_status_type &&
      props.modelValue.activity_description &&
      props.modelValue.aee_full_assessment &&
      props.modelValue.declaration_accuracy &&
      props.modelValue.declaration_authority &&
      props.modelValue.declaration_acknowledgment
    )
    return hasBasicInfo && hasRCRequirements
  }

  return hasBasicInfo
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
