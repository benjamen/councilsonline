<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Consent Information</h2>
    <p class="text-gray-600 mb-8">Select consent types, provide consent details, and describe your proposal</p>

    <div class="space-y-8">
      <!-- SECTION 1: Consent Type & Activity Status -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Consent Type & Activity Status</h3>

        <div class="space-y-6">
          <!-- Card-Based Consent Type Selector -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-4">
              Consent Types Required * <span class="text-xs text-gray-500">(Select all that apply)</span>
            </label>
            <div class="grid md:grid-cols-2 gap-4">
              <div
                v-for="consentType in availableConsentTypes"
                :key="consentType.value"
                @click="toggleConsentType(consentType.value)"
                class="border-2 rounded-lg p-4 cursor-pointer transition-all hover:shadow-md"
                :class="isConsentTypeSelected(consentType.value) ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
              >
                <div class="flex items-start">
                  <input
                    type="checkbox"
                    :checked="isConsentTypeSelected(consentType.value)"
                    class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded pointer-events-none"
                    readonly
                  />
                  <div class="ml-3 flex-1">
                    <h4 class="text-base font-semibold text-gray-900">{{ consentType.label }}</h4>
                    <p class="text-sm text-gray-600 mt-1">{{ consentType.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Activity Status -->
          <div class="border-t border-gray-200 pt-6">
            <label class="block text-sm font-medium text-gray-700 mb-3">
              Activity Status Under District/Regional Plan (Optional)
            </label>
            <div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h5 class="font-semibold text-blue-900 text-sm">Not sure? That's okay!</h5>
                  <p class="text-blue-800 text-sm mt-1">
                    If you're unsure about your activity status, you can leave this blank. The council planner will determine the correct status when processing your application.
                    Alternatively, you can book a free pre-application meeting with the council to discuss this.
                  </p>
                </div>
              </div>
            </div>
            <div class="space-y-2">
              <label
                v-for="status in activityStatuses"
                :key="status.value"
                class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-all hover:bg-gray-50"
                :class="localData.activity_status === status.value ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
              >
                <input
                  type="radio"
                  v-model="localData.activity_status"
                  :value="status.value"
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div class="ml-3">
                  <span class="font-medium text-gray-900">{{ status.label }}</span>
                  <p class="text-xs text-gray-600 mt-1">{{ status.description }}</p>
                </div>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION 2: Consent Details -->
      <div v-if="localData.consent_types && localData.consent_types.length > 0" class="border-b border-gray-200 pb-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Consent Details</h3>

        <div class="space-y-6">
          <!-- Duration - Per Consent Type -->
          <div>
            <h4 class="text-lg font-semibold text-gray-900 mb-4">Requested Duration</h4>
            <p class="text-sm text-gray-600 mb-4">
              Specify the duration for each consent type selected
            </p>
            <div class="space-y-4">
              <div
                v-for="ct in localData.consent_types"
                :key="ct.consent_type"
                class="border border-gray-200 rounded-lg p-4 bg-gray-50"
              >
                <label :for="getDurationInputId(ct.consent_type)" class="block text-sm font-medium text-gray-700 mb-2">
                  {{ ct.consent_type }} Duration
                </label>
                <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 sm:items-start">
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <input
                        :id="getDurationInputId(ct.consent_type)"
                        v-model.number="getDurationData(ct.consent_type).duration_years"
                        type="number"
                        :min="1"
                        :max="getMaxDuration(ct.consent_type)"
                        placeholder="e.g., 10"
                        :disabled="getDurationData(ct.consent_type).duration_unlimited"
                        :aria-label="`Duration in years for ${ct.consent_type} consent`"
                        :aria-describedby="getDurationHelpId(ct.consent_type)"
                        :aria-invalid="!!getDurationError(ct.consent_type)"
                        :class="[
                          'flex-1 min-w-0 px-3 py-2 rounded-lg transition-colors',
                          'focus:ring-2 focus:ring-blue-500 focus:outline-none',
                          getDurationValidationClass(ct.consent_type)
                        ]"
                        @blur="validateDuration(ct.consent_type)"
                        @input="validateDuration(ct.consent_type)"
                      />
                      <span class="text-gray-600 whitespace-nowrap">years</span>
                    </div>

                    <!-- Real-time validation messages -->
                    <div :id="getDurationHelpId(ct.consent_type)" class="mt-1.5 min-h-[20px]">
                      <p v-if="getDurationError(ct.consent_type)"
                         role="alert"
                         class="text-xs text-red-600 flex items-center gap-1.5 font-medium">
                        <svg class="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                        {{ getDurationError(ct.consent_type) }}
                      </p>
                      <p v-else-if="durationTouched[ct.consent_type] && getDurationData(ct.consent_type).duration_years && !getDurationData(ct.consent_type).duration_unlimited"
                         class="text-xs text-green-600 flex items-center gap-1.5 font-medium">
                        <svg class="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                        Valid duration
                      </p>
                      <p v-else class="text-xs text-gray-500">
                        {{ getDurationHelpText(ct.consent_type) }}
                      </p>
                    </div>
                  </div>
                  <label v-if="canBeUnlimited(ct.consent_type)"
                         :for="getUnlimitedCheckboxId(ct.consent_type)"
                         class="flex items-center gap-2 whitespace-nowrap pl-4 sm:pl-0 border-l-2 sm:border-l-0 border-gray-200 sm:pt-2">
                    <input
                      :id="getUnlimitedCheckboxId(ct.consent_type)"
                      v-model="getDurationData(ct.consent_type).duration_unlimited"
                      type="checkbox"
                      :aria-label="`Unlimited duration for ${ct.consent_type} consent`"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      @change="onUnlimitedToggle(ct.consent_type)"
                    />
                    <span class="text-sm font-medium">Unlimited</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Lapsing Period -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Lapsing Period
              <button
                type="button"
                @click="showLapsingHelp = !showLapsingHelp"
                class="ml-2 text-blue-600 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                :aria-expanded="showLapsingHelp"
                aria-label="Toggle lapsing period help"
              >
                <svg class="w-4 h-4 inline" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
                </svg>
              </button>
            </label>

            <!-- Expandable help panel -->
            <div v-if="showLapsingHelp" class="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
              <p class="font-medium text-blue-900 mb-2">How to choose lapsing period:</p>
              <ul class="space-y-1.5 text-blue-800">
                <li class="flex items-start gap-2">
                  <span class="text-blue-600 font-bold mt-0.5">•</span>
                  <span><strong>5 years:</strong> Standard for most consents - construction/use must begin within 5 years</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-blue-600 font-bold mt-0.5">•</span>
                  <span><strong>10 years:</strong> For renewable energy projects requiring longer development timelines (s.125(1A) RMA)</span>
                </li>
                <li v-if="isCoastalPermit" class="flex items-start gap-2">
                  <span class="text-blue-600 font-bold mt-0.5">•</span>
                  <span><strong>3 years:</strong> For aquaculture activities in coastal marine area</span>
                </li>
              </ul>
            </div>

            <select
              v-model.number="localData.lapsing_period_years"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="5">5 years - Standard lapsing period</option>
              <option :value="10">10 years - Renewable energy projects</option>
              <option v-if="isCoastalPermit" :value="3">3 years - Aquaculture activities</option>
            </select>
            <p class="mt-1 text-xs text-gray-500">
              Time period before consent lapses if not given effect to (s.125 RMA)
            </p>
          </div>

          <!-- Consent Notice - Subdivision only -->
          <div v-if="isSubdivision" class="border-t border-gray-200 pt-6">
            <h4 class="text-lg font-semibold text-gray-900 mb-4">Consent Notice (s.221 RMA)</h4>
            <p class="text-sm text-gray-600 mb-4">
              For subdivision consents, indicate whether a consent notice should be placed on the record of title
            </p>
            <div class="space-y-3">
              <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
                :class="localData.consent_notice_required ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
              >
                <input
                  v-model="localData.consent_notice_required"
                  type="checkbox"
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div class="ml-3">
                  <span class="font-medium text-gray-900">Consent notice required</span>
                  <p class="text-xs text-gray-600 mt-1">
                    Check if ongoing conditions need to be recorded on the certificate of title
                  </p>
                </div>
              </label>

              <div v-if="localData.consent_notice_required" class="pl-7">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Consent Notice Details *
                </label>
                <textarea
                  v-model="localData.consent_notice_details"
                  rows="4"
                  placeholder="Describe the matters to be included in the consent notice..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  :required="localData.consent_notice_required"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Coastal Occupation Charge - Coastal Permit only -->
          <div v-if="isCoastalPermit" class="border-t border-gray-200 pt-6">
            <h4 class="text-lg font-semibold text-gray-900 mb-4">Coastal Occupation Charge</h4>
            <p class="text-sm text-gray-600 mb-4">
              For occupation of the coastal marine area, councils may impose a coastal occupation charge
            </p>
            <div class="space-y-3">
              <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
                :class="localData.coastal_occupation_charge_acknowledged ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
              >
                <input
                  v-model="localData.coastal_occupation_charge_acknowledged"
                  type="checkbox"
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div class="ml-3">
                  <span class="font-medium text-gray-900">I acknowledge that a coastal occupation charge may apply</span>
                  <p class="text-xs text-gray-600 mt-1">
                    The council will determine the applicable charge based on the nature and extent of occupation
                  </p>
                </div>
              </label>
            </div>
          </div>

          <!-- Financial Contribution - All types -->
          <div class="border-t border-gray-200 pt-6">
            <h4 class="text-lg font-semibold text-gray-900 mb-4">Financial Contribution (s.108(2)(a) RMA)</h4>
            <p class="text-sm text-gray-600 mb-4">
              Council may impose financial contributions as a condition of consent
            </p>
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h5 class="font-semibold text-blue-900 text-sm">Information Only</h5>
                  <p class="text-blue-800 text-sm mt-1">
                    Financial contributions are determined by council policy and will be advised during processing if applicable. No action required at this stage.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Fast-Track Processing - User Selectable -->
          <div v-if="fastTrackAvailable" class="border-t border-gray-200 pt-6">
            <h4 class="text-lg font-semibold text-gray-900 mb-4">Fast-Track Processing (s.87AAB RMA)</h4>
            <p class="text-sm text-gray-600 mb-4">
              Controlled activities may be eligible for fast-track processing with reduced timeframes
            </p>

            <div v-if="eligibleForFastTrack" class="space-y-3">
              <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h5 class="font-semibold text-green-900 text-sm">Eligible for Fast-Track</h5>
                    <p class="text-green-800 text-sm mt-1">
                      Based on your consent type and activity status (Controlled), this application is eligible for fast-track processing.
                    </p>
                  </div>
                </div>
              </div>

              <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
                :class="localData.request_fast_track ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
              >
                <input
                  v-model="localData.request_fast_track"
                  type="checkbox"
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div class="ml-3">
                  <span class="font-medium text-gray-900">Request fast-track processing</span>
                  <p class="text-xs text-gray-600 mt-1">
                    I would like this application to be processed under fast-track provisions (subject to council availability)
                  </p>
                </div>
              </label>
            </div>

            <div v-else class="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <p class="text-sm text-gray-600">
                Fast-track processing is only available for Controlled activities (excluding Subdivision consents).
                Your current selections do not qualify for fast-track.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION 3: Proposal Details -->
      <div class="pb-4">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Proposal Details</h3>

        <div class="space-y-6">
          <!-- Brief Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Brief Description *
            </label>
            <textarea
              v-model="localData.brief_description"
              rows="2"
              maxlength="200"
              placeholder="Provide a short summary of your proposal (max 200 characters)"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            ></textarea>
            <p class="mt-1 text-xs text-gray-500">
              {{ localData.brief_description?.length || 0 }}/200 characters
            </p>
          </div>

          <!-- Detailed Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Detailed Description *
            </label>
            <textarea
              v-model="localData.detailed_description"
              rows="6"
              placeholder="Provide a comprehensive description of your proposal including scope, materials, dimensions, environmental considerations, and any other relevant information for the planner's assessment"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            ></textarea>
            <p class="mt-1 text-xs text-gray-500">
              Full description of the proposed work for planner assessment
            </p>
          </div>

          <div class="border-t border-gray-200 pt-6">
            <h4 class="text-lg font-semibold text-gray-900 mb-4">Detailed Breakdown (Optional)</h4>
            <p class="text-sm text-gray-600 mb-4">
              Add specific details for different aspects of your proposal
            </p>
          </div>

          <!-- Add Proposal Detail Button -->
          <div class="flex justify-between items-center">
            <p class="text-sm text-gray-700">
              Add details about different aspects of your proposal (building, earthworks, traffic, etc.)
            </p>
            <button
              @click="addProposalDetail"
              type="button"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Add Proposal Detail
            </button>
          </div>

          <!-- Proposal Details List -->
          <div v-if="modelValue.proposal_details && modelValue.proposal_details.length > 0" class="space-y-4">
            <div
              v-for="(detail, index) in modelValue.proposal_details"
              :key="index"
              class="border border-gray-200 rounded-lg p-6 bg-white shadow-sm"
            >
              <div class="flex justify-between items-start mb-4">
                <h5 class="text-base font-semibold text-gray-900">
                  {{ detail.detail_type || 'Proposal Detail' }} #{{ index + 1 }}
                </h5>
                <button
                  @click="removeProposalDetail(index)"
                  type="button"
                  class="text-red-600 hover:text-red-800 p-1"
                  title="Remove"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>

              <!-- Detail Type Selector -->
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Detail Type *
                </label>
                <select
                  v-model="detail.detail_type"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select type</option>
                  <option value="Building">Building</option>
                  <option value="Earthworks">Earthworks</option>
                  <option value="Traffic">Traffic & Parking</option>
                  <option value="Operations">Operations</option>
                  <option value="Subdivision">Subdivision</option>
                  <option value="Discharge">Discharge</option>
                  <option value="Water">Water Take/Use</option>
                  <option value="Coastal">Coastal Activity</option>
                </select>
              </div>

              <!-- Building Details -->
              <div v-if="detail.detail_type === 'Building'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-gray-900">Building Details</h5>
                <div class="grid md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Building Height (m)</label>
                    <input
                      v-model.number="detail.building_height_m"
                      type="number"
                      step="0.1"
                      placeholder="e.g., 8.5"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Total Floor Area (m²)</label>
                    <input
                      v-model.number="detail.total_floor_area_m2"
                      type="number"
                      step="0.1"
                      placeholder="e.g., 250.5"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>

              <!-- Earthworks Details -->
              <div v-if="detail.detail_type === 'Earthworks'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-gray-900">Earthworks Details</h5>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    v-model="detail.earthworks_description"
                    rows="4"
                    placeholder="Describe the earthworks proposed..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>
              </div>

              <!-- Traffic Details -->
              <div v-if="detail.detail_type === 'Traffic'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-gray-900">Traffic & Parking Details</h5>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    v-model="detail.traffic_description"
                    rows="4"
                    placeholder="Describe traffic generation, parking provision, access arrangements..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>
              </div>

              <!-- Operations Details -->
              <div v-if="detail.detail_type === 'Operations'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-gray-900">Operations Details</h5>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    v-model="detail.operations_description"
                    rows="4"
                    placeholder="Describe hours of operation, activities, processes..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>
              </div>

              <!-- Subdivision Details -->
              <div v-if="detail.detail_type === 'Subdivision'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-gray-900">Subdivision Details</h5>
                <div class="grid md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Number of Lots</label>
                    <input
                      v-model.number="detail.subdivision_lots"
                      type="number"
                      placeholder="e.g., 5"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Lot Sizes</label>
                    <input
                      v-model="detail.subdivision_lot_sizes"
                      type="text"
                      placeholder="e.g., 800m², 1000m², 1200m²"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>

              <!-- Discharge Details -->
              <div v-if="detail.detail_type === 'Discharge'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-gray-900">Discharge Details</h5>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Discharge Type</label>
                    <select
                      v-model="detail.discharge_type"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select type</option>
                      <option value="Stormwater">Stormwater</option>
                      <option value="Wastewater">Wastewater</option>
                      <option value="Air">Air</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Receiving Environment</label>
                    <input
                      v-model="detail.discharge_receiver"
                      type="text"
                      placeholder="e.g., Reticulated network, stream, land"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Treatment System</label>
                    <textarea
                      v-model="detail.discharge_treatment"
                      rows="3"
                      placeholder="Describe treatment systems and methods..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    ></textarea>
                  </div>
                </div>
              </div>

              <!-- Water Details -->
              <div v-if="detail.detail_type === 'Water'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-gray-900">Water Take/Use Details</h5>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Water Source</label>
                    <input
                      v-model="detail.water_source"
                      type="text"
                      placeholder="e.g., River, bore, stream"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div class="grid md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Maximum Take (m³/day)</label>
                      <input
                        v-model.number="detail.water_max_take_m3"
                        type="number"
                        step="0.1"
                        placeholder="e.g., 50"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Rate</label>
                      <input
                        v-model="detail.water_rate"
                        type="text"
                        placeholder="e.g., 2 L/s"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Coastal Details -->
              <div v-if="detail.detail_type === 'Coastal'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-gray-900">Coastal Activity Details</h5>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Structure Type</label>
                    <input
                      v-model="detail.coastal_structure_type"
                      type="text"
                      placeholder="e.g., Jetty, mooring, seawall"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Navigation Effects</label>
                    <textarea
                      v-model="detail.coastal_navigation_effects"
                      rows="3"
                      placeholder="Describe potential effects on navigation..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="mt-2 text-sm text-gray-600">No proposal details added yet</p>
            <p class="text-xs text-gray-500 mt-1">Click "Add Proposal Detail" to describe your proposed activity</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch, computed, reactive, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

// Available consent types
const availableConsentTypes = [
  {
    value: 'Land Use',
    label: 'Land Use',
    description: 'For buildings, structures, and use of land'
  },
  {
    value: 'Subdivision',
    label: 'Subdivision',
    description: 'For dividing land into separate lots or titles'
  },
  {
    value: 'Discharge Permit',
    label: 'Discharge Permit',
    description: 'For discharges to land, water, or air'
  },
  {
    value: 'Water Permit',
    label: 'Water Permit',
    description: 'For taking, using, damming, or diverting water'
  },
  {
    value: 'Coastal Permit',
    label: 'Coastal Permit',
    description: 'For activities in the coastal marine area'
  }
]

// Activity statuses
const activityStatuses = [
  {
    value: 'Unsure',
    label: 'Unsure / To Be Determined by Council',
    description: 'Council planner will assess and determine the correct status'
  },
  {
    value: 'Permitted',
    label: 'Permitted Activity',
    description: 'Complies with all permitted activity standards'
  },
  {
    value: 'Controlled',
    label: 'Controlled Activity',
    description: 'Council must grant consent, can impose conditions'
  },
  {
    value: 'Restricted Discretionary',
    label: 'Restricted Discretionary Activity',
    description: "Council's discretion limited to specified matters"
  },
  {
    value: 'Discretionary',
    label: 'Discretionary Activity',
    description: 'Council has full discretion to grant or decline'
  },
  {
    value: 'Non-Complying',
    label: 'Non-Complying Activity',
    description: 'Does not comply with plan, requires special consideration'
  }
]

// Local data
const localData = ref({
  consent_types: props.modelValue.consent_types || [],
  activity_status: props.modelValue.activity_status || '',
  lapsing_period_years: props.modelValue.lapsing_period_years || 5,
  consent_notice_required: props.modelValue.consent_notice_required || false,
  consent_notice_details: props.modelValue.consent_notice_details || '',
  coastal_occupation_charge_acknowledged: props.modelValue.coastal_occupation_charge_acknowledged || false,
  request_fast_track: props.modelValue.request_fast_track || false,
  brief_description: props.modelValue.brief_description || '',
  detailed_description: props.modelValue.detailed_description || ''
})

// Consent type checks
const hasConsentType = (type) => {
  return localData.value.consent_types?.some(ct => ct.consent_type === type) || false
}

const isSubdivision = computed(() => hasConsentType('Subdivision'))
const isCoastalPermit = computed(() => hasConsentType('Coastal Permit'))

// Duration helpers - per consent type
const canBeUnlimited = (consentType) => {
  return consentType === 'Land Use' || consentType === 'Subdivision'
}

const getMaxDuration = (consentType) => {
  return canBeUnlimited(consentType) ? 999 : 35
}

const getDurationHelpText = (consentType) => {
  if (canBeUnlimited(consentType)) {
    return 'Land Use and Subdivision consents can be granted for unlimited duration (s.123 RMA)'
  }
  return 'Water Permits, Discharge Permits, and Coastal Permits have a maximum duration of 35 years (s.123 RMA)'
}

// Duration data management - store per consent type
const durationData = reactive({})

const getDurationData = (consentType) => {
  if (!durationData[consentType]) {
    // Check if data exists in modelValue
    const existing = props.modelValue.consent_type_durations?.find(d => d.consent_type === consentType)
    if (existing) {
      durationData[consentType] = { ...existing }
    } else {
      durationData[consentType] = {
        consent_type: consentType,
        duration_years: 10,
        duration_unlimited: false
      }
    }
  }
  return durationData[consentType]
}

// Real-time validation state
const durationTouched = reactive({})
const durationErrors = reactive({})

// Validate duration input
const validateDuration = (consentType) => {
  durationTouched[consentType] = true
  const data = getDurationData(consentType)

  // Clear error if unlimited is selected
  if (data.duration_unlimited) {
    durationErrors[consentType] = null
    return
  }

  const max = getMaxDuration(consentType)
  const years = data.duration_years

  // Validation rules
  if (!years || years < 1) {
    durationErrors[consentType] = 'Duration must be at least 1 year'
  } else if (years > max) {
    if (canBeUnlimited(consentType)) {
      durationErrors[consentType] = `Maximum ${max} years, or select "Unlimited" (s.123 RMA)`
    } else {
      durationErrors[consentType] = `${consentType} cannot exceed ${max} years (s.123 RMA)`
    }
  } else {
    durationErrors[consentType] = null
  }
}

// Get validation CSS class
const getDurationValidationClass = (consentType) => {
  if (!durationTouched[consentType]) {
    return 'border border-gray-300 bg-white'
  }
  if (durationErrors[consentType]) {
    return 'border-2 border-red-300 bg-red-50'
  }
  if (getDurationData(consentType).duration_years && !getDurationData(consentType).duration_unlimited) {
    return 'border-2 border-green-300 bg-green-50'
  }
  return 'border border-gray-300 bg-white'
}

// Get validation error message
const getDurationError = (consentType) => {
  return durationErrors[consentType]
}

// Handle unlimited checkbox toggle
const onUnlimitedToggle = (consentType) => {
  validateDuration(consentType)
}

// Accessibility helper functions - Generate unique IDs for ARIA
const getDurationInputId = (consentType) => {
  return `duration-${consentType.toLowerCase().replace(/\s+/g, '-')}`
}

const getDurationHelpId = (consentType) => {
  return `duration-help-${consentType.toLowerCase().replace(/\s+/g, '-')}`
}

const getUnlimitedCheckboxId = (consentType) => {
  return `unlimited-${consentType.toLowerCase().replace(/\s+/g, '-')}`
}

// Watch duration data and sync to modelValue
watch(durationData, () => {
  const durations = Object.values(durationData)
  emit('update:modelValue', {
    ...props.modelValue,
    consent_type_durations: durations
  })
}, { deep: true })

// Initialize duration data when consent types change
watch(() => localData.value.consent_types, (newConsentTypes) => {
  // Ensure all selected consent types have duration data initialized
  newConsentTypes.forEach(ct => {
    getDurationData(ct.consent_type)
  })
  // Trigger duration data sync
  const durations = Object.values(durationData)
  emit('update:modelValue', {
    ...props.modelValue,
    consent_type_durations: durations
  })
}, { deep: true, immediate: true })

// Initialize duration data on mount
onMounted(() => {
  // Initialize duration data for any existing consent types
  if (localData.value.consent_types && localData.value.consent_types.length > 0) {
    localData.value.consent_types.forEach(ct => {
      getDurationData(ct.consent_type)
    })
    // Trigger initial sync
    const durations = Object.values(durationData)
    if (durations.length > 0) {
      emit('update:modelValue', {
        ...props.modelValue,
        consent_type_durations: durations
      })
    }
  }
})

// Fast-track eligibility and availability
const eligibleForFastTrack = computed(() => {
  const isControlled = localData.value.activity_status === 'Controlled'
  const notSubdivision = !isSubdivision.value
  return isControlled && notSubdivision
})

const fastTrackAvailable = computed(() => {
  return true
})

// UI state for help panel
const showLapsingHelp = ref(false)

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  localData.value.consent_types = newVal.consent_types || []
  localData.value.activity_status = newVal.activity_status || ''
  localData.value.lapsing_period_years = newVal.lapsing_period_years || 5
  localData.value.consent_notice_required = newVal.consent_notice_required || false
  localData.value.consent_notice_details = newVal.consent_notice_details || ''
  localData.value.coastal_occupation_charge_acknowledged = newVal.coastal_occupation_charge_acknowledged || false
  localData.value.request_fast_track = newVal.request_fast_track || false
  localData.value.brief_description = newVal.brief_description || ''
  localData.value.detailed_description = newVal.detailed_description || ''
}, { deep: true })

// Watch local changes and emit
watch(localData, (newVal) => {
  emit('update:modelValue', {
    ...props.modelValue,
    consent_types: newVal.consent_types,
    activity_status: newVal.activity_status,
    lapsing_period_years: newVal.lapsing_period_years,
    consent_notice_required: newVal.consent_notice_required,
    consent_notice_details: newVal.consent_notice_details,
    coastal_occupation_charge_acknowledged: newVal.coastal_occupation_charge_acknowledged,
    request_fast_track: newVal.request_fast_track,
    brief_description: newVal.brief_description,
    detailed_description: newVal.detailed_description
  })
}, { deep: true })

// Toggle consent type selection
const toggleConsentType = (consentType) => {
  const index = localData.value.consent_types.findIndex(ct => ct.consent_type === consentType)
  if (index > -1) {
    localData.value.consent_types.splice(index, 1)
  } else {
    localData.value.consent_types.push({ consent_type: consentType })
  }
}

// Check if consent type is selected
const isConsentTypeSelected = (consentType) => {
  return localData.value.consent_types.some(ct => ct.consent_type === consentType)
}

// Proposal detail management
const addProposalDetail = () => {
  const updatedData = { ...props.modelValue }
  if (!updatedData.proposal_details) {
    updatedData.proposal_details = []
  }
  updatedData.proposal_details.push({
    detail_type: '',
    building_height_m: null,
    total_floor_area_m2: null,
    earthworks_description: '',
    traffic_description: '',
    operations_description: '',
    subdivision_lots: null,
    subdivision_lot_sizes: '',
    discharge_type: '',
    discharge_receiver: '',
    discharge_treatment: '',
    water_source: '',
    water_max_take_m3: null,
    water_rate: '',
    coastal_structure_type: '',
    coastal_navigation_effects: ''
  })
  emit('update:modelValue', updatedData)
}

const removeProposalDetail = (index) => {
  if (confirm('Remove this proposal detail?')) {
    const updatedData = { ...props.modelValue }
    updatedData.proposal_details.splice(index, 1)
    emit('update:modelValue', updatedData)
  }
}
</script>
