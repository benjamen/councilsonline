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

      <!-- SPISC Eligibility Summary (show for SPISC applications) -->
      <div v-if="isSPISCApplication" class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg overflow-hidden">
        <div class="bg-green-100 px-4 sm:px-6 py-3 border-b border-green-200">
          <h3 class="font-semibold text-green-900 text-sm sm:text-base flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Eligibility Summary
          </h3>
        </div>
        <div class="p-4 sm:p-6">
          <div class="grid md:grid-cols-3 gap-4">
            <div class="flex items-center gap-3">
              <div :class="ageEligible ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'" class="p-2 rounded-full">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-500">Age</p>
                <p class="font-semibold" :class="ageEligible ? 'text-green-700' : 'text-red-700'">
                  {{ calculatedAge !== null ? `${calculatedAge} years old` : 'Not provided' }}
                </p>
                <p v-if="ageEligible" class="text-xs text-green-600">Meets 60+ requirement</p>
                <p v-else-if="calculatedAge !== null" class="text-xs text-red-600">Must be 60 or older</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div :class="incomeEligible ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'" class="p-2 rounded-full">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-500">Monthly Income</p>
                <p class="font-semibold" :class="incomeEligible ? 'text-green-700' : 'text-yellow-700'">
                  {{ formatCurrency(modelValue.monthly_income) }}
                </p>
                <p v-if="incomeEligible" class="text-xs text-green-600">Below poverty threshold</p>
                <p v-else class="text-xs text-yellow-600">May affect eligibility</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div :class="overallEligible ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'" class="p-2 rounded-full">
                <svg v-if="overallEligible" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-500">Preliminary Status</p>
                <p class="font-semibold" :class="overallEligible ? 'text-green-700' : 'text-yellow-700'">
                  {{ overallEligible ? 'Likely Eligible' : 'Needs Review' }}
                </p>
                <p class="text-xs text-gray-500">Final assessment by council</p>
              </div>
            </div>
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
              <p class="font-medium">{{ applicantName || 'Not provided' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Email:</span>
              <p class="font-medium">{{ applicantEmail || 'Not provided' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Phone:</span>
              <p class="font-medium">{{ applicantPhone || 'Not provided' }}</p>
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

      <!-- Dynamic Review Sections (for configured request types) - ALL STEPS -->
      <template v-if="usesConfigurableSteps && allStepsWithData.length > 0">
        <div
          v-for="step in allStepsWithData"
          :key="step.step_code"
          class="bg-white border border-gray-200 rounded-lg overflow-hidden"
        >
          <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200 flex items-center justify-between">
            <h3 class="font-semibold text-gray-900 text-sm sm:text-base">{{ step.step_title }}</h3>
            <span v-if="getStepCompleteness(step)" class="text-xs text-green-600 flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Complete
            </span>
          </div>
          <div class="p-4 sm:p-6 space-y-4">
            <template v-for="section in step.sections" :key="section.section_code">
              <!-- Only show section if it has visible fields with values or show_on_review -->
              <div v-if="shouldShowSection(section)" class="space-y-3">
                <h4 v-if="section.section_title" class="text-sm font-medium text-gray-700 border-b border-gray-100 pb-1">
                  {{ section.section_title }}
                </h4>
                <div class="grid md:grid-cols-2 gap-4">
                  <template v-for="field in section.fields" :key="field.field_name">
                    <div v-if="shouldShowField(field)" :class="isLongField(field) ? 'md:col-span-2' : ''">
                      <span class="text-sm text-gray-500">{{ field.review_label || field.field_label }}:</span>
                      <div class="font-medium">
                        <!-- Attachment fields -->
                        <template v-if="field.field_type === 'Attach' || field.field_type === 'Attach Image'">
                          <div v-if="getFieldValue(field.field_name)" class="flex items-center gap-2 text-green-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>File uploaded</span>
                            <a v-if="getAttachmentUrl(field.field_name)" :href="getAttachmentUrl(field.field_name)" target="_blank" class="text-blue-600 hover:underline text-sm">(View)</a>
                          </div>
                          <span v-else class="text-gray-400">Not uploaded</span>
                        </template>
                        <!-- Checkbox fields -->
                        <template v-else-if="field.field_type === 'Check'">
                          <span :class="modelValue[field.field_name] ? 'text-green-600' : 'text-gray-400'">
                            {{ modelValue[field.field_name] ? 'Yes' : 'No' }}
                          </span>
                        </template>
                        <!-- Date fields -->
                        <template v-else-if="field.field_type === 'Date'">
                          <span>{{ formatDate(modelValue[field.field_name]) }}</span>
                          <span v-if="field.field_name === 'birth_date' && calculatedAge !== null" class="text-gray-500 text-sm ml-2">
                            ({{ calculatedAge }} years old)
                          </span>
                        </template>
                        <!-- Currency fields -->
                        <template v-else-if="field.field_type === 'Currency'">
                          {{ formatCurrency(modelValue[field.field_name]) }}
                        </template>
                        <!-- Pickup Schedule -->
                        <template v-else-if="field.field_type === 'Pickup Schedule'">
                          <span v-if="modelValue[field.field_name]">
                            {{ formatPickupSchedule(modelValue[field.field_name]) }}
                          </span>
                          <span v-else class="text-gray-400">Not scheduled</span>
                        </template>
                        <!-- Default -->
                        <template v-else>
                          {{ formatFieldValue(field, modelValue[field.field_name]) }}
                        </template>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </template>
            <p v-if="!hasAnyContent(step)" class="text-gray-500 text-sm">
              No information entered for this step
            </p>
          </div>
        </div>
      </template>

      <!-- Uploaded Documents Summary -->
      <div v-if="uploadedDocuments.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900 text-sm sm:text-base flex items-center gap-2">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Uploaded Documents ({{ uploadedDocuments.length }})
          </h3>
        </div>
        <div class="p-4 sm:p-6">
          <div class="grid md:grid-cols-2 gap-3">
            <div v-for="doc in uploadedDocuments" :key="doc.field_name" class="flex items-center gap-3 p-2 bg-gray-50 rounded">
              <svg class="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ doc.label }}</p>
                <a v-if="doc.url" :href="doc.url" target="_blank" class="text-xs text-blue-600 hover:underline">View file</a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Missing Documents Warning -->
      <div v-if="missingRequiredDocuments.length > 0" class="bg-orange-50 border border-orange-200 rounded-lg p-4">
        <div class="flex items-start gap-2 sm:gap-3">
          <svg class="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h5 class="font-semibold text-orange-900 text-xs sm:text-sm">Missing Required Documents</h5>
            <ul class="mt-1 text-orange-800 text-xs sm:text-sm list-disc list-inside">
              <li v-for="doc in missingRequiredDocuments" :key="doc.field_name">{{ doc.label }}</li>
            </ul>
          </div>
        </div>
      </div>

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
                Flood Hazard
              </span>
              <span
                v-if="modelValue.hazard_earthquake"
                class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium inline-flex items-center gap-1"
              >
                Earthquake/Fault Line
              </span>
              <span
                v-if="modelValue.hazard_landslip"
                class="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium inline-flex items-center gap-1"
              >
                Landslip/Slope Instability
              </span>
              <span
                v-if="modelValue.hazard_coastal"
                class="px-3 py-1 bg-cyan-100 text-cyan-800 rounded-full text-sm font-medium inline-flex items-center gap-1"
              >
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
              <li v-if="isResourceConsent">For Resource Consent applications, verify all statutory declarations are confirmed</li>
              <li v-if="isSPISCApplication">Ensure all required documents are uploaded</li>
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
            <ul v-if="missingFields.length > 0" class="mt-2 text-red-700 text-xs list-disc list-inside">
              <li v-for="field in missingFields.slice(0, 5)" :key="field">{{ field }}</li>
              <li v-if="missingFields.length > 5">...and {{ missingFields.length - 5 }} more</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
	councilName: {
		type: String,
		default: "Council",
	},
	requestTypeName: {
		type: String,
		default: "Application",
	},
	applicationFee: {
		type: String,
		default: "TBD",
	},
	isResourceConsent: {
		type: Boolean,
		default: false,
	},
	stepConfigs: {
		type: Array,
		default: () => [],
	},
	usesConfigurableSteps: {
		type: Boolean,
		default: false,
	},
	requestTypeDetails: {
		type: Object,
		default: null,
	},
})

// Check if this is a SPISC application
const isSPISCApplication = computed(() => {
	const requestType = props.requestTypeName?.toLowerCase() || ""
	return requestType.includes("spisc") || requestType.includes("social pension")
})

// Applicant details - handle both standard and SPISC field names
const applicantName = computed(() => {
	return props.modelValue.requester_name ||
	       props.modelValue.full_name ||
	       props.modelValue.applicant_name ||
	       null
})

const applicantEmail = computed(() => {
	return props.modelValue.requester_email ||
	       props.modelValue.email ||
	       props.modelValue.applicant_email ||
	       null
})

const applicantPhone = computed(() => {
	return props.modelValue.requester_phone ||
	       props.modelValue.mobile_number ||
	       props.modelValue.phone ||
	       props.modelValue.applicant_phone ||
	       null
})

// Calculate age from birth_date
const calculatedAge = computed(() => {
	const birthDate = props.modelValue.birth_date
	if (!birthDate) return null

	const today = new Date()
	const birth = new Date(birthDate)
	let age = today.getFullYear() - birth.getFullYear()
	const monthDiff = today.getMonth() - birth.getMonth()

	if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
		age--
	}

	return age
})

// SPISC eligibility checks
const ageEligible = computed(() => {
	return calculatedAge.value !== null && calculatedAge.value >= 60
})

const incomeEligible = computed(() => {
	const income = props.modelValue.monthly_income
	if (income === undefined || income === null) return true // Don't show as ineligible if not filled
	return Number(income) < 10000 // PHP 10,000 poverty threshold
})

const overallEligible = computed(() => {
	return ageEligible.value && incomeEligible.value
})

// Get all steps with their data for review (not filtered by show_on_review)
const allStepsWithData = computed(() => {
	if (!props.usesConfigurableSteps || !props.stepConfigs) {
		return []
	}
	// Return all steps that have show_on_review=true at step level OR have any data
	return props.stepConfigs.filter((step) => {
		// Always show steps marked for review
		if (step.show_on_review) return true
		// Also show if step has any entered data
		return hasAnyContent(step)
	})
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

// Get field value, handling various formats
const getFieldValue = (fieldName) => {
	const value = props.modelValue[fieldName]
	if (value === undefined || value === null || value === "") return null

	// Handle file upload arrays
	if (Array.isArray(value) && value.length > 0) {
		if (value[0]?.file_url) return value[0].file_url
	}

	return value
}

// Get attachment URL for viewing
const getAttachmentUrl = (fieldName) => {
	const value = props.modelValue[fieldName]
	if (!value) return null

	// Handle file upload arrays
	if (Array.isArray(value) && value.length > 0) {
		return value[0]?.file_url || value[0]
	}

	// Handle string URL
	if (typeof value === "string" && value.startsWith("/")) {
		return value
	}

	return null
}

// Determine if a section should be shown
const shouldShowSection = (section) => {
	// Check depends_on condition
	if (section.depends_on) {
		const condition = section.depends_on.replace("eval:", "").replace(/doc\./g, "props.modelValue.")
		try {
			// eslint-disable-next-line no-eval
			if (!eval(condition)) return false
		} catch (e) {
			// If eval fails, show the section
		}
	}

	// Show if marked for review or has any data
	if (section.show_on_review) return true

	// Check if any field has data
	for (const field of section.fields || []) {
		if (getFieldValue(field.field_name)) return true
	}

	return false
}

// Determine if a field should be shown
const shouldShowField = (field) => {
	// Check depends_on condition
	if (field.depends_on) {
		const condition = field.depends_on.replace("eval:", "").replace(/doc\./g, "props.modelValue.")
		try {
			// eslint-disable-next-line no-eval
			if (!eval(condition)) return false
		} catch (e) {
			// If eval fails, show the field
		}
	}

	// Show if marked for review or has data
	return field.show_on_review || getFieldValue(field.field_name) !== null
}

// Check if field should span full width
const isLongField = (field) => {
	return field.field_type === "Text Editor" ||
	       field.field_type === "Small Text" ||
	       field.field_type === "Long Text" ||
	       (field.field_type === "Data" && (field.field_label || "").length > 50)
}

// Check if a step has any content
const hasAnyContent = (step) => {
	if (!step.sections) return false

	for (const section of step.sections) {
		for (const field of section.fields || []) {
			if (getFieldValue(field.field_name) !== null) {
				return true
			}
		}
	}

	return false
}

// Check step completeness
const getStepCompleteness = (step) => {
	if (!step.sections) return false

	for (const section of step.sections) {
		for (const field of section.fields || []) {
			if (field.is_required && !getFieldValue(field.field_name)) {
				return false
			}
		}
	}

	return true
}

// Get list of uploaded documents
const uploadedDocuments = computed(() => {
	const docs = []

	for (const step of props.stepConfigs || []) {
		for (const section of step.sections || []) {
			for (const field of section.fields || []) {
				if ((field.field_type === "Attach" || field.field_type === "Attach Image") && getFieldValue(field.field_name)) {
					docs.push({
						field_name: field.field_name,
						label: field.field_label,
						url: getAttachmentUrl(field.field_name),
					})
				}
			}
		}
	}

	return docs
})

// Get list of missing required documents
const missingRequiredDocuments = computed(() => {
	const missing = []

	for (const step of props.stepConfigs || []) {
		for (const section of step.sections || []) {
			for (const field of section.fields || []) {
				if ((field.field_type === "Attach" || field.field_type === "Attach Image") && field.is_required && !getFieldValue(field.field_name)) {
					missing.push({
						field_name: field.field_name,
						label: field.field_label,
					})
				}
			}
		}
	}

	return missing
})

// Get list of missing required fields
const missingFields = computed(() => {
	const missing = []

	for (const step of props.stepConfigs || []) {
		for (const section of step.sections || []) {
			// Check depends_on for section
			if (section.depends_on) {
				const condition = section.depends_on.replace("eval:", "").replace(/doc\./g, "props.modelValue.")
				try {
					// eslint-disable-next-line no-eval
					if (!eval(condition)) continue
				} catch (e) {
					// If eval fails, check the section
				}
			}

			for (const field of section.fields || []) {
				if (!field.is_required) continue

				// Check depends_on for field
				if (field.depends_on) {
					const condition = field.depends_on.replace("eval:", "").replace(/doc\./g, "props.modelValue.")
					try {
						// eslint-disable-next-line no-eval
						if (!eval(condition)) continue
					} catch (e) {
						// If eval fails, check the field
					}
				}

				if (!getFieldValue(field.field_name)) {
					missing.push(field.field_label)
				}
			}
		}
	}

	return missing
})

// Format field value for display
const formatFieldValue = (field, value) => {
	if (value === undefined || value === null || value === "") {
		return "Not provided"
	}

	// Check field type
	if (field.field_type === "Check") {
		return value ? "Yes" : "No"
	}

	if (field.field_type === "Date" && value) {
		return formatDate(value)
	}

	if (field.field_type === "Currency" && value) {
		return formatCurrency(value)
	}

	if (field.field_type === "Select") {
		return value
	}

	if (field.field_type === "Attach" || field.field_type === "Attach Image") {
		return value ? "File attached" : "Not provided"
	}

	if (field.field_type === "Int") {
		return String(value)
	}

	return value
}

// Format date for display
const formatDate = (dateStr) => {
	if (!dateStr) return "Not provided"
	try {
		return new Date(dateStr).toLocaleDateString("en-PH", {
			year: "numeric",
			month: "long",
			day: "numeric",
		})
	} catch (e) {
		return dateStr
	}
}

// Format currency for display
const formatCurrency = (value) => {
	if (value === undefined || value === null || value === "") return "Not provided"
	return `PHP ${Number(value).toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

// Format pickup schedule for display
const formatPickupSchedule = (value) => {
	if (!value) return "Not scheduled"
	if (typeof value === "object") {
		return `${value.date || "Date TBD"} at ${value.time || "Time TBD"}`
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
	if (status === "Permitted") return "bg-green-100 text-green-800"
	if (status === "Controlled") return "bg-blue-100 text-blue-800"
	if (status === "Restricted Discretionary")
		return "bg-yellow-100 text-yellow-800"
	if (status === "Discretionary") return "bg-orange-100 text-orange-800"
	if (status === "Non-Complying") return "bg-red-100 text-red-800"
	if (status === "Prohibited") return "bg-gray-800 text-white"
	return "bg-gray-100 text-gray-800"
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
	if (!html) return ""
	const tmp = document.createElement("div")
	tmp.innerHTML = html
	return tmp.textContent || tmp.innerText || ""
}

const truncate = (text, maxLength) => {
	if (!text) return ""
	const clean = stripHtml(text)
	if (clean.length <= maxLength) return clean
	return clean.substring(0, maxLength) + "..."
}

const formatSignatureDate = (dateStr) => {
	if (!dateStr) return ""
	try {
		return new Date(dateStr).toLocaleDateString("en-PH", {
			year: "numeric",
			month: "long",
			day: "numeric",
		})
	} catch (e) {
		return dateStr
	}
}

const isComplete = computed(() => {
	// For SPISC, check dynamic fields
	if (isSPISCApplication.value) {
		// Check if any required fields are missing
		return missingFields.value.length === 0 && missingRequiredDocuments.value.length === 0
	}

	// Basic required fields for other types
	const hasBasicInfo = !!(
		props.modelValue.council &&
		props.modelValue.request_type &&
		(props.modelValue.requester_name || props.modelValue.full_name) &&
		(props.modelValue.requester_email || props.modelValue.email)
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
