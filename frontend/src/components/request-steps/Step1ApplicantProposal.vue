<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Applicant and Proposal Details</h2>
    <p class="text-gray-600 mb-8">Complete all sections below to provide comprehensive information for your resource consent application</p>

    <div class="space-y-8">
      <!-- SECTION 1: Applicant Details (nested component) -->
      <div class="border-b border-gray-200 pb-8">
        <Step4ApplicantDetails
          v-model="localData"
          :user-profile="userProfile"
          :user-company-account="userCompanyAccount"
        />
      </div>

      <!-- SECTION 2: Property Details (nested component) -->
      <div class="border-b border-gray-200 pb-8">
        <Step5PropertyDetails
          v-model="localData"
          :properties="properties"
          @property-select="handlePropertySelect"
        />
      </div>

      <!-- SECTION 3: Consent Information (nested component) -->
      <div class="border-b border-gray-200 pb-8">
        <Step6ConsentInfo
          v-model="localData"
        />
      </div>

      <!-- SECTION 4: Additional Consents (FRD 3.4) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Additional Consents from Other Councils</h3>
        <p class="text-sm text-gray-600 mb-4">
          Have you applied for, or are required to apply for, any additional resource consents for this proposal from another council/regional council, but not being applied under this application?
        </p>

        <div class="space-y-4">
          <div class="flex items-center space-x-4">
            <label class="flex items-center cursor-pointer">
              <input
                type="radio"
                :value="false"
                v-model="additionalConsentsRequired"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span class="ml-2 text-sm font-medium text-gray-700">No</span>
            </label>
            <label class="flex items-center cursor-pointer">
              <input
                type="radio"
                :value="true"
                v-model="additionalConsentsRequired"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span class="ml-2 text-sm font-medium text-gray-700">Yes</span>
            </label>
          </div>

          <div v-if="additionalConsentsRequired" class="mt-6">
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-base font-semibold text-gray-900">Additional Consents List</h4>
              <button
                @click="openAdditionalConsentModal()"
                type="button"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add Additional Consent
              </button>
            </div>

            <!-- Consents List -->
            <div v-if="localData.additional_consents && localData.additional_consents.length > 0" class="space-y-3">
              <div
                v-for="(consent, index) in localData.additional_consents"
                :key="index"
                class="flex items-start justify-between p-4 border border-gray-200 rounded-lg bg-white"
              >
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-900">{{ consent.consent_type }}</span>
                    <span class="px-2 py-1 text-xs font-medium rounded-full"
                      :class="{
                        'bg-yellow-100 text-yellow-800': consent.consent_status === 'Required',
                        'bg-blue-100 text-blue-800': consent.consent_status === 'Applied',
                        'bg-green-100 text-green-800': consent.consent_status === 'Granted',
                        'bg-red-100 text-red-800': consent.consent_status === 'Declined'
                      }"
                    >
                      {{ consent.consent_status }}
                    </span>
                  </div>
                  <p v-if="consent.reference_number" class="text-sm text-gray-600 mt-1">
                    Ref: {{ consent.reference_number }}
                  </p>
                </div>
                <div class="flex items-center gap-2 ml-4">
                  <button
                    @click="openAdditionalConsentModal(index)"
                    type="button"
                    class="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
                    title="Edit"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="removeAdditionalConsent(index)"
                    type="button"
                    class="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                    title="Remove"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
              <p class="text-sm text-gray-600">No additional consents added yet</p>
              <p class="text-xs text-gray-500 mt-1">Click "Add Additional Consent" to add consents from other councils</p>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION 5: PIM & Building Consent (FRD 3.5) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">PIM and Building Consent</h3>
        <p class="text-sm text-gray-600 mb-4">
          Have you applied for a Project Information Memorandum (PIM) or a Building consent for this project?
        </p>

        <div class="space-y-4">
          <div class="flex items-center space-x-4">
            <label class="flex items-center cursor-pointer">
              <input
                type="radio"
                :value="false"
                v-model="localData.pim_applied"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span class="ml-2 text-sm font-medium text-gray-700">No</span>
            </label>
            <label class="flex items-center cursor-pointer">
              <input
                type="radio"
                :value="true"
                v-model="localData.pim_applied"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span class="ml-2 text-sm font-medium text-gray-700">Yes</span>
            </label>
          </div>

          <div v-if="localData.pim_applied" class="grid md:grid-cols-2 gap-4 mt-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">PIM Number (if applicable)</label>
              <input
                v-model="localData.pim_number"
                type="text"
                placeholder="e.g., PIM-2024-001"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Building Consent Number (if applicable)</label>
              <input
                v-model="localData.building_consent_number"
                type="text"
                placeholder="e.g., BC-2024-001"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION 6: Site Visit Information (FRD 3.6) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Site Visit Information</h3>
        <p class="text-sm text-gray-600 mb-4">
          In order to assess your application it will generally be necessary for the planning officer to visit your site. This typically involves an outdoor inspection only, and there is no need for you to be home for this purpose.
        </p>

        <div class="space-y-4">
          <div class="grid md:grid-cols-2 gap-4">
            <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
              :class="localData.site_visit_locked_gates ? 'border-orange-600 bg-orange-50' : 'border-gray-200 hover:border-gray-300'"
            >
              <input
                v-model="localData.site_visit_locked_gates"
                type="checkbox"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div class="ml-3">
                <span class="font-medium text-gray-900">Locked gates or security systems present</span>
                <p class="text-xs text-gray-600 mt-1">Restricting access by Council staff</p>
              </div>
            </label>

            <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
              :class="localData.site_visit_dogs_present ? 'border-orange-600 bg-orange-50' : 'border-gray-200 hover:border-gray-300'"
            >
              <input
                v-model="localData.site_visit_dogs_present"
                type="checkbox"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div class="ml-3">
                <span class="font-medium text-gray-900">Dogs on the property</span>
                <p class="text-xs text-gray-600 mt-1">Council staff should be aware</p>
              </div>
            </label>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
              :class="localData.site_visit_health_safety_issues ? 'border-orange-600 bg-orange-50' : 'border-gray-200 hover:border-gray-300'"
            >
              <input
                v-model="localData.site_visit_health_safety_issues"
                type="checkbox"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div class="ml-3">
                <span class="font-medium text-gray-900">Other health and safety issues</span>
                <p class="text-xs text-gray-600 mt-1">Council staff should be aware before visiting</p>
              </div>
            </label>

            <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
              :class="localData.site_visit_notice_required ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300'"
            >
              <input
                v-model="localData.site_visit_notice_required"
                type="checkbox"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div class="ml-3">
                <span class="font-medium text-gray-900">Notice required prior to site visit</span>
                <p class="text-xs text-gray-600 mt-1">E.g., if the property is tenanted</p>
              </div>
            </label>
          </div>

          <div v-if="localData.site_visit_locked_gates || localData.site_visit_dogs_present || localData.site_visit_health_safety_issues || localData.site_visit_notice_required" class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Additional Details for Site Visit
            </label>
            <textarea
              v-model="localData.site_visit_details"
              rows="3"
              placeholder="Provide details so Council staff can take the necessary precautions..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- SECTION 7: Agent Details (FRD 3.7) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Agent Details</h3>
        <p class="text-sm text-gray-600 mb-4">
          You may contact Resource Consent Planning Professionals or Agents from list available in eRCS to obtain quotes from and engage them to help you prepare and lodge your application by selecting the Engage Agent button.
        </p>
        <p class="text-sm text-orange-600 mb-4 font-medium">
          Please note: You will not be able to make any more changes or complete this application once you engage an Agent.
        </p>

        <div class="flex items-center gap-4">
          <label class="flex items-center cursor-pointer">
            <input
              v-model="localData.agent_required"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm font-medium text-gray-700">No Agent Required</span>
          </label>
          <button
            type="button"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            disabled
            title="Agent engagement feature coming soon"
          >
            Engage Agent (Coming Soon)
          </button>
        </div>
      </div>

      <!-- SECTION 8: Pre-Application Meeting (FRD 3.8) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Pre-Application Meeting</h3>
        <p class="text-sm text-gray-600 mb-4">
          You may schedule a Pre-Application Meeting with the Council to seek further clarifications in respect of your application by selecting the Pre-Application Meeting button.
        </p>
        <p class="text-sm text-gray-600 mb-4">
          Please include any relevant information or documents such as conceptual plans or draft assessment of environmental effects you have.
        </p>

        <div class="flex items-center gap-4">
          <label class="flex items-center cursor-pointer">
            <input
              v-model="localData.pre_app_meeting_required"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm font-medium text-gray-700">No Meeting Required</span>
          </label>
          <button
            type="button"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            disabled
            title="Pre-application meeting feature coming soon"
          >
            View / Request Pre-Application Meeting (Coming Soon)
          </button>
        </div>
      </div>

      <!-- SECTION 9: Correspondences and Invoices (FRD 3.9) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Correspondences and Invoices</h3>
        <p class="text-sm text-gray-600 mb-4">
          All correspondence and notifications will be sent to the Applicant. If an Applicant engages an Agent, they will be sent to both parties.
        </p>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              All Invoice to be paid by *
            </label>
            <div class="space-y-2">
              <label class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors"
                :class="localData.invoice_responsible_party === 'Applicant' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
              >
                <input
                  v-model="localData.invoice_responsible_party"
                  type="radio"
                  value="Applicant"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-3 font-medium text-gray-900">Applicant</span>
              </label>
              <label class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors"
                :class="localData.invoice_responsible_party === 'Agent' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
              >
                <input
                  v-model="localData.invoice_responsible_party"
                  type="radio"
                  value="Agent"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  :disabled="!localData.agent_id"
                />
                <div class="ml-3">
                  <span class="font-medium text-gray-900">Agent</span>
                  <p v-if="!localData.agent_id" class="text-xs text-gray-500 mt-1">
                    Only available when an agent is engaged
                  </p>
                </div>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION 10: Additional Contact Persons (FRD 3.10) -->
      <div class="pb-4">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Add More Contact Persons</h3>
        <p class="text-sm text-gray-600 mb-4">
          You can also nominate third parties to be included in the list by selecting their names contact details below. You will not be able remove them from the list once the application is submitted, however you can request Consents Online Limited to do that.
        </p>

        <div class="flex justify-between items-center mb-4">
          <h4 class="text-base font-semibold text-gray-900">Additional Contacts</h4>
          <button
            @click="openAdditionalContactModal()"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Contact Person
          </button>
        </div>

        <!-- Contacts List -->
        <div v-if="localData.additional_contact_persons && localData.additional_contact_persons.length > 0" class="space-y-3">
          <div
            v-for="(contact, index) in localData.additional_contact_persons"
            :key="index"
            class="flex items-start justify-between p-4 border border-gray-200 rounded-lg bg-white"
          >
            <div class="flex-1">
              <div class="font-medium text-gray-900">{{ contact.first_name }} {{ contact.last_name }}</div>
              <div class="text-sm text-gray-600 mt-1">
                <p>{{ contact.email }}</p>
                <p>{{ contact.phone }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 ml-4">
              <button
                @click="openAdditionalContactModal(index)"
                type="button"
                class="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
                title="Edit"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                @click="removeAdditionalContact(index)"
                type="button"
                class="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                title="Remove"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
          <p class="text-sm text-gray-600">No additional contact persons added yet</p>
          <p class="text-xs text-gray-500 mt-1">Click "Add Contact Person" to nominate third parties for correspondence</p>
        </div>
      </div>
    </div>

    <!-- Additional Consent Modal -->
    <div v-if="showAdditionalConsentModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ editingConsentIndex !== null ? 'Edit' : 'Add' }} Additional Consent
          </h3>
          <button @click="closeAdditionalConsentModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Consent Type *</label>
            <select
              v-model="currentConsent.consent_type"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select consent type</option>
              <option value="Discharge Permit">Discharge Permit</option>
              <option value="Coastal Permit">Coastal Permit</option>
              <option value="Water Permit">Water Permit</option>
              <option value="NES Soils">NES Soils</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Consent Status *</label>
            <select
              v-model="currentConsent.consent_status"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select status</option>
              <option value="Required">Required</option>
              <option value="Applied">Applied</option>
              <option value="Granted">Granted</option>
              <option value="Declined">Declined</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Reference Number (if applicable)</label>
            <input
              v-model="currentConsent.reference_number"
              type="text"
              placeholder="e.g., DP-2024-001"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div class="sticky bottom-0 bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t border-gray-200">
          <button
            @click="closeAdditionalConsentModal"
            type="button"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="saveAdditionalConsent"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            :disabled="!currentConsent.consent_type || !currentConsent.consent_status"
          >
            {{ editingConsentIndex !== null ? 'Update' : 'Add' }} Consent
          </button>
        </div>
      </div>
    </div>

    <!-- Additional Contact Modal -->
    <div v-if="showAdditionalContactModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ editingContactIndex !== null ? 'Edit' : 'Add' }} Contact Person
          </h3>
          <button @click="closeAdditionalContactModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">First Name *</label>
            <input
              v-model="currentContact.first_name"
              type="text"
              placeholder="John"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Last Name *</label>
            <input
              v-model="currentContact.last_name"
              type="text"
              placeholder="Smith"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Email Address *</label>
            <input
              v-model="currentContact.email"
              type="email"
              placeholder="john@example.com"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number *</label>
            <input
              v-model="currentContact.phone"
              type="tel"
              placeholder="021 123 4567"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
        </div>

        <div class="sticky bottom-0 bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t border-gray-200">
          <button
            @click="closeAdditionalContactModal"
            type="button"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="saveAdditionalContact"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            :disabled="!currentContact.first_name || !currentContact.last_name || !currentContact.email || !currentContact.phone"
          >
            {{ editingContactIndex !== null ? 'Update' : 'Add' }} Contact
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch, computed } from 'vue'
import Step4ApplicantDetails from './Step4ApplicantDetails.vue'
import Step5PropertyDetails from './Step5PropertyDetails.vue'
import Step6ConsentInfo from './Step6ConsentInfo.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  userProfile: {
    type: Object,
    default: null
  },
  userCompanyAccount: {
    type: Object,
    default: null
  },
  properties: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'property-select'])

// Local data with all FRD fields
const localData = ref({
  ...props.modelValue,
  // Additional Consents (FRD 3.4)
  additional_consents: props.modelValue.additional_consents || [],
  // PIM & Building Consent (FRD 3.5)
  pim_applied: props.modelValue.pim_applied || false,
  pim_number: props.modelValue.pim_number || '',
  building_consent_applied: props.modelValue.building_consent_applied || false,
  building_consent_number: props.modelValue.building_consent_number || '',
  // Site Visit (FRD 3.6)
  site_visit_locked_gates: props.modelValue.site_visit_locked_gates || false,
  site_visit_dogs_present: props.modelValue.site_visit_dogs_present || false,
  site_visit_health_safety_issues: props.modelValue.site_visit_health_safety_issues || false,
  site_visit_notice_required: props.modelValue.site_visit_notice_required || false,
  site_visit_details: props.modelValue.site_visit_details || '',
  // Agent Details (FRD 3.7)
  agent_required: props.modelValue.agent_required || false,
  agent_id: props.modelValue.agent_id || null,
  // Pre-App Meeting (FRD 3.8)
  pre_app_meeting_required: props.modelValue.pre_app_meeting_required || false,
  pre_app_meeting_id: props.modelValue.pre_app_meeting_id || null,
  // Correspondence (FRD 3.9)
  correspondence_recipient: props.modelValue.correspondence_recipient || 'Applicant',
  invoice_responsible_party: props.modelValue.invoice_responsible_party || 'Applicant',
  // Additional Contacts (FRD 3.10)
  additional_contact_persons: props.modelValue.additional_contact_persons || []
})

// Additional consents management
const additionalConsentsRequired = computed({
  get: () => localData.value.additional_consents && localData.value.additional_consents.length > 0,
  set: (value) => {
    if (!value) {
      localData.value.additional_consents = []
    }
  }
})

const showAdditionalConsentModal = ref(false)
const editingConsentIndex = ref(null)
const currentConsent = ref({
  consent_type: '',
  consent_status: '',
  reference_number: ''
})

const openAdditionalConsentModal = (index = null) => {
  editingConsentIndex.value = index
  if (index !== null) {
    currentConsent.value = { ...localData.value.additional_consents[index] }
  } else {
    currentConsent.value = {
      consent_type: '',
      consent_status: '',
      reference_number: ''
    }
  }
  showAdditionalConsentModal.value = true
}

const closeAdditionalConsentModal = () => {
  showAdditionalConsentModal.value = false
  editingConsentIndex.value = null
}

const saveAdditionalConsent = () => {
  if (!localData.value.additional_consents) {
    localData.value.additional_consents = []
  }

  if (editingConsentIndex.value !== null) {
    localData.value.additional_consents[editingConsentIndex.value] = { ...currentConsent.value }
  } else {
    localData.value.additional_consents.push({ ...currentConsent.value })
  }

  closeAdditionalConsentModal()
}

const removeAdditionalConsent = (index) => {
  if (confirm('Remove this additional consent?')) {
    localData.value.additional_consents.splice(index, 1)
  }
}

// Additional contacts management
const showAdditionalContactModal = ref(false)
const editingContactIndex = ref(null)
const currentContact = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: ''
})

const openAdditionalContactModal = (index = null) => {
  editingContactIndex.value = index
  if (index !== null) {
    currentContact.value = { ...localData.value.additional_contact_persons[index] }
  } else {
    currentContact.value = {
      first_name: '',
      last_name: '',
      email: '',
      phone: ''
    }
  }
  showAdditionalContactModal.value = true
}

const closeAdditionalContactModal = () => {
  showAdditionalContactModal.value = false
  editingContactIndex.value = null
}

const saveAdditionalContact = () => {
  if (!localData.value.additional_contact_persons) {
    localData.value.additional_contact_persons = []
  }

  if (editingContactIndex.value !== null) {
    localData.value.additional_contact_persons[editingContactIndex.value] = { ...currentContact.value }
  } else {
    localData.value.additional_contact_persons.push({ ...currentContact.value })
  }

  closeAdditionalContactModal()
}

const removeAdditionalContact = (index) => {
  if (confirm('Remove this contact person?')) {
    localData.value.additional_contact_persons.splice(index, 1)
  }
}

// Property select handler
const handlePropertySelect = () => {
  emit('property-select')
}

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  localData.value = {
    ...newVal,
    additional_consents: newVal.additional_consents || [],
    pim_applied: newVal.pim_applied || false,
    pim_number: newVal.pim_number || '',
    building_consent_applied: newVal.building_consent_applied || false,
    building_consent_number: newVal.building_consent_number || '',
    site_visit_locked_gates: newVal.site_visit_locked_gates || false,
    site_visit_dogs_present: newVal.site_visit_dogs_present || false,
    site_visit_health_safety_issues: newVal.site_visit_health_safety_issues || false,
    site_visit_notice_required: newVal.site_visit_notice_required || false,
    site_visit_details: newVal.site_visit_details || '',
    agent_required: newVal.agent_required || false,
    agent_id: newVal.agent_id || null,
    pre_app_meeting_required: newVal.pre_app_meeting_required || false,
    pre_app_meeting_id: newVal.pre_app_meeting_id || null,
    correspondence_recipient: newVal.correspondence_recipient || 'Applicant',
    invoice_responsible_party: newVal.invoice_responsible_party || 'Applicant',
    additional_contact_persons: newVal.additional_contact_persons || []
  }
}, { deep: true })

// Watch local changes and emit
watch(localData, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })
</script>
