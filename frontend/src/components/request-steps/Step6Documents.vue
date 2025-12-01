<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Plans & Documents Upload</h2>
    <p class="text-gray-600 mb-8">Upload all required plans and supporting documents for your application</p>

    <div class="space-y-8">
      <!-- Upload Instructions -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">Document Upload Requirements</h5>
            <p class="text-blue-800 text-sm mt-1">
              Please upload all relevant documents to support your application. Documents should be in PDF format where possible,
              with a maximum file size of 20MB per file. Plans and drawings should be to scale and clearly labelled.
            </p>
          </div>
        </div>
      </div>

      <!-- Record of Title & Legal Documents (FRD 8.1) -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Record of Title, Consent Notices & Easements</h3>
        </div>

        <div class="p-6 space-y-4">
          <p class="text-sm text-gray-600">
            Upload the Certificate(s) of Title for the subject property, including any consent notices, covenants, or easements registered on the title.
          </p>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Upload Record of Title & Legal Documents
            </label>
            <input
              type="file"
              @change="handleFileUpload($event, 'Record of Title')"
              accept=".pdf,.jpg,.jpeg,.png"
              multiple
              class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
            />
            <p class="mt-1 text-xs text-gray-500">Upload CT, consent notices, easements, or covenants (PDF or images, max 20MB each)</p>
          </div>

          <!-- ROT Documents List -->
          <div v-if="getDocumentsByCategory('Record of Title').length > 0" class="mt-4 space-y-2">
            <div
              v-for="(doc, index) in getDocumentsByCategory('Record of Title')"
              :key="index"
              class="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-gray-50"
            >
              <div class="flex items-center gap-3">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ doc.file_name }}</p>
                  <p class="text-xs text-gray-500">{{ doc.file_size }} • {{ doc.category }}</p>
                </div>
              </div>
              <button
                @click="removeDocument(index)"
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
        </div>
      </div>

      <!-- Associated Plans (FRD 8.2) -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Site Plans & Drawings</h3>
        </div>

        <div class="p-6 space-y-4">
          <p class="text-sm text-gray-600">
            Upload site plans, floor plans, elevations, cross-sections, and any other drawings relevant to your proposal.
            Plans should be to scale and clearly show existing and proposed features.
          </p>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Upload Site Plans & Architectural Drawings
            </label>
            <input
              type="file"
              @change="handleFileUpload($event, 'Site Plans')"
              accept=".pdf,.dwg,.jpg,.jpeg,.png"
              multiple
              class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-green-100 file:text-green-700 hover:file:bg-green-200"
            />
            <p class="mt-1 text-xs text-gray-500">Upload plans and drawings (PDF, DWG, or images, max 20MB each)</p>
          </div>

          <!-- Plans List -->
          <div v-if="getDocumentsByCategory('Site Plans').length > 0" class="mt-4 space-y-2">
            <div
              v-for="(doc, index) in getDocumentsByCategory('Site Plans')"
              :key="index"
              class="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-gray-50"
            >
              <div class="flex items-center gap-3">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ doc.file_name }}</p>
                  <p class="text-xs text-gray-500">{{ doc.file_size }} • {{ doc.category }}</p>
                </div>
              </div>
              <button
                @click="removeDocument(getDocumentsByCategory('Site Plans').indexOf(doc))"
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
        </div>
      </div>

      <!-- Supporting Documents (FRD 8.3) -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Supporting Documents</h3>
        </div>

        <div class="p-6 space-y-4">
          <p class="text-sm text-gray-600">
            Upload all supporting documents including specialist reports, written approvals, impact assessments, and any other relevant documentation.
          </p>

          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <p class="text-sm text-yellow-800">
              <strong>Examples of supporting documents:</strong>
            </p>
            <ul class="text-sm text-yellow-800 mt-1 ml-4 list-disc">
              <li>Engineering reports (geotechnical, structural, civil)</li>
              <li>Environmental assessments (traffic, acoustic, landscape, ecological)</li>
              <li>Written approvals from affected parties (s.95E RMA)</li>
              <li>Heritage impact assessments</li>
              <li>Contaminated land reports (PSI/DSI)</li>
              <li>Stormwater management plans</li>
              <li>Correspondence with council or other parties</li>
            </ul>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Upload Supporting Documents
            </label>
            <input
              type="file"
              @change="handleFileUpload($event, 'Supporting Documents')"
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              multiple
              class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-100 file:text-purple-700 hover:file:bg-purple-200"
            />
            <p class="mt-1 text-xs text-gray-500">Upload reports, assessments, and correspondence (PDF, Word, or images, max 20MB each)</p>
          </div>

          <!-- Supporting Documents List -->
          <div v-if="getDocumentsByCategory('Supporting Documents').length > 0" class="mt-4 space-y-2">
            <div
              v-for="(doc, index) in getDocumentsByCategory('Supporting Documents')"
              :key="index"
              class="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-gray-50"
            >
              <div class="flex items-center gap-3">
                <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ doc.file_name }}</p>
                  <p class="text-xs text-gray-500">{{ doc.file_size }} • {{ doc.category }}</p>
                </div>
              </div>
              <button
                @click="removeDocument(getDocumentsByCategory('Supporting Documents').indexOf(doc))"
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
        </div>
      </div>

      <!-- All Documents Summary -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Document Summary</h3>
        </div>

        <div class="p-6">
          <div v-if="localData.application_documents && localData.application_documents.length > 0">
            <div class="grid md:grid-cols-3 gap-4 mb-4">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p class="text-sm text-blue-600 font-medium">Record of Title</p>
                <p class="text-2xl font-bold text-blue-900 mt-1">{{ getDocumentsByCategory('Record of Title').length }}</p>
              </div>
              <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                <p class="text-sm text-green-600 font-medium">Site Plans</p>
                <p class="text-2xl font-bold text-green-900 mt-1">{{ getDocumentsByCategory('Site Plans').length }}</p>
              </div>
              <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <p class="text-sm text-purple-600 font-medium">Supporting Documents</p>
                <p class="text-2xl font-bold text-purple-900 mt-1">{{ getDocumentsByCategory('Supporting Documents').length }}</p>
              </div>
            </div>

            <p class="text-sm text-gray-600">
              <strong>Total: {{ localData.application_documents.length }} document(s)</strong> uploaded
            </p>

            <!-- All Documents Table -->
            <div class="mt-4 overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Document Name</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(doc, index) in localData.application_documents" :key="index">
                    <td class="px-4 py-2 text-sm text-gray-900">{{ doc.file_name }}</td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ doc.category }}</td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ doc.file_size }}</td>
                    <td class="px-4 py-2">
                      <button
                        @click="removeDocument(index)"
                        type="button"
                        class="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p class="mt-2 text-sm text-gray-500">No documents uploaded yet</p>
            <p class="text-sm text-gray-500 mt-1">Use the upload buttons above to add your documents</p>
          </div>
        </div>
      </div>

      <!-- Document Checklist Guidance -->
      <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 class="font-semibold text-gray-900 text-sm mb-2">Document Checklist</h4>
        <div class="space-y-1 text-sm text-gray-700">
          <label class="flex items-start">
            <input type="checkbox" :checked="getDocumentsByCategory('Record of Title').length > 0" disabled class="mt-0.5 h-4 w-4 text-blue-600 border-gray-300 rounded" />
            <span class="ml-2">Certificate of Title (including consent notices, covenants, easements)</span>
          </label>
          <label class="flex items-start">
            <input type="checkbox" :checked="getDocumentsByCategory('Site Plans').length > 0" disabled class="mt-0.5 h-4 w-4 text-blue-600 border-gray-300 rounded" />
            <span class="ml-2">Site plan showing existing and proposed development</span>
          </label>
          <label class="flex items-start">
            <input type="checkbox" :checked="hasWrittenApprovals" disabled class="mt-0.5 h-4 w-4 text-blue-600 border-gray-300 rounded" />
            <span class="ml-2">Written approvals from affected parties (if applicable)</span>
          </label>
          <label class="flex items-start">
            <input type="checkbox" :checked="hasSpecialistReports" disabled class="mt-0.5 h-4 w-4 text-blue-600 border-gray-300 rounded" />
            <span class="ml-2">Specialist reports and assessments (if required)</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Handle file upload
const handleFileUpload = (event, category) => {
  const files = Array.from(event.target.files)
  if (files.length === 0) return

  const updatedData = { ...props.modelValue }
  if (!updatedData.application_documents) {
    updatedData.application_documents = []
  }

  files.forEach(file => {
    // Validate file size (max 20MB)
    const maxSize = 20 * 1024 * 1024
    if (file.size > maxSize) {
      alert(`File ${file.name} exceeds 20MB. Please upload a smaller file.`)
      return
    }

    // Format file size
    const fileSize = formatFileSize(file.size)

    // Add document to array
    updatedData.application_documents.push({
      file_name: file.name,
      category: category,
      file_size: fileSize,
      upload_date: new Date().toISOString()
    })
  })

  emit('update:modelValue', updatedData)

  // Clear the input
  event.target.value = ''
}

// Remove document
const removeDocument = (index) => {
  if (confirm('Remove this document?')) {
    const updatedData = { ...props.modelValue }
    updatedData.application_documents.splice(index, 1)
    emit('update:modelValue', updatedData)
  }
}

// Get documents by category
const getDocumentsByCategory = (category) => {
  return localData.value.application_documents?.filter(doc => doc.category === category) || []
}

// Check if written approvals uploaded
const hasWrittenApprovals = computed(() => {
  return localData.value.application_documents?.some(doc =>
    doc.file_name.toLowerCase().includes('approval') ||
    doc.file_name.toLowerCase().includes('consent')
  ) || false
})

// Check if specialist reports uploaded
const hasSpecialistReports = computed(() => {
  return getDocumentsByCategory('Supporting Documents').length > 0
})

// Format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>
