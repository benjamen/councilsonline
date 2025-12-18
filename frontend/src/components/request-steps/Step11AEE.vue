<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Assessment of Environmental Effects (AEE)</h2>
    <p class="text-gray-600 mb-8">Assess the actual and potential effects of your proposal on the environment</p>

    <div class="space-y-8">
      <!-- Info Box -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">Schedule 4 RMA Requirements</h5>
            <p class="text-blue-800 text-sm mt-1">
              Your AEE must address the matters in Schedule 4 of the RMA, scaled to the nature and scale of the proposal.
            </p>
          </div>
        </div>
      </div>

      <!-- 1. Activity Description -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">1. Description of Activity *</h3>
        <p class="text-sm text-gray-600 mb-4">Describe the proposed activity including its location, design, and how it will be carried out</p>
        <textarea
          v-model="localData.aee_activity_description"
          rows="6"
          required
          placeholder="Provide a detailed description of what you're proposing to do, where it will be located, and how it will be undertaken..."
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        ></textarea>
      </div>

      <!-- 2. Existing Environment -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">2. Description of Existing Environment *</h3>
        <p class="text-sm text-gray-600 mb-4">Describe the current state of the site and surrounding environment</p>
        <textarea
          v-model="localData.aee_existing_environment"
          rows="6"
          required
          placeholder="Describe the site's current characteristics, land use, vegetation, topography, nearby activities, surrounding development..."
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        ></textarea>
      </div>

      <!-- 3. Assessment of Effects -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">3. Assessment of Actual and Potential Effects *</h3>
        <p class="text-sm text-gray-600 mb-4">
          Identify and assess the actual and potential effects on the environment, including positive and negative effects, temporary and permanent effects
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

          <!-- Part 2 RMA Matters -->
          <div class="border-t border-gray-200 pt-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Part 2 RMA Assessment (s5-s8)
            </label>
            <p class="text-xs text-gray-500 mb-3">
              Consider: sustainable management (s5), matters of national importance (s6), other matters (s7), Treaty of Waitangi (s8)
            </p>
            <textarea
              v-model="localData.aee_part2_assessment"
              rows="6"
              placeholder="Assess how your proposal aligns with Part 2 principles of the RMA..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <!-- Consultation Summary -->
          <div class="border-t border-gray-200 pt-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Consultation Undertaken
            </label>
            <p class="text-xs text-gray-500 mb-3">
              Summarize consultation with affected parties, iwi, and other stakeholders
            </p>
            <textarea
              v-model="localData.aee_consultation_summary"
              rows="4"
              placeholder="Describe who you've consulted with, feedback received, and how you've addressed concerns..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- 4. AEE Document Upload (Optional) -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">4. AEE Document (Optional)</h3>
        <p class="text-sm text-gray-600 mb-4">
          For complex proposals, you may upload a comprehensive AEE document prepared by a qualified expert
        </p>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Upload AEE Report</label>
          <input
            type="file"
            @change="handleAEEDocumentUpload"
            accept=".pdf,.doc,.docx"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p class="mt-1 text-xs text-gray-500">PDF or Word document, max 50MB</p>

          <div v-if="localData.aee_document" class="mt-3 flex items-center gap-2 text-sm text-green-600">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>{{ typeof localData.aee_document === 'object' ? localData.aee_document.name : 'Document attached' }}</span>
          </div>
        </div>
      </div>

      <!-- Help Section -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Need Help?</h5>
            <p class="text-yellow-800 text-sm mt-1">
              For complex proposals or activities with significant effects, consider engaging a qualified environmental consultant to prepare your AEE.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

// Create a computed property for local data that syncs with parent
const localData = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

const handleAEEDocumentUpload = (event) => {
	const file = event.target.files[0]
	if (file) {
		// Validate file size (50MB max)
		if (file.size > 50 * 1024 * 1024) {
			alert("File size must be less than 50MB")
			event.target.value = ""
			return
		}

		const updatedData = { ...props.modelValue }
		updatedData.aee_document = file
		emit("update:modelValue", updatedData)
	}
}
</script>
