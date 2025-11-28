<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-slate-100 flex items-center justify-center p-4">
    <div class="w-full max-w-4xl">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4 shadow-lg">
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Register Company Account</h1>
        <p class="text-gray-600">Create a company account to manage applications on behalf of your organization</p>
      </div>

      <!-- Progress Steps -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div v-for="(step, index) in steps" :key="index" class="flex-1">
            <div class="flex items-center">
              <!-- Step Circle -->
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
                    'text-xs mt-2 font-medium',
                    currentStep >= index ? 'text-blue-600' : 'text-gray-400'
                  ]"
                >
                  {{ step.label }}
                </span>
              </div>
              <!-- Connector Line -->
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
          <!-- Step 1: Company Details -->
          <div v-show="currentStep === 0" class="space-y-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Company Details</h2>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label for="company_name" class="block text-sm font-medium text-gray-700 mb-2">
                  Company Name <span class="text-red-500">*</span>
                </label>
                <Input
                  id="company_name"
                  v-model="formData.company_name"
                  type="text"
                  required
                  placeholder="ABC Construction Ltd"
                  class="w-full"
                />
              </div>
              <div>
                <label for="legal_name" class="block text-sm font-medium text-gray-700 mb-2">
                  Legal Name <span class="text-red-500">*</span>
                </label>
                <Input
                  id="legal_name"
                  v-model="formData.legal_name"
                  type="text"
                  required
                  placeholder="ABC Construction Limited"
                  class="w-full"
                />
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label for="trading_name" class="block text-sm font-medium text-gray-700 mb-2">
                  Trading Name (Optional)
                </label>
                <Input
                  id="trading_name"
                  v-model="formData.trading_name"
                  type="text"
                  placeholder="ABC Construction"
                  class="w-full"
                />
              </div>
              <div>
                <label for="company_type" class="block text-sm font-medium text-gray-700 mb-2">
                  Company Type <span class="text-red-500">*</span>
                </label>
                <select
                  id="company_type"
                  v-model="formData.company_type"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Limited Liability Company">Limited Liability Company</option>
                  <option value="Sole Trader">Sole Trader</option>
                  <option value="Partnership">Partnership</option>
                  <option value="Trust">Trust</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
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
                />
                <p class="mt-1 text-xs text-gray-500">New Zealand Business Number (13 digits)</p>
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
              <label for="website" class="block text-sm font-medium text-gray-700 mb-2">
                Website (Optional)
              </label>
              <Input
                id="website"
                v-model="formData.website"
                type="url"
                placeholder="https://www.example.co.nz"
                class="w-full"
              />
            </div>
          </div>

          <!-- Step 2: Contact Information -->
          <div v-show="currentStep === 1" class="space-y-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>

            <div>
              <label for="registered_office_address" class="block text-sm font-medium text-gray-700 mb-2">
                Registered Office Address <span class="text-red-500">*</span>
              </label>
              <textarea
                id="registered_office_address"
                v-model="formData.registered_office_address"
                required
                rows="3"
                placeholder="123 Main Street, Auckland 1010"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label for="postal_address" class="block text-sm font-medium text-gray-700 mb-2">
                Postal Address (Optional)
              </label>
              <div class="flex items-center mb-2">
                <input
                  id="same_as_registered"
                  type="checkbox"
                  v-model="sameAsRegistered"
                  @change="togglePostalAddress"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="same_as_registered" class="ml-2 text-sm text-gray-700">
                  Same as registered office address
                </label>
              </div>
              <textarea
                v-if="!sameAsRegistered"
                id="postal_address"
                v-model="formData.postal_address"
                rows="3"
                placeholder="PO Box 123, Auckland 1140"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label for="primary_email" class="block text-sm font-medium text-gray-700 mb-2">
                  Primary Email <span class="text-red-500">*</span>
                </label>
                <Input
                  id="primary_email"
                  v-model="formData.primary_email"
                  type="email"
                  required
                  placeholder="info@example.co.nz"
                  class="w-full"
                />
              </div>
              <div>
                <label for="primary_phone" class="block text-sm font-medium text-gray-700 mb-2">
                  Primary Phone <span class="text-red-500">*</span>
                </label>
                <Input
                  id="primary_phone"
                  v-model="formData.primary_phone"
                  type="tel"
                  required
                  placeholder="+64 9 123 4567"
                  class="w-full"
                />
              </div>
            </div>
          </div>

          <!-- Step 3: Banking & Billing -->
          <div v-show="currentStep === 2" class="space-y-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Banking & Billing (Optional)</h2>
            <p class="text-sm text-gray-600 mb-4">
              Add banking details for faster invoice processing. You can skip this step and add it later.
            </p>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label for="bank_name" class="block text-sm font-medium text-gray-700 mb-2">
                  Bank Name
                </label>
                <Input
                  id="bank_name"
                  v-model="formData.bank_name"
                  type="text"
                  placeholder="ANZ Bank"
                  class="w-full"
                />
              </div>
              <div>
                <label for="bank_account_number" class="block text-sm font-medium text-gray-700 mb-2">
                  Bank Account Number
                </label>
                <Input
                  id="bank_account_number"
                  v-model="formData.bank_account_number"
                  type="text"
                  placeholder="12-3456-7890123-00"
                  class="w-full"
                />
              </div>
            </div>

            <div>
              <label for="billing_contact_name" class="block text-sm font-medium text-gray-700 mb-2">
                Billing Contact Name
              </label>
              <Input
                id="billing_contact_name"
                v-model="formData.billing_contact_name"
                type="text"
                placeholder="John Doe"
                class="w-full"
              />
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label for="billing_contact_email" class="block text-sm font-medium text-gray-700 mb-2">
                  Billing Contact Email
                </label>
                <Input
                  id="billing_contact_email"
                  v-model="formData.billing_contact_email"
                  type="email"
                  placeholder="billing@example.co.nz"
                  class="w-full"
                />
              </div>
              <div>
                <label for="billing_contact_phone" class="block text-sm font-medium text-gray-700 mb-2">
                  Billing Contact Phone
                </label>
                <Input
                  id="billing_contact_phone"
                  v-model="formData.billing_contact_phone"
                  type="tel"
                  placeholder="+64 9 123 4567"
                  class="w-full"
                />
              </div>
            </div>
          </div>

          <!-- Step 4: Admin User Details -->
          <div v-show="currentStep === 3" class="space-y-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Your Details (Admin User)</h2>
            <p class="text-sm text-gray-600 mb-4">
              You will be set up as the first administrator of this company account with full permissions.
            </p>

            <div>
              <label for="user_designation" class="block text-sm font-medium text-gray-700 mb-2">
                Your Designation/Role <span class="text-red-500">*</span>
              </label>
              <Input
                id="user_designation"
                v-model="formData.user_designation"
                type="text"
                required
                placeholder="Director, Manager, CEO, etc."
                class="w-full"
              />
            </div>

            <div>
              <CouncilSelector
                v-model="formData.default_council"
                label="Default Council (Optional)"
                description="Select your preferred council for submitting applications. This can be changed later."
                display-mode="dropdown"
                :required="false"
                :show-clear-button="true"
              />
            </div>

            <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 class="text-sm font-medium text-blue-900 mb-2">Admin Permissions</h3>
              <ul class="text-sm text-blue-800 space-y-1">
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Edit company profile and settings
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Invite and remove users
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Create, edit, and submit applications
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Manage billing and payment information
                </li>
              </ul>
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
                Create Company Account
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
          Want to create an individual account instead?
          <router-link :to="{ name: 'Register' }" class="font-medium text-blue-600 hover:text-blue-700">
            Register as individual
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
import { ref } from "vue"
import { useRouter } from "vue-router"
import { Input, Button } from "frappe-ui"
import CouncilSelector from "../components/CouncilSelector.vue"

const router = useRouter()

const steps = [
  { label: 'Company Details' },
  { label: 'Contact Info' },
  { label: 'Banking' },
  { label: 'Admin User' }
]

const currentStep = ref(0)
const isLoading = ref(false)
const errorMessage = ref('')
const sameAsRegistered = ref(false)

const formData = ref({
  company_name: '',
  legal_name: '',
  trading_name: '',
  company_type: 'Limited Liability Company',
  nzbn: '',
  company_number: '',
  website: '',
  registered_office_address: '',
  postal_address: '',
  primary_email: '',
  primary_phone: '',
  bank_name: '',
  bank_account_number: '',
  billing_contact_name: '',
  billing_contact_email: '',
  billing_contact_phone: '',
  user_designation: '',
  default_council: null
})

function togglePostalAddress() {
  if (sameAsRegistered.value) {
    formData.value.postal_address = formData.value.registered_office_address
  }
}

function nextStep() {
  // Validate current step before proceeding
  if (currentStep.value === 0) {
    if (!formData.value.company_name || !formData.value.legal_name) {
      errorMessage.value = 'Please fill in all required fields'
      return
    }
    // Validate NZBN format if provided
    if (formData.value.nzbn && !/^\d{13}$/.test(formData.value.nzbn)) {
      errorMessage.value = 'NZBN must be 13 digits'
      return
    }
  } else if (currentStep.value === 1) {
    if (!formData.value.registered_office_address || !formData.value.primary_email || !formData.value.primary_phone) {
      errorMessage.value = 'Please fill in all required fields'
      return
    }
  } else if (currentStep.value === 3) {
    if (!formData.value.user_designation) {
      errorMessage.value = 'Please enter your designation/role'
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
  if (!formData.value.user_designation) {
    errorMessage.value = 'Please enter your designation/role'
    return
  }

  errorMessage.value = ''
  isLoading.value = true

  // Prepare company data for API
  const companyData = {
    ...formData.value,
    // If same as registered, copy the address
    postal_address: sameAsRegistered.value ? formData.value.registered_office_address : formData.value.postal_address
  }

  // Call registration API
  fetch('/api/method/lodgeick.api.register_company_account', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token
    },
    body: JSON.stringify({ company_data: companyData })
  })
  .then(response => response.json())
  .then(data => {
    isLoading.value = false

    if (data.message && data.message.success) {
      // Success - redirect to dashboard with success message
      router.push({
        name: 'Dashboard',
        query: { company_registered: 'true' }
      })
    } else if (data.exc || data._server_messages) {
      // Server error
      const serverMessages = data._server_messages ? JSON.parse(data._server_messages) : []
      const errorMsg = serverMessages.length > 0
        ? JSON.parse(serverMessages[0]).message
        : 'Registration failed. Please try again.'
      errorMessage.value = errorMsg
      console.error('Company registration error:', data.exc || data._server_messages)
    } else {
      errorMessage.value = 'Registration failed. Please try again.'
    }
  })
  .catch(error => {
    isLoading.value = false
    errorMessage.value = 'Network error. Please check your connection and try again.'
    console.error('Company registration error:', error)
  })
}
</script>
