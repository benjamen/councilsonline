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
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
        <p class="text-gray-600">Sign in to {{ councilSettings?.council_name || 'Council' }} portal</p>
      </div>

      <!-- Custom HTML Content -->
      <div
        v-if="councilSettings?.login_page_custom_html"
        class="mb-6 prose prose-sm max-w-none bg-white rounded-lg p-4 shadow-sm"
        v-html="councilSettings.login_page_custom_html"
      />

      <!-- Login Card -->
      <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <form @submit.prevent="submit" class="space-y-5">
          <!-- Email/Username Input -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email or Username
            </label>
            <Input
              id="email"
              name="email"
              type="text"
              required
              placeholder="you@example.com"
              class="w-full"
            />
          </div>

          <!-- Password Input -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label for="password" class="block text-sm font-medium text-gray-700">
                Password
              </label>
              <a href="#" class="text-sm font-medium hover:opacity-80" :style="{ color: primaryColor }">
                Forgot password?
              </a>
            </div>
            <Input
              id="password"
              name="password"
              type="password"
              required
              placeholder="Enter your password"
              class="w-full"
            />
          </div>

          <!-- Remember Me -->
          <div class="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              class="h-4 w-4 border-gray-300 rounded"
              :style="{ accentColor: primaryColor }"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-700">
              Remember me for 30 days
            </label>
          </div>

          <!-- Error Message -->
          <div v-if="session.login.error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-700">{{ session.login.error }}</p>
            </div>
          </div>

          <!-- Submit Button -->
          <Button
            type="submit"
            :loading="session.login.loading"
            variant="solid"
            class="w-full text-white py-3 text-base font-medium"
            :style="{ backgroundColor: primaryColor, borderColor: primaryColor }"
          >
            <template v-if="!session.login.loading">
              Sign In
            </template>
            <template v-else>
              Signing in...
            </template>
          </Button>
        </form>
      </div>

      <!-- Sign Up Link -->
      <div class="text-center mt-6">
        <p class="text-sm text-gray-600">
          Don't have an account?
          <router-link
            :to="{ name: 'CouncilRegister', params: { councilCode } }"
            class="font-medium hover:opacity-80"
            :style="{ color: primaryColor }"
          >
            Create one now
          </router-link>
        </p>
      </div>

      <!-- Back to Council Landing -->
      <div class="text-center mt-4">
        <router-link
          :to="{ name: 'CouncilLanding', params: { councilCode } }"
          class="text-sm text-gray-500 hover:text-gray-700 inline-flex items-center"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to {{ councilSettings?.council_name || 'Council' }} home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { Input, Button } from "frappe-ui"
import { session } from "../data/session"
import { useCouncilStore } from "../stores/councilStore"

const route = useRoute()
const councilStore = useCouncilStore()

const councilCode = computed(() => route.params.councilCode?.toUpperCase())
const councilSettings = ref(null)
const isLoading = ref(true)

// Load council settings on mount
onMounted(async () => {
  try {
    councilSettings.value = await councilStore.getCouncilSettings(councilCode.value)
  } catch (error) {
    console.error('Failed to load council settings:', error)
  } finally {
    isLoading.value = false
  }
})

// Computed styles based on council branding
const primaryColor = computed(() => councilSettings.value?.primary_color || '#2563eb')
const secondaryColor = computed(() => councilSettings.value?.secondary_color || '#64748b')

const backgroundStyle = computed(() => {
  const color = primaryColor.value
  // Create a light gradient based on primary color
  return {
    background: `linear-gradient(to bottom right, ${color}15, ${secondaryColor.value}15)`
  }
})

function submit(e) {
  const formData = new FormData(e.target)
  session.login.submit({
    email: formData.get("email"),
    password: formData.get("password"),
  })
}
</script>
