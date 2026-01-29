<template>
  <div class="min-h-screen bg-gradient-to-br from-brand-light to-slate-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <div v-if="logo" class="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 shadow-lg overflow-hidden">
          <img :src="logo" :alt="displayName" class="w-full h-full object-contain" />
        </div>
        <div v-else class="inline-flex items-center justify-center w-16 h-16 bg-brand rounded-2xl mb-4 shadow-lg">
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Reset Password</h1>
        <p class="text-gray-600">Enter your email address and we'll send you a link to reset your password</p>
      </div>

      <!-- Reset Password Card -->
      <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <!-- Success State -->
        <div v-if="submitted" class="text-center py-4">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Check your email</h3>
          <p class="text-gray-600 mb-6">
            If an account exists for <span class="font-medium">{{ email }}</span>,
            you will receive a password reset link shortly.
          </p>
          <Button @click="resetForm" variant="outline" theme="gray" class="w-full">
            Send another link
          </Button>
        </div>

        <!-- Form State -->
        <form v-else @submit.prevent="handleSubmit" class="space-y-5">
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
              :disabled="loading"
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-700">{{ error }}</p>
            </div>
          </div>

          <!-- Submit Button -->
          <Button
            type="submit"
            :loading="loading"
            variant="solid"
            class="w-full bg-brand hover:bg-brand-hover text-white py-3 text-base font-medium"
          >
            <template v-if="!loading">
              Send Reset Link
            </template>
            <template v-else>
              Sending...
            </template>
          </Button>
        </form>
      </div>

      <!-- Back to Login Link -->
      <div class="text-center mt-6">
        <router-link :to="{ name: 'Login' }" class="text-sm text-gray-600 hover:text-gray-900 inline-flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to sign in
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Input, call } from "frappe-ui"
import { ref, computed } from "vue"
import { useTheme } from "@/composables/useTheme"

const { appName, logo } = useTheme()
const displayName = computed(() => appName.value || "Councils Online")

const email = ref("")
const loading = ref(false)
const error = ref("")
const submitted = ref(false)

async function handleSubmit() {
  if (!email.value) {
    error.value = "Please enter your email address"
    return
  }

  error.value = ""
  loading.value = true

  try {
    // Use Frappe's built-in forgot password API
    await call("frappe.core.doctype.user.user.reset_password", {
      user: email.value
    })
    submitted.value = true
  } catch (err) {
    // Don't reveal if email exists or not for security
    // Always show success message
    submitted.value = true
  } finally {
    loading.value = false
  }
}

function resetForm() {
  email.value = ""
  error.value = ""
  submitted.value = false
}
</script>
