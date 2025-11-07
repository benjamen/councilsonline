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
                  <p class="text-sm text-gray-600">{{ type.description || 'No description available' }}</p>
                  <div class="mt-4 flex items-center space-x-4 text-xs text-gray-500">
                    <span v-if="type.application_fee">Fee: ${{ type.application_fee }}</span>
                    <span v-if="type.statutory_timeframe">{{ type.statutory_timeframe }} days</span>
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

        <!-- Step 4: Documents -->
        <div v-if="currentStep === 4">
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

        <!-- Step 5: Review & Submit -->
        <div v-if="currentStep === 5">
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
              v-else
              @click="submitApplication"
              variant="solid"
              theme="blue"
              :loading="submitting"
              :disabled="!formData.terms_accepted"
            >
              Submit Application
            </Button>
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
const totalSteps = 5
const savingDraft = ref(false)
const submitting = ref(false)
const uploadedFiles = ref([])
const fileInput = ref(null)

const steps = [
  { title: 'Type', number: 1 },
  { title: 'Property', number: 2 },
  { title: 'Details', number: 3 },
  { title: 'Documents', number: 4 },
  { title: 'Review', number: 5 },
]

// Form data
const formData = ref({
  request_type: '',
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
      return true // Documents are optional, but recommended
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
    // TODO: Implement save draft functionality
    console.log('Saving draft...', formData.value)
    alert('Draft saved successfully!')
  } catch (error) {
    console.error('Error saving draft:', error)
    alert('Failed to save draft')
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
  return type?.application_fee ? `$${type.application_fee}` : 'TBD'
}

const submitApplication = async () => {
  if (!formData.value.terms_accepted) {
    alert('Please accept the terms and conditions')
    return
  }

  submitting.value = true
  try {
    // TODO: Implement actual submission
    console.log('Submitting application...', formData.value)
    console.log('Files:', uploadedFiles.value)

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))

    alert('Application submitted successfully!')
    router.push({ name: 'Dashboard' })
  } catch (error) {
    console.error('Error submitting application:', error)
    alert('Failed to submit application')
  } finally {
    submitting.value = false
  }
}
</script>
