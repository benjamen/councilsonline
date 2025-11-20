<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">Easy Council</h1>
              <p class="text-xs text-gray-500">Internal Request Management</p>
            </div>
          </div>

          <div class="flex items-center space-x-4">
            <Dropdown :options="userMenuOptions">
              <template v-slot="{ open }">
                <button class="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
                  <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-green-600">{{ userInitials }}</span>
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

        <!-- Navigation Tabs -->
        <div class="flex space-x-6 border-t border-gray-200 -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="currentTab = tab.id"
            class="py-4 px-1 border-b-2 font-medium text-sm transition-colors"
            :class="currentTab === tab.id
              ? 'border-green-600 text-green-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- All Requests Tab -->
      <div v-if="currentTab === 'requests'">
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <StatCard title="Total Requests" :value="stats.total" icon="inbox" color="blue" />
          <StatCard title="New/Unassigned" :value="stats.unassigned" icon="alert-circle" color="red" />
          <StatCard title="In Progress" :value="stats.inProgress" icon="clock" color="yellow" />
          <StatCard title="RFI Issued" :value="stats.rfi" icon="help-circle" color="orange" />
          <StatCard title="Completed" :value="stats.completed" icon="check-circle" color="green" />
        </div>

        <!-- Filters -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div class="grid md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <Input v-model="searchQuery" placeholder="Request number, property..." />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select v-model="filterStatus" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="">All Statuses</option>
                <option value="Submitted">Submitted</option>
                <option value="Under Review">Under Review</option>
                <option value="RFI Issued">RFI Issued</option>
                <option value="Approved">Approved</option>
                <option value="Declined">Declined</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Assigned To</label>
              <select v-model="filterAssignee" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="">All Staff</option>
                <option value="unassigned">Unassigned</option>
                <option value="me">Assigned to Me</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Request Type</label>
              <select v-model="filterType" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option value="">All Types</option>
                <option value="Building Consent">Building Consent</option>
                <option value="Resource Consent">Resource Consent</option>
                <option value="LIM">LIM Report</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Requests Table -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Request
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Applicant
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Property
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assigned To
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Days Elapsed
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="requests.loading">
                  <td colspan="7" class="px-6 py-12 text-center text-gray-500">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                  </td>
                </tr>
                <tr v-else-if="!requests.data || requests.data.length === 0">
                  <td colspan="7" class="px-6 py-12 text-center text-gray-500">
                    No requests found
                  </td>
                </tr>
                <tr v-else v-for="request in filteredRequests" :key="request.name" class="hover:bg-gray-50 cursor-pointer">
                  <td class="px-6 py-4 whitespace-nowrap" @click="viewRequest(request.name)">
                    <div class="text-sm font-medium text-gray-900">{{ request.request_number }}</div>
                    <div class="text-sm text-gray-500">{{ request.request_type }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">{{ request.applicant_name || request.applicant }}</div>
                    <div class="text-sm text-gray-500">{{ request.applicant_email }}</div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm text-gray-900">{{ request.property_address }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <StatusBadge :status="request.status" />
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div v-if="request.assigned_to" class="flex items-center">
                      <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-2">
                        <span class="text-xs font-medium text-green-600">{{ getInitials(request.assigned_to) }}</span>
                      </div>
                      <span class="text-sm text-gray-900">{{ request.assigned_to_name || request.assigned_to }}</span>
                    </div>
                    <span v-else class="text-sm text-gray-400">Unassigned</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">{{ request.working_days_elapsed || 0 }} days</div>
                    <div v-if="request.working_days_remaining" class="text-xs" :class="request.is_overdue ? 'text-red-600' : 'text-gray-500'">
                      {{ request.working_days_remaining }} remaining
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button @click.stop="assignRequest(request)" class="text-green-600 hover:text-green-900 mr-3">
                      Assign
                    </button>
                    <button @click.stop="viewRequest(request.name)" class="text-blue-600 hover:text-blue-900">
                      View
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- My Tasks Tab -->
      <div v-if="currentTab === 'tasks'">
        <TaskManagement />
      </div>

      <!-- Analytics Tab -->
      <div v-if="currentTab === 'analytics'">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Analytics Dashboard</h3>
          <p class="text-gray-500">Performance metrics and reporting coming soon</p>
        </div>
      </div>
    </main>

    <!-- Assignment Dialog -->
    <Dialog v-model="showAssignDialog" :options="{ title: 'Assign Request', size: 'md' }">
      <template #body-content>
        <div v-if="assigningRequest" class="space-y-4">
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="text-sm font-medium text-gray-900">{{ assigningRequest.request_number }}</div>
            <div class="text-sm text-gray-500">{{ assigningRequest.brief_description }}</div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Assign To <span class="text-red-500">*</span></label>
            <Input
              v-model="assignedTo"
              type="text"
              placeholder="Enter email address"
              class="w-full"
            />
            <p class="mt-1 text-sm text-gray-500">Enter the email address of the staff member</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Notes (Optional)</label>
            <textarea
              v-model="assignmentNotes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Add any notes about this assignment..."
            ></textarea>
          </div>
        </div>
      </template>

      <template #actions>
        <Button @click="cancelAssignment" variant="outline">Cancel</Button>
        <Button @click="confirmAssignment" :loading="isAssigning" variant="solid" theme="blue">
          Assign Request
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Input, Dropdown, Dialog, Button } from 'frappe-ui'
import { session } from '../data/session'
import StatusBadge from '../components/StatusBadge.vue'
import StatCard from '../components/StatCard.vue'
import TaskManagement from '../components/TaskManagement.vue'

const router = useRouter()

// Current tab
const currentTab = ref('requests')

const tabs = [
  { id: 'requests', label: 'All Requests' },
  { id: 'tasks', label: 'My Tasks' },
  { id: 'analytics', label: 'Analytics' },
]

// Filters
const searchQuery = ref('')
const filterStatus = ref('')
const filterAssignee = ref('')
const filterType = ref('')

// Assignment dialog
const showAssignDialog = ref(false)
const assigningRequest = ref(null)
const assignedTo = ref('')
const assignmentNotes = ref('')
const isAssigning = ref(false)

// Fetch all requests for council staff
const requests = createResource({
  url: 'lodgeick.lodgeick.doctype.request.request.get_all_requests_for_staff',
  auto: true,
})

// Computed stats
const stats = computed(() => {
  const data = requests.data || []
  return {
    total: data.length,
    unassigned: data.filter(r => !r.assigned_to).length,
    inProgress: data.filter(r => r.status === 'Under Review').length,
    rfi: data.filter(r => r.status === 'RFI Issued').length,
    completed: data.filter(r => ['Approved', 'Declined', 'Withdrawn'].includes(r.status)).length,
  }
})

// Filtered requests
const filteredRequests = computed(() => {
  let data = requests.data || []

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(r =>
      r.request_number?.toLowerCase().includes(query) ||
      r.property_address?.toLowerCase().includes(query) ||
      r.applicant_name?.toLowerCase().includes(query)
    )
  }

  if (filterStatus.value) {
    data = data.filter(r => r.status === filterStatus.value)
  }

  if (filterAssignee.value === 'unassigned') {
    data = data.filter(r => !r.assigned_to)
  } else if (filterAssignee.value === 'me') {
    data = data.filter(r => r.assigned_to === session.user)
  }

  if (filterType.value) {
    data = data.filter(r => r.request_type === filterType.value)
  }

  return data
})

// User info
const userName = computed(() => session.user || 'User')
const userInitials = computed(() => {
  const name = userName.value
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
})

// Methods
const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
}

const viewRequest = (requestId) => {
  router.push({ name: 'InternalRequestDetail', params: { id: requestId } })
}

const assignRequest = (request) => {
  assigningRequest.value = request
  assignedTo.value = request.assigned_to || ''
  assignmentNotes.value = ''
  showAssignDialog.value = true
}

const confirmAssignment = async () => {
  if (!assignedTo.value) {
    alert('Please select a user to assign')
    return
  }

  isAssigning.value = true
  try {
    const response = await fetch('/api/method/lodgeick.api.assign_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        request_id: assigningRequest.value.name,
        assigned_to: assignedTo.value,
        notes: assignmentNotes.value
      })
    })

    const result = await response.json()

    if (result.message && result.message.success) {
      showAssignDialog.value = false
      assigningRequest.value = null
      assignedTo.value = ''
      assignmentNotes.value = ''
      // Reload requests
      requests.reload()
      alert('Request assigned successfully!')
    } else {
      throw new Error('Failed to assign request')
    }
  } catch (error) {
    console.error('Error assigning request:', error)
    alert('Failed to assign request. Please try again.')
  } finally {
    isAssigning.value = false
  }
}

const cancelAssignment = () => {
  showAssignDialog.value = false
  assigningRequest.value = null
  assignedTo.value = ''
  assignmentNotes.value = ''
}

// Navigation back to public view
const goToPublicDashboard = () => {
  router.push({ name: 'Dashboard' })
}

// User menu
const userMenuOptions = [
  {
    label: 'Public Dashboard',
    onClick: goToPublicDashboard,
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
    label: 'Logout',
    onClick: () => session.logout.submit(),
  },
]
</script>
