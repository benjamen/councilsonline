<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-2xl">
      <!-- Progress Indicator -->
      <div v-if="currentStep > 1" class="mb-8">
        <div class="flex items-center justify-center space-x-2 text-sm text-gray-600 mb-4">
          <span class="font-medium">Step {{ currentStep }} of {{ totalSteps }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <div
            v-for="step in totalSteps"
            :key="step"
            class="flex-1 h-2 rounded-full"
            :class="step <= currentStep ? 'bg-blue-600' : 'bg-gray-200'"
          />
        </div>
        <div class="flex items-center justify-center space-x-4 text-xs text-gray-500 mt-2">
          <span v-if="formData.user_role === 'Individual'">
            Account → Role → Contact → Properties → Councils → Complete
          </span>
          <span v-else-if="formData.user_role === 'Agent'">
            Account → Role → Business → Preferences → Clients → Councils → Complete
          </span>
        </div>
      </div>

      <!-- Step Content -->
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <!-- STEP 1: Account Creation -->
        <div v-if="currentStep === 1">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Create Your Account</h2>
          <p class="text-gray-600 mb-8">Get started with Lodgeick</p>

          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700">Full Name *</label>
              <input
                v-model="formData.full_name"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Email Address *</label>
              <input
                v-model="formData.email"
                type="email"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Phone Number *</label>
              <input
                v-model="formData.phone"
                type="tel"
                required
                placeholder="021-123-4567"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
              />
              <p class="mt-1 text-sm text-gray-500">For important application updates</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Password *</label>
              <input
                v-model="formData.password"
                type="password"
                required
                minlength="8"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
              />
              <p class="mt-1 text-sm text-gray-500">At least 8 characters</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Confirm Password *</label>
              <input
                v-model="formData.password_confirm"
                type="password"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div class="flex items-start">
              <input
                v-model="formData.terms_accepted"
                type="checkbox"
                required
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
              />
              <label class="ml-2 block text-sm text-gray-700">
                I agree to the <a href="/terms" class="text-blue-600 hover:text-blue-500">Terms of Service</a> and
                <a href="/privacy" class="text-blue-600 hover:text-blue-500">Privacy Policy</a>
              </label>
            </div>

            <button
              type="button"
              @click="nextStep"
              :disabled="!canProceedStep1"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Account
            </button>

            <p class="text-center text-sm text-gray-600">
              Already have an account?
              <router-link to="/login" class="font-medium text-blue-600 hover:text-blue-500">
                Login
              </router-link>
            </p>
          </div>
        </div>

        <!-- STEP 2: Role Selection -->
        <div v-if="currentStep === 2">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">How will you be using Lodgeick?</h2>
          <p class="text-gray-600 mb-8">Select your primary role</p>

          <div class="space-y-4">
            <div
              @click="formData.user_role = 'Individual'"
              class="cursor-pointer border-2 rounded-lg p-6 transition"
              :class="formData.user_role === 'Individual' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
            >
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div class="ml-4 flex-1">
                  <h3 class="text-lg font-medium text-gray-900">Individual / Property Owner</h3>
                  <p class="mt-1 text-sm text-gray-600">
                    I'm applying for consents for my own properties or representing myself
                  </p>
                </div>
                <div v-if="formData.user_role === 'Individual'" class="flex-shrink-0 ml-4">
                  <svg class="h-6 w-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>

            <div
              @click="formData.user_role = 'Agent'"
              class="cursor-pointer border-2 rounded-lg p-6 transition"
              :class="formData.user_role === 'Agent' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
            >
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div class="ml-4 flex-1">
                  <h3 class="text-lg font-medium text-gray-900">Agent / Consultant</h3>
                  <p class="mt-1 text-sm text-gray-600">
                    I'm submitting applications on behalf of clients or managing multiple properties
                  </p>
                </div>
                <div v-if="formData.user_role === 'Agent'" class="flex-shrink-0 ml-4">
                  <svg class="h-6 w-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <p class="mt-6 text-sm text-gray-500 text-center">
            ℹ️ You can change this later in settings
          </p>

          <div class="mt-8 flex space-x-4">
            <button
              type="button"
              @click="previousStep"
              class="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Previous
            </button>
            <button
              type="button"
              @click="nextStep"
              :disabled="!formData.user_role"
              class="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue
            </button>
          </div>
        </div>

        <!-- STEP 3A: Individual Contact Details -->
        <div v-if="currentStep === 3 && formData.user_role === 'Individual'">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Contact Information</h2>
          <p class="text-gray-600 mb-8">Help us reach you about your applications</p>

          <div class="space-y-6">
            <div class="border-b border-gray-200 pb-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Postal Address (Optional)</h3>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Street Address</label>
                  <input
                    v-model="formData.postal_address.street"
                    type="text"
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Suburb</label>
                    <input
                      v-model="formData.postal_address.suburb"
                      type="text"
                      class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">City</label>
                    <input
                      v-model="formData.postal_address.city"
                      type="text"
                      class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Postcode</label>
                  <input
                    v-model="formData.postal_address.postcode"
                    type="text"
                    class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">Communication Preferences *</h3>
              <p class="text-sm text-gray-600 mb-4">How would you like to receive updates about your applications? (Select at least one)</p>

              <div class="space-y-3">
                <label class="flex items-center">
                  <input
                    v-model="formData.communication_preferences.email"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">
                    Email ({{ formData.email }})
                  </span>
                </label>

                <label class="flex items-center">
                  <input
                    v-model="formData.communication_preferences.phone"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">
                    Phone/SMS ({{ formData.phone }})
                  </span>
                </label>

                <label class="flex items-center">
                  <input
                    v-model="formData.communication_preferences.post"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">
                    Post (to address above)
                  </span>
                </label>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">Invoice Preference *</h3>

              <div class="space-y-2">
                <label class="flex items-center">
                  <input
                    v-model="formData.invoice_preference"
                    type="radio"
                    value="Email"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span class="ml-2 text-sm text-gray-700">Email</span>
                </label>

                <label class="flex items-center">
                  <input
                    v-model="formData.invoice_preference"
                    type="radio"
                    value="Post"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span class="ml-2 text-sm text-gray-700">Post</span>
                </label>
              </div>
            </div>
          </div>

          <div class="mt-8 flex space-x-4">
            <button
              type="button"
              @click="previousStep"
              class="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Previous
            </button>
            <button
              type="button"
              @click="nextStep"
              :disabled="!hasAnyCommunicationPreference"
              class="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue
            </button>
          </div>
        </div>

        <!-- Additional steps would continue here -->
        <!-- For brevity, I'll create separate component files for the remaining steps -->

        <!-- Placeholder for other steps -->
        <div v-if="currentStep > 3">
          <p class="text-center text-gray-600">Step {{ currentStep }} - Work in Progress</p>
          <div class="mt-8 flex space-x-4">
            <button
              type="button"
              @click="previousStep"
              class="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              type="button"
              @click="currentStep === totalSteps ? completeRegistration() : nextStep()"
              class="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              {{ currentStep === totalSteps ? 'Complete Registration' : 'Continue' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const currentStep = ref(1)

const formData = ref({
	// Step 1
	email: "",
	password: "",
	password_confirm: "",
	full_name: "",
	phone: "",
	terms_accepted: false,

	// Step 2
	user_role: "",

	// Step 3A
	postal_address: {
		street: "",
		suburb: "",
		city: "",
		postcode: "",
	},
	communication_preferences: {
		email: true,
		phone: false,
		post: false,
	},
	invoice_preference: "Email",

	// Step 3B (Agent)
	business_details: {
		company_name: "",
		business_type: "",
		company_number: "",
		business_phone: "",
		business_email: "",
	},

	// Step 4A
	properties: [],

	// Step 5A/6
	councils: [],

	// Step 5B (Agent)
	clients: [],
})

const totalSteps = computed(() => {
	return formData.value.user_role === "Agent" ? 7 : 6
})

const canProceedStep1 = computed(() => {
	return (
		formData.value.email &&
		formData.value.password &&
		formData.value.password === formData.value.password_confirm &&
		formData.value.full_name &&
		formData.value.phone &&
		formData.value.terms_accepted
	)
})

const hasAnyCommunicationPreference = computed(() => {
	const prefs = formData.value.communication_preferences
	return prefs.email || prefs.phone || prefs.post
})

const nextStep = () => {
	currentStep.value++
}

const previousStep = () => {
	currentStep.value--
}

const completeRegistration = async () => {
	try {
		const response = await fetch(
			"/api/method/lodgeick.api.complete_registration",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({ data: formData.value }),
			},
		)

		const result = await response.json()

		if (result.message && result.message.success) {
			router.push("/dashboard")
		} else {
			alert("Registration failed. Please try again.")
		}
	} catch (error) {
		console.error("Registration error:", error)
		alert("Registration failed. Please try again.")
	}
}
</script>
