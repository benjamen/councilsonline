<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
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

          <div class="flex items-center space-x-4">
            <!-- Taytay Council Link -->
            <a
              href="https://taytay.gov.ph"
              target="_blank"
              rel="noopener noreferrer"
              class="hidden md:flex items-center space-x-2 text-gray-600 hover:text-brand transition-colors px-3 py-2 rounded-md hover:bg-brand-light"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span class="text-sm font-medium">Taytay Council</span>
              <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>

            <Button @click="goToNewRequest" variant="solid" theme="blue">
              <template #prefix>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </template>
              New Request
            </Button>

            <Dropdown :options="userMenuOptions">
              <template v-slot="{ open }">
                <button
                  class="flex items-center space-x-2 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg p-1"
                  aria-haspopup="true"
                  :aria-expanded="open"
                  aria-label="User menu"
                >
                  <div class="w-8 h-8 bg-brand-light rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-brand" aria-hidden="true">{{ userInitials }}</span>
                  </div>
                  <span class="text-sm font-medium">{{ userName }}</span>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </template>
            </Dropdown>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Welcome back, {{ userName }}!</h2>
        <p class="text-gray-600">Manage your council requests and track their progress</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Requests"
          :value="stats.total"
          icon="file-text"
          color="blue"
        />
        <StatCard
          title="Under Review"
          :value="stats.underReview"
          icon="clock"
          color="yellow"
        />
        <StatCard
          title="Approved"
          :value="stats.approved"
          icon="check-circle"
          color="green"
        />
        <StatCard
          title="Info Requested"
          :value="stats.rfiPending"
          icon="alert-circle"
          color="orange"
        />
      </div>

      <!-- Filters and Search -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <Input
              v-model="searchQuery"
              placeholder="Search by request number or address..."
              type="text"
            >
              <template #prefix>
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </template>
            </Input>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
            <select v-model="filterType" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand focus:border-brand">
              <option value="">All Types</option>
              <option value="Resource Consent">Resource Consent</option>
              <option value="Building Consent">Building Consent</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Requests List -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Your Requests</h3>
        </div>

        <!-- Loading State -->
        <div v-if="requests.loading" class="p-12 text-center" role="status" aria-live="polite">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-brand" aria-hidden="true"></div>
          <p class="mt-4 text-gray-600">Loading applications...</p>
          <span class="sr-only">Loading your applications, please wait</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="!filteredRequests || filteredRequests.length === 0" class="p-12 text-center">
          <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">No applications found</h3>
          <p class="text-gray-500 mb-6">{{ searchQuery ? 'Try adjusting your search or filters' : 'Get started by creating your first application' }}</p>
          <Button @click="goToNewRequest" variant="solid" theme="blue">
            Create New Application
          </Button>
        </div>

        <!-- Mobile Card View -->
        <div v-else class="md:hidden divide-y divide-gray-200">
          <div
            v-for="request in filteredRequests"
            :key="request.name"
            class="p-4 hover:bg-gray-50 cursor-pointer"
            @click="viewRequest(request.name)"
          >
            <div class="flex justify-between items-start mb-2">
              <span class="text-sm font-medium text-brand">{{ request.request_number }}</span>
              <span class="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">{{ request.workflow_state || 'N/A' }}</span>
            </div>
            <p class="text-sm text-gray-900 mb-2 line-clamp-2">{{ request.request_type }}</p>
            <div class="flex justify-between items-center text-xs text-gray-600">
              <span>{{ formatDate(request.creation) }}</span>
              <span>{{ request.working_days_elapsed || 0 }} days</span>
            </div>
          </div>
        </div>

        <!-- Desktop Table View -->
        <div v-else class="hidden md:block overflow-x-auto">
          <table class="w-full" role="table" aria-label="Your requests">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Request #</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Type</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">State</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Submitted</th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider whitespace-nowrap">Days Elapsed</th>
                <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="request in filteredRequests" :key="request.name" class="hover:bg-gray-50 transition cursor-pointer" @click="viewRequest(request.name)">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="text-sm font-medium text-brand">{{ request.request_number }}</div>
                </td>
                <td class="px-4 py-3 max-w-xs">
                  <div class="text-sm text-gray-900 truncate" :title="request.request_type">
                    {{ request.request_type }}
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ request.workflow_state || 'N/A' }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="text-sm text-gray-600">{{ formatDate(request.creation) }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-center">
                  <div class="text-sm font-medium text-gray-900">{{ request.working_days_elapsed || 0 }} days</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    @click.stop="viewRequest(request.name)"
                    class="text-brand hover:text-brand-hover mr-3 focus:outline-none focus:underline"
                    aria-label="View request details"
                  >
                    View
                  </button>
                  <button
                    v-if="request.status === 'Draft'"
                    @click.stop="editRequest(request.name)"
                    class="text-gray-600 hover:text-gray-900 focus:outline-none focus:underline"
                    aria-label="Edit draft request"
                  >
                    Edit
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { Button, Dropdown, Input } from "frappe-ui"
import { computed, ref } from "vue"
import { useRouter } from "vue-router"
import StatCard from "../components/StatCard.vue"
import StatusBadge from "../components/StatusBadge.vue"
import { session } from "../data/session"
import { requestService } from "../services"
import { useTheme } from "@/composables/useTheme"

const router = useRouter()
const { appName, tagline, logo } = useTheme()

const displayName = computed(() => appName.value || "Councils Online")
const displayTagline = computed(() => tagline.value || "Council Request Management")

// User info
const userName = computed(() => {
	const fullName = session.user_info?.full_name || session.user
	return fullName.replace("@", " ").split(".").join(" ")
})

const userInitials = computed(() => {
	const name = userName.value
	const parts = name.split(" ")
	if (parts.length >= 2) {
		return (parts[0][0] + parts[1][0]).toUpperCase()
	}
	return name.substring(0, 2).toUpperCase()
})

// Filters
const searchQuery = ref("")
const filterStatus = ref("")
const filterCouncil = ref("")
const filterType = ref("")

// Get user's requests using service
const requests = requestService.getUserRequests()

// Available councils from requests
const availableCouncils = computed(() => {
	const data = requests.data || []
	const councils = [...new Set(data.map((r) => r.council).filter(Boolean))]
	return councils.sort()
})

// Computed stats
const stats = computed(() => {
	const data = requests.data || []
	return {
		total: data.length,
		underReview: data.filter((r) => r.status === "Under Review").length,
		approved: data.filter((r) => r.status === "Approved").length,
		rfiPending: data.filter((r) => r.status === "RFI Issued").length,
	}
})

// Filtered requests
const filteredRequests = computed(() => {
	let data = requests.data || []

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		data = data.filter(
			(r) =>
				r.request_number?.toLowerCase().includes(query) ||
				r.property_address?.toLowerCase().includes(query) ||
				r.brief_description?.toLowerCase().includes(query),
		)
	}

	// Status filter
	if (filterStatus.value) {
		data = data.filter((r) => r.status === filterStatus.value)
	}

	// Council filter
	if (filterCouncil.value) {
		data = data.filter((r) => r.council === filterCouncil.value)
	}

	// Type filter
	if (filterType.value) {
		data = data.filter((r) => r.request_type?.includes(filterType.value))
	}

	return data
})

// Format date
const formatDate = (dateStr) => {
	if (!dateStr) return "N/A"
	const date = new Date(dateStr)
	return date.toLocaleDateString("en-NZ", {
		year: "numeric",
		month: "short",
		day: "numeric",
	})
}

// Get short council name
const getCouncilShortName = (councilName) => {
	if (!councilName) return "N/A"
	// Extract council code from names like "TAYTAY-PH"
	return councilName.split("-")[0]
}

// Navigation
const goToNewRequest = () => {
	router.push({ name: "NewRequest" })
}

const viewRequest = (requestId) => {
	router.push({ name: "RequestDetail", params: { id: requestId } })
}

const editRequest = (requestId) => {
	router.push({ name: "RequestDetail", params: { id: requestId } })
}

// Navigation
const goToSettings = () => {
	router.push({ name: "Settings" })
}

// User menu options
const userMenuOptions = [
	{
		label: "Settings",
		onClick: goToSettings,
	},
	{
		label: "Sign Out",
		onClick: () => session.logout.submit(),
	},
]
</script>
