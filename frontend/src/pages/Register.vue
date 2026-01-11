<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-slate-100 flex items-center justify-center p-4">
    <div class="w-full max-w-2xl">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4 shadow-lg">
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Create Your Account</h1>
        <p class="text-gray-600">Join thousands using Lodgeick for council requests</p>
      </div>

      <!-- Requester vs Agent Selection -->
      <div class="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 text-center">Choose Account Type</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="p-6 border-2 border-blue-600 bg-blue-50 rounded-lg">
            <div class="text-center">
              <svg class="w-12 h-12 mx-auto mb-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Register as Requester</h3>
              <p class="text-sm text-gray-600 mb-4">Submit requests for yourself or on behalf of an organization</p>
              <div class="text-sm text-blue-900 font-medium">✓ Currently selected</div>
            </div>
          </div>
          <button
            type="button"
            @click="$router.push({ name: 'CompanyRegistration' })"
            class="p-6 border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 rounded-lg transition text-left"
          >
            <div class="text-center">
              <svg class="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Register as Agent</h3>
              <p class="text-sm text-gray-600 mb-4">Consultants or representatives submitting on behalf of clients</p>
              <div class="text-sm text-blue-600 font-medium">Click to register as agent →</div>
            </div>
          </button>
        </div>
      </div>

      <!-- Registration Card -->
      <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <form @submit.prevent="submit" class="space-y-6">
          <!-- Account Type Selection -->
          <AccountTypeSelector v-model="requesterType" />

          <!-- Personal Information -->
          <PersonalInfoFields
            v-model:first-name="formData.first_name"
            v-model:last-name="formData.last_name"
            v-model:email="formData.email"
            v-model:phone="formData.phone"
            :email-error="emailError"
            :phone-error="phoneError"
            @validate-email="validateEmailField"
            @validate-phone="validatePhoneField"
          />

          <!-- Properties Section -->
          <PropertySection
            :requester-type="requesterType"
            :properties="properties"
            @open-add-property="openAddPropertyModal"
            @remove-property="removeProperty"
            @set-default-property="setDefaultProperty"
          />

          <!-- Add Property Modal -->
          <AddPropertyModal
            :show="showAddPropertyModal"
            v-model:property-name="currentProperty.property_name"
            :selected-property-address="selectedAddress"
            v-model:is-default="currentProperty.is_default"
            @close="closeAddPropertyModal"
            @property-address-selected="handleAddressSelected"
            @add-property="addProperty"
          />

          <!-- Company/Organisation/Trust Details -->
          <EntityDetailsFields
            :requester-type="requesterType"
            v-model:organization-name="formData.organization_name"
            v-model:company-number="formData.company_number"
            v-model:trust-name="formData.trust_name"
          />

          <!-- Password -->
          <PasswordFields
            v-model:password="formData.password"
            v-model:confirm-password="formData.confirm_password"
            :password-error="passwordError"
            :confirm-password-error="confirmPasswordError"
            :password-strength="passwordStrength"
            @validate-password="validatePasswordField"
            @validate-password-match="validatePasswordMatch"
          />

          <!-- Terms and Conditions -->
          <TermsCheckbox v-model="formData.terms" />

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-700">{{ errorMessage }}</p>
            </div>
          </div>

          <!-- Submit Button -->
          <Button
            type="submit"
            :loading="isLoading"
            variant="solid"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-base font-medium"
          >
            <template v-if="!isLoading">
              Create Account
            </template>
            <template v-else>
              Creating account...
            </template>
          </Button>
        </form>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-4 bg-white text-gray-500">or</span>
          </div>
        </div>

        <!-- SSO Options -->
        <div class="space-y-3">
          <button
            type="button"
            class="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition"
          >
            <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign up with Google
          </button>
        </div>
      </div>

      <!-- Sign In Link -->
      <div class="text-center mt-6">
        <p class="text-sm text-gray-600">
          Already have an account?
          <router-link :to="{ name: 'Login' }" class="font-medium text-blue-600 hover:text-blue-700">
            Sign in
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
import { Button, Input } from "frappe-ui"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import AddressLookup from "../components/AddressLookup.vue"
import AccountTypeSelector from "../components/register/AccountTypeSelector.vue"
import PersonalInfoFields from "../components/register/PersonalInfoFields.vue"
import PropertySection from "../components/register/PropertySection.vue"
import AddPropertyModal from "../components/company/AddPropertyModal.vue"
import EntityDetailsFields from "../components/register/EntityDetailsFields.vue"
import PasswordFields from "../components/register/PasswordFields.vue"
import TermsCheckbox from "../components/register/TermsCheckbox.vue"
import {
	validateEmail,
	validateNZPhoneNumber,
	validatePassword,
} from "../utils/validation"

const router = useRouter()
const route = useRoute()

const requesterType = ref("Individual")
const selectedAddress = ref(null)
const isLoading = ref(false)
const errorMessage = ref("")

// Form data
const formData = ref({
	first_name: "",
	last_name: "",
	email: "",
	phone: "",
	password: "",
	confirm_password: "",
	organization_name: "",
	company_number: "",
	trust_name: "",
	terms: false,
})

// Validation errors
const phoneError = ref("")
const emailError = ref("")
const passwordError = ref("")
const confirmPasswordError = ref("")
const passwordStrength = ref("")

const passwordStrengthClass = computed(() => {
	if (passwordStrength.value === "strong") return "text-green-600"
	if (passwordStrength.value === "medium") return "text-yellow-600"
	return "text-red-600"
})

// Properties management
const properties = ref([])
const showAddPropertyModal = ref(false)
const currentProperty = ref({
	property_name: "",
	street: "",
	suburb: "",
	city: "",
	postcode: "",
	is_default: false,
})

const openAddPropertyModal = () => {
	currentProperty.value = {
		property_name: "",
		street: "",
		suburb: "",
		city: "",
		postcode: "",
		is_default: properties.value.length === 0, // First property is default
	}
	selectedAddress.value = null
	showAddPropertyModal.value = true
}

const closeAddPropertyModal = () => {
	showAddPropertyModal.value = false
	currentProperty.value = {
		property_name: "",
		street: "",
		suburb: "",
		city: "",
		postcode: "",
		is_default: false,
	}
	selectedAddress.value = null
}

const addProperty = () => {
	if (!currentProperty.value.property_name) {
		alert("Please enter a property name")
		return
	}

	if (!selectedAddress.value) {
		alert("Please select a property address")
		return
	}

	// If this property is set as default, remove default from others
	if (currentProperty.value.is_default) {
		properties.value.forEach((p) => (p.is_default = false))
	}

	properties.value.push({
		property_name: currentProperty.value.property_name,
		street:
			selectedAddress.value.street_address ||
			selectedAddress.value.full_address,
		suburb: selectedAddress.value.suburb || "",
		city: selectedAddress.value.city || "",
		postcode: selectedAddress.value.postcode || "",
		is_default: currentProperty.value.is_default,
	})

	closeAddPropertyModal()
}

const removeProperty = (index) => {
	if (confirm("Are you sure you want to remove this property?")) {
		const wasDefault = properties.value[index].is_default
		properties.value.splice(index, 1)

		// If we removed the default and have other properties, set the first one as default
		if (wasDefault && properties.value.length > 0) {
			properties.value[0].is_default = true
		}
	}
}

const setDefaultProperty = (index) => {
	properties.value.forEach((p, i) => {
		p.is_default = i === index
	})
}

// onMounted removed - no longer needed in single-tenant mode

// Validation functions
const validatePhoneField = () => {
	const validation = validateNZPhoneNumber(formData.value.phone)
	if (!validation.isValid) {
		phoneError.value = validation.message
	} else {
		phoneError.value = ""
		// Auto-format phone number
		formData.value.phone = validation.formatted
	}
	return validation.isValid
}

const validateEmailField = () => {
	const validation = validateEmail(formData.value.email)
	if (!validation.isValid) {
		emailError.value = validation.message
	} else {
		emailError.value = ""
	}
	return validation.isValid
}

const validatePasswordField = () => {
	const validation = validatePassword(formData.value.password)
	if (!validation.isValid) {
		passwordError.value = validation.message
		passwordStrength.value = ""
	} else {
		passwordError.value = ""
		passwordStrength.value = validation.strength
	}
	return validation.isValid
}

const validatePasswordMatch = () => {
	if (formData.value.password !== formData.value.confirm_password) {
		confirmPasswordError.value = "Passwords do not match"
		return false
	}
	confirmPasswordError.value = ""
	return true
}

const handleAddressSelected = (address) => {
	selectedAddress.value = address
}

function submit() {
	// Clear previous errors
	errorMessage.value = ""
	phoneError.value = ""
	emailError.value = ""
	passwordError.value = ""
	confirmPasswordError.value = ""

	// Validate all fields
	const isPhoneValid = validatePhoneField()
	const isEmailValid = validateEmailField()
	const isPasswordValid = validatePasswordField()
	const isPasswordMatch = validatePasswordMatch()

	if (!isPhoneValid || !isEmailValid || !isPasswordValid || !isPasswordMatch) {
		errorMessage.value = "Please correct the errors above before submitting"
		return
	}

	// Validate account-type specific fields
	if (requesterType.value === "Individual" && properties.value.length === 0) {
		errorMessage.value =
			"At least one property is required for individual requesters"
		return
	}

	if (
		(requesterType.value === "Company" ||
			requesterType.value === "Organisation") &&
		!formData.value.organization_name
	) {
		errorMessage.value = `${requesterType.value} name is required`
		return
	}

	if (requesterType.value === "Trust" && !formData.value.trust_name) {
		errorMessage.value = "Trust name is required"
		return
	}

	if (!formData.value.terms) {
		errorMessage.value =
			"You must agree to the Terms of Service and Privacy Policy"
		return
	}

	isLoading.value = true

	// Prepare user data
	const userData = {
		email: formData.value.email,
		first_name: formData.value.first_name,
		last_name: formData.value.last_name,
		phone: formData.value.phone,
		password: formData.value.password,
		user_role: "requester", // This is a requester registration
		applicant_type: requesterType.value, // Individual, Company, Trust, Organisation (entity type)
		properties: properties.value, // Send all properties
	}

	// Add type-specific data
	if (
		requesterType.value === "Company" ||
		requesterType.value === "Organisation"
	) {
		userData.organization_name = formData.value.organization_name
		userData.company_number = formData.value.company_number
	} else if (requesterType.value === "Trust") {
		userData.trust_name = formData.value.trust_name
	}

	// Single-tenant: no council selection needed

	// Call registration API
	fetch("/api/method/lodgeick.api.register_user", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-Frappe-CSRF-Token": window.csrf_token,
		},
		body: JSON.stringify(userData),
	})
		.then((response) => response.json())
		.then((data) => {
			isLoading.value = false

			if (data.message && data.message.success) {
				// Success - redirect to login with success message
				router.push({
					name: "Login",
					query: { registered: "true" },
				})
			} else if (data.exc || data._server_messages) {
				// Server error
				const serverMessages = data._server_messages
					? JSON.parse(data._server_messages)
					: []
				const errorMsg =
					serverMessages.length > 0
						? JSON.parse(serverMessages[0]).message
						: "Registration failed. Please try again."
				errorMessage.value = errorMsg
				console.error("Registration error:", data.exc || data._server_messages)
			} else {
				errorMessage.value = "Registration failed. Please try again."
			}
		})
		.catch((error) => {
			isLoading.value = false
			errorMessage.value =
				"Network error. Please check your connection and try again."
			console.error("Registration error:", error)
		})
}
</script>
