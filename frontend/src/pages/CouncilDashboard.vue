<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Council-branded Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-3">
            <!-- Council Logo -->
            <div v-if="councilSettings?.logo" class="h-10">
              <img :src="councilSettings.logo" :alt="councilSettings.council_name" class="h-full object-contain" />
            </div>
            <div v-else class="w-10 h-10 rounded-lg flex items-center justify-center" :style="{ backgroundColor: primaryColor }">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">{{ councilSettings?.council_name || councilCode }}</h1>
              <p class="text-xs text-gray-500">Application Portal</p>
            </div>
          </div>

          <div class="flex items-center space-x-4">
            <!-- Switch Council Button (if allowed) -->
            <button
              v-if="councilSettings?.show_council_switcher"
              @click="router.push({ name: 'Dashboard' })"
              class="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              Switch Council
            </button>

            <Button @click="goToNewRequest" variant="solid" :style="{ backgroundColor: primaryColor, borderColor: primaryColor }">
              <template #prefix>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </template>
              New Application
            </Button>

            <Dropdown :options="userMenuOptions">
              <template v-slot="{ open }">
                <button class="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center" :style="{ backgroundColor: `${primaryColor}20`, color: primaryColor }">
                    <span class="text-sm font-medium">{{ userInitials }}</span>
                  </div>
                  <span class="text-sm font-medium">{{ userName }}</span>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
        <p class="text-gray-600">Manage your {{ councilSettings?.council_name || councilCode }} applications and track their progress</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div
          v-for="stat in statsArray"
          :key="stat.title"
          class="bg-white rounded-lg shadow-sm border p-6"
          :style="{ borderTopColor: primaryColor, borderTopWidth: '4px' }"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">{{ stat.title }}</p>
              <p class="text-3xl font-bold mt-2" :style="{ color: primaryColor }">{{ stat.value }}</p>
            </div>
            <div class="w-12 h-12 rounded-lg flex items-center justify-center" :style="{ backgroundColor: `${primaryColor}20` }">
              <svg class="w-6 h-6" :style="{ color: primaryColor }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="stat.icon === 'file-text'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                <path v-else-if="stat.icon === 'clock'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path v-else-if="stat.icon === 'check-circle'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-1">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <Input
              v-model="searchQuery"
              placeholder="Search by request number or property..."
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
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select v-model="filterStatus" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent" :style="{ '--tw-ring-color': primaryColor }">
              <option value="">All Statuses</option>
              <option value="Draft">Draft</option>
              <option value="Submitted">Submitted</option>
              <option value="Under Review">Under Review</option>
              <option value="RFI Issued">RFI Issued</option>
              <option value="Approved">Approved</option>
              <option value="Declined">Declined</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
            <select v-model="filterType" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent" :style="{ '--tw-ring-color': primaryColor }">
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
          <h3 class="text-lg font-semibold text-gray-900">My {{ councilSettings?.council_name || councilCode }} Applications</h3>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="p-12 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2" :style="{ borderColor: primaryColor }"></div>
          <p class="mt-4 text-gray-500">Loading applications...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="!filteredRequests || filteredRequests.length === 0" class="p-12 text-center">
          <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" :style="{ backgroundColor: `${primaryColor}20` }">
            <svg class="w-8 h-8" :style="{ color: primaryColor }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">No applications found</h3>
          <p class="text-gray-500 mb-6">{{ searchQuery ? 'Try adjusting your search or filters' : 'Get started by creating your first application' }}</p>
          <Button @click="goToNewRequest" variant="solid" :style="{ backgroundColor: primaryColor, borderColor: primaryColor }">
            Create New Application
          </Button>
        </div>

        <!-- Requests Table -->
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Request #</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Property</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Submitted</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Days Elapsed</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="request in filteredRequests" :key="request.name" class="hover:bg-gray-50 transition cursor-pointer" @click="viewRequest(request.name)">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium" :style="{ color: primaryColor }">{{ request.request_number }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ request.request_type }}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-900">{{ request.property_address || 'N/A' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <StatusBadge :status="request.status" />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-500">{{ formatDate(request.creation) }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ request.working_days_elapsed || 0 }} days</div>
                  <div v-if="request.statutory_clock_started" class="text-xs text-gray-500">
                    of 20 day limit
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click.stop="viewRequest(request.name)" class="hover:opacity-80 mr-4" :style="{ color: primaryColor }">
                    View
                  </button>
                  <button v-if="request.status === 'Draft'" @click.stop="editRequest(request.name)" class="text-gray-600 hover:text-gray-900">
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Dropdown, Input, Button, call } from 'frappe-ui'
import { session } from '../data/session'
import { useCouncilStore } from '../stores/councilStore'
import StatusBadge from '../components/StatusBadge.vue'

const router = useRouter()
const route = useRoute()
const councilStore = useCouncilStore()

const councilCode = computed(() => route.params.councilCode?.toUpperCase())
const councilSettings = ref(null)
const requests = ref([])
const isLoading = ref(true)

// User info
const userName = computed(() => {
  const fullName = session.user_info?.full_name || session.user
  return fullName.replace('@', ' ').split('.').join(' ')
})

const userInitials = computed(() => {
  const name = userName.value
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
})

// Filters
const searchQuery = ref('')
const filterStatus = ref('')
const filterType = ref('')

// Computed styles
const primaryColor = computed(() => councilSettings.value?.primary_color || '#2563eb')

// Computed stats
const stats = computed(() => {
  const data = requests.value || []
  return {
    total: data.length,
    underReview: data.filter(r => r.status === 'Under Review').length,
    approved: data.filter(r => r.status === 'Approved').length,
    rfiPending: data.filter(r => r.status === 'RFI Issued').length,
  }
})

const statsArray = computed(() => [
  { title: 'Total Requests', value: stats.value.total, icon: 'file-text' },
  { title: 'Under Review', value: stats.value.underReview, icon: 'clock' },
  { title: 'Approved', value: stats.value.approved, icon: 'check-circle' },
  { title: 'Info Requested', value: stats.value.rfiPending, icon: 'alert-circle' },
])

// Filtered requests
const filteredRequests = computed(() => {
  let data = requests.value || []

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(r =>
      r.request_number?.toLowerCase().includes(query) ||
      r.property_address?.toLowerCase().includes(query) ||
      r.brief_description?.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (filterStatus.value) {
    data = data.filter(r => r.status === filterStatus.value)
  }

  // Type filter
  if (filterType.value) {
    data = data.filter(r => r.request_type?.includes(filterType.value))
  }

  return data
})

// Load council settings and requests
onMounted(async () => {
  try {
    // Load council settings
    councilSettings.value = await councilStore.getCouncilSettings(councilCode.value)

    // Load council-specific requests
    const response = await call('lodgeick.api.get_council_requests', {
      council_code: councilCode.value
    })
    requests.value = response || []
  } catch (error) {
    console.error('Failed to load council data:', error)
  } finally {
    isLoading.value = false
  }
})

// Format date
const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-NZ', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Navigation
const goToNewRequest = () => {
  router.push({
    name: 'NewRequest',
    query: {
      council: councilCode.value,
      locked: 'true'
    }
  })
}

const viewRequest = (requestId) => {
  router.push({ name: 'RequestDetail', params: { id: requestId } })
}

const editRequest = (requestId) => {
  router.push({ name: 'RequestDetail', params: { id: requestId } })
}

const goToAccount = () => {
  router.push({ name: 'CouncilAccount', params: { councilCode: councilCode.value } })
}

// User menu
const userMenuOptions = [
  {
    label: 'My Account',
    onClick: goToAccount,
  },
  {
    label: 'Sign Out',
    onClick: () => session.logout.submit(),
  },
]
</script>
