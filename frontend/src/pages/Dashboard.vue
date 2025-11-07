<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">Lodgeick</h1>
              <p class="text-xs text-gray-500">Council Request Management</p>
            </div>
          </div>

          <div class="flex items-center space-x-4">
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
                <button class="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
                  <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-blue-600">{{ userInitials }}</span>
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
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="md:col-span-2">
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
            <select v-model="filterStatus" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
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
            <select v-model="filterType" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
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
          <h3 class="text-lg font-semibold text-gray-900">My Applications</h3>
        </div>

        <!-- Loading State -->
        <div v-if="requests.loading" class="p-12 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-4 text-gray-500">Loading applications...</p>
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
                  <div class="text-sm font-medium text-blue-600">{{ request.request_number }}</div>
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
                  <button @click.stop="viewRequest(request.name)" class="text-blue-600 hover:text-blue-900 mr-4">
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
import { useRouter } from 'vue-router'
import { createResource, Dropdown, Input, Button } from 'frappe-ui'
import { session } from '../data/session'
import StatusBadge from '../components/StatusBadge.vue'
import StatCard from '../components/StatCard.vue'

const router = useRouter()

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

// Get user's requests
const requests = createResource({
  url: 'lodgeick.lodgeick.doctype.request.request.get_my_applications',
  auto: true,
})

// Computed stats
const stats = computed(() => {
  const data = requests.data || []
  return {
    total: data.length,
    underReview: data.filter(r => r.status === 'Under Review').length,
    approved: data.filter(r => r.status === 'Approved').length,
    rfiPending: data.filter(r => r.status === 'RFI Issued').length,
  }
})

// Filtered requests
const filteredRequests = computed(() => {
  let data = requests.data || []

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
  router.push({ name: 'NewRequest' })
}

const viewRequest = (requestId) => {
  router.push({ name: 'RequestDetail', params: { id: requestId } })
}

const editRequest = (requestId) => {
  router.push({ name: 'RequestDetail', params: { id: requestId } })
}

// Navigation to internal view
const goToInternal = () => {
  router.push({ name: 'InternalRequestManagement' })
}

// User menu
const userMenuOptions = [
  {
    label: 'Staff Portal',
    onClick: goToInternal,
  },
  {
    label: 'My Profile',
    onClick: () => console.log('Profile'),
  },
  {
    label: 'Settings',
    onClick: () => console.log('Settings'),
  },
  {
    label: 'Sign Out',
    onClick: () => session.logout.submit(),
  },
]
</script>
