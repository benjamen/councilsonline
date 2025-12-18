<template>
  <div class="space-y-6">
    <FormSection
      title="Supporting Documents"
      subtitle="Upload required identification and supporting documents"
      :required="true"
    >
      <template #icon>
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </template>

      <div class="space-y-6">
        <!-- Document Requirements Info -->
        <div class="bg-blue-50 border-l-4 border-blue-500 rounded-r-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <div>
              <h4 class="text-sm font-semibold text-blue-900">Document Guidelines</h4>
              <ul class="mt-2 text-sm text-blue-800 space-y-1">
                <li>• Clear, readable photos or scanned copies</li>
                <li>• Maximum file size: 20MB per document</li>
                <li>• Accepted formats: JPG, PNG, PDF</li>
                <li>• Use your camera to capture documents directly</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Required Documents List -->
        <div v-for="(docType, index) in documentTypes" :key="index" class="space-y-3">
          <div class="bg-white border-2 border-gray-200 rounded-xl p-5 hover:border-blue-300 transition-colors">
            <!-- Document Type Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <h4 class="text-base font-semibold text-gray-900">{{ docType.label }}</h4>
                  <span v-if="docType.required" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                    Required
                  </span>
                  <span v-else class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                    Optional
                  </span>
                </div>
                <p class="text-sm text-gray-600 mt-1">{{ docType.description }}</p>

                <!-- Examples -->
                <div v-if="docType.examples && docType.examples.length > 0" class="mt-2">
                  <p class="text-xs text-gray-500 font-medium">Examples:</p>
                  <ul class="mt-1 text-xs text-gray-600 space-y-0.5">
                    <li v-for="example in docType.examples" :key="example">• {{ example }}</li>
                  </ul>
                </div>
              </div>

              <!-- Upload Status Indicator -->
              <div v-if="getDocuments(docType.key).length > 0" class="flex-shrink-0 ml-4">
                <div class="flex items-center justify-center w-10 h-10 rounded-full bg-green-100">
                  <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            </div>

            <!-- Upload Component -->
            <CameraUpload
              :model-value="getDocuments(docType.key)"
              @update:model-value="(files) => updateDocuments(docType.key, files)"
              :label="''"
              :help-text="''"
              :required="docType.required"
              :allow-camera="true"
              :multiple="docType.multiple"
              :accept="docType.accept || 'image/*,.pdf'"
              @upload="(file, callback) => handleUpload(docType.key, file, callback)"
            />
          </div>
        </div>

        <!-- Upload Summary -->
        <div class="bg-gradient-to-r from-gray-50 to-blue-50 border-2 border-gray-200 rounded-xl p-6">
          <h4 class="text-sm font-semibold text-gray-900 mb-4">Upload Summary</h4>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Total Documents -->
            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-600">Total Documents</p>
                  <p class="text-2xl font-bold text-gray-900 mt-1">{{ totalDocuments }}</p>
                </div>
                <svg class="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>

            <!-- Required Complete -->
            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-600">Required Complete</p>
                  <p class="text-2xl font-bold mt-1" :class="allRequiredUploaded ? 'text-green-600' : 'text-red-600'">
                    {{ requiredComplete }} / {{ requiredTotal }}
                  </p>
                </div>
                <svg v-if="allRequiredUploaded" class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else class="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>

            <!-- Total Size -->
            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-600">Total Size</p>
                  <p class="text-2xl font-bold text-gray-900 mt-1">{{ totalSize }}</p>
                </div>
                <svg class="w-10 h-10 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Checklist -->
          <div v-if="!allRequiredUploaded" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p class="text-sm font-medium text-yellow-900">Missing Required Documents:</p>
            <ul class="mt-2 text-sm text-yellow-800 space-y-1">
              <li v-for="doc in missingRequired" :key="doc.key">• {{ doc.label }}</li>
            </ul>
          </div>
        </div>
      </div>
    </FormSection>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import CameraUpload from "./CameraUpload.vue"
import FormSection from "./FormSection.vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
	documentTypes: {
		type: Array,
		default: () => [
			{
				key: "valid_id",
				label: "Valid ID",
				description: "Government-issued identification document",
				examples: [
					"Philippine ID",
					"Driver's License",
					"Passport",
					"Voter's ID",
					"SSS/GSIS ID",
				],
				required: true,
				multiple: false,
				accept: "image/*,.pdf",
			},
			{
				key: "barangay_certificate",
				label: "Barangay Certificate of Indigency",
				description:
					"Certificate from your barangay confirming indigency status",
				examples: ["Certificate of Indigency", "Barangay Certification"],
				required: false,
				multiple: false,
				accept: "image/*,.pdf",
			},
			{
				key: "proof_of_residence",
				label: "Proof of Residence",
				description: "Document showing your current address",
				examples: ["Utility Bill", "Barangay Clearance", "Lease Contract"],
				required: false,
				multiple: true,
				accept: "image/*,.pdf",
			},
		],
	},
})

const emit = defineEmits(["update:modelValue"])

// Get documents for a specific type
const getDocuments = (docType) => {
	return props.modelValue[docType] || []
}

// Update documents for a specific type
const updateDocuments = (docType, files) => {
	const updated = { ...props.modelValue, [docType]: files }
	emit("update:modelValue", updated)
}

// Handle upload
const handleUpload = (docType, fileData, callback) => {
	console.log(`Upload ${docType}:`, fileData)
	// Parent component should handle actual upload
	setTimeout(() => {
		callback()
	}, 500)
}

// Computed: Total documents uploaded
const totalDocuments = computed(() => {
	return Object.values(props.modelValue).reduce((total, docs) => {
		return total + (Array.isArray(docs) ? docs.length : 0)
	}, 0)
})

// Computed: Required documents complete
const requiredTotal = computed(() => {
	return props.documentTypes.filter((dt) => dt.required).length
})

const requiredComplete = computed(() => {
	return props.documentTypes.filter((dt) => {
		if (!dt.required) return false
		const docs = getDocuments(dt.key)
		return docs && docs.length > 0
	}).length
})

const allRequiredUploaded = computed(() => {
	return requiredComplete.value === requiredTotal.value
})

// Computed: Missing required documents
const missingRequired = computed(() => {
	return props.documentTypes.filter((dt) => {
		if (!dt.required) return false
		const docs = getDocuments(dt.key)
		return !docs || docs.length === 0
	})
})

// Computed: Total size
const totalSize = computed(() => {
	let totalBytes = 0
	Object.values(props.modelValue).forEach((docs) => {
		if (Array.isArray(docs)) {
			docs.forEach((doc) => {
				totalBytes += doc.size || 0
			})
		}
	})

	const k = 1024
	const sizes = ["Bytes", "KB", "MB", "GB"]
	if (totalBytes === 0) return "0 Bytes"
	const i = Math.floor(Math.log(totalBytes) / Math.log(k))
	return Math.round((totalBytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
})
</script>
