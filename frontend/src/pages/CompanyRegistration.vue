<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-slate-100 flex items-center justify-center p-4">
    <div class="w-full max-w-4xl">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4 shadow-lg">
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Register as Agent</h1>
        <p class="text-gray-600">Planning consultants who assist applicants with resource consent applications</p>
      </div>

      <!-- Info Banner -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm text-blue-800">
            <p class="font-medium">You are registering as an Agent</p>
            <p class="mt-1">Agents are planning consultants who assist applicants with resource consent applications. You can be a sole trader or represent a company.</p>
          </div>
        </div>
      </div>

      <!-- Progress Steps -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div v-for="(step, index) in steps" :key="index" class="flex-1">
            <div class="flex items-center">
              <div class="flex items-center flex-col flex-1">
                <div
                  :class="[
                    'w-10 h-10 rounded-full flex items-center justify-center border-2 transition',
                    currentStep > index
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : currentStep === index
                      ? 'border-blue-600 bg-white text-blue-600'
                      : 'border-gray-300 bg-white text-gray-400'
                  ]"
                >
                  <svg v-if="currentStep > index" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span v-else class="text-sm font-semibold">{{ index + 1 }}</span>
                </div>
                <span
                  :class="[
                    'text-xs mt-2 font-medium text-center',
                    currentStep >= index ? 'text-blue-600' : 'text-gray-400'
                  ]"
                >
                  {{ step.label }}
                </span>
              </div>
              <div
                v-if="index < steps.length - 1"
                :class="[
                  'h-0.5 flex-1 -mt-8',
                  currentStep > index ? 'bg-blue-600' : 'bg-gray-300'
                ]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Registration Card -->
      <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <form @submit.prevent="handleSubmit">
          <!-- Step 1: Agent Type & Personal Details -->
          <div v-show="currentStep === 0" class="space-y-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Agent Type & Your Details</h2>

            <!-- Agent Business Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-3">
                Agent Type <span class="text-red-500">*</span>
              </label>
              <div class="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  @click="formData.agent_type = 'Sole Trader'"
                  :class="[
                    'p-4 border-2 rounded-lg text-center transition',
                    formData.agent_type === 'Sole Trader'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  ]"
                >
                  <svg class="w-8 h-8 mx-auto mb-2" :class="formData.agent_type === 'Sole Trader' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <div class="text-sm font-medium" :class="formData.agent_type === 'Sole Trader' ? 'text-blue-900' : 'text-gray-700'">
                    Sole Trader
                  </div>
                  <div class="text-xs text-gray-500 mt-1">Individual consultant</div>
                </button>
                <button
                  type="button"
                  @click="formData.agent_type = 'Company'"
                  :class="[
                    'p-4 border-2 rounded-lg text-center transition',
                    formData.agent_type === 'Company'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  ]"
                >
                  <svg class="w-8 h-8 mx-auto mb-2" :class="formData.agent_type === 'Company' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <div class="text-sm font-medium" :class="formData.agent_type === 'Company' ? 'text-blue-900' : 'text-gray-700'">
                    Company
                  </div>
                  <div class="text-xs text-gray-500 mt-1">Consulting firm</div>
                </button>
              </div>
            </div>

            <!-- Personal Information -->
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
                  First Name <span class="text-red-500">*</span>
                </label>
                <Input
                  id="first_name"
                  v-model="formData.first_name"
                  type="text"
                  required
                  placeholder="John"
                  class="w-full"
                />
              </div>
              <div>
                <label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
                  Last Name <span class="text-red-500">*</span>
                </label>
                <Input
                  id="last_name"
                  v-model="formData.last_name"
                  type="text"
                  required
                  placeholder="Doe"
                  class="w-full"
                />
              </div>
            </div>

            <!-- Contact Information -->
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                  Email Address <span class="text-red-500">*</span>
                </label>
                <Input
                  id="email"
                  v-model="formData.email"
                  type="email"
                  required
                  placeholder="you@example.com"
                  class="w-full"
                  @blur="validateEmailField"
                />
                <p v-if="emailError" class="mt-1 text-xs text-red-600">{{ emailError }}</p>
              </div>
              <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number <span class="text-red-500">*</span>
                </label>
                <Input
                  id="phone"
                  v-model="formData.phone"
                  type="tel"
                  required
                  placeholder="021 234 5678"
                  class="w-full"
                  @blur="validatePhoneField"
                />
                <p v-if="phoneError" class="mt-1 text-xs text-red-600">{{ phoneError }}</p>
                <p v-else class="mt-1 text-xs text-gray-500">NZ mobile (02x) or landline (03-09)</p>
              </div>
            </div>

            <!-- Password -->
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                  Password <span class="text-red-500">*</span>
                </label>
                <Input
                  id="password"
                  v-model="formData.password"
                  type="password"
                  required
                  placeholder="Min. 8 characters"
                  class="w-full"
                  @input="validatePasswordField"
                />
                <p v-if="passwordError" class="mt-1 text-xs text-red-600">{{ passwordError }}</p>
                <p v-else-if="passwordStrength" class="mt-1 text-xs" :class="passwordStrengthClass">
                  Password strength: {{ passwordStrength }}
                </p>
              </div>
              <div>
                <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password <span class="text-red-500">*</span>
                </label>
                <Input
                  id="confirm_password"
                  v-model="formData.confirm_password"
                  type="password"
                  required
                  placeholder="Repeat password"
                  class="w-full"
                  @blur="validatePasswordMatch"
                />
                <p v-if="confirmPasswordError" class="mt-1 text-xs text-red-600">{{ confirmPasswordError }}</p>
              </div>
            </div>
          </div>

          <!-- Step 2: Business Details (if Company) -->
          <div v-show="currentStep === 1" class="space-y-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">
              {{ formData.agent_type === 'Company' ? 'Company Details' : 'Business Details' }}
            </h2>

            <div v-if="formData.agent_type === 'Company'" class="space-y-4">
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <label for="company_name" class="block text-sm font-medium text-gray-700 mb-2">
                    Company Name <span class="text-red-500">*</span>
                  </label>
                  <Input
                    id="company_name"
                    v-model="formData.company_name"
                    type="text"
                    :required="formData.agent_type === 'Company'"
                    placeholder="ABC Planning Consultants Ltd"
                    class="w-full"
                  />
                </div>
                <div>
                  <label for="company_number" class="block text-sm font-medium text-gray-700 mb-2">
                    Company Number (Optional)
                  </label>
                  <Input
                    id="company_number"
                    v-model="formData.company_number"
                    type="text"
                    placeholder="1234567"
                    class="w-full"
                  />
                </div>
              </div>

              <div>
                <label for="nzbn" class="block text-sm font-medium text-gray-700 mb-2">
                  NZBN (Optional)
                </label>
                <Input
                  id="nzbn"
                  v-model="formData.nzbn"
                  type="text"
                  maxlength="13"
                  placeholder="1234567890123"
                  class="w-full"
                  @blur="validateNZBNField"
                />
                <p v-if="nzbnError" class="mt-1 text-xs text-red-600">{{ nzbnError }}</p>
                <p v-else class="mt-1 text-xs text-gray-500">New Zealand Business Number (13 digits)</p>
              </div>
            </div>

            <div v-else>
              <div>
                <label for="trading_name" class="block text-sm font-medium text-gray-700 mb-2">
                  Trading Name (Optional)
                </label>
                <Input
                  id="trading_name"
                  v-model="formData.trading_name"
                  type="text"
                  placeholder="e.g., Smith Planning Services"
                  class="w-full"
                />
                <p class="mt-1 text-xs text-gray-500">If you trade under a business name</p>
              </div>
            </div>

            <!-- Business Address -->
            <div>
              <AddressLookup
                v-model="selectedBusinessAddress"
                id="business_address"
                label="Business Address"
                placeholder="Start typing your business address..."
                description="Your business/office address"
                :required="false"
                @address-selected="handleBusinessAddressSelected"
              />
            </div>
          </div>

          <!-- Step 3: Default Settings -->
          <div v-show="currentStep === 2" class="space-y-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Default Settings</h2>

            <div>
              <CouncilSelector
                v-model="formData.default_council"
                label="Default Council (Optional)"
                description="Select your primary council for applications. You can work with multiple councils."
                display-mode="dropdown"
                :required="false"
                :show-clear-button="true"
              />
            </div>

            <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 class="text-sm font-medium text-blue-900 mb-2">Agent Permissions</h3>
              <ul class="text-sm text-blue-800 space-y-1">
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Create and submit applications on behalf of clients
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Manage multiple client applications
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Receive notifications on application progress
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Professional dashboard for tracking all applications
                </li>
              </ul>
            </div>

            <!-- Terms and Conditions -->
            <div class="flex items-start">
              <input
                id="terms"
                v-model="formData.terms"
                type="checkbox"
                required
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
              />
              <label for="terms" class="ml-2 block text-sm text-gray-700">
                I agree to the
                <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Terms of Service</a>
                and
                <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Privacy Policy</a>
              </label>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="mt-6 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-700">{{ errorMessage }}</p>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
            <Button
              v-if="currentStep > 0"
              type="button"
              @click="previousStep"
              variant="outline"
              class="px-6 py-2"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </Button>
            <div v-else></div>

            <Button
              v-if="currentStep < steps.length - 1"
              type="button"
              @click="nextStep"
              variant="solid"
              class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2"
            >
              Next
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </Button>
            <Button
              v-else
              type="submit"
              :loading="isLoading"
              variant="solid"
              class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2"
            >
              <template v-if="!isLoading">
                Create Agent Account
              </template>
              <template v-else>
                Creating...
              </template>
            </Button>
          </div>
        </form>
      </div>

      <!-- Back to Register -->
      <div class="text-center mt-6">
        <p class="text-sm text-gray-600">
          Want to register as an applicant instead?
          <router-link :to="{ name: 'Register' }" class="font-medium text-blue-600 hover:text-blue-700">
            Register as applicant
          </router-link>
        </p>
      </div>

      <!-- Back to Home -->
      <div class="text-center mt-4">
        <router-link to="/" class="text-sm text-gray-500 hover:text-gray-700 inline-flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRouter } from "vue-router"
import { Input, Button } from "frappe-ui"
import CouncilSelector from "../components/CouncilSelector.vue"
import AddressLookup from "../components/AddressLookup.vue"
import { validateNZPhoneNumber, validateEmail, validatePassword, validateNZBN } from "../utils/validation"

const router = useRouter()

const steps = [
  { label: 'Your Details' },
  { label: 'Business Info' },
  { label: 'Settings' }
]

const currentStep = ref(0)
const isLoading = ref(false)
const errorMessage = ref('')
const selectedBusinessAddress = ref(null)

const formData = ref({
  agent_type: 'Sole Trader', // Sole Trader or Company
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  password: '',
  confirm_password: '',
  company_name: '',
  company_number: '',
  nzbn: '',
  trading_name: '',
  default_council: null,
  terms: false
})

// Validation errors
const phoneError = ref('')
const emailError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')
const nzbnError = ref('')
const passwordStrength = ref('')

const passwordStrengthClass = computed(() => {
  if (passwordStrength.value === 'strong') return 'text-green-600'
  if (passwordStrength.value === 'medium') return 'text-yellow-600'
  return 'text-red-600'
})

// Validation functions
const validatePhoneField = () => {
  const validation = validateNZPhoneNumber(formData.value.phone)
  if (!validation.isValid) {
    phoneError.value = validation.message
  } else {
    phoneError.value = ''
    formData.value.phone = validation.formatted
  }
  return validation.isValid
}

const validateEmailField = () => {
  const validation = validateEmail(formData.value.email)
  if (!validation.isValid) {
    emailError.value = validation.message
  } else {
    emailError.value = ''
  }
  return validation.isValid
}

const validatePasswordField = () => {
  const validation = validatePassword(formData.value.password)
  if (!validation.isValid) {
    passwordError.value = validation.message
    passwordStrength.value = ''
  } else {
    passwordError.value = ''
    passwordStrength.value = validation.strength
  }
  return validation.isValid
}

const validatePasswordMatch = () => {
  if (formData.value.password !== formData.value.confirm_password) {
    confirmPasswordError.value = 'Passwords do not match'
    return false
  }
  confirmPasswordError.value = ''
  return true
}

const validateNZBNField = () => {
  const validation = validateNZBN(formData.value.nzbn)
  if (!validation.isValid) {
    nzbnError.value = validation.message
  } else {
    nzbnError.value = ''
  }
  return validation.isValid
}

const handleBusinessAddressSelected = (address) => {
  selectedBusinessAddress.value = address
}

function nextStep() {
  // Validate current step before proceeding
  if (currentStep.value === 0) {
    // Validate personal details
    const isPhoneValid = validatePhoneField()
    const isEmailValid = validateEmailField()
    const isPasswordValid = validatePasswordField()
    const isPasswordMatch = validatePasswordMatch()

    if (!formData.value.first_name || !formData.value.last_name) {
      errorMessage.value = 'Please fill in all required fields'
      return
    }

    if (!isPhoneValid || !isEmailValid || !isPasswordValid || !isPasswordMatch) {
      errorMessage.value = 'Please correct the errors above'
      return
    }
  } else if (currentStep.value === 1) {
    // Validate business details
    if (formData.value.agent_type === 'Company' && !formData.value.company_name) {
      errorMessage.value = 'Company name is required'
      return
    }
    if (formData.value.nzbn && !validateNZBNField()) {
      return
    }
  }

  errorMessage.value = ''
  currentStep.value++
}

function previousStep() {
  errorMessage.value = ''
  currentStep.value--
}

function handleSubmit() {
  // Final validation
  if (!formData.value.terms) {
    errorMessage.value = 'You must agree to the Terms of Service and Privacy Policy'
    return
  }

  errorMessage.value = ''
  isLoading.value = true

  // Prepare agent data for API
  const userData = {
    email: formData.value.email,
    first_name: formData.value.first_name,
    last_name: formData.value.last_name,
    phone: formData.value.phone,
    password: formData.value.password,
    user_role: 'agent', // This is an AGENT registration
    agent_type: formData.value.agent_type, // Sole Trader or Company
  }

  // Add business data
  if (formData.value.agent_type === 'Company') {
    userData.company_name = formData.value.company_name
    userData.company_number = formData.value.company_number
    userData.nzbn = formData.value.nzbn
  } else {
    userData.trading_name = formData.value.trading_name
  }

  // Add business address if selected
  if (selectedBusinessAddress.value) {
    userData.business_address = selectedBusinessAddress.value.full_address
    userData.business_street = selectedBusinessAddress.value.street_address
    userData.business_suburb = selectedBusinessAddress.value.suburb
    userData.business_city = selectedBusinessAddress.value.city
    userData.business_postcode = selectedBusinessAddress.value.postcode
  }

  // Add default council if selected
  if (formData.value.default_council) {
    userData.council_code = formData.value.default_council
  }

  // Call registration API
  fetch('/api/method/lodgeick.api.register_agent', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token
    },
    body: JSON.stringify(userData)
  })
  .then(response => response.json())
  .then(data => {
    isLoading.value = false

    if (data.message && data.message.success) {
      // Success - redirect to login
      router.push({
        name: 'Login',
        query: { registered: 'true', type: 'agent' }
      })
    } else if (data.exc || data._server_messages) {
      const serverMessages = data._server_messages ? JSON.parse(data._server_messages) : []
      const errorMsg = serverMessages.length > 0
        ? JSON.parse(serverMessages[0]).message
        : 'Registration failed. Please try again.'
      errorMessage.value = errorMsg
      console.error('Agent registration error:', data.exc || data._server_messages)
    } else {
      errorMessage.value = 'Registration failed. Please try again.'
    }
  })
  .catch(error => {
    isLoading.value = false
    errorMessage.value = 'Network error. Please check your connection and try again.'
    console.error('Agent registration error:', error)
  })
}
</script>
