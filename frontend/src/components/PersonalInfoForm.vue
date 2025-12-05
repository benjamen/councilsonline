<template>
  <div class="space-y-6">
    <!-- Photo Upload Section -->
    <FormSection
      title="Profile Photo"
      subtitle="Upload a recent photo for identification"
      :required="photoRequired"
    >
      <template #icon>
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </template>

      <CameraUpload
        v-model="formData.photos"
        label="Photo"
        helpText="Take a photo or upload a recent picture"
        :required="photoRequired"
        :allow-camera="true"
        :multiple="false"
        accept="image/*"
        @upload="handlePhotoUpload"
      />
    </FormSection>

    <!-- Personal Information Section -->
    <FormSection
      title="Personal Information"
      subtitle="Basic details about yourself"
      :required="true"
    >
      <template #icon>
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </template>

      <div class="space-y-5">
        <!-- Full Name -->
        <div>
          <label class="block text-sm font-semibold text-gray-900 mb-2">
            Full Name <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.full_name"
            type="text"
            placeholder="Juan Santos Dela Cruz"
            class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            required
          />
          <p class="mt-1.5 text-xs text-gray-500 flex items-center">
            <svg class="w-3.5 h-3.5 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            Enter your complete name as it appears on your ID
          </p>
        </div>

        <!-- Personal Details Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Sex -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              Sex <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.sex"
              class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all appearance-none bg-white"
              required
            >
              <option value="">Select</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>

          <!-- Civil Status -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              Civil Status <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.civil_status"
              class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all appearance-none bg-white"
              required
            >
              <option value="">Select</option>
              <option value="Single">Single</option>
              <option value="Married">Married</option>
              <option value="Widowed">Widowed</option>
              <option value="Separated">Separated</option>
              <option value="Divorced">Divorced</option>
            </select>
          </div>

          <!-- Date of Birth -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              Date of Birth <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.date_of_birth"
              type="date"
              class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
              :max="maxDate"
              required
            />
            <p v-if="age" class="mt-1.5 text-xs text-gray-500">Age: {{ age }} years old</p>
          </div>
        </div>
      </div>
    </FormSection>

    <!-- Contact Information Section -->
    <FormSection
      title="Contact Information"
      subtitle="How we can reach you"
      :required="true"
    >
      <template #icon>
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </template>

      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Email Address -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              Email Address
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <input
                v-model="formData.email"
                type="email"
                placeholder="juan.delacruz@example.com"
                class="w-full pl-10 pr-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
              />
            </div>
            <p class="mt-1.5 text-xs text-gray-500">Optional - for email notifications</p>
          </div>

          <!-- Mobile Number -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              Mobile Number <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <input
                v-model="formData.mobile_number"
                type="tel"
                placeholder="09XX XXX XXXX"
                class="w-full pl-10 pr-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                pattern="[0-9]{11}"
                required
              />
            </div>
            <p class="mt-1.5 text-xs text-gray-500">11-digit mobile number (e.g., 09171234567)</p>
          </div>
        </div>
      </div>
    </FormSection>

    <!-- Residential Address Section -->
    <FormSection
      title="Residential Address"
      subtitle="Your current place of residence"
      :required="true"
    >
      <template #icon>
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      </template>

      <div class="space-y-4">
        <!-- Street Address -->
        <div>
          <label class="block text-sm font-semibold text-gray-900 mb-2">
            Street / House Number <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.street_address"
            type="text"
            placeholder="123 Mabini Street, Sitio Maligaya"
            class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            required
          />
        </div>

        <!-- Location Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Barangay -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              Barangay <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.barangay"
              class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all appearance-none bg-white"
              required
            >
              <option value="">Select Barangay</option>
              <option v-for="brgy in barangayList" :key="brgy" :value="brgy">{{ brgy }}</option>
            </select>
          </div>

          <!-- Municipality -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              Municipality <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.municipality"
              type="text"
              readonly
              class="w-full px-4 py-3 text-base border-2 border-gray-200 rounded-lg bg-gray-50 text-gray-700"
            />
          </div>

          <!-- Province -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              Province <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.province"
              type="text"
              readonly
              class="w-full px-4 py-3 text-base border-2 border-gray-200 rounded-lg bg-gray-50 text-gray-700"
            />
          </div>

          <!-- ZIP Code -->
          <div>
            <label class="block text-sm font-semibold text-gray-900 mb-2">
              ZIP Code
            </label>
            <input
              v-model="formData.zip_code"
              type="text"
              placeholder="1920"
              pattern="[0-9]{4}"
              class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            />
          </div>
        </div>
      </div>
    </FormSection>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import FormSection from './FormSection.vue'
import CameraUpload from './CameraUpload.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  municipality: {
    type: String,
    default: 'Taytay'
  },
  province: {
    type: String,
    default: 'Rizal'
  },
  barangayList: {
    type: Array,
    default: () => [
      'San Juan', 'Dolores', 'San Isidro', 'Muzon', 'Sta. Ana',
      'Bamban', 'Calantipay', 'Mauway', 'Resettlement'
    ]
  },
  photoRequired: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const formData = computed({
  get: () => ({
    ...props.modelValue,
    municipality: props.municipality,
    province: props.province,
    photos: props.modelValue.photos || []
  }),
  set: (value) => emit('update:modelValue', value)
})

// Computed: Age from date of birth
const age = computed(() => {
  if (!formData.value.date_of_birth) return null
  const today = new Date()
  const birthDate = new Date(formData.value.date_of_birth)
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
})

// Computed: Max date (today)
const maxDate = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Handle photo upload
const handlePhotoUpload = (fileData, callback) => {
  // Parent component should handle actual upload to server
  console.log('Photo upload:', fileData)

  // Simulate upload completion
  setTimeout(() => {
    callback()
  }, 500)
}

// Watch for changes and emit
watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })
</script>
