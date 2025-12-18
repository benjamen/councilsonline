<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Natural Hazards Assessment</h2>
    <p class="text-gray-600 mb-8">Identify any natural hazards that may affect the site (RMA s.104 & s.106)</p>

    <div class="space-y-8">
      <!-- Inundation Advice Upload (FRD 4.1) -->
      <div class="border-b border-gray-200 pb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Inundation Advice</h3>
        <p class="text-sm text-gray-600 mb-4">
          If your property is subject to inundation then please attach any advice received from Regional Council regarding inundation and your proposals.
        </p>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Upload Inundation Advice (if applicable)
          </label>
          <input
            type="file"
            @change="handleInundationAdviceUpload"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
          />
          <p v-if="localData.inundation_advice_document" class="text-xs text-green-600 mt-1">
            ✓ Document uploaded: {{ localData.inundation_advice_document }}
          </p>
          <p class="mt-1 text-xs text-gray-500">PDF, Word documents, or images (max 10MB)</p>
        </div>
      </div>

      <!-- Natural Hazards Identification (FRD 4.2) -->
      <div>
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Natural Hazards Identification</h3>

        <div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p class="text-sm text-blue-900 font-medium mb-2">Question:</p>
          <p class="text-sm text-blue-800">
            Would the land, or any structure on the land, for which consent is sought, be or is likely to be subject to any of the following natural hazards listed below:
          </p>
        </div>

        <!-- Conditional importance notice for LUC/SC (FRD 4.3 Guidance) -->
        <div v-if="requiresHazardsAssessment" class="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <h5 class="font-semibold text-amber-900 text-sm">Critical Assessment Required - s.106 RMA</h5>
              <p class="text-amber-800 text-sm mt-1">
                <strong>Important:</strong> Under s.106 RMA, councils <strong>must refuse</strong> Land Use and Subdivision consents if building on land subject to certain natural hazards would:
              </p>
              <ul class="text-amber-800 text-sm mt-2 ml-4 list-disc">
                <li>Accelerate, worsen, or result in material damage</li>
                <li>Create or worsen a natural hazard on the property or other property</li>
              </ul>
              <p class="text-amber-800 text-sm mt-2">
                Please carefully identify all natural hazards affecting the site and detail mitigation measures.
              </p>
            </div>
          </div>
        </div>

        <p class="text-sm text-gray-600 mb-4">
          Under s.104(1)(c) RMA, councils must consider the risk of natural hazards. Identify any hazards that may affect the site.
        </p>

        <!-- "No hazards" confirmation checkbox for LUC/SC -->
        <div v-if="requiresHazardsAssessment && (!localData.natural_hazards || localData.natural_hazards.length === 0)" class="mb-4">
          <label for="no-hazards-confirmation" class="flex items-start p-3 border-2 rounded-lg cursor-pointer bg-white transition-colors"
            :class="localData.no_natural_hazards_confirmed ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
          >
            <input
              id="no-hazards-confirmation"
              v-model="localData.no_natural_hazards_confirmed"
              type="checkbox"
              aria-describedby="no-hazards-description"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">I confirm there are no natural hazards affecting this site</span>
              <p id="no-hazards-description" class="text-xs text-gray-600 mt-1">
                By checking this box, I confirm that I have considered all potential natural hazards (flooding, erosion, landslip, earthquake, tsunami, etc.) and none are applicable to this site.
              </p>
            </div>
          </label>
        </div>

        <!-- Add Hazard Button -->
        <div class="flex justify-between items-center mb-4">
          <p class="text-sm text-gray-700">
            Select hazard types that may affect your site and describe mitigation measures
          </p>
          <button
            @click="addHazard"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Natural Hazard
          </button>
        </div>

        <!-- Hazards List -->
        <div v-if="localData.natural_hazards && localData.natural_hazards.length > 0" class="space-y-4">
          <div
            v-for="(hazard, index) in localData.natural_hazards"
            :key="index"
            class="border border-gray-200 rounded-lg p-4 bg-white shadow-sm"
          >
            <div class="flex justify-between items-start mb-4">
              <h4 class="text-base font-semibold text-gray-900">
                Hazard #{{ index + 1 }}{{ hazard.hazard_type ? ': ' + hazard.hazard_type : '' }}
              </h4>
              <button
                @click="removeHazard(index)"
                type="button"
                class="text-red-600 hover:text-red-800 p-1"
                title="Remove"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Hazard Type *</label>
                <select
                  v-model="hazard.hazard_type"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select hazard type</option>
                  <option value="Earthquake">Earthquake</option>
                  <option value="Sedimentation">Sedimentation</option>
                  <option value="Fire">Fire</option>
                  <option value="Subsidence">Subsidence</option>
                  <option value="Tsunami">Tsunami</option>
                  <option value="Wind">Wind</option>
                  <option value="Erosion">Erosion</option>
                  <option value="Landslip">Landslip</option>
                  <option value="Volcanic">Volcanic & Geothermal</option>
                  <option value="Drought">Drought</option>
                  <option value="Flood">Flood Activity</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Risk Level</label>
                <select
                  v-model="hazard.risk_level"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select risk level</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>

            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Assessment Notes</label>
              <textarea
                v-model="hazard.assessment_notes"
                rows="2"
                placeholder="Describe the nature and extent of the hazard as it relates to this site..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Mitigation Measures</label>
              <textarea
                v-model="hazard.mitigation_measures"
                rows="3"
                placeholder="Describe mitigation measures to address this hazard (design features, engineering solutions, management plans)..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="mt-2 text-sm text-gray-600">No natural hazards identified</p>
          <p class="text-xs text-gray-500 mt-1">Click "Add Natural Hazard" if any hazards may affect the site</p>
        </div>
      </div>

      <!-- Document Upload Display (FRD 4.4) -->
      <div v-if="localData.natural_hazards && localData.natural_hazards.length > 0" class="border-t border-gray-200 pt-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Supporting Documentation</h3>
        <p class="text-sm text-gray-600 mb-4">
          Upload any hazard reports, geotechnical assessments, flood studies, or other documentation supporting your hazard assessment.
        </p>

        <!-- Document table placeholder - will integrate with main document management -->
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p class="text-sm text-gray-600">
            Hazard-related documents can be uploaded in Step 6 (Plans & Documents).
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

const localData = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

// Consent type checks
const hasConsentType = (type) => {
	return (
		props.modelValue.consent_types?.some((ct) => ct.consent_type === type) ||
		false
	)
}

const requiresHazardsAssessment = computed(() => {
	return hasConsentType("Land Use") || hasConsentType("Subdivision")
})

// Watch no_natural_hazards_confirmed
watch(
	() => localData.value.no_natural_hazards_confirmed,
	(newVal) => {
		if (newVal && requiresHazardsAssessment.value) {
			// Clear any hazards if user confirms none
			const updatedData = { ...props.modelValue }
			updatedData.natural_hazards = []
			updatedData.no_natural_hazards_confirmed = true
			emit("update:modelValue", updatedData)
		}
	},
)

// Inundation advice upload
const handleInundationAdviceUpload = (event) => {
	const file = event.target.files[0]
	if (file) {
		// Validate file size (max 10MB)
		const maxSize = 10 * 1024 * 1024 // 10MB in bytes
		if (file.size > maxSize) {
			alert("File size exceeds 10MB. Please upload a smaller file.")
			event.target.value = ""
			return
		}

		// Validate file type
		const allowedTypes = [
			"application/pdf",
			"application/msword",
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
			"image/jpeg",
			"image/png",
			"image/jpg",
		]
		if (!allowedTypes.includes(file.type)) {
			alert("Invalid file type. Please upload a PDF, Word document, or image.")
			event.target.value = ""
			return
		}

		// File upload will be handled by the parent component
		emit("update:modelValue", {
			...props.modelValue,
			inundation_advice_document: file.name,
		})
	}
}

// Hazard management
const addHazard = () => {
	const updatedData = { ...props.modelValue }
	if (!updatedData.natural_hazards) {
		updatedData.natural_hazards = []
	}
	updatedData.natural_hazards.push({
		hazard_type: "",
		risk_level: "",
		assessment_notes: "",
		mitigation_measures: "",
	})

	// Uncheck "no hazards" confirmation when adding a hazard
	updatedData.no_natural_hazards_confirmed = false

	emit("update:modelValue", updatedData)
}

const removeHazard = (index) => {
	if (confirm("Remove this natural hazard?")) {
		const updatedData = { ...props.modelValue }
		updatedData.natural_hazards.splice(index, 1)
		emit("update:modelValue", updatedData)
	}
}
</script>
