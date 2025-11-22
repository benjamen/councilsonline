<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <button @click="goBack" class="text-gray-500 hover:text-gray-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div v-if="request.data">
              <h1 class="text-xl font-bold text-gray-900">{{ request.data.request_number }}</h1>
              <p class="text-sm text-gray-500">{{ request.data.request_type }}</p>
            </div>
          </div>

          <div v-if="request.data" class="flex items-center space-x-3">
            <StatusBadge :status="request.data.status" />
            <Dropdown :options="actionMenuOptions">
              <template #default="{ open }">
                <Button variant="outline" theme="gray">
                  Actions
                  <template #suffix>
                    <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </template>
                </Button>
              </template>
            </Dropdown>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div v-if="request.loading" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>

    <div v-else-if="request.data" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Column -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Request Details -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Request Details</h2>
            <dl class="grid grid-cols-2 gap-4">
              <div>
                <dt class="text-sm text-gray-600">Applicant</dt>
                <dd class="mt-1 text-sm font-medium text-gray-900">{{ request.data.applicant_name }}</dd>
                <dd class="text-xs text-gray-500">{{ request.data.applicant_email }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-600">Property</dt>
                <dd class="mt-1 text-sm font-medium text-gray-900">{{ request.data.property_address }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-600">Submitted</dt>
                <dd class="mt-1 text-sm font-medium text-gray-900">{{ formatDate(request.data.submitted_date) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-600">Days Elapsed</dt>
                <dd class="mt-1 text-sm font-medium" :class="isOverdue ? 'text-red-600' : 'text-gray-900'">
                  {{ clockData.working_days_elapsed }} days
                </dd>
              </div>
            </dl>

            <div class="mt-4 pt-4 border-t border-gray-200">
              <dt class="text-sm text-gray-600 mb-2">Description</dt>
              <dd class="text-sm text-gray-900">{{ request.data.brief_description }}</dd>
            </div>
          </div>

          <!-- Tasks & Work Management -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="p-6 border-b border-gray-200 flex justify-between items-center">
              <h2 class="text-lg font-semibold text-gray-900">Tasks & Work</h2>
              <Button @click="addTask" variant="solid" theme="green" size="sm">
                <template #prefix>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </template>
                Add Task
              </Button>
            </div>

            <div class="p-6">
              <div class="space-y-4">
                <div v-for="task in mockTasks" :key="task.id" class="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                  <input type="checkbox" :checked="task.completed" class="mt-1 h-5 w-5 text-green-600 rounded" />
                  <div class="flex-1">
                    <h4 class="text-sm font-medium text-gray-900">{{ task.title }}</h4>
                    <div class="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                      <span>{{ task.assignee }}</span>
                      <span>{{ task.hours }}h</span>
                      <span v-if="task.cost">${{ task.cost }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Costing Summary -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Costing Summary</h2>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Application Fee</span>
                <span class="text-sm font-medium text-gray-900">${{ request.data.application_fee || 0 }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Additional Charges</span>
                <span class="text-sm font-medium text-gray-900">${{ request.data.additional_charges || 0 }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Staff Time ({{ totalHours }}h @ $150/h)</span>
                <span class="text-sm font-medium text-gray-900">${{ totalStaffCost }}</span>
              </div>
              <div class="pt-3 border-t border-gray-200 flex justify-between items-center">
                <span class="text-base font-semibold text-gray-900">Total Cost</span>
                <span class="text-base font-bold text-green-600">${{ totalCost }}</span>
              </div>
            </div>

            <Button @click="addCharge" variant="outline" theme="green" class="w-full mt-4">
              Add Additional Charge
            </Button>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Assignment -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Assignment</h3>
            <div class="space-y-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-2">Assigned To</label>
                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  <option value="">Unassigned</option>
                  <option value="planner1">John Smith (Planner)</option>
                  <option value="planner2">Jane Doe (Planner)</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-2">Priority</label>
                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Timeline -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Timeline</h3>

            <!-- Statutory Clock -->
            <div v-if="clockData.statutory_clock_started" class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-medium text-gray-700">Statutory Clock</span>
                <span class="text-xs text-gray-600">
                  {{ clockData.working_days_elapsed }} / {{ request.data.statutory_timeframe || 20 }} days
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="h-2 rounded-full transition-all"
                  :class="isOverdue ? 'bg-red-600' : 'bg-green-600'"
                  :style="{ width: `${progressPercent}%` }"
                ></div>
              </div>
              <p class="mt-2 text-xs text-gray-500">
                {{ clockData.working_days_remaining }} days remaining
                {{ clockData.statutory_clock_stopped ? '(Clock stopped)' : '' }}
              </p>
            </div>

            <!-- Status History -->
            <div class="space-y-3">
              <div v-for="(event, index) in mockTimeline" :key="index" class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center" :class="event.color">
                  <div class="w-2 h-2 rounded-full bg-white"></div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900">{{ event.title }}</p>
                  <p class="text-xs text-gray-500">{{ event.date }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div class="space-y-2">
              <Button @click="issueRFI" variant="outline" theme="orange" class="w-full justify-center">
                Issue RFI
              </Button>
              <Button @click="approve" variant="outline" theme="green" class="w-full justify-center">
                Approve
              </Button>
              <Button @click="decline" variant="outline" theme="red" class="w-full justify-center">
                Decline
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createResource, Button, Dropdown } from 'frappe-ui'
import StatusBadge from '../components/StatusBadge.vue'
import { useStatutoryClock } from '../composables/useStatutoryClock'

const router = useRouter()
const route = useRoute()

// Fetch request details
const request = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'Request',
    name: route.params.id
  },
  auto: true,
})

// Get statutory clock data from appropriate source (RC Application or Request)
const { clockData, progressPercent, isOverdue } = useStatutoryClock(request)

// Mock data (replace with real data)
const mockTasks = ref([
  { id: 1, title: 'Review application documents', assignee: 'John Smith', hours: 2, cost: 300, completed: true },
  { id: 2, title: 'Site inspection', assignee: 'Jane Doe', hours: 4, cost: 600, completed: false },
  { id: 3, title: 'Prepare decision report', assignee: 'John Smith', hours: 3, cost: 450, completed: false },
])

const mockTimeline = ref([
  { title: 'Application Submitted', date: '10 Oct 2025', color: 'bg-blue-500' },
  { title: 'Assigned to John Smith', date: '11 Oct 2025', color: 'bg-green-500' },
  { title: 'Under Review', date: '12 Oct 2025', color: 'bg-yellow-500' },
])

// Computed
const totalHours = computed(() => mockTasks.value.reduce((sum, t) => sum + t.hours, 0))
const totalStaffCost = computed(() => totalHours.value * 150)
const totalCost = computed(() => {
  const appFee = parseFloat(request.data?.application_fee || 0)
  const addCharges = parseFloat(request.data?.additional_charges || 0)
  return appFee + addCharges + totalStaffCost.value
})

// Methods
const goBack = () => {
  router.push({ name: 'InternalRequestManagement' })
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-NZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const addTask = () => {
  console.log('Add task')
}

const addCharge = () => {
  console.log('Add charge')
}

const issueRFI = () => {
  console.log('Issue RFI')
}

const approve = () => {
  console.log('Approve request')
}

const decline = () => {
  console.log('Decline request')
}

// Action menu
const actionMenuOptions = [
  { label: 'Send Message', onClick: () => console.log('Message') },
  { label: 'Generate Report', onClick: () => console.log('Report') },
  { label: 'View History', onClick: () => console.log('History') },
]
</script>
