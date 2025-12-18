<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Boundary Approvals & Affected Parties</h2>
    <p class="text-gray-600 mb-8">Obtain approvals for boundary activities and identify affected parties (RMA s.95A-s.95F)</p>

    <div class="space-y-8">
      <!-- Permitted Boundary Activity (PBA) Section (FRD 6.1) -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Permitted Boundary Activity (PBA) Approvals</h3>
        </div>

        <div class="p-6 space-y-4">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h5 class="font-semibold text-blue-900 text-sm">About Permitted Boundary Activities</h5>
                <p class="text-blue-800 text-sm mt-1">
                  A Permitted Boundary Activity is an activity within prescribed proximity to a property boundary that would normally be permitted.
                  Under s.87BA RMA, if you obtain written approval from the affected neighbor(s), the activity may be permitted without consent.
                </p>
                <p class="text-blue-800 text-sm mt-2">
                  <strong>Note:</strong> If you are applying for consent because you could not obtain PBA approval, please complete this section.
                </p>
              </div>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Does this application relate to a Permitted Boundary Activity?
            </label>
            <div class="flex gap-4">
              <label class="flex items-center">
                <input
                  v-model="localData.pba_approval_required"
                  type="radio"
                  :value="true"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">Yes</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="localData.pba_approval_required"
                  type="radio"
                  :value="false"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">No</span>
              </label>
            </div>
          </div>

          <!-- PBA Details (show if Yes selected) -->
          <div v-if="localData.pba_approval_required" class="space-y-4 border-t border-gray-200 pt-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">PBA Status</label>
              <select
                v-model="localData.pba_status"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select status</option>
                <option value="Approval sought but not obtained">Approval sought but not obtained</option>
                <option value="Approval obtained from some neighbors">Approval obtained from some neighbors</option>
                <option value="Approval obtained from all neighbors">Approval obtained from all neighbors</option>
                <option value="Approval not sought">Approval not sought</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">PBA Details</label>
              <textarea
                v-model="localData.pba_details"
                rows="3"
                placeholder="Describe the boundary activity, which neighbors were approached, and the outcome..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- PBA Affected Neighbors -->
            <div class="border-t border-gray-200 pt-4">
              <div class="flex justify-between items-center mb-3">
                <label class="block text-sm font-medium text-gray-700">
                  Neighbors Affected by Boundary Activity
                </label>
                <button
                  @click="showPBAModal = true"
                  type="button"
                  class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Add Neighbor
                </button>
              </div>

              <!-- PBA Contacts List -->
              <div v-if="localData.pba_contacts && localData.pba_contacts.length > 0" class="space-y-2">
                <div
                  v-for="(contact, index) in localData.pba_contacts"
                  :key="index"
                  class="border border-gray-200 rounded-lg p-3 bg-gray-50 flex justify-between items-start"
                >
                  <div class="flex-1">
                    <div class="font-medium text-gray-900">{{ contact.organisation_name || contact.contact_name }}</div>
                    <div class="text-sm text-gray-600 mt-1">
                      {{ contact.contact_name }}
                      <span v-if="contact.email"> • {{ contact.email }}</span>
                      <span v-if="contact.phone"> • {{ contact.phone }}</span>
                    </div>
                    <div v-if="contact.address" class="text-xs text-gray-500 mt-1">
                      {{ [contact.address, contact.rd_number, contact.suburb, contact.city, contact.postcode].filter(Boolean).join(', ') }}
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <button
                      @click="editPBA(index)"
                      type="button"
                      class="text-blue-600 hover:text-blue-800 p-1"
                      title="Edit"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      @click="removePBA(index)"
                      type="button"
                      class="text-red-600 hover:text-red-800 p-1"
                      title="Remove"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
                <p class="text-sm text-gray-500">No neighbors added yet</p>
              </div>
            </div>

            <!-- PBA Document Upload -->
            <div class="border-t border-gray-200 pt-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Upload PBA Documents (if applicable)
              </label>
              <input
                type="file"
                @change="handlePBADocumentUpload"
                accept=".pdf,.doc,.docx"
                multiple
                class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
              />
              <p v-if="localData.pba_documents && localData.pba_documents.length > 0" class="text-xs text-green-600 mt-1">
                ✓ {{ localData.pba_documents.length }} document(s) uploaded
              </p>
              <p class="mt-1 text-xs text-gray-500">Upload PBA forms, neighbor correspondence, or written approvals (PDF or Word)</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Affected Parties Section (existing Step13 functionality) -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Affected Parties (RMA s.95A-s.95F)</h3>
        </div>

        <div class="p-6 space-y-6">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h5 class="font-semibold text-blue-900 text-sm">About Affected Parties</h5>
                <p class="text-blue-800 text-sm mt-1">
                  List all parties (neighbors, landowners, infrastructure providers, etc.) who may be affected by your proposal.
                  If you have obtained written approvals under s.95E, upload them as supporting documents. Written approvals can reduce notification requirements.
                </p>
              </div>
            </div>
          </div>

          <!-- Add Affected Party Button -->
          <div class="flex justify-between items-center">
            <p class="text-sm text-gray-700">
              Identify all parties who may experience adverse effects from your proposal
            </p>
            <button
              @click="openAddModal"
              type="button"
              class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Add Affected Party
            </button>
          </div>

          <!-- Affected Parties List -->
          <div v-if="localData.affected_parties && localData.affected_parties.length > 0" class="space-y-3">
            <div
              v-for="(party, index) in localData.affected_parties"
              :key="index"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50"
            >
              <div class="flex items-start justify-between mb-3">
                <h4 class="font-semibold text-gray-900">{{ party.party_name || 'Unnamed Party' }}</h4>
                <div class="flex items-center gap-2">
                  <button
                    @click="openEditModal(index)"
                    type="button"
                    class="text-blue-600 hover:text-blue-800 p-1"
                    title="Edit"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="removeParty(index)"
                    type="button"
                    class="text-red-600 hover:text-red-800 p-1"
                    title="Remove"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <span class="text-sm text-gray-500">Relationship:</span>
                  <p class="font-medium">{{ party.relationship || 'Not specified' }}</p>
                </div>
                <div>
                  <span class="text-sm text-gray-500">Contact:</span>
                  <p class="font-medium">{{ party.contact_info || 'Not specified' }}</p>
                </div>
                <div>
                  <span class="text-sm text-gray-500">Address:</span>
                  <p class="font-medium">{{ party.address || 'Not specified' }}</p>
                </div>
                <div>
                  <span class="text-sm text-gray-500">Written Approval (s.95E):</span>
                  <p class="font-medium">
                    <span v-if="party.written_approval" class="text-green-600">✓ Obtained</span>
                    <span v-else class="text-gray-500">Not obtained</span>
                  </p>
                </div>
              </div>
              <div v-if="party.effects" class="mt-3">
                <span class="text-sm text-gray-500">Effects:</span>
                <p class="text-sm mt-1">{{ party.effects }}</p>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p class="mt-2 text-sm text-gray-500">No affected parties identified yet</p>
            <p class="text-sm text-gray-500 mt-1">Click "Add Affected Party" to get started</p>
          </div>

          <!-- Written Approvals Summary -->
          <div v-if="writtenApprovals.length > 0" class="border-t border-gray-200 pt-4">
            <h4 class="text-sm font-semibold text-gray-900 mb-2">Written Approvals Summary (s.95E RMA)</h4>
            <p class="text-sm text-gray-600 mb-3">
              You have obtained written approvals from {{ writtenApprovals.length }} affected {{ writtenApprovals.length === 1 ? 'party' : 'parties' }}.
            </p>
            <div class="space-y-2">
              <div
                v-for="party in writtenApprovals"
                :key="party.party_name"
                class="flex items-center text-sm"
              >
                <svg class="w-4 h-4 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>{{ party.party_name }} ({{ party.relationship }})</span>
              </div>
            </div>
            <div class="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p class="text-sm text-green-800">
                Remember to upload written approval documents in Step 6 (Plans & Documents).
              </p>
            </div>
          </div>

          <!-- Consultation Notes -->
          <div class="border-t border-gray-200 pt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Consultation Summary
            </label>
            <textarea
              v-model="localData.aee_consultation_summary"
              rows="6"
              placeholder="Describe who you consulted with, when, how, and the outcomes of consultation. Include any mitigation measures agreed to address concerns..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
            <p class="text-sm text-gray-500 mt-2">
              Documenting consultation efforts can demonstrate good faith engagement and help the council understand community views.
            </p>
          </div>
        </div>
      </div>

      <!-- Guidance -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Affected Parties Guidance</h5>
            <ul class="text-yellow-800 text-sm mt-2 space-y-1 list-disc list-inside">
              <li>Consider immediate neighbors, landowners with shared boundaries</li>
              <li>Infrastructure providers (e.g., power, water, telecommunications)</li>
              <li>Parties with interests over the land (e.g., easements, covenants)</li>
              <li>Anyone who may experience adverse effects from your proposal</li>
              <li>Written approvals under s.95E can reduce notification requirements and costs</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- PBA Contact Modal -->
    <Teleport to="body">
      <div
        v-if="showPBAModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closePBAModal"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingPBAIndex !== null ? 'Edit' : 'Add' }} PBA Neighbor Contact
            </h3>
            <button @click="closePBAModal" type="button" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="px-6 py-4 space-y-4">
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Organisation Name</label>
                <input v-model="pbaForm.organisation_name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Contact Name *</label>
                <input v-model="pbaForm.contact_name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input v-model="pbaForm.email" type="email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                <input v-model="pbaForm.phone" type="tel" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Street Address</label>
              <input v-model="pbaForm.address" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>

            <div class="grid md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">RD Number</label>
                <input v-model="pbaForm.rd_number" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Suburb</label>
                <input v-model="pbaForm.suburb" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">City</label>
                <input v-model="pbaForm.city" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Postcode</label>
              <input v-model="pbaForm.postcode" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>

          <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
            <button @click="closePBAModal" type="button" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100">
              Cancel
            </button>
            <button @click="savePBA" type="button" :disabled="!pbaForm.contact_name" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {{ editingPBAIndex !== null ? 'Update' : 'Add' }} Contact
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Affected Party Modal (existing Step13 modal) -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
        <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingIndex !== null ? 'Edit' : 'Add' }} Affected Party
            </h3>
            <button @click="closeModal" type="button" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Party Name *</label>
              <input v-model="currentParty.party_name" type="text" placeholder="e.g., John Smith, ABC Infrastructure Ltd" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Relationship *</label>
              <select v-model="currentParty.relationship" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option value="">Select relationship</option>
                <option value="Adjacent neighbor">Adjacent neighbor</option>
                <option value="Nearby neighbor">Nearby neighbor</option>
                <option value="Property owner">Property owner</option>
                <option value="Leaseholder">Leaseholder</option>
                <option value="Easement holder">Easement holder</option>
                <option value="Infrastructure provider">Infrastructure provider</option>
                <option value="Iwi/Hapū">Iwi/Hapū</option>
                <option value="Community group">Community group</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Contact Information</label>
              <input v-model="currentParty.contact_info" type="text" placeholder="Email or phone number" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Address</label>
              <textarea v-model="currentParty.address" rows="2" placeholder="Physical or postal address" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Potential Effects</label>
              <textarea v-model="currentParty.effects" rows="3" placeholder="Describe how your proposal may affect this party (e.g., visual, noise, access, etc.)" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
            </div>

            <div class="flex items-start">
              <input v-model="currentParty.written_approval" type="checkbox" class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
              <label class="ml-3 text-sm text-gray-700">
                <span class="font-medium">Written approval obtained (s.95E RMA)</span>
                <p class="text-xs text-gray-500 mt-1">
                  Check this if you have obtained written approval from this party (upload approval document in Step 6)
                </p>
              </label>
            </div>
          </div>

          <div class="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-end gap-3">
            <button @click="closeModal" type="button" class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
              Cancel
            </button>
            <button @click="saveParty" type="button" :disabled="!currentParty.party_name || !currentParty.relationship" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              {{ editingIndex !== null ? 'Update' : 'Add' }} Party
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps, reactive, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

// Create local data reference
const localData = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

// PBA Modal Management
const showPBAModal = ref(false)
const editingPBAIndex = ref(null)
const pbaForm = reactive({
	organisation_name: "",
	contact_name: "",
	email: "",
	phone: "",
	address: "",
	rd_number: "",
	suburb: "",
	city: "",
	postcode: "",
})

const resetPBAForm = () => {
	Object.assign(pbaForm, {
		organisation_name: "",
		contact_name: "",
		email: "",
		phone: "",
		address: "",
		rd_number: "",
		suburb: "",
		city: "",
		postcode: "",
	})
}

const editPBA = (index) => {
	editingPBAIndex.value = index
	Object.assign(pbaForm, localData.value.pba_contacts[index])
	showPBAModal.value = true
}

const removePBA = (index) => {
	if (confirm("Remove this PBA contact?")) {
		const updatedData = { ...props.modelValue }
		updatedData.pba_contacts.splice(index, 1)
		emit("update:modelValue", updatedData)
	}
}

const savePBA = () => {
	if (!pbaForm.contact_name) return

	const updatedData = { ...props.modelValue }
	if (!updatedData.pba_contacts) updatedData.pba_contacts = []

	const contactData = { ...pbaForm }

	if (editingPBAIndex.value !== null) {
		updatedData.pba_contacts[editingPBAIndex.value] = contactData
	} else {
		updatedData.pba_contacts.push(contactData)
	}

	emit("update:modelValue", updatedData)
	closePBAModal()
}

const closePBAModal = () => {
	showPBAModal.value = false
	editingPBAIndex.value = null
	resetPBAForm()
}

// PBA Document upload
const handlePBADocumentUpload = (event) => {
	const files = Array.from(event.target.files)
	if (files.length > 0) {
		const updatedData = { ...props.modelValue }
		if (!updatedData.pba_documents) updatedData.pba_documents = []

		files.forEach((file) => {
			// Validate file size (max 10MB)
			const maxSize = 10 * 1024 * 1024
			if (file.size > maxSize) {
				alert(`File ${file.name} exceeds 10MB. Please upload a smaller file.`)
				return
			}
			updatedData.pba_documents.push(file.name)
		})

		emit("update:modelValue", updatedData)
	}
}

// Affected Parties Modal state (existing Step13 functionality)
const showModal = ref(false)
const editingIndex = ref(null)
const currentParty = ref({
	party_name: "",
	relationship: "",
	contact_info: "",
	address: "",
	effects: "",
	written_approval: false,
})

// Computed property for parties with written approvals
const writtenApprovals = computed(() => {
	return (
		localData.value.affected_parties?.filter(
			(party) => party.written_approval === true,
		) || []
	)
})

// Open modal for adding new party
const openAddModal = () => {
	editingIndex.value = null
	currentParty.value = {
		party_name: "",
		relationship: "",
		contact_info: "",
		address: "",
		effects: "",
		written_approval: false,
	}
	showModal.value = true
}

// Open modal for editing existing party
const openEditModal = (index) => {
	editingIndex.value = index
	currentParty.value = { ...localData.value.affected_parties[index] }
	showModal.value = true
}

// Close modal
const closeModal = () => {
	showModal.value = false
	editingIndex.value = null
	currentParty.value = {
		party_name: "",
		relationship: "",
		contact_info: "",
		address: "",
		effects: "",
		written_approval: false,
	}
}

// Save party (add or update)
const saveParty = () => {
	if (!currentParty.value.party_name || !currentParty.value.relationship) {
		return
	}

	const updatedData = { ...props.modelValue }
	if (!updatedData.affected_parties) updatedData.affected_parties = []

	if (editingIndex.value !== null) {
		// Update existing party
		updatedData.affected_parties[editingIndex.value] = { ...currentParty.value }
	} else {
		// Add new party
		updatedData.affected_parties.push({ ...currentParty.value })
	}

	emit("update:modelValue", updatedData)
	closeModal()
}

// Remove party
const removeParty = (index) => {
	if (confirm("Are you sure you want to remove this affected party?")) {
		const updatedData = { ...props.modelValue }
		updatedData.affected_parties.splice(index, 1)
		emit("update:modelValue", updatedData)
	}
}
</script>
