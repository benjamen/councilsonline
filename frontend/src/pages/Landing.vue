<template>
  <div class="min-h-screen bg-gradient-to-br from-brand-light to-slate-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center space-x-3">
            <div v-if="logo" class="w-10 h-10 rounded-lg flex items-center justify-center overflow-hidden">
              <img :src="logo" :alt="displayName" class="w-full h-full object-contain" />
            </div>
            <div v-else class="w-10 h-10 bg-brand rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">{{ displayName }}</h1>
              <p class="text-xs text-gray-500">{{ displayTagline }}</p>
            </div>
          </div>
          <nav class="hidden md:flex items-center space-x-6">
            <a href="#features" class="text-gray-600 hover:text-gray-900 transition">Features</a>
            <a href="#how-it-works" class="text-gray-600 hover:text-gray-900 transition">How it Works</a>
            <a href="#contact" class="text-gray-600 hover:text-gray-900 transition">Contact</a>
            <router-link
              to="/council/taytay-ph"
              class="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors px-3 py-2 rounded-md hover:bg-blue-50"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span class="text-sm font-medium">Taytay Council</span>
            </router-link>
            <Button @click="goToLogin" variant="solid" theme="blue">
              Log In
            </Button>
          </nav>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
      <div class="grid md:grid-cols-2 gap-12 items-center">
        <div>
          <div class="inline-block mb-4 px-3 py-1 bg-brand-light text-brand rounded-full text-sm font-medium">
            Modern Council Request Management
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6 leading-tight">
            Request Council Services
            <span class="text-brand">Online</span>
          </h2>
          <p class="text-xl text-gray-600 mb-8 leading-relaxed">
            {{ displayName }} is a comprehensive platform for ratepayers, civilians, and suppliers to request
            council services digitally. Submit consents, service requests, and applications online.
            Track progress and manage all your council interactions in one place.
          </p>
          <div class="flex flex-col sm:flex-row gap-4">
            <Button @click="goToRegister" size="lg" variant="solid" theme="blue">
              <template #prefix>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </template>
              Create Account
            </Button>
            <Button @click="goToLogin" size="lg" variant="outline" theme="gray">
              <template #prefix>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
              </template>
              Sign In
            </Button>
          </div>

          <!-- Trust Indicators -->
          <div class="mt-12 pt-8 border-t border-gray-200">
            <p class="text-sm text-gray-500 mb-4">Trusted by councils across New Zealand</p>
            <div class="flex items-center space-x-8">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">20+</div>
                <div class="text-xs text-gray-500">Councils</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">10k+</div>
                <div class="text-xs text-gray-500">Applications</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">99.9%</div>
                <div class="text-xs text-gray-500">Uptime</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Hero Image/Illustration -->
        <div class="relative">
          <div class="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
            <div class="space-y-4">
              <div class="flex items-center space-x-3 p-4 bg-green-50 rounded-lg border border-green-200">
                <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="text-sm font-medium text-gray-900">BC-2025-001 Approved</div>
                  <div class="text-xs text-gray-500">Building Consent - New Dwelling</div>
                </div>
              </div>

              <div class="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="text-sm font-medium text-gray-900">RC-2025-042 Under Review</div>
                  <div class="text-xs text-gray-500">15 days remaining</div>
                </div>
              </div>

              <div class="flex items-center space-x-3 p-4 bg-amber-50 rounded-lg border border-amber-200">
                <div class="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="text-sm font-medium text-gray-900">RFI Required</div>
                  <div class="text-xs text-gray-500">Additional information needed</div>
                </div>
              </div>
            </div>

            <div class="mt-6 p-4 bg-gray-50 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs text-gray-600">Processing time</span>
                <span class="text-xs font-medium text-gray-900">12 days average</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-brand h-2 rounded-full" style="width: 60%"></div>
              </div>
            </div>
          </div>

          <!-- Floating badge -->
          <div class="absolute -top-4 -right-4 bg-green-500 text-white px-4 py-2 rounded-full shadow-lg text-sm font-medium">
            ✓ Secure & Compliant
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="bg-white py-16 md:py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h3 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Everything You Need for Council Requests
          </h3>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Streamline your council interactions with powerful tools for ratepayers, civilians, and suppliers
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon="file-text"
            title="Digital Requests"
            description="Submit consents, service requests, and applications online with guided forms and instant validation"
          />
          <FeatureCard
            icon="clock"
            title="Real-time Tracking"
            description="Monitor your request status, processing timeline, and receive instant notifications"
          />
          <FeatureCard
            icon="credit-card"
            title="Secure Payments"
            description="Pay fees and invoices online with credit card or bank transfer, with instant receipt generation"
          />
          <FeatureCard
            icon="message-circle"
            title="Direct Communication"
            description="Communicate directly with council staff, respond to information requests, and manage all correspondence"
          />
          <FeatureCard
            icon="upload-cloud"
            title="Document Management"
            description="Upload plans, quotes, reports, and supporting documents with version control and secure storage"
          />
          <FeatureCard
            icon="shield-check"
            title="Transparent Process"
            description="Clear status updates, statutory timeframes, and automated compliance checks for your requests"
          />
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-16 md:py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h3 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Simple Process, Powerful Results
          </h3>
          <p class="text-xl text-gray-600">Submit your council request in 4 easy steps</p>
        </div>

        <div class="grid md:grid-cols-4 gap-8">
          <ProcessStep
            number="1"
            title="Create Account"
            description="Register for free and set up your profile as a ratepayer, civilian, or supplier"
          />
          <ProcessStep
            number="2"
            title="Submit Request"
            description="Complete the guided form and upload any required documents or quotes"
          />
          <ProcessStep
            number="3"
            title="Track Progress"
            description="Monitor status updates and respond to any council information requests"
          />
          <ProcessStep
            number="4"
            title="Get Result"
            description="Receive your decision, approval, or service completion notification"
          />
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="bg-gradient-to-r from-brand to-brand-dark py-16">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h3 class="text-3xl md:text-4xl font-bold text-white mb-4">
          Ready to Get Started?
        </h3>
        <p class="text-xl text-white/80 mb-8">
          Join thousands of ratepayers and suppliers using {{ displayName }} for faster, easier council service requests
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            @click="goToRegister"
            class="inline-flex items-center justify-center gap-2 h-12 px-6 text-lg font-medium rounded-md transition-colors bg-white text-brand hover:bg-gray-100 focus:outline-none focus-visible:ring focus-visible:ring-white/50"
          >
            Create Free Account
          </button>
          <button
            @click="goToLogin"
            class="inline-flex items-center justify-center gap-2 h-12 px-6 text-lg font-medium rounded-md transition-colors border-2 border-white text-white hover:bg-white/10 focus:outline-none focus-visible:ring focus-visible:ring-white/50"
          >
            Sign In to Existing Account
          </button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer id="contact" class="bg-gray-900 text-gray-300 py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-4 gap-8">
          <div>
            <h4 class="text-white font-bold mb-4">{{ displayName }}</h4>
            <p class="text-sm text-gray-400">
              Modern request management platform connecting ratepayers, civilians, and suppliers with their councils
            </p>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Product</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="#features" class="hover:text-white transition">Features</a></li>
              <li><a href="#how-it-works" class="hover:text-white transition">How it Works</a></li>
              <li><a href="#" class="hover:text-white transition">Pricing</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Support</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="hover:text-white transition">Help Center</a></li>
              <li><a href="#" class="hover:text-white transition">Contact Us</a></li>
              <li><a href="#" class="hover:text-white transition">System Status</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Contact</h4>
            <ul class="space-y-2 text-sm text-gray-400">
              <li>support@councilsonline.com</li>
              <li>0800 COUNCILS</li>
              <li>Wellington, New Zealand</li>
            </ul>
          </div>
        </div>
        <div class="border-t border-gray-800 mt-12 pt-8 text-center text-sm text-gray-500">
          <p>&copy; {{ new Date().getFullYear() }} {{ displayName }}. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { useRouter } from "vue-router"
import { computed } from "vue"
import FeatureCard from "../components/FeatureCard.vue"
import ProcessStep from "../components/ProcessStep.vue"
import { useTheme } from "@/composables/useTheme"

const router = useRouter()
const { appName, tagline, logo, branding } = useTheme()

// Dynamic text based on branding
const displayName = computed(() => appName.value || "Councils Online")
const displayTagline = computed(() => tagline.value || "Council Request Management")

const goToLogin = () => {
	router.push({ name: "Login" })
}

const goToRegister = () => {
	router.push({ name: "Register" })
}
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
