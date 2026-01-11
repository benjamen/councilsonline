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
        <p class="text-gray-600">Consultants or representatives who submit requests on behalf of clients</p>
      </div>

      <!-- Info Banner -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm text-blue-800">
            <p class="font-medium">You are registering as an Agent</p>
            <p class="mt-1">Agents are consultants or representatives who submit requests on behalf of clients. You can be a sole trader or represent a company.</p>
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
          <div v-show="currentStep === 0">
            <AgentPersonalDetailsStep
              v-model:agent-type="formData.agent_type"
              v-model:first-name="formData.first_name"
              v-model:last-name="formData.last_name"
              v-model:email="formData.email"
              v-model:phone="formData.phone"
              v-model:password="formData.password"
              v-model:confirm-password="formData.confirm_password"
              :email-error="emailError"
              :phone-error="phoneError"
              :password-error="passwordError"
              :confirm-password-error="confirmPasswordError"
              :password-strength="passwordStrength"
              @validate-email="validateEmailField"
              @validate-phone="validatePhoneField"
              @validate-password="validatePasswordField"
              @validate-password-match="validatePasswordMatch"
            />
          </div>

          <!-- Step 2: Business Details -->
          <div v-show="currentStep === 1">
            <AgentBusinessDetailsStep
              :agent-type="formData.agent_type"
              v-model:company-name="formData.company_name"
              v-model:company-number="formData.company_number"
              v-model:nzbn="formData.nzbn"
              v-model:trading-name="formData.trading_name"
              :selected-business-address="selectedBusinessAddress"
              :properties="properties"
              :nzbn-error="nzbnError"
              @validate-nzbn="validateNZBNField"
              @business-address-selected="handleBusinessAddressSelected"
              @open-add-property="openAddPropertyModal"
              @remove-property="removeProperty"
              @set-default-property="setDefaultProperty"
            />
          </div>

          <!-- Add Property Modal -->
          <AddPropertyModal
            :show="showAddPropertyModal"
            v-model:property-name="currentProperty.property_name"
            :selected-property-address="selectedPropertyAddress"
            v-model:is-default="currentProperty.is_default"
            @close="closeAddPropertyModal"
            @property-address-selected="handlePropertyAddressSelected"
            @add-property="addProperty"
          />

          <!-- Step 3: Default Settings -->
          <div v-show="currentStep === 2">
            <AgentSettingsStep
              v-model:terms="formData.terms"
            />
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
          Want to register as a requester instead?
          <router-link :to="{ name: 'Register' }" class="font-medium text-blue-600 hover:text-blue-700">
            Register as requester
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
import { computed, ref } from "vue"
import { useRouter } from "vue-router"
import AddressLookup from "../components/AddressLookup.vue"
import AgentPersonalDetailsStep from "../components/company/AgentPersonalDetailsStep.vue"
import AgentBusinessDetailsStep from "../components/company/AgentBusinessDetailsStep.vue"
import AddPropertyModal from "../components/company/AddPropertyModal.vue"
import AgentSettingsStep from "../components/company/AgentSettingsStep.vue"
import {
	validateEmail,
	validateNZBN,
	validateNZPhoneNumber,
	validatePassword,
} from "../utils/validation"

const router = useRouter()

const steps = [
	{ label: "Your Details" },
	{ label: "Business Info" },
	{ label: "Settings" },
]

const currentStep = ref(0)
const isLoading = ref(false)
const errorMessage = ref("")
const selectedBusinessAddress = ref(null)

const formData = ref({
	agent_type: "Sole Trader", // Sole Trader or Company
	first_name: "",
	last_name: "",
	email: "",
	phone: "",
	password: "",
	confirm_password: "",
	company_name: "",
	company_number: "",
	nzbn: "",
	trading_name: "",
	default_council: null,
	terms: false,
})

// Validation errors
const phoneError = ref("")
const emailError = ref("")
const passwordError = ref("")
const confirmPasswordError = ref("")
const nzbnError = ref("")
const passwordStrength = ref("")

const passwordStrengthClass = computed(() => {
	if (passwordStrength.value === "strong") return "text-green-600"
	if (passwordStrength.value === "medium") return "text-yellow-600"
	return "text-red-600"
})

// Properties management
const properties = ref([])
const showAddPropertyModal = ref(false)
const selectedPropertyAddress = ref(null)
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
	selectedPropertyAddress.value = null
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
	selectedPropertyAddress.value = null
}

const addProperty = () => {
	if (!currentProperty.value.property_name) {
		alert("Please enter a property name")
		return
	}

	if (!selectedPropertyAddress.value) {
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
			selectedPropertyAddress.value.street_address ||
			selectedPropertyAddress.value.full_address,
		suburb: selectedPropertyAddress.value.suburb || "",
		city: selectedPropertyAddress.value.city || "",
		postcode: selectedPropertyAddress.value.postcode || "",
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

const handlePropertyAddressSelected = (address) => {
	selectedPropertyAddress.value = address
}

// Validation functions
const validatePhoneField = () => {
	const validation = validateNZPhoneNumber(formData.value.phone)
	if (!validation.isValid) {
		phoneError.value = validation.message
	} else {
		phoneError.value = ""
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

const validateNZBNField = () => {
	const validation = validateNZBN(formData.value.nzbn)
	if (!validation.isValid) {
		nzbnError.value = validation.message
	} else {
		nzbnError.value = ""
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
			errorMessage.value = "Please fill in all required fields"
			return
		}

		if (
			!isPhoneValid ||
			!isEmailValid ||
			!isPasswordValid ||
			!isPasswordMatch
		) {
			errorMessage.value = "Please correct the errors above"
			return
		}
	} else if (currentStep.value === 1) {
		// Validate business details
		if (
			formData.value.agent_type === "Company" &&
			!formData.value.company_name
		) {
			errorMessage.value = "Company name is required"
			return
		}
		if (formData.value.nzbn && !validateNZBNField()) {
			return
		}
	}

	errorMessage.value = ""
	currentStep.value++
}

function previousStep() {
	errorMessage.value = ""
	currentStep.value--
}

function handleSubmit() {
	// Final validation
	if (!formData.value.terms) {
		errorMessage.value =
			"You must agree to the Terms of Service and Privacy Policy"
		return
	}

	errorMessage.value = ""
	isLoading.value = true

	// Prepare agent data for API
	const userData = {
		email: formData.value.email,
		first_name: formData.value.first_name,
		last_name: formData.value.last_name,
		phone: formData.value.phone,
		password: formData.value.password,
		user_role: "agent", // This is an AGENT registration
		agent_type: formData.value.agent_type, // Sole Trader or Company
		properties: properties.value, // Send all properties
	}

	// Add business data
	if (formData.value.agent_type === "Company") {
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
	fetch("/api/method/lodgeick.api.register_agent", {
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
				// Success - redirect to login
				router.push({
					name: "Login",
					query: { registered: "true", type: "agent" },
				})
			} else if (data.exc || data._server_messages) {
				const serverMessages = data._server_messages
					? JSON.parse(data._server_messages)
					: []
				const errorMsg =
					serverMessages.length > 0
						? JSON.parse(serverMessages[0]).message
						: "Registration failed. Please try again."
				errorMessage.value = errorMsg
				console.error(
					"Agent registration error:",
					data.exc || data._server_messages,
				)
			} else {
				errorMessage.value = "Registration failed. Please try again."
			}
		})
		.catch((error) => {
			isLoading.value = false
			errorMessage.value =
				"Network error. Please check your connection and try again."
			console.error("Agent registration error:", error)
		})
}
</script>
