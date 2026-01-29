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
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
        <p class="text-gray-600">Sign in to your {{ displayName }} account</p>
      </div>

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
              placeholder="Administrator or you@example.com"
              class="w-full"
            />
          </div>

          <!-- Password Input -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label for="password" class="block text-sm font-medium text-gray-700">
                Password
              </label>
              <router-link
                :to="{ name: 'ForgotPassword' }"
                class="text-sm text-brand hover:text-brand-hover font-medium focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 rounded"
              >
                Forgot password?
              </router-link>
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
              class="h-4 w-4 text-brand focus:ring-brand border-gray-300 rounded"
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
            class="w-full bg-brand hover:bg-brand-hover text-white py-3 text-base font-medium"
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
          <router-link :to="{ name: 'Register' }" class="font-medium text-brand hover:text-brand-hover focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 rounded">
            Create one now
          </router-link>
        </p>
      </div>

      <!-- Back to Home -->
      <div class="text-center mt-4">
        <router-link to="/" class="text-sm text-gray-500 hover:text-gray-700 inline-flex items-center focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 rounded px-1">
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
import { watch, computed } from "vue"
import { useRouter } from "vue-router"
import { session } from "../data/session"
import { useTheme } from "@/composables/useTheme"

const router = useRouter()
const { appName, logo, branding } = useTheme()

const displayName = computed(() => appName.value || "Councils Online")

function submit(e) {
	const formData = new FormData(e.target)
	session.login.submit({
		email: formData.get("email"),
		password: formData.get("password"),
	})
}

// Watch for successful login and redirect
watch(
	() => session.isLoggedIn,
	(isLoggedIn) => {
		if (isLoggedIn) {
			router.push({ name: "Dashboard" })
		}
	},
)
</script>
