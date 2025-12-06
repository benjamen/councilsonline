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

      <!-- SECTION 2: Consent Information / Proposal Details (nested component) -->
      <div class="border-b border-gray-200 pb-8">
        <Step6ConsentInfo
          v-model="localData"
        />
      </div>

      <!-- SECTION 3: Property Details (nested component) -->
      <div class="border-b border-gray-200 pb-8">
        <Step5PropertyDetailsMulti
          v-model="localData"
          :properties="properties"
          @property-select="handlePropertySelect"
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

      <!-- SECTION 7: Agent Details (FRD 3.7) - Only for non-individual applicants or those acting on behalf -->
      <div v-if="showAgentSection" class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Agent Details</h3>
        <p class="text-sm text-gray-600 mb-4">
          You may contact Resource Consent Planning Professionals or Agents from the list available in eRCS to obtain quotes from and engage them to help you prepare and lodge your application by selecting the Request Quote button.
        </p>
        <p class="text-sm text-orange-600 mb-4 font-medium">
          Please note: You will not be able to make any more changes or complete this application once you engage an Agent.
        </p>

        <div class="space-y-4">
          <div class="flex items-center space-x-4">
            <button
              type="button"
              @click="openRFQModal"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Request Quote from Agent
            </button>
          </div>

          <!-- RFQ List (if any exist) -->
          <div v-if="localData.agent_rfqs && localData.agent_rfqs.length > 0" class="mt-6">
            <h4 class="text-sm font-semibold text-gray-700 mb-2">Agent Requests for Quote</h4>
            <div class="space-y-2">
              <div
                v-for="(rfq, index) in localData.agent_rfqs"
                :key="index"
                class="p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow"
              >
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <span class="text-sm font-semibold text-gray-900">RFQ #{{ rfq.rfq_id || (index + 1) }}</span>
                      <span
                        :class="[
                          'px-2 py-1 text-xs font-medium rounded-full',
                          rfq.status === 'Draft' ? 'bg-gray-100 text-gray-800' :
                          rfq.status === 'Sent to Agent' ? 'bg-blue-100 text-blue-800' :
                          rfq.status === 'Quote Received' ? 'bg-yellow-100 text-yellow-800' :
                          rfq.status === 'Quote Accepted' ? 'bg-purple-100 text-purple-800' :
                          rfq.status === 'Agent Engaged' ? 'bg-green-100 text-green-800' :
                          rfq.status === 'Cancelled' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        ]"
                      >
                        {{ rfq.status || 'Draft' }}
                      </span>
                    </div>
                    <div v-if="rfq.agent_name" class="text-sm text-gray-600 mb-1">
                      <span class="font-medium">Agent:</span> {{ rfq.agent_name }}
                    </div>
                    <div v-if="rfq.agent_quote_amount" class="text-sm text-gray-600">
                      <span class="font-medium">Quote:</span> ${{ Number(rfq.agent_quote_amount).toFixed(2) }}
                    </div>
                    <div v-if="rfq.sent_date" class="text-xs text-gray-500 mt-1">
                      Sent: {{ new Date(rfq.sent_date).toLocaleDateString() }}
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <button
                      type="button"
                      @click="viewRFQ(index)"
                      class="px-3 py-1.5 text-blue-600 hover:text-blue-800 text-sm font-medium border border-blue-600 rounded hover:bg-blue-50 transition-colors"
                    >
                      View Details
                    </button>
                    <button
                      v-if="rfq.status === 'Quote Received' || rfq.status === 'Quote Accepted'"
                      type="button"
                      @click="acceptQuote(index)"
                      class="px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 transition-colors"
                      :disabled="rfq.status === 'Agent Engaged'"
                    >
                      {{ rfq.status === 'Agent Engaged' ? 'Engaged' : 'Accept Quote' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg text-center">
            <p class="text-sm text-gray-600">No agent quotes requested yet. Click "Request Quote from Agent" to get started.</p>
          </div>
        </div>
      </div>

      <!-- SECTION 8: Council Meeting (FRD 3.8) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Council Meeting</h3>
        <p class="text-sm text-gray-600 mb-4">
          You may schedule a Council Meeting with the Council to seek further clarifications in respect of your application by selecting the Council Meeting button.
        </p>
        <p class="text-sm text-gray-600 mb-4">
          Please include any relevant information or documents such as conceptual plans or draft assessment of environmental effects you have.
        </p>

        <div class="flex items-center gap-4">
          <label class="flex items-center cursor-pointer">
            <input
              v-model="localData.pre_app_meeting_not_required"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm font-medium text-gray-700">No Meeting Required</span>
          </label>
          <button
            type="button"
            @click="showPreAppMeetingModal = true"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Request Council Meeting
          </button>
        </div>

        <!-- Council Meeting List -->
        <div v-if="localData.pre_app_meetings && localData.pre_app_meetings.length > 0" class="mt-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">Scheduled Meetings</h4>
          <div class="space-y-2">
            <div
              v-for="(meeting, index) in localData.pre_app_meetings"
              :key="index"
              class="p-3 bg-gray-50 border border-gray-200 rounded-lg flex items-center justify-between"
            >
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-900">{{ meeting.meeting_type || 'Council Meeting' }}</span>
                  <span
                    :class="[
                      'px-2 py-1 text-xs rounded-full',
                      meeting.status === 'Scheduled' ? 'bg-blue-100 text-blue-800' :
                      meeting.status === 'Confirmed' ? 'bg-green-100 text-green-800' :
                      meeting.status === 'Completed' ? 'bg-gray-100 text-gray-800' :
                      'bg-yellow-100 text-yellow-800'
                    ]"
                  >
                    {{ meeting.status || 'Requested' }}
                  </span>
                </div>
                <div v-if="meeting.scheduled_start" class="text-xs text-gray-600 mt-1">
                  <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ new Date(meeting.scheduled_start).toLocaleString() }}
                </div>
              </div>
              <button
                type="button"
                @click="editPreAppMeeting(index)"
                class="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION 9: Correspondences and Invoices (FRD 3.9) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Correspondences and Invoices</h3>
        <p class="text-sm text-gray-600 mb-4">
          {{ showAgentSection ? 'All correspondence and notifications will be sent to the Applicant. If an Applicant engages an Agent, they will be sent to both parties.' : 'All correspondence and notifications will be sent to the Applicant and any additional contacts you specify.' }}
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

              <!-- Agent option - only show for non-individual applicants or those acting on behalf -->
              <label v-if="showAgentSection" class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors"
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

              <!-- Contact option - show list of added contacts -->
              <label
                v-for="(contact, index) in localData.additional_contacts"
                :key="`contact-${index}`"
                class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors"
                :class="localData.invoice_responsible_party === `Contact-${contact.contact_id || index}` ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
              >
                <input
                  v-model="localData.invoice_responsible_party"
                  type="radio"
                  :value="`Contact-${contact.contact_id || index}`"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div class="ml-3">
                  <span class="font-medium text-gray-900">{{ contact.contact_name }}</span>
                  <p class="text-xs text-gray-500 mt-1">{{ contact.contact_email }}</p>
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
            @click="openContactSelectorForContactPersons"
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
        <div v-if="localData.additional_contact_persons && localData.additional_contact_persons.length > 0" class="space-y-2">
          <div
            v-for="(contact, index) in localData.additional_contact_persons"
            :key="index"
            class="p-3 bg-white border border-gray-200 rounded-lg flex items-center justify-between"
          >
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">{{ contact.attendee_name }}</p>
              <p class="text-xs text-gray-600">{{ contact.attendee_email }}</p>
              <p v-if="contact.attendee_phone" class="text-xs text-gray-500">{{ contact.attendee_phone }}</p>
              <p v-if="contact.organization" class="text-xs text-gray-500">{{ contact.organization }}</p>
            </div>
            <button
              @click="removeContactPerson(index)"
              type="button"
              class="text-red-600 hover:text-red-800 text-sm"
            >
              Remove
            </button>
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

    <!-- Contact Selector for Additional Contact Persons -->
    <ContactSelector
      :is-open="showContactSelectorForContactPersons"
      :existing-contacts="existingContacts"
      @close="showContactSelectorForContactPersons = false"
      @select="addContactPerson"
    />

    <!-- Council Meeting Modal -->
    <div
      v-if="showPreAppMeetingModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closePreAppMeetingModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">Request Council Meeting</h3>
          <button
            @click="closePreAppMeetingModal"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="overflow-y-auto max-h-[calc(90vh-140px)] px-6 py-4">
          <div class="space-y-6">
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p class="text-sm text-blue-900">
                A council meeting allows you to discuss your proposal with council planners before formally submitting your application. This can help clarify requirements and identify potential issues early.
              </p>
            </div>

            <!-- Meeting Type & Format -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Meeting Type *</label>
                <select
                  v-model="currentPreAppMeeting.meeting_type"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="Council Meeting">Council Meeting</option>
                  <option value="Site Visit">Site Visit</option>
                  <option value="Technical Review">Technical Review</option>
                  <option value="Follow-up Meeting">Follow-up Meeting</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Meeting Format *</label>
                <select
                  v-model="currentPreAppMeeting.meeting_format"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="In Person">In Person</option>
                  <option value="Video Call">Video Call</option>
                  <option value="Phone Call">Phone Call</option>
                  <option value="Hybrid">Hybrid</option>
                </select>
              </div>
            </div>

            <!-- Preferred Time Slots -->
            <div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-gray-900">Preferred Meeting Times *</h4>
                <span class="text-xs text-gray-600">Select up to 3 time slots</span>
              </div>
              <p class="text-xs text-gray-600 mb-4">
                Select your 3 preferred times. The planner will accept one of these times or propose an alternative.
              </p>

              <div class="space-y-4">
                <!-- Time Slot 1 -->
                <div class="bg-white p-4 rounded-lg border border-gray-200">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">1st Preference</span>
                    <button
                      v-if="currentPreAppMeeting.preferred_time_slot_1_start"
                      @click="clearTimeSlot(1)"
                      type="button"
                      class="text-xs text-red-600 hover:text-red-800"
                    >
                      Clear
                    </button>
                  </div>
                  <DateTimePicker
                    v-model="currentPreAppMeeting.preferred_time_slot_1_start"
                    label="Start Time"
                    :required="true"
                  />
                </div>

                <!-- Time Slot 2 -->
                <div class="bg-white p-4 rounded-lg border border-gray-200">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">2nd Preference</span>
                    <button
                      v-if="currentPreAppMeeting.preferred_time_slot_2_start"
                      @click="clearTimeSlot(2)"
                      type="button"
                      class="text-xs text-red-600 hover:text-red-800"
                    >
                      Clear
                    </button>
                  </div>
                  <DateTimePicker
                    v-model="currentPreAppMeeting.preferred_time_slot_2_start"
                    label="Start Time"
                    :required="true"
                  />
                </div>

                <!-- Time Slot 3 -->
                <div class="bg-white p-4 rounded-lg border border-gray-200">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">3rd Preference</span>
                    <button
                      v-if="currentPreAppMeeting.preferred_time_slot_3_start"
                      @click="clearTimeSlot(3)"
                      type="button"
                      class="text-xs text-red-600 hover:text-red-800"
                    >
                      Clear
                    </button>
                  </div>
                  <DateTimePicker
                    v-model="currentPreAppMeeting.preferred_time_slot_3_start"
                    label="Start Time"
                    :required="true"
                  />
                </div>
              </div>
            </div>

            <!-- Meeting Purpose & Discussion Points -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Meeting Purpose *</label>
              <textarea
                v-model="currentPreAppMeeting.meeting_purpose"
                rows="3"
                placeholder="Describe the purpose of this meeting and what you'd like to discuss..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Discussion Points</label>
              <textarea
                v-model="currentPreAppMeeting.discussion_points"
                rows="4"
                placeholder="List key topics you'd like to discuss (bullet points or list format)"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- Location (if In Person) -->
            <div v-if="currentPreAppMeeting.meeting_format === 'In Person' || currentPreAppMeeting.meeting_format === 'Hybrid'">
              <label class="block text-sm font-medium text-gray-700 mb-2">Preferred Location</label>
              <input
                v-model="currentPreAppMeeting.meeting_location"
                type="text"
                placeholder="e.g., Council offices, or site address"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <!-- Additional Attendees -->
            <div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-gray-900">Additional Attendees</h4>
                <button
                  @click="openContactSelectorForMeeting"
                  type="button"
                  class="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  + Add Attendee
                </button>
              </div>

              <div v-if="currentPreAppMeeting.meeting_attendees && currentPreAppMeeting.meeting_attendees.length > 0" class="space-y-2">
                <div
                  v-for="(attendee, index) in currentPreAppMeeting.meeting_attendees"
                  :key="index"
                  class="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200"
                >
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ attendee.attendee_name }}</p>
                    <p class="text-xs text-gray-600">{{ attendee.attendee_email }}</p>
                    <p v-if="attendee.organization" class="text-xs text-gray-500">{{ attendee.organization }}</p>
                  </div>
                  <button
                    @click="removeMeetingAttendee(index)"
                    type="button"
                    class="text-red-600 hover:text-red-800 ml-2"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <p v-else class="text-sm text-gray-500 italic">No additional attendees added yet</p>
            </div>
          </div>
        </div>

        <!-- Contact Selector Modal -->
        <ContactSelector
          :is-open="showContactSelectorForMeeting"
          :existing-contacts="existingContacts"
          @close="showContactSelectorForMeeting = false"
          @select="addMeetingAttendee"
        />

        <div class="sticky bottom-0 bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t border-gray-200">
          <button
            @click="closePreAppMeetingModal"
            type="button"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="savePreAppMeeting"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            :disabled="!currentPreAppMeeting.meeting_type || !currentPreAppMeeting.meeting_format || !currentPreAppMeeting.meeting_purpose"
          >
            {{ editingPreAppMeetingIndex !== null ? 'Update' : 'Request' }} Meeting
          </button>
        </div>
      </div>
    </div>

    <!-- RFQ Modal -->
    <RFQModal
      :is-open="isRFQModalOpen"
      :rfq="currentRFQ"
      :request-id="localData.name"
      @close="closeRFQModal"
      @save="saveRFQ"
      @send-to-agent="sendRFQToAgent"
      @engage-agent="engageAgentFromRFQ"
    />
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch, computed, toRaw } from 'vue'
import Step4ApplicantDetails from './Step4ApplicantDetails.vue'
import Step5PropertyDetailsMulti from './Step5PropertyDetailsMulti.vue'
import Step6ConsentInfo from './Step6ConsentInfo.vue'
import RFQModal from '../modals/RFQModal.vue'
import DateTimePicker from '../common/DateTimePicker.vue'
import ContactSelector from '../common/ContactSelector.vue'
import { updateRFQ, sendRFQToAgent as sendRFQToAgentAPI, engageAgent as engageAgentAPI } from '../../api/rfq'

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
// CRITICAL FIX: Use toRaw() to break reactive chain and prevent infinite reactivity loops
// This prevents the browser freeze issue when navigating to Step 4
const rawModelValue = toRaw(props.modelValue)
console.log('[Step1ApplicantProposal] Using toRaw to prevent freeze - fix v2.0')
const localData = ref({
  ...rawModelValue,
  // Additional Consents (FRD 3.4)
  additional_consents: rawModelValue.additional_consents || [],
  // PIM & Building Consent (FRD 3.5)
  pim_applied: rawModelValue.pim_applied || false,
  pim_number: rawModelValue.pim_number || '',
  building_consent_applied: rawModelValue.building_consent_applied || false,
  building_consent_number: rawModelValue.building_consent_number || '',
  // Site Visit (FRD 3.6)
  site_visit_locked_gates: rawModelValue.site_visit_locked_gates || false,
  site_visit_dogs_present: rawModelValue.site_visit_dogs_present || false,
  site_visit_health_safety_issues: rawModelValue.site_visit_health_safety_issues || false,
  site_visit_notice_required: rawModelValue.site_visit_notice_required || false,
  site_visit_details: rawModelValue.site_visit_details || '',
  // Agent Details (FRD 3.7)
  agent_required: rawModelValue.agent_required || false,
  agent_id: rawModelValue.agent_id || null,
  agent_rfqs: rawModelValue.agent_rfqs || [],
  // Pre-App Meeting (FRD 3.8)
  pre_app_meeting_not_required: rawModelValue.pre_app_meeting_not_required || false,
  pre_app_meetings: rawModelValue.pre_app_meetings || [],
  // Correspondence (FRD 3.9)
  correspondence_recipient: rawModelValue.correspondence_recipient || 'Applicant',
  invoice_responsible_party: rawModelValue.invoice_responsible_party || 'Applicant',
  // Additional Contacts (FRD 3.10)
  additional_contact_persons: rawModelValue.additional_contact_persons || []
})

// Migrate old contact persons data format to new standardized format
// Old format: { first_name, last_name, email, phone }
// New format: { attendee_name, attendee_email, attendee_phone, organization }
if (localData.value.additional_contact_persons && localData.value.additional_contact_persons.length > 0) {
  localData.value.additional_contact_persons = localData.value.additional_contact_persons.map(contact => {
    // Check if already in new format
    if (contact.attendee_name || contact.attendee_email) {
      return contact
    }
    // Convert old format to new format
    return {
      attendee_name: contact.first_name && contact.last_name
        ? `${contact.first_name} ${contact.last_name}`
        : contact.first_name || contact.last_name || '',
      attendee_email: contact.email || '',
      attendee_phone: contact.phone || '',
      organization: contact.organization || ''
    }
  })
}

// Additional consents management
// Initialize based on existing data
const additionalConsentsRequired = ref(
  localData.value.additional_consents && localData.value.additional_consents.length > 0
)

// Watch for changes to additional_consents array to update the radio button
watch(() => localData.value.additional_consents, (newVal) => {
  if (newVal && newVal.length > 0) {
    additionalConsentsRequired.value = true
  }
}, { deep: true })

// When user selects "Yes", we need to show the section even if empty
watch(additionalConsentsRequired, (newVal) => {
  if (!newVal) {
    // User selected "No" - clear the consents
    localData.value.additional_consents = []
  } else {
    // User selected "Yes" - ensure array exists (but keep it empty to show empty state)
    if (!localData.value.additional_consents) {
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

// Additional contacts management - using ContactSelector
const showContactSelectorForContactPersons = ref(false)

const openContactSelectorForContactPersons = () => {
  showContactSelectorForContactPersons.value = true
}

const addContactPerson = (contact) => {
  if (!localData.value.additional_contact_persons) {
    localData.value.additional_contact_persons = []
  }

  localData.value.additional_contact_persons.push({
    attendee_name: contact.name,
    attendee_email: contact.email,
    attendee_phone: contact.phone || '',
    organization: contact.organization || ''
  })

  showContactSelectorForContactPersons.value = false
}

const removeContactPerson = (index) => {
  if (confirm('Remove this contact person?')) {
    localData.value.additional_contact_persons.splice(index, 1)
  }
}

// Agent RFQ management
const agentRequired = ref(false)
const isRFQModalOpen = ref(false)
const currentRFQ = ref({})
const currentRFQIndex = ref(null)
const showRFQModal = ref(false)

// Computed property to determine if agent section should be shown
// Only show for non-individual applicants or those acting on behalf of others
const showAgentSection = computed(() => {
  // Check if applicant_type exists in modelValue (from parent)
  const applicantType = props.modelValue?.applicant_type || props.userProfile?.applicant_type
  const actingOnBehalf = props.modelValue?.acting_on_behalf || false

  // Show agent section if:
  // 1. Acting on behalf of someone else, OR
  // 2. Applicant type is NOT Individual (i.e., Company, Trust, Organisation)
  return actingOnBehalf || (applicantType && applicantType !== 'Individual')
})

const openRFQModal = () => {
  // Create a new RFQ
  currentRFQ.value = {
    rfq_id: null,
    status: 'Draft',
    created_date: new Date().toISOString(),
    selected_agent: null,
    agent_name: null,
    agent_email: null,
    agent_quote_amount: null,
    agent_quote_details: '',
    rfq_message: 'You may contact Resource Consent Planning Professionals or Agents from the list available in eRCS to obtain quotes from and engage them to help you prepare and lodge your application by selecting the Engage Agent button.\n\nPlease note: You will not be able to make any more changes or complete this application once you engage an Agent.'
  }
  currentRFQIndex.value = null
  isRFQModalOpen.value = true
}

const viewRFQ = (index) => {
  currentRFQIndex.value = index
  currentRFQ.value = { ...localData.value.agent_rfqs[index] }
  isRFQModalOpen.value = true
}

const acceptQuote = async (index) => {
  const rfq = localData.value.agent_rfqs[index]

  if (confirm(`Accept quote from ${rfq.agent_name} for $${Number(rfq.agent_quote_amount).toFixed(2)}?`)) {
    rfq.status = 'Agent Engaged'
    rfq.agent_engaged_date = new Date().toISOString()
    localData.value.agent_id = rfq.selected_agent

    // TODO: Call backend API to engage agent
    alert('Agent engaged successfully!')
  }
}

const closeRFQModal = () => {
  isRFQModalOpen.value = false
  currentRFQIndex.value = null
  currentRFQ.value = {}
}

const saveRFQ = async (rfqData) => {
  try {
    // Only update if RFQ has an ID (already created in backend)
    if (rfqData.name || rfqData.rfq_id) {
      const rfqId = rfqData.name || rfqData.rfq_id
      await updateRFQ(rfqId, {
        rfq_message: rfqData.rfq_message
      })
    }

    // Update the RFQ in the list
    if (currentRFQIndex.value !== null) {
      localData.value.agent_rfqs[currentRFQIndex.value] = { ...rfqData }
    }

    closeRFQModal()
  } catch (error) {
    console.error('Failed to save RFQ:', error)
    alert('Failed to save RFQ changes. Please try again.')
  }
}

const sendRFQToAgent = async ({ rfq, agent }) => {
  try {
    const rfqId = rfq.name || rfq.rfq_id
    if (!rfqId) {
      throw new Error('RFQ ID not found')
    }

    // Call backend API to send RFQ to agent
    await sendRFQToAgentAPI(rfqId, agent)

    // Update status in local data
    if (currentRFQIndex.value !== null) {
      localData.value.agent_rfqs[currentRFQIndex.value].status = 'Sent to Agent'
      localData.value.agent_rfqs[currentRFQIndex.value].agent = agent
      localData.value.agent_rfqs[currentRFQIndex.value].sent_date = new Date().toISOString()
    }

    closeRFQModal()
  } catch (error) {
    console.error('Failed to send RFQ to agent:', error)
    alert('Failed to send RFQ to agent. Please try again.')
  }
}

const engageAgentFromRFQ = async (rfqData) => {
  try {
    const rfqId = rfqData.name || rfqData.rfq_id
    if (!rfqId) {
      throw new Error('RFQ ID not found')
    }

    // Call backend API to engage agent (this will lock the request)
    await engageAgentAPI(rfqId, rfqData.quote_amount, rfqData.quote_details)

    // Update status and lock application in local data
    if (currentRFQIndex.value !== null) {
      localData.value.agent_rfqs[currentRFQIndex.value].status = 'Agent Engaged'
      localData.value.agent_rfqs[currentRFQIndex.value].agent_engaged = true
      localData.value.agent_rfqs[currentRFQIndex.value].agent_engaged_date = new Date().toISOString()
    }

    // Lock the application
    localData.value.locked_for_editing = true
    localData.value.locked_reason = 'Agent engaged'
    localData.value.agent_engaged = true

    closeRFQModal()

    // Show success message
    alert('Agent successfully engaged. This application is now locked for editing.')
  } catch (error) {
    console.error('Failed to engage agent:', error)
    alert('Failed to engage agent. Please try again.')
  }
}

// Council Meeting modal management
const showPreAppMeetingModal = ref(false)
const editingPreAppMeetingIndex = ref(null)
const showContactSelectorForMeeting = ref(false)
const existingContacts = ref([])  // TODO: Load from backend

const currentPreAppMeeting = ref({
  meeting_type: 'Council Meeting',
  meeting_format: 'In Person',
  meeting_purpose: '',
  discussion_points: '',
  meeting_location: '',
  preferred_time_slot_1_start: '',
  preferred_time_slot_2_start: '',
  preferred_time_slot_3_start: '',
  meeting_attendees: [],
  status: 'Requested'
})

const editPreAppMeeting = (index) => {
  editingPreAppMeetingIndex.value = index
  currentPreAppMeeting.value = { ...localData.value.pre_app_meetings[index] }
  showPreAppMeetingModal.value = true
}

const closePreAppMeetingModal = () => {
  showPreAppMeetingModal.value = false
  editingPreAppMeetingIndex.value = null
  currentPreAppMeeting.value = {
    meeting_type: 'Council Meeting',
    meeting_format: 'In Person',
    meeting_purpose: '',
    discussion_points: '',
    meeting_location: '',
    preferred_time_slot_1_start: '',
    preferred_time_slot_2_start: '',
    preferred_time_slot_3_start: '',
    meeting_attendees: [],
    status: 'Requested'
  }
}

const savePreAppMeeting = () => {
  // Validate at least one time slot is selected
  if (!currentPreAppMeeting.value.preferred_time_slot_1_start &&
      !currentPreAppMeeting.value.preferred_time_slot_2_start &&
      !currentPreAppMeeting.value.preferred_time_slot_3_start) {
    alert('Please select at least one preferred meeting time')
    return
  }

  if (!localData.value.pre_app_meetings) {
    localData.value.pre_app_meetings = []
  }

  // Prepare meeting data with time slots
  const meetingData = {
    ...currentPreAppMeeting.value,
    preferred_time_slots: []
  }

  // Add time slots in order
  if (currentPreAppMeeting.value.preferred_time_slot_1_start) {
    meetingData.preferred_time_slots.push({
      preference_order: 1,
      preferred_start: currentPreAppMeeting.value.preferred_time_slot_1_start,
      preferred_end: calculateEndTime(currentPreAppMeeting.value.preferred_time_slot_1_start),
      planner_response: 'Pending'
    })
  }
  if (currentPreAppMeeting.value.preferred_time_slot_2_start) {
    meetingData.preferred_time_slots.push({
      preference_order: 2,
      preferred_start: currentPreAppMeeting.value.preferred_time_slot_2_start,
      preferred_end: calculateEndTime(currentPreAppMeeting.value.preferred_time_slot_2_start),
      planner_response: 'Pending'
    })
  }
  if (currentPreAppMeeting.value.preferred_time_slot_3_start) {
    meetingData.preferred_time_slots.push({
      preference_order: 3,
      preferred_start: currentPreAppMeeting.value.preferred_time_slot_3_start,
      preferred_end: calculateEndTime(currentPreAppMeeting.value.preferred_time_slot_3_start),
      planner_response: 'Pending'
    })
  }

  if (editingPreAppMeetingIndex.value !== null) {
    localData.value.pre_app_meetings[editingPreAppMeetingIndex.value] = meetingData
  } else {
    localData.value.pre_app_meetings.push(meetingData)
  }

  closePreAppMeetingModal()
}

// Helper function to calculate end time (1 hour after start by default)
const calculateEndTime = (startTime) => {
  if (!startTime) return ''
  const start = new Date(startTime)
  const end = new Date(start.getTime() + 60 * 60 * 1000) // Add 1 hour
  return end.toISOString()
}

// Clear a specific time slot
const clearTimeSlot = (slotNumber) => {
  currentPreAppMeeting.value[`preferred_time_slot_${slotNumber}_start`] = ''
}

// Contact selector for meeting attendees
const openContactSelectorForMeeting = () => {
  showContactSelectorForMeeting.value = true
}

const addMeetingAttendee = (contact) => {
  if (!currentPreAppMeeting.value.meeting_attendees) {
    currentPreAppMeeting.value.meeting_attendees = []
  }

  // Add the contact as a meeting attendee
  currentPreAppMeeting.value.meeting_attendees.push({
    attendee_name: contact.name,
    attendee_email: contact.email,
    attendee_phone: contact.phone || '',
    organization: contact.organization || '',
    role: contact.role || ''
  })

  showContactSelectorForMeeting.value = false
}

const removeMeetingAttendee = (index) => {
  if (confirm('Remove this attendee?')) {
    currentPreAppMeeting.value.meeting_attendees.splice(index, 1)
  }
}

// Property select handler
const handlePropertySelect = () => {
  emit('property-select')
}

// Watch local changes and emit
// NOTE: We do NOT watch props.modelValue because that creates an infinite loop
// The component initializes from props once, then localData changes flow up via emit
watch(localData, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })
</script>
