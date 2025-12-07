<template>
  <div
    class="min-h-screen flex items-center justify-center p-4"
    :style="backgroundStyle"
  >
    <div class="w-full max-w-md">
      <!-- Council Logo & Header -->
      <div class="text-center mb-8">
        <div v-if="councilSettings?.logo" class="mb-4">
          <img
            :src="councilSettings.logo"
            :alt="councilSettings.council_name"
            class="h-20 mx-auto object-contain"
          />
        </div>
        <div v-else class="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 shadow-lg" :style="{ backgroundColor: primaryColor }">
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Reset Password</h1>
        <p class="text-gray-600">Enter your email to receive reset instructions</p>
      </div>

      <!-- Reset Password Card -->
      <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <!-- Success State -->
        <div v-if="emailSent" class="text-center">
          <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" :style="{ backgroundColor: `${primaryColor}20` }">
            <svg class="w-8 h-8" :style="{ color: primaryColor }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Check your email</h3>
          <p class="text-gray-600 mb-6">
            We've sent password reset instructions to <strong>{{ email }}</strong>
          </p>
          <p class="text-sm text-gray-500 mb-6">
            Didn't receive the email? Check your spam folder or try again.
          </p>
          <button
            @click="resetForm"
            class="text-sm hover:opacity-80"
            :style="{ color: primaryColor }"
          >
            Try different email
          </button>
        </div>

        <!-- Form State -->
        <form v-else @submit.prevent="submit" class="space-y-5">
          <!-- Email Input -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <Input
              id="email"
              v-model="email"
              type="email"
              required
              placeholder="you@example.com"
              class="w-full"
              :disabled="isLoading"
            />
          </div>

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
            class="w-full text-white py-3 text-base font-medium"
            :style="{ backgroundColor: primaryColor, borderColor: primaryColor }"
          >
            <template v-if="!isLoading">
              Send Reset Link
            </template>
            <template v-else>
              Sending...
            </template>
          </Button>
        </form>
      </div>

      <!-- Back to Login -->
      <div class="text-center mt-6">
        <router-link
          :to="{ name: 'CouncilLogin', params: { councilCode } }"
          class="text-sm text-gray-600 hover:text-gray-900 inline-flex items-center"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to login
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { Input, Button, call } from "frappe-ui"
import { useCouncilStore } from "../stores/councilStore"

const route = useRoute()
const councilStore = useCouncilStore()

const councilCode = computed(() => route.params.councilCode?.toUpperCase())
const councilSettings = ref(null)
const email = ref('')
const isLoading = ref(false)
const emailSent = ref(false)
const errorMessage = ref('')

// Load council settings on mount
onMounted(async () => {
  try {
    councilSettings.value = await councilStore.getCouncilSettings(councilCode.value)
  } catch (error) {
    console.error('Failed to load council settings:', error)
  }
})

// Computed styles based on council branding
const primaryColor = computed(() => councilSettings.value?.primary_color || '#2563eb')
const secondaryColor = computed(() => councilSettings.value?.secondary_color || '#64748b')

const backgroundStyle = computed(() => {
  const color = primaryColor.value
  return {
    background: `linear-gradient(to bottom right, ${color}15, ${secondaryColor.value}15)`
  }
})

async function submit() {
  errorMessage.value = ''
  isLoading.value = true

  try {
    await call('frappe.core.doctype.user.user.reset_password', {
      user: email.value
    })
    emailSent.value = true
  } catch (error) {
    console.error('Password reset error:', error)
    errorMessage.value = error.message || 'Failed to send reset email. Please try again.'
  } finally {
    isLoading.value = false
  }
}

function resetForm() {
  emailSent.value = false
  email.value = ''
  errorMessage.value = ''
}
</script>
