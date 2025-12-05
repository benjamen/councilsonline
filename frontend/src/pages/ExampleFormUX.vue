<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Page Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Enhanced Form UI/UX Demo</h1>
        <p class="text-gray-600">Modern form design with camera integration and better user experience</p>
      </div>

      <!-- Progress Indicator -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
        <div class="flex items-center justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Application Progress</span>
              <span class="text-sm font-bold text-blue-600">{{ progressPercentage }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div
                class="bg-blue-600 h-3 rounded-full transition-all duration-500"
                :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Steps -->
        <div class="grid grid-cols-3 gap-2">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="flex items-center space-x-2"
            :class="currentStep > index ? 'text-green-600' : currentStep === index ? 'text-blue-600' : 'text-gray-400'"
          >
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center border-2"
              :class="currentStep > index ? 'bg-green-100 border-green-600' : currentStep === index ? 'bg-blue-100 border-blue-600' : 'bg-gray-100 border-gray-300'"
            >
              <svg v-if="currentStep > index" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span v-else class="text-sm font-bold">{{ index + 1 }}</span>
            </div>
            <span class="text-sm font-medium hidden md:block">{{ step }}</span>
          </div>
        </div>
      </div>

      <!-- Form Container -->
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Step 1: Personal Information -->
        <div v-if="currentStep === 0">
          <PersonalInfoForm
            v-model="formData.personalInfo"
            :municipality="'Taytay'"
            :province="'Rizal'"
            :barangay-list="barangayList"
            :photo-required="true"
          />
        </div>

        <!-- Step 2: Supporting Documents -->
        <div v-if="currentStep === 1">
          <DocumentsUploadForm
            v-model="formData.documents"
            :document-types="documentTypes"
          />
        </div>

        <!-- Step 3: Review -->
        <div v-if="currentStep === 2">
          <FormSection
            title="Review & Submit"
            subtitle="Please review your information before submitting"
            :required="false"
          >
            <template #icon>
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </template>

            <div class="space-y-6">
              <!-- Personal Info Review -->
              <div>
                <h4 class="text-sm font-semibold text-gray-900 mb-3">Personal Information</h4>
                <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <dt class="text-xs text-gray-500">Full Name</dt>
                    <dd class="text-sm font-medium text-gray-900 mt-1">{{ formData.personalInfo.full_name || 'Not provided' }}</dd>
                  </div>
                  <div>
                    <dt class="text-xs text-gray-500">Date of Birth</dt>
                    <dd class="text-sm font-medium text-gray-900 mt-1">{{ formData.personalInfo.date_of_birth || 'Not provided' }}</dd>
                  </div>
                  <div>
                    <dt class="text-xs text-gray-500">Sex</dt>
                    <dd class="text-sm font-medium text-gray-900 mt-1">{{ formData.personalInfo.sex || 'Not provided' }}</dd>
                  </div>
                  <div>
                    <dt class="text-xs text-gray-500">Civil Status</dt>
                    <dd class="text-sm font-medium text-gray-900 mt-1">{{ formData.personalInfo.civil_status || 'Not provided' }}</dd>
                  </div>
                  <div>
                    <dt class="text-xs text-gray-500">Mobile Number</dt>
                    <dd class="text-sm font-medium text-gray-900 mt-1">{{ formData.personalInfo.mobile_number || 'Not provided' }}</dd>
                  </div>
                  <div>
                    <dt class="text-xs text-gray-500">Email</dt>
                    <dd class="text-sm font-medium text-gray-900 mt-1">{{ formData.personalInfo.email || 'Not provided' }}</dd>
                  </div>
                  <div class="md:col-span-2">
                    <dt class="text-xs text-gray-500">Address</dt>
                    <dd class="text-sm font-medium text-gray-900 mt-1">
                      {{ formatAddress(formData.personalInfo) }}
                    </dd>
                  </div>
                </dl>
              </div>

              <!-- Documents Review -->
              <div>
                <h4 class="text-sm font-semibold text-gray-900 mb-3">Uploaded Documents</h4>
                <div class="space-y-2">
                  <div v-for="(docs, key) in formData.documents" :key="key" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span class="text-sm font-medium text-gray-900">{{ getDocumentLabel(key) }}</span>
                    <span class="text-sm text-gray-600">{{ docs.length }} file(s)</span>
                  </div>
                  <div v-if="Object.keys(formData.documents).length === 0" class="text-center py-4 text-sm text-gray-500">
                    No documents uploaded
                  </div>
                </div>
              </div>

              <!-- Consent -->
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <label class="flex items-start space-x-3 cursor-pointer">
                  <input
                    v-model="formData.consent"
                    type="checkbox"
                    required
                    class="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">I hereby declare that the information provided is true and correct</p>
                    <p class="text-xs text-gray-600 mt-1">
                      I understand that any false information may result in the rejection of this application.
                      I also consent to the processing of my personal data in accordance with the Data Privacy Act.
                    </p>
                  </div>
                </label>
              </div>
            </div>
          </FormSection>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex items-center justify-between pt-6 border-t border-gray-200">
          <button
            v-if="currentStep > 0"
            @click="previousStep"
            type="button"
            class="inline-flex items-center px-6 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Previous
          </button>
          <div v-else></div>

          <button
            v-if="currentStep < steps.length - 1"
            @click="nextStep"
            type="button"
            class="inline-flex items-center px-6 py-3 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Next
            <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            v-else
            type="submit"
            :disabled="!formData.consent"
            class="inline-flex items-center px-8 py-3 border border-transparent rounded-lg text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Submit Application
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PersonalInfoForm from '../components/PersonalInfoForm.vue'
import DocumentsUploadForm from '../components/DocumentsUploadForm.vue'
import FormSection from '../components/FormSection.vue'

const steps = ['Personal Info', 'Documents', 'Review']
const currentStep = ref(0)

const barangayList = [
  'San Juan', 'Dolores', 'San Isidro', 'Muzon', 'Sta. Ana',
  'Bamban', 'Calantipay', 'Mauway', 'Resettlement'
]

const documentTypes = [
  {
    key: 'valid_id',
    label: 'Valid ID',
    description: 'Government-issued identification document',
    examples: ['Philippine ID', 'Driver\'s License', 'Passport', 'Voter\'s ID', 'SSS/GSIS ID'],
    required: true,
    multiple: false,
    accept: 'image/*,.pdf'
  },
  {
    key: 'barangay_certificate',
    label: 'Barangay Certificate of Indigency',
    description: 'Certificate from your barangay confirming indigency status',
    examples: ['Certificate of Indigency', 'Barangay Certification'],
    required: false,
    multiple: false,
    accept: 'image/*,.pdf'
  }
]

const formData = ref({
  personalInfo: {
    full_name: '',
    sex: '',
    civil_status: '',
    date_of_birth: '',
    email: '',
    mobile_number: '',
    street_address: '',
    barangay: '',
    municipality: 'Taytay',
    province: 'Rizal',
    zip_code: '',
    photos: []
  },
  documents: {},
  consent: false
})

const progressPercentage = computed(() => {
  return Math.round(((currentStep.value + 1) / steps.length) * 100)
})

const nextStep = () => {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const formatAddress = (info) => {
  const parts = [
    info.street_address,
    info.barangay,
    info.municipality,
    info.province,
    info.zip_code
  ].filter(Boolean)
  return parts.join(', ') || 'Not provided'
}

const getDocumentLabel = (key) => {
  const doc = documentTypes.find(d => d.key === key)
  return doc ? doc.label : key
}

const handleSubmit = () => {
  console.log('Form submitted:', formData.value)
  alert('Application submitted successfully!\n\nCheck the console for form data.')
}
</script>
