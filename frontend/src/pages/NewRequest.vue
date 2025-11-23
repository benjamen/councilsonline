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
          <Button @click="saveDraft" variant="outline" theme="gray" :loading="savingDraft">
            Save Draft
          </Button>
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

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <!-- Step 1: Request Type -->
        <div v-if="currentStep === 1">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Application Type</h2>
          <p class="text-gray-600 mb-8">Choose the type of consent you wish to apply for</p>

          <div v-if="requestTypes.loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div v-else class="grid md:grid-cols-2 gap-4">
            <div
              v-for="type in requestTypes.data"
              :key="type.name"
              @click="selectRequestType(type)"
              class="border-2 rounded-lg p-6 cursor-pointer transition-all hover:shadow-md"
              :class="formData.request_type === type.name ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ type.type_name }}</h3>
                  <p class="text-sm text-gray-600" v-html="type.description || 'No description available'"></p>
                  <div class="mt-4 flex items-center space-x-4 text-xs text-gray-500">
                    <span v-if="type.base_fee">Fee: ${{ type.base_fee }}</span>
                    <span v-if="type.processing_sla_days">{{ type.processing_sla_days }} days</span>
                    <span v-if="type.category" class="px-2 py-1 bg-gray-100 rounded">{{ type.category }}</span>
                  </div>
                </div>
                <div v-if="formData.request_type === type.name" class="ml-4">
                  <div class="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Property Details -->
        <div v-if="currentStep === 2">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Property Details</h2>
          <p class="text-gray-600 mb-8">Provide details about the property for this application</p>

          <div class="space-y-6">
            <!-- Property Search/Select -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Select Existing Property or Enter New
              </label>
              <select
                v-model="formData.property"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                @change="onPropertySelect"
              >
                <option value="">-- Select a property or enter new --</option>
                <option v-for="prop in properties.data" :key="prop.name" :value="prop.name">
                  {{ prop.property_id }} - {{ prop.street_address }}, {{ prop.suburb }}
                </option>
              </select>
            </div>

            <!-- Manual Property Entry -->
            <div v-if="!formData.property" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Property Address *</label>
                <Input
                  v-model="formData.property_address"
                  placeholder="123 Main Street, Wellington"
                  type="text"
                />
              </div>

              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Legal Description</label>
                  <Input
                    v-model="formData.legal_description"
                    placeholder="Lot 1 DP 12345"
                    type="text"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Valuation Reference</label>
                  <Input
                    v-model="formData.valuation_reference"
                    placeholder="1234567"
                    type="text"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Zone</label>
                <select
                  v-model="formData.zone"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select zone</option>
                  <option value="Residential">Residential</option>
                  <option value="Commercial">Commercial</option>
                  <option value="Industrial">Industrial</option>
                  <option value="Rural">Rural</option>
                  <option value="Mixed Use">Mixed Use</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Application Details -->
        <div v-if="currentStep === 3">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Application Details</h2>
          <p class="text-gray-600 mb-8">Describe your proposed activity or development</p>

          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Brief Description *</label>
              <Input
                v-model="formData.brief_description"
                placeholder="e.g., Two-storey residential dwelling"
                type="text"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Detailed Description *</label>
              <textarea
                v-model="formData.detailed_description"
                rows="6"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Provide a detailed description of the proposed activity, including any relevant technical details, dimensions, materials, and timeframes..."
              ></textarea>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Estimated Project Value</label>
                <Input
                  v-model="formData.estimated_value"
                  placeholder="e.g., 500000"
                  type="number"
                >
                  <template #prefix>
                    <span class="text-gray-500">$</span>
                  </template>
                </Input>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Proposed Start Date</label>
                <Input
                  v-model="formData.proposed_start_date"
                  type="date"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Step 4: Resource Consent Details (conditional) -->
        <div v-if="isResourceConsent && currentStep === 4">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Resource Consent Details</h2>
          <p class="text-gray-600 mb-8">Provide Resource Management Act (RMA) specific information</p>

          <div class="space-y-6">
            <!-- Consent Type and Activity Status -->
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Consent Type *
                </label>
                <select
                  v-model="formData.consent_types"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select consent type</option>
                  <option value="Land Use">Land Use</option>
                  <option value="Subdivision">Subdivision</option>
                  <option value="Discharge Permit">Discharge Permit</option>
                  <option value="Water Permit">Water Permit</option>
                  <option value="Coastal Permit">Coastal Permit</option>
                </select>
                <p class="mt-1 text-xs text-gray-500">Type of resource consent under the RMA</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Activity Status *
                  <button
                    type="button"
                    @click="showActivityStatusHelp = !showActivityStatusHelp"
                    class="ml-1 text-blue-600 hover:text-blue-800"
                    title="Click for help"
                  >
                    <svg class="w-4 h-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                </label>

                <div v-if="showActivityStatusHelp" class="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-900">
                  <p class="font-semibold mb-2">RMA Activity Status Guide:</p>
                  <ul class="space-y-1 ml-4 list-disc">
                    <li><strong>Permitted:</strong> Allowed without consent (no application needed)</li>
                    <li><strong>Controlled:</strong> Consent must be granted; council sets conditions</li>
                    <li><strong>Restricted Discretionary:</strong> Council has limited grounds to decline</li>
                    <li><strong>Discretionary:</strong> Council has full discretion to grant or decline</li>
                    <li><strong>Non-Complying:</strong> Does not comply with plan; requires special justification</li>
                    <li><strong>Prohibited:</strong> Cannot be consented under any circumstances</li>
                  </ul>
                  <p class="mt-2 text-xs text-blue-700">Check your district plan zone rules to determine status</p>
                </div>

                <select
                  v-model="formData.activity_status"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select activity status</option>
                  <option value="Controlled">Controlled</option>
                  <option value="Restricted Discretionary">Restricted Discretionary</option>
                  <option value="Discretionary">Discretionary</option>
                  <option value="Non-Complying">Non-Complying</option>
                </select>
                <p class="mt-1 text-xs text-gray-500">Activity classification under district plan</p>

                <div v-if="activityStatusWarning" class="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                  {{ activityStatusWarning }}
                </div>
              </div>
            </div>

            <!-- Assessment of Environmental Effects -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Assessment of Environmental Effects (AEE) *
              </label>
              <textarea
                v-model="formData.assessment_of_effects"
                rows="8"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe the actual and potential effects on the environment as per Schedule 4 of the RMA. Include effects on people, physical environment, ecosystems, and cultural/heritage values..."
                required
              ></textarea>
              <p class="mt-1 text-xs text-gray-500">Required under Schedule 4 of the Resource Management Act</p>
            </div>

            <!-- Effects Breakdown (Optional) -->
            <div class="border-t border-gray-200 pt-4">
              <h3 class="text-sm font-semibold text-gray-900 mb-3">Detailed Effects Assessment (Optional)</h3>

              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Effects on People</label>
                  <textarea
                    v-model="formData.effects_on_people"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="Privacy, sunlight access, visual amenity, noise impacts..."
                  ></textarea>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Physical Effects</label>
                  <textarea
                    v-model="formData.physical_effects"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="Traffic, parking, stormwater, infrastructure impacts..."
                  ></textarea>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Ecosystem Effects</label>
                  <textarea
                    v-model="formData.ecosystem_effects"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="Indigenous vegetation, habitat values, watercourses..."
                  ></textarea>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Cultural/Heritage Effects</label>
                  <textarea
                    v-model="formData.cultural_effects"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="Heritage values, sites of significance to Māori, archaeological sites..."
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Planning Assessment -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Planning Assessment *
              </label>
              <textarea
                v-model="formData.planning_assessment"
                rows="6"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Assess the proposal against relevant district plan provisions, objectives and policies. Address how the proposal aligns with planning framework..."
                required
              ></textarea>
              <p class="mt-1 text-xs text-gray-500">Assessment against district plan objectives and policies</p>
            </div>

            <!-- Alternatives and Mitigation -->
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Alternatives Considered
                </label>
                <textarea
                  v-model="formData.alternatives_considered"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  placeholder="What alternative designs, locations, or methods were considered?..."
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Mitigation Measures
                </label>
                <textarea
                  v-model="formData.mitigation_proposed"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  placeholder="What measures will be implemented to avoid, remedy or mitigate adverse effects?..."
                ></textarea>
              </div>
            </div>

            <!-- Affected Parties -->
            <div class="border-t border-gray-200 pt-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold text-gray-900">Affected Parties</h3>
                <Button @click="addAffectedParty" variant="outline" theme="blue" size="sm">
                  <template #prefix>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </template>
                  Add Party
                </Button>
              </div>

              <p class="text-xs text-gray-500 mb-3">
                List any parties (neighbors, landowners, etc.) who may be adversely affected by the proposal
              </p>

              <div v-if="formData.affected_parties.length > 0" class="space-y-2 mb-3">
                <div
                  v-for="(party, index) in formData.affected_parties"
                  :key="index"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ party.party_name }}</p>
                    <p class="text-xs text-gray-500">{{ party.address }}</p>
                    <p v-if="party.written_approval_obtained" class="text-xs text-green-600 mt-1">
                      ✓ Written approval obtained
                    </p>
                  </div>
                  <button @click="removeAffectedParty(index)" class="text-red-600 hover:text-red-800">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <div v-else class="text-center py-6 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <p class="text-sm text-gray-500">No affected parties added yet</p>
              </div>
            </div>

            <!-- Specialist Reports -->
            <div class="border-t border-gray-200 pt-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold text-gray-900">Specialist Reports</h3>
                <Button @click="addSpecialistReport" variant="outline" theme="blue" size="sm">
                  <template #prefix>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </template>
                  Add Report
                </Button>
              </div>

              <p class="text-xs text-gray-500 mb-3">
                Add any specialist technical reports (traffic, geotechnical, acoustic, ecological, etc.)
              </p>

              <div v-if="formData.specialist_reports.length > 0" class="space-y-2 mb-3">
                <div
                  v-for="(report, index) in formData.specialist_reports"
                  :key="index"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ report.report_type }}</p>
                    <p class="text-xs text-gray-500">{{ report.specialist_name }} | {{ report.date_prepared }}</p>
                  </div>
                  <button @click="removeSpecialistReport(index)" class="text-red-600 hover:text-red-800">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <div v-else class="text-center py-6 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <p class="text-sm text-gray-500">No specialist reports added yet</p>
                <p class="text-xs text-gray-400 mt-1">Upload report files in the Documents step</p>
              </div>
            </div>

            <!-- Iwi Consultation -->
            <div class="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 class="text-sm font-semibold text-green-900 mb-3">
                Iwi Consultation
                <span class="ml-2 text-xs font-normal text-green-700">(Treaty of Waitangi obligations)</span>
              </h3>

              <div class="space-y-3">
                <div class="flex items-start">
                  <input
                    type="checkbox"
                    v-model="formData.iwi_consultation_undertaken"
                    class="mt-1 h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <label class="ml-3 text-sm text-green-800">
                    Consultation with iwi/hapū has been undertaken
                  </label>
                </div>

                <div v-if="formData.iwi_consultation_undertaken">
                  <label class="block text-xs font-medium text-green-700 mb-1">
                    Iwi/Hapū Consulted
                  </label>
                  <textarea
                    v-model="formData.iwi_consulted"
                    rows="2"
                    class="w-full px-3 py-2 border border-green-300 rounded-lg text-sm bg-white"
                    placeholder="List the iwi/hapū that were consulted and summarize their response..."
                  ></textarea>

                  <label class="block text-xs font-medium text-green-700 mb-1 mt-3">
                    Cultural Impact Assessment (CIA) Document
                  </label>
                  <input
                    type="file"
                    ref="ciaFileInput"
                    @change="handleCIAUpload"
                    accept=".pdf,.doc,.docx"
                    class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-green-100 file:text-green-700 hover:file:bg-green-200"
                  />
                  <p v-if="formData.cultural_impact_assessment" class="text-xs text-green-600 mt-1">
                    ✓ {{ formData.cultural_impact_assessment.name }} uploaded
                  </p>
                </div>
              </div>
            </div>

            <!-- Proposed Conditions -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Proposed Conditions (Optional)
              </label>
              <textarea
                v-model="formData.proposed_conditions"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                placeholder="If you wish to propose specific conditions of consent, list them here..."
              ></textarea>
              <p class="mt-1 text-xs text-gray-500">The council will determine final consent conditions</p>
            </div>

            <!-- Pre-Application Meeting -->
            <div class="border-t border-gray-200 pt-6 mt-6">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div class="flex items-start">
                  <div class="flex-shrink-0">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div class="ml-3 flex-1">
                    <h3 class="text-sm font-semibold text-blue-900 mb-2">
                      Need Help with Your Application?
                    </h3>
                    <p class="text-sm text-blue-800 mb-3">
                      For <strong>discretionary</strong> or <strong>non-complying</strong> activities, we recommend booking a pre-application meeting with our planning team. This can help:
                    </p>
                    <ul class="text-sm text-blue-800 space-y-1 ml-4 list-disc mb-4">
                      <li>Clarify district plan requirements</li>
                      <li>Identify potential issues early</li>
                      <li>Understand what information you'll need</li>
                      <li>Get preliminary feedback on your proposal</li>
                    </ul>
                    <Button
                      @click="requestPreAppMeeting"
                      variant="solid"
                      theme="blue"
                      size="sm"
                      :loading="requestingMeeting"
                    >
                      <template #prefix>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </template>
                      Request Pre-Application Meeting
                    </Button>
                    <p class="text-xs text-blue-700 mt-2">
                      A planning officer will contact you within 2 business days to schedule.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 4/5: Documents -->
        <div v-if="currentStep === (isResourceConsent ? 5 : 4)">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Upload Documents</h2>
          <p class="text-gray-600 mb-8">Attach all required supporting documents</p>

          <div class="space-y-6">
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition">
              <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="text-gray-600 mb-2">Drag and drop files here, or click to browse</p>
              <p class="text-xs text-gray-500">PDF, DOC, DOCX, JPG, PNG (Max 10MB per file)</p>
              <Button @click="triggerFileUpload" variant="outline" theme="blue" class="mt-4">
                Select Files
              </Button>
              <input type="file" ref="fileInput" multiple class="hidden" @change="handleFileUpload" />
            </div>

            <!-- Uploaded Files List -->
            <div v-if="uploadedFiles.length > 0" class="space-y-2">
              <h4 class="font-medium text-gray-900">Uploaded Documents ({{ uploadedFiles.length }})</h4>
              <div
                v-for="(file, index) in uploadedFiles"
                :key="index"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ file.name }}</p>
                    <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
                  </div>
                </div>
                <button @click="removeFile(index)" class="text-red-600 hover:text-red-800">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Required Documents Checklist -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h4 class="font-medium text-blue-900 mb-3">Required Documents</h4>
              <ul class="space-y-2 text-sm text-blue-800">
                <li class="flex items-start">
                  <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  Site plans and location maps
                </li>
                <li class="flex items-start">
                  <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  Architectural drawings and specifications
                </li>
                <li class="flex items-start">
                  <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  Assessment of Environmental Effects (AEE)
                </li>
                <li class="flex items-start">
                  <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  Written approvals from affected parties (if required)
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Step 5/6: Review & Submit -->
        <div v-if="currentStep === (isResourceConsent ? 6 : 5)">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Review & Submit</h2>
          <p class="text-gray-600 mb-8">Please review your application before submission</p>

          <div class="space-y-6">
            <!-- Application Summary -->
            <div class="border border-gray-200 rounded-lg p-6">
              <h3 class="font-semibold text-gray-900 mb-4">Application Summary</h3>

              <dl class="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <dt class="text-gray-600">Application Type</dt>
                  <dd class="font-medium text-gray-900 mt-1">{{ getRequestTypeName() }}</dd>
                </div>
                <div>
                  <dt class="text-gray-600">Property Address</dt>
                  <dd class="font-medium text-gray-900 mt-1">{{ formData.property_address || 'N/A' }}</dd>
                </div>
                <div>
                  <dt class="text-gray-600">Brief Description</dt>
                  <dd class="font-medium text-gray-900 mt-1">{{ formData.brief_description || 'N/A' }}</dd>
                </div>
                <div>
                  <dt class="text-gray-600">Estimated Value</dt>
                  <dd class="font-medium text-gray-900 mt-1">
                    {{ formData.estimated_value ? `$${formData.estimated_value}` : 'N/A' }}
                  </dd>
                </div>
                <div>
                  <dt class="text-gray-600">Documents Uploaded</dt>
                  <dd class="font-medium text-gray-900 mt-1">{{ uploadedFiles.length }} files</dd>
                </div>
              </dl>
            </div>

            <!-- Terms & Conditions -->
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <div class="flex items-start">
                <input
                  type="checkbox"
                  v-model="formData.terms_accepted"
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label class="ml-3 text-sm text-gray-700">
                  I confirm that the information provided in this application is true and accurate to the best of my knowledge.
                  I understand that providing false or misleading information may result in the application being declined or
                  consent being revoked. I have read and agree to the
                  <a href="#" class="text-blue-600 hover:text-blue-800">terms and conditions</a>.
                </label>
              </div>
            </div>

            <!-- Fee Summary -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h4 class="font-medium text-blue-900 mb-3">Fee Summary</h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-blue-800">Application Fee</span>
                  <span class="font-medium text-blue-900">{{ getApplicationFee() }}</span>
                </div>
                <div class="flex justify-between pt-2 border-t border-blue-200">
                  <span class="font-medium text-blue-900">Total Due</span>
                  <span class="text-lg font-bold text-blue-900">{{ getApplicationFee() }}</span>
                </div>
              </div>
              <p class="text-xs text-blue-700 mt-3">
                Payment will be processed after submission. You will receive an invoice via email.
              </p>
            </div>

            <!-- Pre-Application Meeting (Resource Consent Only) -->
            <div v-if="isResourceConsent" class="bg-green-50 border border-green-200 rounded-lg p-6">
              <h4 class="font-medium text-green-900 mb-2">Pre-Application Meeting</h4>
              <p class="text-sm text-green-700 mb-4">
                For Resource Consent applications, we strongly recommend booking a pre-application meeting with our planning team.
                This helps ensure your application meets all requirements and can speed up the approval process.
              </p>
              <Button
                @click="bookPreApplicationMeeting"
                variant="solid"
                theme="green"
                :loading="bookingMeeting"
              >
                <template #prefix>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </template>
                Book Pre-Application Meeting
              </Button>
            </div>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
          <Button
            v-if="currentStep > 1"
            @click="previousStep"
            variant="outline"
            theme="gray"
          >
            <template #prefix>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </template>
            Previous
          </Button>
          <div v-else></div>

          <div class="flex space-x-3">
            <Button
              v-if="currentStep < totalSteps"
              @click="nextStep"
              variant="solid"
              theme="blue"
              :disabled="!canProceed()"
            >
              Next
              <template #suffix>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </template>
            </Button>
            <Button
              v-else-if="canSubmit"
              @click="submitApplication"
              variant="solid"
              theme="blue"
              :loading="submitting"
              :disabled="!formData.terms_accepted"
            >
              Submit Application
            </Button>
            <div v-else class="text-sm text-gray-500">
              Make changes to your application to enable submission
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Input, Button } from 'frappe-ui'

const router = useRouter()

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

const steps = computed(() => {
  const baseSteps = [
    { title: 'Type', number: 1 },
    { title: 'Property', number: 2 },
    { title: 'Details', number: 3 }
  ]

  // Add RC-specific step if Resource Consent selected
  if (isResourceConsent.value) {
    baseSteps.push({ title: 'RC Details', number: 4 })
  }

  baseSteps.push(
    { title: 'Documents', number: baseSteps.length + 1 },
    { title: 'Review', number: baseSteps.length + 2 }
  )

  return baseSteps
})

// Form data
const formData = ref({
  request_type: '',
  request_category: '', // Store the category of the selected request type
  property: '',
  property_address: '',
  legal_description: '',
  valuation_reference: '',
  zone: '',
  brief_description: '',
  detailed_description: '',
  estimated_value: null,
  proposed_start_date: '',
  terms_accepted: false,

  // Resource Consent specific fields
  consent_types: '',
  activity_status: '',
  assessment_of_effects: '',
  effects_on_people: '',
  physical_effects: '',
  ecosystem_effects: '',
  cultural_effects: '',
  planning_assessment: '',
  alternatives_considered: '',
  mitigation_proposed: '',
  iwi_consultation_undertaken: false,
  iwi_consulted: '',
  cultural_impact_assessment: null, // CIA file upload
  proposed_conditions: '',
  affected_parties: [], // Array of affected parties
  specialist_reports: [], // Array of specialist reports
})

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

// Get request types
const requestTypes = createResource({
  url: 'lodgeick.lodgeick.doctype.request_type.request_type.get_active_request_types',
  auto: true,
})

// Get user's properties
const properties = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Property',
    fields: ['name', 'property_id', 'street_address', 'suburb', 'city'],
    limit_page_length: 100,
  },
  auto: true,
})

// Methods
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

const selectRequestType = (type) => {
  formData.value.request_type = type.name
  formData.value.request_category = type.category || ''
}

const onPropertySelect = () => {
  if (formData.value.property) {
    const selected = properties.data.find(p => p.name === formData.value.property)
    if (selected) {
      formData.value.property_address = `${selected.street_address}, ${selected.suburb}, ${selected.city}`
    }
  }
}

const canProceed = () => {
  switch (currentStep.value) {
    case 1:
      return !!formData.value.request_type
    case 2:
      return !!formData.value.property_address
    case 3:
      return !!formData.value.brief_description && !!formData.value.detailed_description
    case 4:
      // If RC, this is RC Details step - validate required fields
      if (isResourceConsent.value) {
        return !!(
          formData.value.consent_types &&
          formData.value.activity_status &&
          formData.value.assessment_of_effects &&
          formData.value.planning_assessment
        )
      }
      // Otherwise, this is Documents step (optional)
      return true
    case 5:
      // If RC, this is Documents step (optional)
      // Otherwise, this is Review step
      return true
    default:
      return true
  }
}

const nextStep = () => {
  if (canProceed() && currentStep.value < totalSteps) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const saveDraft = async () => {
  savingDraft.value = true
  try {
    const response = await fetch('/api/method/lodgeick.api.create_draft_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        data: formData.value
      })
    })

    const result = await response.json()

    if (result.message && result.message.success) {
      alert(`Draft saved successfully! Request ID: ${result.message.request_number}`)
      // Optionally redirect to dashboard
      // router.push({ name: 'Dashboard' })
    } else {
      throw new Error(result.message || 'Failed to save draft')
    }
  } catch (error) {
    console.error('Error saving draft:', error)
    alert('Failed to save draft. Please try again.')
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

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const getRequestTypeName = () => {
  const type = requestTypes.data?.find(t => t.name === formData.value.request_type)
  return type?.type_name || 'N/A'
}

const getApplicationFee = () => {
  const type = requestTypes.data?.find(t => t.name === formData.value.request_type)
  return type?.base_fee ? `$${type.base_fee}` : 'TBD'
}

const submitApplication = async () => {
  if (!formData.value.terms_accepted) {
    alert('Please accept the terms and conditions')
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

const addAffectedParty = () => {
  const partyName = prompt('Enter affected party name:')
  if (!partyName) return

  const address = prompt('Enter address:')
  if (!address) return

  const writtenApproval = confirm('Has written approval been obtained from this party?')

  formData.value.affected_parties.push({
    party_name: partyName,
    address: address,
    written_approval_obtained: writtenApproval
  })
}

const removeAffectedParty = (index) => {
  if (confirm('Remove this affected party?')) {
    formData.value.affected_parties.splice(index, 1)
  }
}

const addSpecialistReport = () => {
  const reportTypes = [
    'Traffic Assessment',
    'Geotechnical Report',
    'Acoustic Assessment',
    'Stormwater Design',
    'Ecological Assessment',
    'Heritage Impact Assessment',
    'Archaeological Assessment',
    'Landscape Assessment',
    'Other'
  ]

  const reportType = prompt(`Select report type:\n${reportTypes.map((t, i) => `${i + 1}. ${t}`).join('\n')}\n\nEnter number or type custom:`)
  if (!reportType) return

  const reportTypeValue = reportTypes[parseInt(reportType) - 1] || reportType

  const specialistName = prompt('Enter specialist/consultant name:')
  if (!specialistName) return

  const datePrepared = prompt('Enter date prepared (YYYY-MM-DD):')

  formData.value.specialist_reports.push({
    report_type: reportTypeValue,
    specialist_name: specialistName,
    date_prepared: datePrepared || new Date().toISOString().split('T')[0]
  })
}

const removeSpecialistReport = (index) => {
  if (confirm('Remove this specialist report?')) {
    formData.value.specialist_reports.splice(index, 1)
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
</script>
