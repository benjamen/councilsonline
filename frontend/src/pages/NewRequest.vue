<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-4">
          <div class="flex items-center space-x-3">
            <button @click="goBack" class="text-gray-500 hover:text-gray-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h1 class="text-xl font-bold text-gray-900">New Application</h1>
              <p class="text-sm text-gray-500">Step {{ currentStep }} of {{ totalSteps }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button @click="saveDraft(false)" variant="outline" theme="gray" :loading="savingDraft">
              Save Draft
            </Button>
            <Button @click="saveDraft(true)" variant="outline" theme="gray" :loading="savingDraft">
              Save Draft & Close
            </Button>
          </div>
        </div>
      </div>
    </header>

    <!-- Progress Bar -->
    <div class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between mb-2">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="flex items-center"
            :class="{ 'flex-1': index < steps.length - 1 }"
          >
            <div class="flex flex-col items-center">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm"
                :class="getStepClass(index + 1)"
              >
                <span v-if="index + 1 < currentStep">✓</span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <span
                class="text-xs mt-2 text-center"
                :class="index + 1 === currentStep ? 'text-blue-600 font-medium' : 'text-gray-500'"
              >
                {{ step.title }}
              </span>
            </div>
            <div
              v-if="index < steps.length - 1"
              class="flex-1 h-1 mx-4 rounded"
              :class="index + 1 < currentStep ? 'bg-blue-600' : 'bg-gray-200'"
            ></div>
          </div>
        </div>
      </div>
    </div>

<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div v-if="currentStep === 1">
            <Step1CouncilSelection
                v-model="formData"
                @council-change="onCouncilChange"
            />
        </div>

        <div v-if="currentStep === 2">
            <Step2RequestType
                v-model="formData"
                :request-types="requestTypes"
                @type-selected="selectRequestType"
            />
        </div>

        <div v-if="currentStep === 3">
            <Step3ProcessInfo
                :request-type-details="selectedRequestTypeDetails"
                :council-name="getCouncilName()"
                v-model="formData"
                @continue="handleNext"
            />
        </div>

        <!-- Dynamic Steps (for configured request types like Philippines SPISC) -->
        <DynamicStepRenderer
          v-if="currentStep > 3 && currentStep < totalSteps && usesConfigurableSteps && getCurrentStepConfig()"
          :stepConfig="getCurrentStepConfig()"
          v-model="formData"
          :showBackButton="currentStep > 1"
          :isLastStep="currentStep === totalSteps - 1"
          @continue="handleNext"
          @back="handlePrevious"
        />

        <!-- FRD Step 1: Applicant & Proposal Details (consolidates old Steps 4,5,6) -->
        <Step1ApplicantProposal
          v-if="currentStep === 4 && isResourceConsent && !usesConfigurableSteps"
          v-model="formData"
          :user-profile="userProfile"
          :properties="properties"
        />

        <!-- FRD Step 2: Natural Hazards Assessment -->
        <Step2NaturalHazards
          v-if="currentStep === 5 && isResourceConsent && !usesConfigurableSteps"
          v-model="formData"
        />

        <!-- FRD Step 3: NES Assessment -->
        <Step3NESAssessment
          v-if="currentStep === 6 && isResourceConsent && !usesConfigurableSteps"
          v-model="formData"
        />

        <!-- FRD Step 4: Boundary Approvals & Affected Parties -->
        <Step4Approvals
          v-if="currentStep === 7 && isResourceConsent && !usesConfigurableSteps"
          v-model="formData"
        />

        <!-- FRD Step 5: Consultation with Other Parties -->
        <Step5Consultation
          v-if="currentStep === 8 && isResourceConsent && !usesConfigurableSteps"
          v-model="formData"
        />

        <!-- FRD Step 6: Plans & Documents Upload -->
        <Step6Documents
          v-if="currentStep === 9 && isResourceConsent && !usesConfigurableSteps"
          v-model="formData"
        />

        <!-- FRD Step 7: Assessment of Environmental Effects (AEE) -->
        <Step7AEE
          v-if="currentStep === 10 && isResourceConsent && !usesConfigurableSteps"
          v-model="formData"
        />

        <!-- FRD Step 9: Declaration & Submission -->
        <Step9Submission
          v-if="currentStep === 11 && isResourceConsent && !usesConfigurableSteps"
          v-model="formData"
        />

        <!-- Review Step (Final Step for all request types) -->
        <div v-if="currentStep === totalSteps">
            <Step17Review
                v-model="formData"
                :council-name="getCouncilName()"
                :request-type-name="getRequestTypeName()"
                :application-fee="getApplicationFee()"
                :is-resource-consent="isResourceConsent"
                :step-configs="stepConfigs"
                :uses-configurable-steps="usesConfigurableSteps"
            />
        </div>
    </div>

    <!-- Navigation Buttons -->
        <div class="mt-8 flex justify-between items-center">
            <button
                v-if="currentStep > 1"
                @click="currentStep--"
                class="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
            >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Previous
            </button>
            <div v-else></div>

            <!-- Next button: Show on all steps except the last step -->
            <button
                type="button"
                v-if="currentStep < totalSteps"
                @click="handleNext"
                :disabled="!canProceed"
                class="px-6 py-3 font-medium rounded-lg transition-colors flex items-center"
                :class="canProceed
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'"
            >
                Next
                <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </button>

            <!-- Submit button: Only show on the last step -->
            <button
                v-else
                @click="handleSubmit"
                :disabled="!canSubmit || submitting"
                class="px-6 py-3 font-medium rounded-lg transition-colors"
                :class="canSubmit && !submitting
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'"
            >
                <span v-if="submitting">Submitting...</span>
                <span v-else>Submit Application</span>
            </button>
        </div>
</main>

    <!-- Affected Party Modal -->
    <div
      v-if="showAffectedPartyModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="cancelAffectedParty"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingPartyIndex !== null ? 'Edit' : 'Add' }} Affected Party
            </h3>
            <button
              @click="cancelAffectedParty"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="px-6 py-4 space-y-4">
          <!-- Party Name * -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Party Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="affectedPartyForm.party_name"
              type="text"
              required
              placeholder="e.g., John Smith"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Relationship * -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Relationship <span class="text-red-500">*</span>
            </label>
            <select
              v-model="affectedPartyForm.relationship"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select relationship</option>
              <option value="Adjacent Property Owner">Adjacent Property Owner</option>
              <option value="Neighbor">Neighbor</option>
              <option value="Iwi">Iwi</option>
              <option value="Infrastructure Provider">Infrastructure Provider</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <!-- Contact Information -->
          <div class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Contact Information</h4>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Email</label>
                <input
                  v-model="affectedPartyForm.email"
                  type="email"
                  placeholder="email@example.com"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Phone</label>
                <input
                  v-model="affectedPartyForm.phone"
                  type="tel"
                  placeholder="021 123 4567"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>
            </div>
          </div>

          <!-- Addresses -->
          <div class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Addresses</h4>

            <div class="space-y-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Property Address</label>
                <textarea
                  v-model="affectedPartyForm.property_address"
                  rows="2"
                  placeholder="123 Main Street, Suburb, City"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">The property address affected by this proposal</p>
              </div>

              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Postal Address</label>
                <textarea
                  v-model="affectedPartyForm.postal_address"
                  rows="2"
                  placeholder="PO Box 123, Suburb, City"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">For correspondence (if different from property address)</p>
              </div>
            </div>
          </div>

          <!-- Approval -->
          <div class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Written Approval</h4>

            <div class="flex items-start mb-3">
              <input
                type="checkbox"
                v-model="affectedPartyForm.approval_obtained"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label class="ml-3 text-sm text-gray-700">
                Written approval obtained from this party
              </label>
            </div>

            <div v-if="affectedPartyForm.approval_obtained" class="ml-7 space-y-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Approval Date</label>
                <input
                  v-model="affectedPartyForm.approval_date"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Approval Document</label>
                <input
                  type="file"
                  @change="handleApprovalDocumentUpload"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                <p class="mt-1 text-xs text-gray-500">Upload written approval (PDF, Word, or image, max 10MB)</p>
                <div v-if="affectedPartyForm.approval_document" class="mt-2 text-xs text-green-600 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>{{ typeof affectedPartyForm.approval_document === 'object' ? affectedPartyForm.approval_document.name : 'Document attached' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Comments -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Comments</label>
            <textarea
              v-model="affectedPartyForm.comments"
              rows="3"
              placeholder="Any additional notes about this party or their concerns..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            ></textarea>
          </div>
        </div>

        <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            @click="cancelAffectedParty"
            type="button"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="saveAffectedParty"
            type="button"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            {{ editingPartyIndex !== null ? 'Update' : 'Add' }} Party
          </button>
        </div>
      </div>
    </div>

    <!-- Specialist Report Modal -->
    <div
      v-if="showSpecialistReportModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="cancelSpecialistReport"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingReportIndex !== null ? 'Edit' : 'Add' }} Specialist Report
            </h3>
            <button
              @click="cancelSpecialistReport"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="px-6 py-4 space-y-4">
          <!-- Report Type * -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Report Type <span class="text-red-500">*</span>
            </label>
            <select
              v-model="specialistReportForm.report_type"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select report type</option>
              <option value="Traffic Impact Assessment">Traffic Impact Assessment</option>
              <option value="Acoustic Assessment">Acoustic Assessment</option>
              <option value="Geotechnical Report">Geotechnical Report</option>
              <option value="Ecological Assessment">Ecological Assessment</option>
              <option value="Archaeological Assessment">Archaeological Assessment</option>
              <option value="Landscape Assessment">Landscape Assessment</option>
              <option value="Contaminated Land Assessment">Contaminated Land Assessment</option>
              <option value="Flood Risk Assessment">Flood Risk Assessment</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <!-- Consultant Details -->
          <div class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Consultant Details</h4>

            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Specialist Name <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="specialistReportForm.specialist_name"
                  type="text"
                  required
                  placeholder="e.g., Dr. Jane Smith"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Company/Organization</label>
                <input
                  v-model="specialistReportForm.specialist_company"
                  type="text"
                  placeholder="e.g., ABC Consultants Ltd"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- Report Details -->
          <div class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Report Details</h4>

            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Report Date <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="specialistReportForm.report_date"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p class="mt-1 text-xs text-gray-500">Date the report was prepared or finalized</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Document <span class="text-red-500">*</span>
                </label>
                <input
                  type="file"
                  @change="handleReportDocumentUpload"
                  accept=".pdf,.doc,.docx"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                <p class="mt-1 text-xs text-gray-500">Upload the specialist report (PDF or Word, max 10MB)</p>
                <div v-if="specialistReportForm.document" class="mt-2 text-xs text-green-600 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>{{ typeof specialistReportForm.document === 'object' ? specialistReportForm.document.name : 'Document attached' }}</span>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Summary</label>
                <textarea
                  v-model="specialistReportForm.summary"
                  rows="4"
                  placeholder="Brief summary of key findings and recommendations..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">Optional: Provide a brief summary of the report's key findings</p>
              </div>
            </div>
          </div>
        </div>

        <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            @click="cancelSpecialistReport"
            type="button"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="saveSpecialistReport"
            type="button"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            {{ editingReportIndex !== null ? 'Update' : 'Add' }} Report
          </button>
        </div>
      </div>
    </div>

    <!-- HAIL Activity Modal -->
    <div
      v-if="showHAILModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="cancelHAIL"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingHAILIndex !== null ? 'Edit' : 'Add' }} HAIL Activity
            </h3>
            <button
              @click="cancelHAIL"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="px-6 py-4 space-y-4">
          <!-- Activity Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Activity Description <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="hailForm.activity_description"
              rows="3"
              required
              placeholder="Describe the HAIL activity (e.g., Former service station, industrial site)..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <!-- HAIL Category -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              HAIL Category
            </label>
            <select
              v-model="hailForm.hail_category"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select HAIL category</option>
              <option value="Category A - Petroleum/Oil Storage">Category A - Petroleum/Oil Storage</option>
              <option value="Category B - Asbestos Products">Category B - Asbestos Products</option>
              <option value="Category C - Chemicals">Category C - Chemicals</option>
              <option value="Category D - Engineering Workshops">Category D - Engineering Workshops</option>
              <option value="Category E - Gasworks/Coke Works">Category E - Gasworks/Coke Works</option>
              <option value="Category F - Horticulture">Category F - Horticulture</option>
              <option value="Category G - Landfills/Waste Disposal">Category G - Landfills/Waste Disposal</option>
              <option value="Category H - Metal Treatment">Category H - Metal Treatment</option>
              <option value="Category I - Timber Treatment">Category I - Timber Treatment</option>
            </select>
          </div>

          <!-- Status Checkboxes -->
          <div class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Activity Status</h4>
            <div class="grid md:grid-cols-3 gap-3">
              <div class="flex items-center">
                <input
                  type="checkbox"
                  id="hail-current"
                  v-model="hailForm.currently_undertaken"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="hail-current" class="ml-2 text-sm text-gray-700">Currently Being Undertaken</label>
              </div>

              <div class="flex items-center">
                <input
                  type="checkbox"
                  id="hail-previous"
                  v-model="hailForm.previously_undertaken"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="hail-previous" class="ml-2 text-sm text-gray-700">Previously Undertaken</label>
              </div>

              <div class="flex items-center">
                <input
                  type="checkbox"
                  id="hail-likely"
                  v-model="hailForm.likely_undertaken"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="hail-likely" class="ml-2 text-sm text-gray-700">Likely to Have Been Undertaken</label>
              </div>
            </div>
          </div>

          <!-- Investigation -->
          <div class="flex items-center">
            <input
              type="checkbox"
              id="hail-investigated"
              v-model="hailForm.preliminary_investigation_done"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="hail-investigated" class="ml-2 text-sm text-gray-700">Preliminary Investigation Completed</label>
          </div>

          <!-- Proposed Activities -->
          <div class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-900 mb-3">Proposed Activities</h4>
            <div class="space-y-2 p-3 border border-gray-200 rounded bg-gray-50">
              <div class="flex items-center">
                <input
                  type="checkbox"
                  id="hail-activity-fuel"
                  v-model="proposedActivities.fuel"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="hail-activity-fuel" class="ml-2 text-sm text-gray-700">Removing or replacing fuel storage system</label>
              </div>
              <div class="flex items-center">
                <input
                  type="checkbox"
                  id="hail-activity-disturb"
                  v-model="proposedActivities.disturb"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="hail-activity-disturb" class="ml-2 text-sm text-gray-700">Disturbing soil</label>
              </div>
              <div class="flex items-center">
                <input
                  type="checkbox"
                  id="hail-activity-sample"
                  v-model="proposedActivities.sample"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="hail-activity-sample" class="ml-2 text-sm text-gray-700">Sampling soil</label>
              </div>
              <div class="flex items-center">
                <input
                  type="checkbox"
                  id="hail-activity-subdivide"
                  v-model="proposedActivities.subdivide"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="hail-activity-subdivide" class="ml-2 text-sm text-gray-700">Subdividing land</label>
              </div>
              <div class="flex items-center">
                <input
                  type="checkbox"
                  id="hail-activity-change"
                  v-model="proposedActivities.change"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="hail-activity-change" class="ml-2 text-sm text-gray-700">Changing use of land</label>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-2">Select all proposed activities that apply</p>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Additional Notes</label>
            <textarea
              v-model="hailForm.notes"
              rows="3"
              placeholder="Additional notes about the HAIL activity..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
        </div>

        <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            @click="cancelHAIL"
            type="button"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="saveHAIL"
            type="button"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            {{ editingHAILIndex !== null ? 'Update' : 'Add' }} Activity
          </button>
        </div>
      </div>
    </div>

    <!-- Proposed Conditions Modal -->
    <div
      v-if="showConditionsModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showConditionsModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              Browse Condition Templates
            </h3>
            <button
              @click="showConditionsModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto">
          <div class="grid md:grid-cols-3 gap-6 p-6">
            <!-- Left Column: Template Browser (2/3 width) -->
            <div class="md:col-span-2 space-y-4">
              <!-- Category Filter -->
              <div class="flex items-center gap-2 mb-4 pb-4 border-b border-gray-200">
                <label class="text-sm font-medium text-gray-700">Filter by Category:</label>
                <select
                  v-model="selectedCategory"
                  class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option v-for="category in conditionCategories" :key="category" :value="category">
                    {{ category }}
                  </option>
                </select>
                <span class="ml-auto text-xs text-gray-500">
                  {{ filteredConditionTemplates.length }} template{{ filteredConditionTemplates.length !== 1 ? 's' : '' }}
                </span>
              </div>

              <!-- Loading State -->
              <div v-if="loadingTemplates" class="text-center py-12">
                <svg class="animate-spin h-8 w-8 mx-auto text-blue-600" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p class="mt-2 text-sm text-gray-500">Loading templates...</p>
              </div>

              <!-- Templates List -->
              <div v-else-if="filteredConditionTemplates.length > 0" class="space-y-3">
                <div
                  v-for="template in filteredConditionTemplates"
                  :key="template.name"
                  class="p-4 bg-white border border-gray-300 rounded-lg hover:border-blue-400 hover:shadow-sm transition-all"
                >
                  <div class="flex items-start justify-between mb-2">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-1">
                        <h4 class="text-sm font-semibold text-gray-900">{{ template.template_name }}</h4>
                        <span v-if="template.condition_code" class="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs font-mono rounded">
                          {{ template.condition_code }}
                        </span>
                      </div>
                      <div class="flex items-center gap-2 mb-2">
                        <span class="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">
                          {{ template.condition_category }}
                        </span>
                        <span v-if="template.timing" class="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded">
                          {{ template.timing }}
                        </span>
                        <span v-if="template.monitoring_required" class="px-2 py-0.5 text-xs bg-orange-100 text-orange-700 rounded">
                          Monitoring Required
                        </span>
                      </div>
                      <div class="text-xs text-gray-700 line-clamp-3" v-html="template.condition_text"></div>
                    </div>
                    <button
                      @click="addConditionFromTemplate(template)"
                      type="button"
                      class="ml-3 px-3 py-1.5 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 flex items-center gap-1 flex-shrink-0"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                      Add
                    </button>
                  </div>
                </div>
              </div>

              <!-- No Templates -->
              <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <svg class="w-12 h-12 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-sm text-gray-500">No templates found for selected category</p>
              </div>

              <!-- Add Custom Condition Button -->
              <div class="pt-4 border-t border-gray-200">
                <button
                  @click="addCustomCondition"
                  type="button"
                  class="w-full px-4 py-2.5 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 flex items-center justify-center gap-2 border-2 border-dashed border-gray-300"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Add Custom Condition
                </button>
              </div>
            </div>

            <!-- Right Column: Selected Conditions (1/3 width) -->
            <div class="md:col-span-1 bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 class="text-sm font-semibold text-gray-900 mb-3 flex items-center justify-between">
                <span>Selected Conditions</span>
                <span class="px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">
                  {{ formData.proposed_conditions.length }}
                </span>
              </h4>

              <div v-if="formData.proposed_conditions.length > 0" class="space-y-2 max-h-[600px] overflow-y-auto">
                <div
                  v-for="(condition, index) in formData.proposed_conditions"
                  :key="index"
                  class="p-2 bg-white rounded border border-gray-300 text-xs"
                >
                  <div class="flex items-start justify-between mb-1">
                    <div class="flex items-center gap-1">
                      <span class="px-1.5 py-0.5 bg-gray-100 text-gray-700 font-mono text-xs rounded">
                        {{ condition.condition_number }}
                      </span>
                      <span class="px-1.5 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                        {{ condition.condition_category }}
                      </span>
                    </div>
                    <button
                      @click="removeCondition(index)"
                      type="button"
                      class="text-red-600 hover:bg-red-50 rounded p-0.5"
                      title="Remove"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <div class="text-gray-700 line-clamp-2" v-html="condition.condition_text"></div>
                </div>
              </div>

              <div v-else class="text-center py-8 text-xs text-gray-500">
                <svg class="w-8 h-8 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                No conditions selected
              </div>
            </div>
          </div>

          <!-- Custom Condition Editor (appears when editing) -->
          <div v-if="editingConditionIndex !== null || conditionForm.condition_text || conditionForm.condition_category" class="border-t border-gray-200 bg-gray-50 p-6">
            <h4 class="text-sm font-semibold text-gray-900 mb-4">
              {{ editingConditionIndex !== null ? 'Edit' : 'Add Custom' }} Condition
            </h4>

            <div class="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">
                  Condition Number <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="conditionForm.condition_number"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., 1"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">
                  Category <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="conditionForm.condition_category"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select category</option>
                  <option v-for="category in conditionCategories.filter(c => c !== 'All')" :key="category" :value="category">
                    {{ category }}
                  </option>
                </select>
              </div>
            </div>

            <div class="mb-4">
              <label class="block text-xs font-medium text-gray-700 mb-1">
                Condition Text <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="conditionForm.condition_text"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter the condition text..."
              ></textarea>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                v-model="conditionForm.compliance_notes"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Optional notes about this condition..."
              ></textarea>
            </div>

            <div class="flex justify-end gap-2 mt-4">
              <button
                @click="cancelConditionEdit"
                type="button"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                @click="saveCondition"
                type="button"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              >
                {{ editingConditionIndex !== null ? 'Update' : 'Add' }} Condition
              </button>
            </div>
          </div>
        </div>

        <div class="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex justify-end">
          <button
            @click="showConditionsModal = false"
            type="button"
            class="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createResource, Input, Button, call } from 'frappe-ui'
import CouncilSelector from '../components/CouncilSelector.vue'
import Step1CouncilSelection from '../components/request-steps/Step1CouncilSelection.vue'
import Step2RequestType from '../components/request-steps/Step2RequestType.vue'
import Step3ProcessInfo from '../components/request-steps/Step3ProcessInfo.vue'
// FRD-compliant step components
import Step1ApplicantProposal from '../components/request-steps/Step1ApplicantProposal.vue'
import Step2NaturalHazards from '../components/request-steps/Step2NaturalHazards.vue'
import Step3NESAssessment from '../components/request-steps/Step3NESAssessment.vue'
import Step4Approvals from '../components/request-steps/Step4Approvals.vue'
import Step5Consultation from '../components/request-steps/Step5Consultation.vue'
import Step6Documents from '../components/request-steps/Step6Documents.vue'
import Step7AEE from '../components/request-steps/Step7AEE.vue'
import Step9Submission from '../components/request-steps/Step9Submission.vue'
import Step17Review from '../components/request-steps/Step17Review.vue'
import DynamicStepRenderer from '../components/DynamicStepRenderer.vue'
import { useCouncilStore } from '../stores/councilStore'
import { session } from '../data/session'
import { useFormValidation } from '../composables/useFormValidation'
import { useStepNavigation } from '../composables/useStepNavigation'
import { formatFileSize } from '../utils/fileHelpers'

const router = useRouter()
const route = useRoute()
const councilStore = useCouncilStore()

// User profile data
const userProfile = ref(null)
const loadingProfile = ref(false)
const userCompanyAccount = ref(null)

// Form state
const currentStep = ref(1)
const totalSteps = computed(() => steps.value.length)
const savingDraft = ref(false)
const submitting = ref(false)
const uploadedFiles = ref([])
const fileInput = ref(null)
const bookingMeeting = ref(false)
const requestingMeeting = ref(false)
const showActivityStatusHelp = ref(false)

// Dynamic step configuration
const stepConfigs = ref([])
const loadingStepConfigs = ref(false)
const usesConfigurableSteps = ref(false)

// Available consent types (managed configuration)
const availableConsentTypes = [
  'Land Use',
  'Subdivision',
  'Discharge Permit',
  'Water Permit',
  'Coastal Permit'
]

const steps = computed(() => {
  const baseSteps = [
    { title: 'Council', number: 1 },
    { title: 'Type', number: 2 },
    { title: 'Process Info', number: 3 }
  ]

  // If using configurable steps, add them dynamically
  if (usesConfigurableSteps.value && stepConfigs.value.length > 0) {
    stepConfigs.value.forEach((config, index) => {
      baseSteps.push({
        title: config.step_title,
        number: baseSteps.length + 1,
        code: config.step_code,
        config: config,
        isDynamic: true
      })
    })
  }
  // Add RC-specific steps (FRD 9-step structure) - backward compatibility
  else if (isResourceConsent.value) {
    baseSteps.push({ title: 'Applicant & Proposal', number: 4 })  // FRD Step 1
    baseSteps.push({ title: 'Natural Hazards', number: 5 })        // FRD Step 2
    baseSteps.push({ title: 'NES Assessment', number: 6 })         // FRD Step 3
    baseSteps.push({ title: 'Approvals', number: 7 })              // FRD Step 4
    baseSteps.push({ title: 'Consultation', number: 8 })           // FRD Step 5
    baseSteps.push({ title: 'Documents', number: 9 })              // FRD Step 6
    baseSteps.push({ title: 'AEE', number: 10 })                   // FRD Step 7
    baseSteps.push({ title: 'Submission', number: 11 })            // FRD Step 9
  }

  // Review step is always last
  baseSteps.push({ title: 'Review', number: baseSteps.length + 1 })

  return baseSteps
})

// Form data
const formData = ref({
  council: '',
  request_type: '',
  request_category: '', // Store the category of the selected request type
  property: '',
  property_address: '',
  legal_description: '',
  valuation_reference: '',
  parcel_id: '',
  ct_reference: '',
  property_coordinates: '',
  hazard_data: null,
  zone: '',
  activity_zone: '',
  brief_description: '',
  detailed_description: '',
  estimated_value: null,
  proposed_start_date: '',
  terms_accepted: false,

  // Required applicant fields
  applicant_phone: '',
  applicant_type: '',

  // Company submission fields
  submitted_on_behalf_of: 'Myself', // 'Myself' or 'Company'
  company_account: null,

  // Agent workflow fields
  acting_on_behalf: false,
  applicant_name: '',
  applicant_email: '',

  // Resource Consent specific fields
  consent_types: [], // Array of consent type objects
  activity_status: '',
  applicant_reference_number: '',
  delivery_preference: '',
  pim_reference: '',

  // Proposal Details
  building_height: null,
  building_floor_area: null,
  earthworks_volume: null,
  earthworks_vertical_alteration: null,
  vehicle_movements_daily: null,
  parking_spaces_provided: null,
  hours_of_operation: '',
  consent_term_requested: '',

  // Site & Environment
  site_topography: '',
  existing_vegetation_description: '',
  watercourses_present: false,
  watercourse_description: '',
  existing_infrastructure: '',
  contamination_status_hail: '',

  // Permitted Boundary Activity (RMA s87BA)
  boundary_description: '',
  boundary_activity_description: '',
  boundary_owner_approval_obtained: false,
  boundary_approval_date: '',
  boundary_approval_document: null,

  // Natural Hazards (structured)
  natural_hazards: [],

  // NES Assessments
  nes_assessments: [],

  // HAIL Activities
  hail_activities: [],

  // Confidential Information (RMA s42)
  confidential_information_claimed: false,
  confidential_information_reason: '',

  // AEE Fields
  assessment_of_effects: '',
  effects_on_people: '',
  physical_effects: '',
  earthworks_effects: '',
  discharge_contaminants_effects: '',
  ecosystem_effects: '',
  hazard_risk_assessment: '',
  cultural_effects: '',

  // NEW: Structured AEE fields + document upload
  aee_document: null,
  aee_activity_description: '',
  aee_activity_status: '',
  aee_existing_environment: '',
  aee_site_area: null,
  aee_current_use: '',
  aee_zoning: '',
  aee_overlays: '',
  aee_designations: '',
  aee_part2_assessment: '',

  // NEW: AEE child tables
  aee_plan_rules: [],
  aee_compliance_standards: [],
  aee_written_approvals: [],
  aee_proposed_conditions: [],
  aee_consultation_summary: '',

  // Note: planning_assessment and rma_part2_assessment are back-office fields
  // completed by council officers, not applicants
  alternatives_considered: '',
  mitigation_proposed: '',

  // NEW: Owner/Occupier fields
  applicant_is_not_owner: false,
  owner_name: '',
  owner_email: '',
  owner_phone: '',
  owner_address: '',

  // NEW: Certificate of Title document
  certificate_of_title_document: null,

  // NEW: Statutory declarations
  declaration_rma_compliance: false,
  declaration_public_information: false,
  declaration_authorized: false,

  // NEW: Invoicing details
  invoice_to: 'Applicant',
  invoice_name: '',
  invoice_email: '',
  invoice_address: '',
  purchase_order_number: '',

  // NEW: Transfer deposit (RC-specific)
  transfer_deposit_required: false,
  transfer_deposit_consent_number: '',

  // Affected Parties
  affected_parties: [], // Array of affected parties
  written_approvals_obtained: 0, // Count of approvals obtained

  // Iwi Consultation
  iwi_consultation_undertaken: false,
  iwi_consulted: '',
  cultural_impact_assessment: null, // CIA file upload
  iwi_response_summary: '', // Summary of iwi consultation responses

  // Specialist Reports & Conditions
  specialist_reports: [], // Array of specialist reports
  proposed_conditions: [], // Array of proposed conditions
})

// Property Search Autocomplete State
const propertySearchQuery = ref('')
const propertySearchResults = ref([])
const propertySearchLoading = ref(false)
const showPropertyDropdown = ref(false)
let propertySearchTimeout = null

// Selected Request Type Details (with council-specific info)
const selectedRequestTypeDetails = ref(null)

// Natural Hazards - RMA s104
const naturalHazardTypes = [
  'Earthquake',
  'Fire',
  'Tsunami',
  'Erosion',
  'Volcanic and Geothermal',
  'Flood',
  'Sedimentation',
  'Subsidence',
  'Wind',
  'Landslip',
  'Drought'
]

const selectedHazards = ref([])
const hazardData = ref({})

// Get or create hazard data object
const getHazardData = (hazard) => {
  if (!hazardData.value[hazard]) {
    hazardData.value[hazard] = {
      hazard_type: hazard,
      present: true,
      risk_level: '',
      assessment_notes: '',
      mitigation_required: false
    }
  }
  return hazardData.value[hazard]
}

// Watch selectedHazards to update formData.natural_hazards
watch(selectedHazards, (newHazards) => {
  formData.value.natural_hazards = newHazards.map(hazard => getHazardData(hazard))
}, { deep: true })

// Watch hazardData to update formData.natural_hazards
watch(hazardData, () => {
  formData.value.natural_hazards = selectedHazards.value.map(hazard => getHazardData(hazard))
}, { deep: true })

// National Environmental Standards - Must match backend RC NES Item options exactly
const nesTypes = [
  { value: 'Contaminated Soil (HAIL)', label: 'NES for Assessing and Managing Contaminants in Soil (HAIL)' },
  { value: 'Air Quality', label: 'NES for Air Quality' },
  { value: 'Drinking Water', label: 'NES for Sources of Human Drinking Water' },
  { value: 'Freshwater', label: 'NES for Freshwater Management' },
  { value: 'Plantation Forestry', label: 'NES for Plantation Forestry' },
  { value: 'Electricity Transmission', label: 'NES for Electricity Transmission Activities' },
  { value: 'Telecommunications', label: 'NES for Telecommunication Facilities' },
  { value: 'Other', label: 'Other NES' }
]

const nesData = ref({})

// Get or create NES data object
const getNESData = (nesType) => {
  if (!nesData.value[nesType]) {
    nesData.value[nesType] = {
      nes_type: nesType,
      applies: false,
      description: '',
      compliance_notes: ''
    }
  }
  return nesData.value[nesType]
}

// NES Document Upload Handling
const handleNESDocumentUpload = (event, nesType) => {
  const file = event.target.files[0]
  if (!file) return

  // Validation
  if (file.size > 10 * 1024 * 1024) {
    alert('File size must be less than 10MB')
    event.target.value = ''
    return
  }

  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/jpg', 'image/png']
  if (!allowedTypes.includes(file.type)) {
    alert('Only PDF, Word documents, and images are allowed')
    event.target.value = ''
    return
  }

  // Add to attachments with NES category
  formData.value.attachments.push({
    document_category: 'NES Documentation',
    document_type: 'NES Assessment',
    file: file,
    description: `NES Assessment for ${nesType}`,
    nes_type: nesType  // Track which NES this belongs to
  })

  event.target.value = ''
}

const getNESDocuments = (nesType) => {
  return formData.value.attachments.filter(att =>
    att.document_category === 'NES Documentation' && att.nes_type === nesType
  )
}

const removeNESDocument = (nesType, docIdx) => {
  const nesDocuments = getNESDocuments(nesType)
  const docToRemove = nesDocuments[docIdx]
  const globalIdx = formData.value.attachments.indexOf(docToRemove)
  if (globalIdx > -1) {
    formData.value.attachments.splice(globalIdx, 1)
  }
}

// Certificate of Title Upload Handler
const handleCTUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validation
  if (file.size > 10 * 1024 * 1024) {
    alert('File size must be less than 10MB')
    event.target.value = ''
    return
  }

  const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
  if (!allowedTypes.includes(file.type)) {
    alert('Only PDF and image files (JPG, PNG) are allowed for Certificate of Title')
    event.target.value = ''
    return
  }

  // Store the file reference
  formData.value.certificate_of_title_document = file

  event.target.value = ''
}

// AEE Document Upload Handler
const handleAEEUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validation
  if (file.size > 20 * 1024 * 1024) {
    alert('File size must be less than 20MB')
    event.target.value = ''
    return
  }

  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  if (!allowedTypes.includes(file.type)) {
    alert('Only PDF and Word documents (.doc, .docx) are allowed for AEE documents')
    event.target.value = ''
    return
  }

  // Store the file reference
  formData.value.aee_document = file

  event.target.value = ''
}

// Watch nesData to update formData.nes_assessments
watch(nesData, () => {
  formData.value.nes_assessments = nesTypes
    .filter(nes => getNESData(nes.value).applies)
    .map(nes => getNESData(nes.value))
}, { deep: true })

// Computed: Check if NES Soils is selected (for conditional HAIL section)
const isNESSoilsSelected = computed(() => {
  return formData.value.nes_assessments.some(
    nes => nes.nes_type && nes.nes_type.includes('HAIL')
  )
})

// HAIL Activities Management
// HAIL Activity Modal
const showHAILModal = ref(false)
const editingHAILIndex = ref(null)
const hailForm = ref({
  activity_description: '',
  hail_category: '',
  currently_undertaken: false,
  previously_undertaken: false,
  likely_undertaken: false,
  preliminary_investigation_done: false,
  proposed_activities: [],
  notes: ''
})
const proposedActivities = ref({
  fuel: false,
  disturb: false,
  sample: false,
  subdivide: false,
  change: false
})

const addHAILActivity = () => {
  // Reset form
  hailForm.value = {
    activity_description: '',
    hail_category: '',
    currently_undertaken: false,
    previously_undertaken: false,
    likely_undertaken: false,
    preliminary_investigation_done: false,
    proposed_activities: [],
    notes: ''
  }
  proposedActivities.value = {
    fuel: false,
    disturb: false,
    sample: false,
    subdivide: false,
    change: false
  }
  editingHAILIndex.value = null
  showHAILModal.value = true
}

const editHAILActivity = (index) => {
  const hail = formData.value.hail_activities[index]
  hailForm.value = { ...hail }

  // Convert proposed_activities array to checkbox states
  proposedActivities.value = {
    fuel: hail.proposed_activities?.some(a => a.activity_type === 'Removing or replacing fuel storage system') || false,
    disturb: hail.proposed_activities?.some(a => a.activity_type === 'Disturbing soil') || false,
    sample: hail.proposed_activities?.some(a => a.activity_type === 'Sampling soil') || false,
    subdivide: hail.proposed_activities?.some(a => a.activity_type === 'Subdividing land') || false,
    change: hail.proposed_activities?.some(a => a.activity_type === 'Changing use of land') || false
  }

  editingHAILIndex.value = index
  showHAILModal.value = true
}

const saveHAIL = () => {
  if (!hailForm.value.activity_description) {
    alert('Please enter activity description')
    return
  }

  // Convert checkbox states back to proposed_activities array
  const proposedActivitiesArray = []
  if (proposedActivities.value.fuel) proposedActivitiesArray.push({ activity_type: 'Removing or replacing fuel storage system' })
  if (proposedActivities.value.disturb) proposedActivitiesArray.push({ activity_type: 'Disturbing soil' })
  if (proposedActivities.value.sample) proposedActivitiesArray.push({ activity_type: 'Sampling soil' })
  if (proposedActivities.value.subdivide) proposedActivitiesArray.push({ activity_type: 'Subdividing land' })
  if (proposedActivities.value.change) proposedActivitiesArray.push({ activity_type: 'Changing use of land' })

  const hailData = {
    ...hailForm.value,
    proposed_activities: proposedActivitiesArray
  }

  if (editingHAILIndex.value !== null) {
    // Edit existing
    formData.value.hail_activities[editingHAILIndex.value] = hailData
  } else {
    // Add new
    formData.value.hail_activities.push(hailData)
  }

  showHAILModal.value = false
}

const cancelHAIL = () => {
  showHAILModal.value = false
}

const removeHAILActivity = (index) => {
  if (confirm('Remove this HAIL activity?')) {
    formData.value.hail_activities.splice(index, 1)
  }
}

// HAIL Proposed Activity checkbox handlers
const toggleHAILProposedActivity = (hailIndex, activityType) => {
  const hail = formData.value.hail_activities[hailIndex]
  if (!hail.proposed_activities) {
    hail.proposed_activities = []
  }

  const activityIndex = hail.proposed_activities.findIndex(a => a.activity_type === activityType)
  if (activityIndex > -1) {
    hail.proposed_activities.splice(activityIndex, 1)
  } else {
    hail.proposed_activities.push({ activity_type: activityType })
  }
}

const isHAILActivitySelected = (hailIndex, activityType) => {
  const hail = formData.value.hail_activities[hailIndex]
  if (!hail.proposed_activities) return false
  return hail.proposed_activities.some(a => a.activity_type === activityType)
}

// Proposal Details Accordion State
const proposalAccordion = ref({
  building: true,  // Start with first section open
  earthworks: false,
  traffic: false,
  operations: false
})

const toggleProposalSection = (section) => {
  proposalAccordion.value[section] = !proposalAccordion.value[section]
}

// Boundary Approval Document Upload
const handleBoundaryApprovalUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    formData.value.boundary_approval_document = file
  }
}

// Track initial form state to detect changes
const initialFormData = ref(JSON.parse(JSON.stringify(formData.value)))

// Computed property to check if form has changes
// Exclude terms_accepted from change detection since it's not actual application data
const hasFormChanges = computed(() => {
  const currentCopy = { ...formData.value }
  const initialCopy = { ...initialFormData.value }

  // Remove terms_accepted from comparison
  delete currentCopy.terms_accepted
  delete initialCopy.terms_accepted

  const current = JSON.stringify(currentCopy)
  const initial = JSON.stringify(initialCopy)
  return current !== initial
})

// Computed property to check if Resource Consent request
const isResourceConsent = computed(() => {
  return formData.value.request_category === 'Resource Consent'
})

// Consent type helpers
const hasConsentType = (type) => {
  return formData.value.consent_types?.some(ct => ct.consent_type === type) || false
}

const isLandUse = computed(() => hasConsentType('Land Use'))
const isSubdivision = computed(() => hasConsentType('Subdivision'))
const isWaterPermit = computed(() => hasConsentType('Water Permit'))
const isDischargePermit = computed(() => hasConsentType('Discharge Permit'))
const isCoastalPermit = computed(() => hasConsentType('Coastal Permit'))

// Combined checks for common requirements
const requiresNaturalHazardsAssessment = computed(() => {
  return isLandUse.value || isSubdivision.value
})

const eligibleForFastTrack = computed(() => {
  // Fast-track available for all except Subdivision, and only if Controlled activity
  const isControlled = formData.value.activity_status === 'Controlled'
  const notSubdivision = !isSubdivision.value
  return isControlled && notSubdivision && isResourceConsent.value
})

const hasUnlimitedDuration = computed(() => {
  // LUC and SC can have unlimited duration
  return (isLandUse.value || isSubdivision.value) &&
         !(isWaterPermit.value || isDischargePermit.value || isCoastalPermit.value)
})

// Activity status validation warning
const activityStatusWarning = computed(() => {
  if (!formData.value.activity_status) return null

  switch (formData.value.activity_status) {
    case 'Non-Complying':
      return '⚠️ Non-complying activities face higher scrutiny and longer processing times. Consider pre-application meeting.'
    case 'Discretionary':
      return 'ℹ️ Discretionary activities may require public notification depending on effects assessment.'
    case 'Controlled':
      return '✓ Controlled activities must be granted consent. Council will focus on appropriate conditions.'
    default:
      return null
  }
})

// Show submit button only if there are changes or files uploaded
const canSubmit = computed(() => {
  return hasFormChanges.value || uploadedFiles.value.length > 0
})

// Get request types (will be loaded based on council selection)
const requestTypes = ref({ data: [], loading: false, error: null })

// Get user's properties
const properties = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Property',
    fields: ['name', 'property_id', 'street_address', 'suburb', 'city', 'legal_description', 'certificate_of_title'],
    limit_page_length: 100,
  },
  auto: true,
})

// Methods
const onCouncilChange = async (councilCode) => {
  if (!councilCode) {
    requestTypes.value = { data: [], loading: false, error: null }
    return
  }

  // Load request types for the selected council
  requestTypes.value.loading = true
  requestTypes.value.error = null

  try {
    await councilStore.loadRequestTypesForCouncil(councilCode)
    requestTypes.value.data = councilStore.availableRequestTypes
    console.log(`[NewRequest] Loaded ${requestTypes.value.data.length} request types for council ${councilCode}`)
  } catch (error) {
    requestTypes.value.error = error.message || 'Failed to load request types'
    console.error('[NewRequest] Failed to load request types:', error)
  } finally {
    requestTypes.value.loading = false
  }
}

const goBack = () => {
  if (confirm('Are you sure you want to leave? Any unsaved changes will be lost.')) {
    router.push({ name: 'Dashboard' })
  }
}

const getStepClass = (stepNumber) => {
  if (stepNumber < currentStep.value) {
    return 'bg-blue-600 text-white'
  } else if (stepNumber === currentStep.value) {
    return 'bg-blue-600 text-white'
  } else {
    return 'bg-gray-200 text-gray-600'
  }
}

const selectRequestType = async (type) => {
  console.log('[NewRequest] Selecting Request Type:', type.name, type.type_name)
  formData.value.request_type = type.name
  formData.value.request_category = type.category || ''

  // Store the full request type details for the Process Info step
  selectedRequestTypeDetails.value = type

  console.log('[NewRequest] Form data updated:', {
    request_type: formData.value.request_type,
    request_category: formData.value.request_category,
    details: selectedRequestTypeDetails.value
  })

  // Load step configuration for this request type
  await loadStepConfiguration(type.name)
}

// Load step configuration from API
const loadStepConfiguration = async (requestType) => {
  if (!requestType || !formData.value.council) {
    console.log('[NewRequest] Skipping step config load - missing requestType or council')
    return
  }

  try {
    loadingStepConfigs.value = true
    console.log('[NewRequest] Loading step config for:', requestType, 'council:', formData.value.council)

    const result = await call('lodgeick.api.get_request_type_steps', {
      request_type: requestType,
      council_code: formData.value.council
    })

    console.log('[NewRequest] Step config API result:', result)

    if (result && result.uses_config && result.steps && result.steps.length > 0) {
      stepConfigs.value = result.steps
      usesConfigurableSteps.value = true
      console.log('[NewRequest] Loaded', stepConfigs.value.length, 'configured steps')
    } else {
      // No configuration found - use hardcoded flow
      stepConfigs.value = []
      usesConfigurableSteps.value = false
      console.log('[NewRequest] No step configuration found - using hardcoded flow')
    }
  } catch (error) {
    console.error('[NewRequest] Error loading step configuration:', error)
    stepConfigs.value = []
    usesConfigurableSteps.value = false
  } finally {
    loadingStepConfigs.value = false
  }
}

const onPropertySelect = () => {
  if (formData.value.property) {
    const selected = properties.data.find(p => p.name === formData.value.property)
    if (selected) {
      // Populate address
      formData.value.property_address = `${selected.street_address}, ${selected.suburb}, ${selected.city}`

      // Populate property details
      formData.value.legal_description = selected.legal_description || ''
      formData.value.ct_reference = selected.certificate_of_title || ''
      formData.value.parcel_id = selected.property_id || ''
      formData.value.zone = selected.zoning || ''

      // Populate coordinates if available
      if (selected.latitude && selected.longitude) {
        formData.value.property_coordinates = `${selected.latitude},${selected.longitude}`
      }

      console.log('[NewRequest] Populated property details from existing property:', {
        address: formData.value.property_address,
        legal_description: formData.value.legal_description,
        ct_reference: formData.value.ct_reference,
        parcel_id: formData.value.parcel_id,
        zone: formData.value.zone
      })
    }
  }
}

// Property Search Autocomplete Handlers
const handlePropertySearch = () => {
  // Clear existing timeout
  if (propertySearchTimeout) {
    clearTimeout(propertySearchTimeout)
  }

  const query = propertySearchQuery.value.trim()

  // Only search if query is at least 3 characters
  if (query.length < 3) {
    propertySearchResults.value = []
    return
  }

  // Debounce search
  propertySearchTimeout = setTimeout(async () => {
    propertySearchLoading.value = true
    showPropertyDropdown.value = true

    try {
      const response = await fetch('/api/method/lodgeick.api.search_property_address', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token
        },
        body: JSON.stringify({ query })
      })

      const data = await response.json()

      if (data.message && data.message.results) {
        propertySearchResults.value = data.message.results
      } else {
        propertySearchResults.value = []
      }
    } catch (error) {
      console.error('[PropertySearch] Error searching properties:', error)
      propertySearchResults.value = []
    } finally {
      propertySearchLoading.value = false
    }
  }, 300) // 300ms debounce
}

const selectProperty = (result) => {
  // Set the property address
  formData.value.property_address = result.address
  propertySearchQuery.value = result.address

  // Set legal description if available
  if (result.property?.legal_description) {
    formData.value.legal_description = result.property.legal_description
  }

  // Set title number if available
  if (result.property?.title_no) {
    formData.value.ct_reference = result.property.title_no
  }

  // Set valuation reference if available
  if (result.property?.valuation_reference) {
    formData.value.valuation_reference = result.property.valuation_reference
  }

  // Set parcel ID if available
  if (result.property?.parcel_id) {
    formData.value.parcel_id = result.property.parcel_id
  }

  // Set property coordinates if available
  if (result.projected_x && result.projected_y) {
    formData.value.property_coordinates = `NZTM2000: ${result.projected_x.toFixed(2)}, ${result.projected_y.toFixed(2)}`
  }

  // Extract and set zoning from district plan hazards
  if (result.hazards?.districtPlan && Array.isArray(result.hazards.districtPlan) && result.hazards.districtPlan.length > 0) {
    const districtPlan = result.hazards.districtPlan[0]
    if (districtPlan.attributes?.Zone_Code || districtPlan.attributes?.ZONE_CODE) {
      formData.value.zone = districtPlan.attributes.Zone_Code || districtPlan.attributes.ZONE_CODE
    } else if (districtPlan.attributes?.Zone_Name || districtPlan.attributes?.ZONE_NAME) {
      formData.value.zone = districtPlan.attributes.Zone_Name || districtPlan.attributes.ZONE_NAME
    }
  }

  // Store full hazard data for potential future use
  formData.value.hazard_data = result.hazards

  // Close dropdown
  showPropertyDropdown.value = false
  propertySearchResults.value = []

  console.log('[PropertySearch] Selected property:', {
    address: result.address,
    legal_description: formData.value.legal_description,
    title_no: formData.value.ct_reference,
    zone: formData.value.zone,
    hazards: result.hazards
  })
}

// Close dropdown when clicking outside
const closePropertyDropdown = () => {
  showPropertyDropdown.value = false
}

// Clear property address to allow new search
const clearPropertyAddress = () => {
  formData.value.property_address = ''
  formData.value.legal_description = ''
  formData.value.ct_reference = ''
  formData.value.valuation_reference = ''
  formData.value.parcel_id = ''
  formData.value.zone = ''
  formData.value.property_coordinates = ''
  formData.value.hazard_data = null
  propertySearchQuery.value = ''
  propertySearchResults.value = []
  console.log('[PropertySearch] Cleared property data for new search')
}

const canProceed = computed(() => {
  const step = currentStep.value

  switch (step) {
    case 1:
      // Step 1: Council selection
      return !!formData.value.council

    case 2:
      // Step 2: Request type selection
      return !!formData.value.request_type

    case 3:
      // Step 3: Process Info - always can proceed (just informational)
      return true

    case 4:
      // Step 4: Applicant & Proposal (FRD) - always can proceed
      // toRaw() is used in Step1ApplicantProposal to prevent reactive loops
      return true

    case 5:
      // Step 5: Natural Hazards (FRD Step 2) - Required for Land Use/Subdivision only
      if (isResourceConsent.value) {
        // Extract to avoid reactive tracking issues
        const consentTypes = formData.value.consent_types
        const requiresHazards = consentTypes?.some(ct =>
          ct.consent_type === 'Land Use' || ct.consent_type === 'Subdivision'
        )
        if (requiresHazards) {
          const hazards = formData.value.natural_hazards
          const confirmed = formData.value.no_natural_hazards_confirmed
          const hasHazards = hazards && hazards.length > 0
          return hasHazards || confirmed
        }
        return true
      }
      return true

    case 6:
      // Step 6: NES Assessment (FRD Step 3) - Optional (can have "no NES confirmed")
      return true

    case 7:
      // Step 7: Approvals (FRD Step 4) - Optional
      return true

    case 8:
      // Step 8: Consultation (FRD Step 5) - Optional
      return true

    case 9:
      // Step 9: Documents (FRD Step 6) - Optional (but recommended)
      return true

    case 10:
      // Step 10: AEE (FRD Step 7) - REQUIRED based on completion method
      if (isResourceConsent.value) {
        if (formData.value.aee_completion_method === 'upload') {
          return !!formData.value.aee_document && !!formData.value.aee_document_confirmed
        } else {
          // Inline method - require key fields
          return !!formData.value.aee_activity_description?.trim() &&
            !!formData.value.aee_existing_environment?.trim() &&
            !!formData.value.assessment_of_effects?.trim() &&
            !!formData.value.aee_inline_confirmed
        }
      }
      return true

    case 11:
      // Step 11: Submission (FRD Step 9) - REQUIRED all 3 declarations and signature
      if (isResourceConsent.value) {
        const hasDeclarations = formData.value.declaration_rma_compliance &&
          formData.value.declaration_public_information &&
          formData.value.declaration_authorized
        const hasSignature = !!formData.value.applicant_signature_first_name?.trim() &&
          !!formData.value.applicant_signature_last_name?.trim() &&
          !!formData.value.applicant_signature_date

        return hasDeclarations && hasSignature
      }
      return true

    default:
      // Review step and any other steps - always allow
      return true
  }
})

const nextStep = () => {
  const totalStepsValue = totalSteps.value
  const currentStepValue = currentStep.value
  const canProceedValue = canProceed.value

  console.log('[NewRequest] nextStep called', {
    canProceed: canProceedValue,
    currentStep: currentStepValue,
    totalSteps: totalStepsValue,
    steps: steps.value,
    willProceed: canProceedValue && currentStepValue < totalStepsValue
  })

  if (canProceedValue && currentStepValue < totalStepsValue) {
    currentStep.value++
    console.log('[NewRequest] Moved to step:', currentStep.value)
  } else {
    console.warn('[NewRequest] Cannot proceed:', {
      canProceed: canProceedValue,
      currentStep: currentStepValue,
      totalSteps: totalStepsValue,
      reason: !canProceedValue ? 'canProceed returned false' : 'at last step'
    })
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const loadDraft = async (requestId) => {
  try {
    const response = await fetch('/api/method/lodgeick.api.load_draft_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        request_id: requestId
      })
    })

    const result = await response.json()

    if (result.message && result.message.success) {
      // Load the form data
      formData.value = result.message.form_data || {}

      // Redirect to the saved step
      currentStep.value = result.message.current_step || 1

      console.log(`Draft loaded successfully. Resuming at step ${currentStep.value}`)
    } else {
      throw new Error(result.message || 'Failed to load draft')
    }
  } catch (error) {
    console.error('Error loading draft:', error)
    alert('Failed to load draft. Starting new application.')
  }
}

const saveDraft = async (closeAfterSave = false) => {
  savingDraft.value = true
  try {
    const response = await fetch('/api/method/lodgeick.api.create_draft_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        data: formData.value,
        current_step: currentStep.value,
        total_steps: totalSteps.value
      })
    })

    const result = await response.json()

    if (result.message && result.message.success) {
      // Store the request ID in formData for future updates
      if (result.message.request_id && !formData.value.request_id) {
        formData.value.request_id = result.message.request_id
      }

      alert(`Draft saved successfully! Request ID: ${result.message.request_number}`)

      // If closeAfterSave, redirect to dashboard
      if (closeAfterSave) {
        router.push({ name: 'Dashboard' })
      }

      // Return the result for use by other functions
      return result.message
    } else {
      throw new Error(result.message || 'Failed to save draft')
    }
  } catch (error) {
    console.error('Error saving draft:', error)
    alert('Failed to save draft. Please try again.')
    return null
  } finally {
    savingDraft.value = false
  }
}

const triggerFileUpload = () => {
  fileInput.value.click()
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  uploadedFiles.value.push(...files)
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
}

// formatFileSize is now imported from utils/fileHelpers.js

const getCouncilName = () => {
  const council = councilStore.councils?.find(c => c.council_code === formData.value.council)
  return council?.council_name || 'Council'
}

const getRequestTypeName = () => {
  const type = requestTypes.data?.find(t => t.name === formData.value.request_type)
  return type?.type_name || 'N/A'
}

const getApplicationFee = () => {
  const type = requestTypes.data?.find(t => t.name === formData.value.request_type)
  return type?.base_fee ? `$${type.base_fee}` : 'TBD'
}

// Navigation handlers
const handleNext = () => {
  if (canProceed.value) {
    currentStep.value++
  }
}

const handlePrevious = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// Get the step configuration for the current step
const getCurrentStepConfig = () => {
  if (!usesConfigurableSteps.value || stepConfigs.value.length === 0) {
    return null
  }

  // Current step is 4+ (after Council, Type, Process Info)
  // Map to stepConfigs array (0-indexed)
  const configIndex = currentStep.value - 4

  if (configIndex >= 0 && configIndex < stepConfigs.value.length) {
    return stepConfigs.value[configIndex]
  }

  return null
}

const handleSubmit = async () => {
  await submitApplication()
}

const submitApplication = async () => {
  // NEW: Check statutory declarations instead of single terms_accepted
  if (!formData.value.declaration_rma_compliance ||
      !formData.value.declaration_public_information ||
      !formData.value.declaration_authorized) {
    alert('Please confirm all three statutory declarations before submitting your application')
    return
  }

  submitting.value = true
  try {
    // Step 1: Create draft request
    const createResponse = await fetch('/api/method/lodgeick.api.create_draft_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        data: formData.value
      })
    })

    const createResult = await createResponse.json()

    if (!createResult.message || !createResult.message.success) {
      throw new Error('Failed to create request')
    }

    const requestId = createResult.message.request_id

    // Step 2: Upload files if any
    if (uploadedFiles.value.length > 0) {
      for (const file of uploadedFiles.value) {
        const fileFormData = new FormData()
        fileFormData.append('file', file)
        fileFormData.append('doctype', 'Request')
        fileFormData.append('docname', requestId)
        fileFormData.append('is_private', 0)

        await fetch('/api/method/upload_file', {
          method: 'POST',
          headers: {
            'X-Frappe-CSRF-Token': window.csrf_token
          },
          body: fileFormData
        })
      }
    }

    // NEW: Upload Certificate of Title document if provided
    if (formData.value.certificate_of_title_document) {
      const ctFormData = new FormData()
      ctFormData.append('file', formData.value.certificate_of_title_document)
      ctFormData.append('doctype', 'Request')
      ctFormData.append('docname', requestId)
      ctFormData.append('fieldname', 'certificate_of_title_document')
      ctFormData.append('is_private', 0)

      await fetch('/api/method/upload_file', {
        method: 'POST',
        headers: {
          'X-Frappe-CSRF-Token': window.csrf_token
        },
        body: ctFormData
      })
    }

    // NEW: Upload AEE document if provided
    if (formData.value.aee_document) {
      const aeeFormData = new FormData()
      aeeFormData.append('file', formData.value.aee_document)
      aeeFormData.append('doctype', 'Resource Consent Application')
      aeeFormData.append('docname', requestId)
      aeeFormData.append('fieldname', 'aee_document')
      aeeFormData.append('is_private', 0)

      await fetch('/api/method/upload_file', {
        method: 'POST',
        headers: {
          'X-Frappe-CSRF-Token': window.csrf_token
        },
        body: aeeFormData
      })
    }

    // Step 3: Submit the request
    const submitResponse = await fetch('/api/method/lodgeick.lodgeick.doctype.request.request.submit_application', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        request_id: requestId
      })
    })

    const submitResult = await submitResponse.json()

    if (submitResult.message && submitResult.message.success) {
      alert(`Application submitted successfully! Request Number: ${submitResult.message.request_number}`)
      router.push({ name: 'Dashboard' })
    } else {
      throw new Error('Failed to submit application')
    }
  } catch (error) {
    console.error('Error submitting application:', error)
    alert('Failed to submit application')
  } finally {
    submitting.value = false
  }
}

const bookPreApplicationMeeting = async () => {
  if (!formData.value.request_type) {
    alert('Please complete your application details first')
    return
  }

  bookingMeeting.value = true
  try {
    // First, save as draft if not already saved
    const draftResponse = await fetch('/api/method/lodgeick.api.create_draft_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        data: formData.value
      })
    })

    const draftResult = await draftResponse.json()

    if (!draftResult.message || !draftResult.message.success) {
      throw new Error('Failed to save application')
    }

    const requestId = draftResult.message.request_id

    // Book the meeting via backend API
    const meetingResponse = await fetch('/api/method/lodgeick.api.book_council_meeting', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        request_id: requestId,
        meeting_type: 'Pre-Application Meeting'
      })
    })

    const meetingResult = await meetingResponse.json()

    if (meetingResult.message && meetingResult.message.success) {
      alert(`Pre-Application Meeting request has been submitted! A council officer will contact you within 2 business days to schedule the meeting. Task ID: ${meetingResult.message.task_id}`)
    } else {
      throw new Error(meetingResult.message || 'Failed to book meeting')
    }
  } catch (error) {
    console.error('Error booking meeting:', error)
    alert('Failed to book pre-application meeting. Please try again.')
  } finally {
    bookingMeeting.value = false
  }
}

// Resource Consent specific methods
const ciaFileInput = ref(null)

// Affected Party Modal
const showAffectedPartyModal = ref(false)
const editingPartyIndex = ref(null)
const affectedPartyForm = ref({
  party_name: '',
  relationship: '',
  property_address: '',
  email: '',
  phone: '',
  postal_address: '',
  approval_obtained: false,
  approval_date: '',
  approval_document: null,
  comments: ''
})

const addAffectedParty = () => {
  // Reset form
  affectedPartyForm.value = {
    party_name: '',
    relationship: '',
    property_address: '',
    email: '',
    phone: '',
    postal_address: '',
    approval_obtained: false,
    approval_date: '',
    approval_document: null,
    comments: ''
  }
  editingPartyIndex.value = null
  showAffectedPartyModal.value = true
}

const editAffectedParty = (index) => {
  affectedPartyForm.value = { ...formData.value.affected_parties[index] }
  editingPartyIndex.value = index
  showAffectedPartyModal.value = true
}

const saveAffectedParty = () => {
  if (!affectedPartyForm.value.party_name || !affectedPartyForm.value.relationship) {
    alert('Please enter party name and relationship')
    return
  }

  if (editingPartyIndex.value !== null) {
    // Edit existing
    formData.value.affected_parties[editingPartyIndex.value] = { ...affectedPartyForm.value }
  } else {
    // Add new
    formData.value.affected_parties.push({ ...affectedPartyForm.value })
  }

  showAffectedPartyModal.value = false
}

const cancelAffectedParty = () => {
  showAffectedPartyModal.value = false
}

const removeAffectedParty = (index) => {
  if (confirm('Remove this affected party?')) {
    formData.value.affected_parties.splice(index, 1)
  }
}

const handleApprovalDocumentUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      event.target.value = ''
      return
    }

    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/jpg',
      'image/png'
    ]
    if (!allowedTypes.includes(file.type)) {
      alert('Only PDF, Word documents, and images (JPG, PNG) are allowed')
      event.target.value = ''
      return
    }

    affectedPartyForm.value.approval_document = file
  }
}

// Specialist Report Modal
const showSpecialistReportModal = ref(false)
const editingReportIndex = ref(null)
const specialistReportForm = ref({
  report_type: '',
  specialist_name: '',
  specialist_company: '',
  report_date: '',
  document: null,
  summary: ''
})

const addSpecialistReport = () => {
  specialistReportForm.value = {
    report_type: '',
    specialist_name: '',
    specialist_company: '',
    report_date: '',
    document: null,
    summary: ''
  }
  editingReportIndex.value = null
  showSpecialistReportModal.value = true
}

const editSpecialistReport = (index) => {
  specialistReportForm.value = { ...formData.value.specialist_reports[index] }
  editingReportIndex.value = index
  showSpecialistReportModal.value = true
}

const saveSpecialistReport = () => {
  if (!specialistReportForm.value.report_type || !specialistReportForm.value.specialist_name || !specialistReportForm.value.report_date) {
    alert('Please enter report type, specialist name, and report date')
    return
  }

  if (editingReportIndex.value !== null) {
    formData.value.specialist_reports[editingReportIndex.value] = { ...specialistReportForm.value }
  } else {
    formData.value.specialist_reports.push({ ...specialistReportForm.value })
  }
  showSpecialistReportModal.value = false
}

const cancelSpecialistReport = () => {
  showSpecialistReportModal.value = false
}

const removeSpecialistReport = (index) => {
  if (confirm('Remove this specialist report?')) {
    formData.value.specialist_reports.splice(index, 1)
  }
}

const handleReportDocumentUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      event.target.value = ''
      return
    }

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      alert('Only PDF and Word documents are allowed')
      event.target.value = ''
      return
    }

    specialistReportForm.value.document = file
  }
}

const handleCIAUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      event.target.value = ''
      return
    }

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      alert('Only PDF and Word documents are allowed')
      event.target.value = ''
      return
    }

    formData.value.cultural_impact_assessment = file
  }
}

// ===== AEE Plan Assessment Handlers =====

// Plan Rules
const addPlanRule = () => {
  const rule = prompt('Enter plan rule reference (e.g., Rule 16.4.2.1)')
  if (!rule) return

  const activityStatus = prompt('Activity status (Permitted/Controlled/Restricted Discretionary/Discretionary/Non-Complying/Prohibited)')
  if (!activityStatus) return

  const description = prompt('Rule description (optional)', '')

  formData.value.aee_plan_rules.push({
    rule_reference: rule,
    activity_status: activityStatus,
    rule_description: description || ''
  })
}

const removePlanRule = (index) => {
  if (confirm('Remove this plan rule?')) {
    formData.value.aee_plan_rules.splice(index, 1)
  }
}

// Compliance Standards
const addComplianceStandard = () => {
  const standard = prompt('Enter standard reference (e.g., Building height: 8m maximum)')
  if (!standard) return

  const complies = confirm('Does the proposal comply with this standard?')
  const analysis = prompt('Compliance analysis (optional)', '')

  formData.value.aee_compliance_standards.push({
    standard_reference: standard,
    complies: complies,
    compliance_analysis: analysis || '',
    standard_description: ''
  })
}

const removeComplianceStandard = (index) => {
  if (confirm('Remove this compliance standard?')) {
    formData.value.aee_compliance_standards.splice(index, 1)
  }
}

// Written Approvals
const addWrittenApproval = () => {
  const name = prompt('Enter party name')
  if (!name) return

  const address = prompt('Party address (optional)', '')
  const attached = confirm('Is the written approval attached?')

  formData.value.aee_written_approvals.push({
    party_name: name,
    party_address: address || '',
    approval_attached: attached,
    approval_document: null
  })
}

const removeWrittenApproval = (index) => {
  if (confirm('Remove this written approval?')) {
    formData.value.aee_written_approvals.splice(index, 1)
  }
}

// AEE Proposed Conditions
const addAEECondition = () => {
  const text = prompt('Enter proposed condition')
  if (!text) return

  const number = formData.value.aee_proposed_conditions.length + 1

  formData.value.aee_proposed_conditions.push({
    condition_number: number,
    condition_text: text
  })
}

const removeAEECondition = (index) => {
  if (confirm('Remove this proposed condition?')) {
    formData.value.aee_proposed_conditions.splice(index, 1)
    // Renumber remaining conditions
    formData.value.aee_proposed_conditions.forEach((cond, idx) => {
      cond.condition_number = idx + 1
    })
  }
}

// Proposed Conditions Modal
const showConditionsModal = ref(false)
const editingConditionIndex = ref(null)
const availableConditionTemplates = ref([])
const loadingTemplates = ref(false)
const selectedCategory = ref('All')

const conditionForm = ref({
  condition_number: '',
  condition_category: '',
  condition_text: '',
  compliance_status: 'Not Started',
  compliance_due_date: '',
  compliance_notes: ''
})

const conditionCategories = [
  'All',
  'General',
  'Timing',
  'Lapse',
  'Review',
  'Financial Contribution',
  'Bonds',
  'Monitoring',
  'Environmental Management',
  'Construction',
  'Operation',
  'Landscape',
  'Ecology',
  'Archaeology',
  'Cultural',
  'Traffic',
  'Parking',
  'Noise',
  'Discharge',
  'Earthworks',
  'Heritage',
  'Water',
  'Coastal',
  'Other'
]

// Fetch condition templates based on selected consent types
const fetchConditionTemplates = async () => {
  loadingTemplates.value = true
  try {
    const selectedTypes = formData.value.consent_types.map(ct => ct.consent_type)

    // Fetch templates from backend
    const response = await fetch('/api/method/frappe.client.get_list', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        doctype: 'Consent Condition Template',
        fields: ['name', 'template_name', 'condition_code', 'condition_category', 'condition_text', 'applies_to_consent_types', 'timing', 'monitoring_required'],
        filters: {
          is_active: 1
        },
        limit_page_length: 0
      })
    })

    const data = await response.json()

    if (data.message) {
      // Filter templates that apply to selected consent types
      availableConditionTemplates.value = data.message.filter(template => {
        if (!template.applies_to_consent_types || template.applies_to_consent_types === 'All') {
          return true
        }
        return selectedTypes.some(type => template.applies_to_consent_types.includes(type))
      })
    }
  } catch (error) {
    console.error('Error fetching condition templates:', error)
    alert('Failed to load condition templates')
  } finally {
    loadingTemplates.value = false
  }
}

const filteredConditionTemplates = computed(() => {
  if (selectedCategory.value === 'All') {
    return availableConditionTemplates.value
  }
  return availableConditionTemplates.value.filter(t => t.condition_category === selectedCategory.value)
})

const openConditionsModal = async () => {
  if (!formData.value.consent_types || formData.value.consent_types.length === 0) {
    alert('Please select at least one consent type first')
    return
  }

  await fetchConditionTemplates()
  conditionForm.value = {
    condition_number: '',
    condition_category: '',
    condition_text: '',
    compliance_status: 'Not Started',
    compliance_due_date: '',
    compliance_notes: ''
  }
  editingConditionIndex.value = null
  showConditionsModal.value = true
}

const addConditionFromTemplate = (template) => {
  // Generate a condition number
  const conditionNum = (formData.value.proposed_conditions.length + 1).toString()

  const newCondition = {
    condition_number: conditionNum,
    condition_category: template.condition_category,
    condition_text: template.condition_text,
    compliance_status: 'Not Started',
    compliance_due_date: '',
    compliance_notes: ''
  }

  formData.value.proposed_conditions.push(newCondition)
}

const addCustomCondition = () => {
  conditionForm.value = {
    condition_number: (formData.value.proposed_conditions.length + 1).toString(),
    condition_category: '',
    condition_text: '',
    compliance_status: 'Not Started',
    compliance_due_date: '',
    compliance_notes: ''
  }
  editingConditionIndex.value = null
}

const editCondition = (index) => {
  conditionForm.value = { ...formData.value.proposed_conditions[index] }
  editingConditionIndex.value = index
}

const saveCondition = () => {
  if (!conditionForm.value.condition_category || !conditionForm.value.condition_text) {
    alert('Please enter condition category and text')
    return
  }

  if (editingConditionIndex.value !== null) {
    formData.value.proposed_conditions[editingConditionIndex.value] = { ...conditionForm.value }
  } else {
    formData.value.proposed_conditions.push({ ...conditionForm.value })
  }

  conditionForm.value = {
    condition_number: '',
    condition_category: '',
    condition_text: '',
    compliance_status: 'Not Started',
    compliance_due_date: '',
    compliance_notes: ''
  }
  editingConditionIndex.value = null
}

const cancelConditionEdit = () => {
  conditionForm.value = {
    condition_number: '',
    condition_category: '',
    condition_text: '',
    compliance_status: 'Not Started',
    compliance_due_date: '',
    compliance_notes: ''
  }
  editingConditionIndex.value = null
}

const removeCondition = (index) => {
  if (confirm('Remove this condition?')) {
    formData.value.proposed_conditions.splice(index, 1)
    // Renumber remaining conditions
    formData.value.proposed_conditions.forEach((cond, idx) => {
      cond.condition_number = (idx + 1).toString()
    })
  }
}

// Pre-Application Meeting Request
const meetingResource = createResource({
  url: 'lodgeick.api.book_council_meeting',
  makeParams: (values) => values,
  onSuccess: (data) => {
    if (data && data.success) {
      alert(`✅ Pre-Application Meeting Request Sent!\n\nTask #${data.task_id} has been created for the planning team.\n\nThey will contact you within 2 business days to schedule.`)
    } else {
      alert('Meeting request sent successfully! The planning team will contact you soon.')
    }
    requestingMeeting.value = false
  },
  onError: (error) => {
    console.error('Error requesting meeting:', error)
    alert('Failed to request pre-application meeting. Please try again or contact the planning team directly.')
    requestingMeeting.value = false
  }
})

const requestPreAppMeeting = async () => {
  if (!formData.value.request_type || !formData.value.property_address) {
    alert('Please complete the Request Type and Property Details first.')
    return
  }

  if (!confirm('Request a pre-application meeting? A planning officer will contact you within 2 business days to schedule.\n\nNote: You should save your application as a draft first.')) {
    return
  }

  try {
    requestingMeeting.value = true

    // First, save the draft
    const draftResult = await saveDraft()

    if (!draftResult || !draftResult.request_id) {
      alert('Please save your draft application first.')
      requestingMeeting.value = false
      return
    }

    // Then request the meeting
    meetingResource.submit({
      request_id: draftResult.request_id,
      meeting_type: 'Pre-Application Meeting'
    })
  } catch (error) {
    console.error('Error in meeting request:', error)
    alert('Failed to request pre-application meeting. Please try again.')
    requestingMeeting.value = false
  }
}

// Initialize on mount
// Load user profile and auto-populate fields
const loadUserProfile = async () => {
  try {
    loadingProfile.value = true
    const profile = await call('lodgeick.api.get_user_profile')
    userProfile.value = profile

    // Auto-populate applicant type from profile default
    if (profile.applicant_type && !formData.value.applicant_type) {
      formData.value.applicant_type = profile.applicant_type
    }

    // Auto-populate phone if not acting on behalf
    if (profile.phone && !formData.value.applicant_phone && !formData.value.acting_on_behalf) {
      formData.value.applicant_phone = profile.phone
    }

    // Auto-populate applicant name and email when not acting on behalf
    if (!formData.value.acting_on_behalf) {
      formData.value.applicant_name = `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || profile.email
      formData.value.applicant_email = profile.email
    }
  } catch (error) {
    console.error('Error loading user profile:', error)
  } finally {
    loadingProfile.value = false
  }
}

const loadCompanyAccount = async () => {
  try {
    const companyAccount = await call('lodgeick.api.get_user_company_account')
    if (companyAccount) {
      userCompanyAccount.value = companyAccount
    }
  } catch (error) {
    console.error('Error loading company account:', error)
  }
}

// Watch submitted_on_behalf_of to set company_account
watch(() => formData.value.submitted_on_behalf_of, (submittedAs) => {
  if (submittedAs === 'Company' && userCompanyAccount.value) {
    formData.value.company_account = userCompanyAccount.value.name
  } else {
    formData.value.company_account = null
  }
})

// Watch acting_on_behalf to auto-populate or clear applicant details
watch(() => formData.value.acting_on_behalf, (actingOnBehalf) => {
  if (!actingOnBehalf && userProfile.value) {
    // Auto-populate from profile
    formData.value.applicant_name = `${userProfile.value.first_name || ''} ${userProfile.value.last_name || ''}`.trim() || userProfile.value.email
    formData.value.applicant_email = userProfile.value.email
    if (userProfile.value.phone) {
      formData.value.applicant_phone = userProfile.value.phone
    }
    if (userProfile.value.applicant_type) {
      formData.value.applicant_type = userProfile.value.applicant_type
    }
  } else if (actingOnBehalf) {
    // Clear fields for agent to fill in client details
    formData.value.applicant_name = ''
    formData.value.applicant_email = ''
    formData.value.applicant_phone = ''
    // Keep applicant_type as it might be different for the client
  }
})

// Watch phone number to save back to profile when user updates it (and not acting on behalf)
watch(() => formData.value.applicant_phone, async (newPhone, oldPhone) => {
  // Only save if:
  // 1. Not acting on behalf (it's their own application)
  // 2. Profile is loaded
  // 3. Phone has actually changed
  // 4. New phone is not empty
  if (!formData.value.acting_on_behalf && userProfile.value && newPhone && newPhone !== oldPhone && newPhone !== userProfile.value.phone) {
    try {
      await call('lodgeick.api.update_user_profile', {
        phone: newPhone
      })
      // Update local profile copy
      userProfile.value.phone = newPhone
      console.log('[NewRequest] Phone number saved to profile:', newPhone)
    } catch (error) {
      console.error('[NewRequest] Error saving phone to profile:', error)
      // Don't show error to user - this is a background operation
    }
  }
})

onMounted(async () => {
  // Load user profile first
  await loadUserProfile()

  // Load company account if user has one
  await loadCompanyAccount()

  // Check if we're loading a draft
  const draftId = route.params.id || route.query.draft_id
  if (draftId) {
    await loadDraft(draftId)
  }

  // Check if council was preselected via URL or user default
  if (councilStore.preselectedFromUrl) {
    formData.value.council = councilStore.preselectedFromUrl
    await onCouncilChange(councilStore.preselectedFromUrl)
  } else {
    // Try to load user's default council
    const userCouncils = await councilStore.getUserCouncils()
    if (userCouncils.default_council) {
      formData.value.council = userCouncils.default_council
      await onCouncilChange(userCouncils.default_council)
    }
  }
})
</script>
