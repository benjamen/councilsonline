<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Review & Submit</h2>
    <p class="text-gray-600 mb-8">Review your application details before submitting</p>

    <div class="space-y-6">
      <!-- Application Summary -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div class="flex items-start justify-between">
          <div>
            <h3 class="text-lg font-semibold text-blue-900">{{ requestTypeName }}</h3>
            <p class="text-sm text-blue-700 mt-1">{{ councilName }}</p>
          </div>
          <div class="text-right">
            <div class="text-sm text-blue-600 font-medium">Application Fee</div>
            <div class="text-2xl font-bold text-blue-900">{{ applicationFee }}</div>
          </div>
        </div>
      </div>

      <!-- Applicant Details -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Applicant Details</h3>
        </div>
        <div class="p-6 space-y-3">
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <span class="text-sm text-gray-500">Name:</span>
              <p class="font-medium">{{ modelValue.applicant_name || 'Not provided' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Email:</span>
              <p class="font-medium">{{ modelValue.applicant_email || 'Not provided' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Phone:</span>
              <p class="font-medium">{{ modelValue.applicant_phone || 'Not provided' }}</p>
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
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Property Details</h3>
        </div>
        <div class="p-6">
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
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Delivery & Payment</h3>
        </div>
        <div class="p-6 space-y-3">
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
          <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900">{{ step.step_title }}</h3>
          </div>
          <div class="p-6 space-y-4">
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
          <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900">Consent Types & Activity Status</h3>
          </div>
          <div class="p-6">
            <div class="space-y-3">
              <div>
                <span class="text-sm text-gray-500">Consent Types:</span>
                <div class="mt-2 flex flex-wrap gap-2">
                  <span
                    v-for="type in (modelValue.consent_types || [])"
                    :key="type.consent_type"
                    class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                  >
                    {{ type.consent_type }}
                  </span>
                  <span v-if="!modelValue.consent_types || modelValue.consent_types.length === 0" class="text-gray-500">
                    None selected
                  </span>
                </div>
              </div>
              <div>
                <span class="text-sm text-gray-500">Activity Status:</span>
                <p class="font-medium">{{ modelValue.activity_status || 'Not specified' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- AEE Summary -->
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900">Assessment of Environmental Effects</h3>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div v-if="modelValue.aee_activity_description">
                <span class="text-sm text-gray-500">Activity Description:</span>
                <p class="text-sm mt-1 line-clamp-3">{{ modelValue.aee_activity_description }}</p>
              </div>
              <div v-if="modelValue.aee_existing_environment">
                <span class="text-sm text-gray-500">Existing Environment:</span>
                <p class="text-sm mt-1 line-clamp-3">{{ modelValue.aee_existing_environment }}</p>
              </div>
              <div v-if="modelValue.assessment_of_effects">
                <span class="text-sm text-gray-500">Effects Assessment:</span>
                <p class="text-sm mt-1 line-clamp-3">{{ modelValue.assessment_of_effects }}</p>
              </div>
              <div v-if="modelValue.aee_document" class="flex items-center gap-2 text-sm text-green-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>AEE Document attached</span>
              </div>
              <p v-if="!hasAEEContent" class="text-gray-500 text-sm">
                AEE not yet completed
              </p>
            </div>
          </div>
        </div>

        <!-- Statutory Declarations -->
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
            <h3 class="font-semibold text-gray-900">Statutory Declarations</h3>
          </div>
          <div class="p-6">
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <svg
                  class="w-5 h-5"
                  :class="modelValue.declaration_rma_compliance ? 'text-green-600' : 'text-gray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span :class="modelValue.declaration_rma_compliance ? 'text-gray-900' : 'text-gray-500'">
                  RMA Compliance Declaration
                </span>
              </div>
              <div class="flex items-center gap-2">
                <svg
                  class="w-5 h-5"
                  :class="modelValue.declaration_public_information ? 'text-green-600' : 'text-gray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span :class="modelValue.declaration_public_information ? 'text-gray-900' : 'text-gray-500'">
                  Public Information Declaration
                </span>
              </div>
              <div class="flex items-center gap-2">
                <svg
                  class="w-5 h-5"
                  :class="modelValue.declaration_authorized ? 'text-green-600' : 'text-gray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span :class="modelValue.declaration_authorized ? 'text-gray-900' : 'text-gray-500'">
                  Authorization Declaration
                </span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Important Notice -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div class="flex items-start">
          <svg class="w-6 h-6 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h4 class="font-semibold text-yellow-900">Before You Submit</h4>
            <ul class="mt-2 text-sm text-yellow-800 space-y-1 list-disc list-inside">
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
        <div class="flex items-start">
          <svg class="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-red-900 text-sm">Application Incomplete</h5>
            <p class="text-red-800 text-sm mt-1">
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

const hasAEEContent = computed(() => {
  return !!(
    props.modelValue.aee_activity_description ||
    props.modelValue.aee_existing_environment ||
    props.modelValue.assessment_of_effects ||
    props.modelValue.aee_document
  )
})

const isComplete = computed(() => {
  // Basic required fields
  const hasBasicInfo = !!(
    props.modelValue.council &&
    props.modelValue.request_type &&
    props.modelValue.applicant_name &&
    props.modelValue.applicant_email &&
    props.modelValue.property_address &&
    props.modelValue.delivery_preference
  )

  // If RC, check additional requirements
  if (props.isResourceConsent) {
    const hasRCRequirements = !!(
      props.modelValue.consent_types && props.modelValue.consent_types.length > 0 &&
      props.modelValue.activity_status &&
      props.modelValue.aee_activity_description &&
      props.modelValue.aee_existing_environment &&
      props.modelValue.assessment_of_effects &&
      props.modelValue.declaration_rma_compliance &&
      props.modelValue.declaration_public_information &&
      props.modelValue.declaration_authorized
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
