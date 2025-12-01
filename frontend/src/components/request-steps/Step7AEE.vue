<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Assessment of Environmental Effects (AEE)</h2>
    <p class="text-gray-600 mb-8">Assess the actual and potential effects of your proposal on the environment (RMA Schedule 4)</p>

    <div class="space-y-8">
      <!-- FRD Info Box (Enhanced) -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">Schedule 4 RMA Requirements</h5>
            <p class="text-blue-800 text-sm mt-1">
              Your AEE must address the matters in Schedule 4 of the RMA, scaled to the nature and scale of the proposal.
              The level of detail should correspond to the scale and significance of environmental effects.
            </p>
            <a
              href="https://www.legislation.govt.nz/act/public/1991/0069/latest/whole.html#DLM242504"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-700 text-sm font-medium mt-2 inline-flex items-center hover:underline"
            >
              View Schedule 4 RMA
              <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>

      <!-- AEE Completion Method (FRD 9.1) -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">How will you provide your AEE?</h3>
        <div class="space-y-3">
          <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
            :class="localData.aee_completion_method === 'inline' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
          >
            <input
              v-model="localData.aee_completion_method"
              type="radio"
              value="inline"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">Complete AEE using form fields below</span>
              <p class="text-xs text-gray-600 mt-1">
                Suitable for most applications - complete the structured questions below
              </p>
            </div>
          </label>

          <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors"
            :class="localData.aee_completion_method === 'upload' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
          >
            <input
              v-model="localData.aee_completion_method"
              type="radio"
              value="upload"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">Upload a prepared AEE document</span>
              <p class="text-xs text-gray-600 mt-1">
                For complex proposals - upload an AEE prepared by a qualified consultant
              </p>
            </div>
          </label>
        </div>
      </div>

      <!-- Upload Method (FRD 9.2) -->
      <div v-if="localData.aee_completion_method === 'upload'" class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Upload AEE Document</h3>
        <p class="text-sm text-gray-600 mb-4">
          Upload a comprehensive AEE document prepared by a qualified expert that addresses all Schedule 4 matters
        </p>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Upload AEE Report *</label>
          <input
            type="file"
            @change="handleAEEDocumentUpload"
            accept=".pdf,.doc,.docx"
            class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
          />
          <p class="mt-1 text-xs text-gray-500">PDF or Word document, max 50MB</p>

          <div v-if="localData.aee_document" class="mt-3 flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span class="text-sm font-medium text-green-900">
              {{ typeof localData.aee_document === 'object' ? localData.aee_document.name : 'Document attached' }}
            </span>
          </div>
        </div>

        <!-- Confirmation Checkbox (FRD 9.3) -->
        <div class="mt-6 border-t border-gray-200 pt-6">
          <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer"
            :class="localData.aee_document_confirmed ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
          >
            <input
              v-model="localData.aee_document_confirmed"
              type="checkbox"
              required
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">I confirm that the uploaded AEE addresses all Schedule 4 matters *</span>
              <p class="text-xs text-gray-600 mt-1">
                The uploaded document must comprehensively address all matters required under Schedule 4 of the RMA
              </p>
            </div>
          </label>
        </div>
      </div>

      <!-- Inline Completion Method (existing fields) -->
      <div v-if="localData.aee_completion_method === 'inline'" class="space-y-8">
        <!-- 1. Activity Description (Schedule 4 clause 2(1)(a)) -->
        <div class="bg-white border border-gray-200 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">1. Description of Activity *</h3>
          <p class="text-sm text-gray-600 mb-4">
            <strong>Schedule 4 clause 2(1)(a):</strong> Description of the activity including its location, design, and how it will be carried out
          </p>
          <textarea
            v-model="localData.aee_activity_description"
            rows="6"
            required
            placeholder="Provide a detailed description of what you're proposing to do, where it will be located, and how it will be undertaken..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
        </div>

        <!-- 2. Existing Environment (Schedule 4 clause 2(1)(b)) -->
        <div class="bg-white border border-gray-200 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">2. Description of Existing Environment *</h3>
          <p class="text-sm text-gray-600 mb-4">
            <strong>Schedule 4 clause 2(1)(b):</strong> Description of the current state of the site and surrounding environment
          </p>
          <textarea
            v-model="localData.aee_existing_environment"
            rows="6"
            required
            placeholder="Describe the site's current characteristics, land use, vegetation, topography, nearby activities, surrounding development..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
        </div>

        <!-- 3. Assessment of Effects (Schedule 4 clause 2(1)(c)) -->
        <div class="bg-white border border-gray-200 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">3. Assessment of Actual and Potential Effects *</h3>
          <p class="text-sm text-gray-600 mb-4">
            <strong>Schedule 4 clause 2(1)(c):</strong> Identify and assess the actual and potential effects on the environment
          </p>

          <div class="space-y-6">
            <!-- Main Assessment -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Overall Effects Assessment *</label>
              <textarea
                v-model="localData.assessment_of_effects"
                rows="10"
                required
                placeholder="Address effects on:
• Physical environment (land, water, air, noise, vibration)
• Ecological environment (vegetation, wildlife, habitats)
• Social and cultural environment (amenity, heritage, iwi values)
• Economic environment
• Cumulative effects
• Risk of natural hazards

Include consideration of:
• Magnitude and scale of effects
• Duration (temporary vs permanent)
• Reversibility
• Mitigation measures proposed"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- Positive Effects -->
            <div class="border-t border-gray-200 pt-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Positive Effects (if any)
              </label>
              <p class="text-xs text-gray-500 mb-3">
                Describe any positive effects the proposal may have (e.g., employment, amenity improvements, environmental enhancements)
              </p>
              <textarea
                v-model="localData.aee_positive_effects"
                rows="4"
                placeholder="Describe positive environmental, social, or economic effects..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- Part 2 RMA Matters (Schedule 4 clause 2(1)(e)) -->
            <div class="border-t border-gray-200 pt-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Part 2 RMA Assessment (s5-s8)
              </label>
              <p class="text-xs text-gray-500 mb-3">
                <strong>Schedule 4 clause 2(1)(e):</strong> Consider sustainable management (s5), matters of national importance (s6), other matters (s7), Treaty of Waitangi (s8)
              </p>
              <textarea
                v-model="localData.aee_part2_assessment"
                rows="6"
                placeholder="Assess how your proposal aligns with Part 2 principles of the RMA..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- Consultation Summary (Schedule 4 clause 2(1)(d)) -->
            <div class="border-t border-gray-200 pt-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Consultation Undertaken
              </label>
              <p class="text-xs text-gray-500 mb-3">
                <strong>Schedule 4 clause 2(1)(d):</strong> Summarize consultation with affected parties, iwi, and other stakeholders
              </p>
              <textarea
                v-model="localData.aee_consultation_summary"
                rows="4"
                placeholder="Describe who you've consulted with, feedback received, and how you've addressed concerns..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
              <p class="text-xs text-gray-500 mt-2">
                Note: Consultation details from Step 5 will be automatically included here
              </p>
            </div>

            <!-- Alternatives Considered (Schedule 4 clause 2(1)(f)) -->
            <div class="border-t border-gray-200 pt-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Alternatives Considered
              </label>
              <p class="text-xs text-gray-500 mb-3">
                <strong>Schedule 4 clause 2(1)(f):</strong> Describe alternative locations or methods considered (if any)
              </p>
              <textarea
                v-model="localData.aee_alternatives_considered"
                rows="4"
                placeholder="Describe any alternative sites, designs, or methods you considered and why you selected the proposed option..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <!-- Monitoring (Schedule 4 clause 2(1)(g)) -->
            <div class="border-t border-gray-200 pt-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Proposed Monitoring (if applicable)
              </label>
              <p class="text-xs text-gray-500 mb-3">
                <strong>Schedule 4 clause 2(1)(g):</strong> Describe any monitoring proposed to measure effects
              </p>
              <textarea
                v-model="localData.aee_monitoring_proposed"
                rows="4"
                placeholder="Describe any environmental monitoring you propose (e.g., water quality, noise levels, ecological surveys)..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Confirmation (FRD 9.3) -->
        <div class="bg-white border border-gray-200 rounded-lg p-6">
          <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer"
            :class="localData.aee_inline_confirmed ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
          >
            <input
              v-model="localData.aee_inline_confirmed"
              type="checkbox"
              required
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">I confirm that I have completed the AEE to the best of my knowledge *</span>
              <p class="text-xs text-gray-600 mt-1">
                This AEE addresses Schedule 4 requirements scaled to the nature and significance of my proposal's effects
              </p>
            </div>
          </label>
        </div>
      </div>

      <!-- Help Section -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Need Help with Your AEE?</h5>
            <p class="text-yellow-800 text-sm mt-1">
              For complex proposals or activities with significant effects, consider engaging a qualified environmental consultant to prepare your AEE.
              The level of detail required depends on the scale and significance of potential environmental effects.
            </p>
            <p class="text-yellow-800 text-sm mt-2">
              <strong>Simple activities</strong> (e.g., minor additions, internal alterations) may only need brief responses.
              <strong>Complex activities</strong> (e.g., subdivisions, significant buildings, discharges) typically require comprehensive assessment.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

// Create a computed property for local data that syncs with parent
const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Set default completion method
if (!localData.value.aee_completion_method) {
  const updatedData = { ...props.modelValue }
  updatedData.aee_completion_method = 'inline'
  emit('update:modelValue', updatedData)
}

// Watch for method change and reset confirmations
watch(() => localData.value.aee_completion_method, (newMethod) => {
  const updatedData = { ...props.modelValue }
  updatedData.aee_inline_confirmed = false
  updatedData.aee_document_confirmed = false
  emit('update:modelValue', updatedData)
})

const handleAEEDocumentUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      alert('File size must be less than 50MB')
      event.target.value = ''
      return
    }

    const updatedData = { ...props.modelValue }
    updatedData.aee_document = file
    emit('update:modelValue', updatedData)
  }
}
</script>
