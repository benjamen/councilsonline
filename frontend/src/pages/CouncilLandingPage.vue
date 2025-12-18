<template>
	<div class="min-h-screen bg-gray-50">
		<!-- Loading State -->
		<div v-if="loading" class="flex items-center justify-center min-h-screen">
			<div class="text-center">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
				<p class="mt-4 text-gray-600">Loading...</p>
			</div>
		</div>

		<!-- Error State -->
		<div v-else-if="error" class="container mx-auto px-4 py-16">
			<div class="bg-red-50 border border-red-200 rounded-lg p-6 max-w-2xl mx-auto">
				<h2 class="text-2xl font-bold text-red-800 mb-2">Council Not Found</h2>
				<p class="text-red-700 mb-4">{{ error }}</p>
				<router-link to="/" class="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
					Return Home
				</router-link>
			</div>
		</div>

		<!-- Landing Page Content -->
		<div v-else>
			<!-- Hero Section -->
			<div
				class="hero-section relative bg-gradient-to-r from-blue-600 to-purple-600 text-white"
				:style="heroBackgroundStyle"
			>
				<div class="absolute inset-0 bg-black bg-opacity-30"></div>
				<div class="container mx-auto px-4 py-20 relative z-10">
					<div class="max-w-4xl mx-auto text-center">
						<img
							v-if="council.logo"
							:src="council.logo"
							:alt="council.council_name"
							class="h-24 mx-auto mb-6 drop-shadow-lg"
						/>
						<h1 class="text-5xl font-bold mb-4">{{ heroTitle }}</h1>
						<p class="text-xl mb-8 opacity-90">{{ landingPage.hero_subtitle }}</p>

						<!-- Not Logged In: Show Login/Register Buttons -->
						<div v-if="!session.isLoggedIn" class="flex flex-col sm:flex-row gap-4 justify-center items-center">
							<router-link
								:to="{ name: 'CouncilLogin', params: { councilCode: route.params.councilCode } }"
								class="inline-block bg-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition shadow-lg"
								:style="ctaButtonStyle"
							>
								Log In
							</router-link>
							<router-link
								:to="{ name: 'CouncilRegister', params: { councilCode: route.params.councilCode } }"
								class="inline-block bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:bg-opacity-10 transition shadow-lg"
							>
								Sign Up
							</router-link>
						</div>

						<!-- Logged In: Show Dashboard and New Application Buttons -->
						<div v-else class="flex flex-col sm:flex-row gap-4 justify-center items-center">
							<router-link
								:to="{ name: 'CouncilDashboard', params: { councilCode: route.params.councilCode } }"
								class="inline-block bg-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition shadow-lg"
								:style="ctaButtonStyle"
							>
								My Requests
							</router-link>
							<router-link
								:to="{ name: 'NewRequest', query: { council: route.params.councilCode, locked: 'true' } }"
								class="inline-block bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:bg-opacity-10 transition shadow-lg"
							>
								{{ landingPage.primary_cta_text || 'New Application' }}
							</router-link>
							<router-link
								:to="{ name: 'CouncilAccount', params: { councilCode: route.params.councilCode } }"
								class="text-sm text-white hover:text-gray-200 underline"
							>
								My Account
							</router-link>
						</div>
					</div>
				</div>
			</div>

			<!-- Introduction Content -->
			<div v-if="landingPage.intro_html" class="container mx-auto px-4 py-12">
				<div class="max-w-4xl mx-auto prose prose-lg" v-html="landingPage.intro_html"></div>
			</div>

			<!-- Request Type Cards -->
			<div v-if="requestTypes.length > 0" class="container mx-auto px-4 py-12">
				<h2 class="text-3xl font-bold text-center mb-8 text-gray-900">Available Services</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					<div
						v-for="rt in requestTypes"
						:key="rt.name"
						class="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-lg transition-shadow p-6"
					>
						<h3 class="text-xl font-semibold mb-2 text-gray-900">{{ rt.name }}</h3>
						<p class="text-sm text-gray-500 mb-3">{{ rt.category }}</p>
						<p v-if="rt.description" class="text-gray-700 mb-4 line-clamp-3">
							{{ rt.description }}
						</p>
						<div class="space-y-1 text-sm text-gray-600 mb-4">
							<div v-if="rt.base_fee" class="flex items-center">
								<span class="font-medium">Base Fee:</span>
								<span class="ml-2">${{ rt.base_fee.toFixed(2) }}</span>
							</div>
							<div v-if="rt.processing_sla_days" class="flex items-center">
								<span class="font-medium">Processing Time:</span>
								<span class="ml-2">{{ rt.processing_sla_days }} days</span>
							</div>
						</div>
						<router-link
							:to="{ name: 'NewRequest', query: { locked: 'true', type: rt.name } }"
							class="inline-block w-full text-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
						>
							Start Application
						</router-link>
					</div>
				</div>
			</div>

			<!-- Features Section -->
			<div class="bg-gray-100 py-16">
				<div class="container mx-auto px-4">
					<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
						<div class="text-center">
							<div class="text-5xl mb-4">⏱️</div>
							<h3 class="text-xl font-semibold mb-2">Fast Processing</h3>
							<p class="text-gray-600">Track your application online 24/7</p>
						</div>
						<div class="text-center">
							<div class="text-5xl mb-4">🛡️</div>
							<h3 class="text-xl font-semibold mb-2">Secure</h3>
							<p class="text-gray-600">Your data is encrypted and protected</p>
						</div>
						<div class="text-center">
							<div class="text-5xl mb-4">✅</div>
							<h3 class="text-xl font-semibold mb-2">Easy to Use</h3>
							<p class="text-gray-600">Step-by-step guidance through the process</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { call } from "frappe-ui"
import { computed, onMounted, ref } from "vue"
import { useRoute } from "vue-router"
import { session } from "../data/session"

const route = useRoute()

const loading = ref(true)
const error = ref(null)
const council = ref({})
const landingPage = ref({})
const requestTypes = ref([])

const heroBackgroundStyle = computed(() => {
	if (landingPage.value.hero_image) {
		return {
			backgroundImage: `url('${landingPage.value.hero_image}')`,
			backgroundSize: "cover",
			backgroundPosition: "center",
		}
	}
	return {}
})

const ctaButtonStyle = computed(() => {
	if (council.value.primary_color) {
		return {
			backgroundColor: "white",
			color: council.value.primary_color,
		}
	}
	return {}
})

const heroTitle = computed(() => {
	const title = landingPage.value.hero_title || ""
	return title.replace("{council_name}", council.value.council_name || "")
})

const loadCouncilData = async () => {
	try {
		const councilCode = route.params.councilCode.toUpperCase()

		// Get council data
		const councilResponse = await call("lodgeick.api.get_council_by_code", {
			council_code: councilCode,
		})

		if (!councilResponse) {
			throw new Error("Council not found")
		}

		council.value = councilResponse

		// Get landing page data
		const landingPageResponse = await call(
			"lodgeick.api.get_council_landing_page",
			{
				council_code: councilCode,
			},
		)

		landingPage.value = landingPageResponse || {
			hero_title: `Welcome to ${council.value.council_name}`,
			hero_subtitle: "Submit planning applications online",
			primary_cta_text: "Start New Request",
			show_request_types: true,
		}

		// Get request types if enabled
		if (landingPage.value.show_request_types) {
			const rtResponse = await call(
				"lodgeick.api.get_request_types_for_council",
				{
					council_code: councilCode,
				},
			)
			requestTypes.value = rtResponse || []
		}

		loading.value = false
	} catch (err) {
		error.value = err.message || "Failed to load council landing page"
		loading.value = false
	}
}

onMounted(() => {
	loadCouncilData()
})
</script>

<style scoped>
.hero-section {
	min-height: 500px;
}

.line-clamp-3 {
	display: -webkit-box;
	-webkit-line-clamp: 3;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.prose {
	max-width: 65ch;
}
</style>
