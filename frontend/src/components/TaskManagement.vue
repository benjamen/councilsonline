<template>
  <div class="space-y-6">
    <!-- Task Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <StatCard title="My Tasks" :value="stats.myTasks" icon="clipboard" color="blue" />
      <StatCard title="In Progress" :value="stats.inProgress" icon="clock" color="yellow" />
      <StatCard title="Completed Today" :value="stats.completedToday" icon="check" color="green" />
      <StatCard title="Overdue" :value="stats.overdue" icon="alert-triangle" color="red" />
    </div>

    <!-- Task List -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <div class="p-6 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-900">My Tasks</h2>
          <Button @click="openNewTaskDialog" variant="solid" theme="green">
            <template #prefix>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </template>
            New Task
          </Button>
        </div>
      </div>

      <div class="divide-y divide-gray-200">
        <div v-if="tasks.loading" class="p-12 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        </div>

        <div v-else-if="!tasks.data || tasks.data.length === 0" class="p-12 text-center text-gray-500">
          <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p>No tasks assigned</p>
        </div>

        <div
          v-else
          v-for="task in tasks.data"
          :key="task.name"
          class="p-6 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-start justify-between gap-6">
            <div class="flex items-start space-x-4 flex-1">
              <!-- Checkbox -->
              <input
                type="checkbox"
                :checked="task.status === 'Completed'"
                @change="toggleTaskStatus(task)"
                class="mt-1 h-5 w-5 text-green-600 focus:ring-green-500 border-gray-300 rounded cursor-pointer"
              />

              <!-- Task Details -->
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h3
                    class="text-base font-semibold"
                    :class="task.status === 'Completed' ? 'text-gray-400 line-through' : 'text-gray-900'"
                  >
                    {{ task.title }}
                  </h3>
                  <span
                    v-if="task.priority"
                    class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold"
                    :class="getPriorityClass(task.priority)"
                  >
                    {{ task.priority }}
                  </span>
                </div>

                <p class="text-sm text-gray-600 mb-4">{{ task.description }}</p>

                <!-- Key Metadata Row -->
                <div class="flex flex-wrap items-center gap-3">
                  <div v-if="task.request" class="flex items-center text-sm text-gray-600">
                    <svg class="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span class="font-medium">{{ task.request }}</span>
                  </div>

                  <div v-if="task.assigned_role" class="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold">
                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    {{ task.assigned_role }}
                  </div>

                  <div v-if="task.due_date" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold"
                    :class="isOverdue(task.due_date) ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'">
                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {{ formatDate(task.due_date) }}
                    <span v-if="isOverdue(task.due_date)" class="ml-1">⚠️</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Side: Key Metrics + Actions -->
            <div class="flex flex-col items-end space-y-3 min-w-[180px]">
              <!-- Cost Badge (Most Prominent) -->
              <div v-if="task.total_cost" class="px-4 py-2 bg-green-50 border-2 border-green-200 rounded-lg">
                <div class="text-xs text-green-700 font-medium mb-0.5">Total Cost</div>
                <div class="text-2xl font-bold text-green-900">${{ task.total_cost.toFixed(2) }}</div>
              </div>

              <!-- Hours Badge -->
              <div v-if="task.estimated_hours || task.actual_hours" class="px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg w-full">
                <div class="flex items-center justify-between">
                  <div class="text-xs text-blue-700 font-medium">
                    {{ task.actual_hours ? 'Actual' : 'Est.' }} Hours
                  </div>
                  <div class="text-lg font-bold text-blue-900">
                    <span v-if="task.actual_hours">{{ task.actual_hours }}h</span>
                    <span v-else-if="task.estimated_hours">~{{ task.estimated_hours }}h</span>
                  </div>
                </div>
                <div v-if="task.hourly_rate" class="text-xs text-blue-600 mt-1">
                  @ ${{ task.hourly_rate.toFixed(2) }}/hr
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center space-x-2">
                <button
                  v-if="task.request"
                  @click="viewRequest(task.request)"
                  class="p-2 text-gray-400 hover:text-blue-600 transition rounded-lg hover:bg-blue-50"
                  title="View Request"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button
                  @click="openEditTaskDialog(task)"
                  class="p-2 text-gray-400 hover:text-green-600 transition rounded-lg hover:bg-green-50"
                  title="Edit Task"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Task Dialog -->
    <TaskDialog
      v-model="showTaskDialog"
      :task="selectedTask"
      @task-saved="handleTaskSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button, call } from 'frappe-ui'
import StatCard from './StatCard.vue'
import TaskDialog from './TaskDialog.vue'

const router = useRouter()
const showTaskDialog = ref(false)
const selectedTask = ref(null)

// Fetch tasks for current user
const tasks = createResource({
  url: 'lodgeick.lodgeick.doctype.task.task.get_my_tasks',
  auto: true,
})

// Computed stats
const stats = computed(() => {
  const data = tasks.data || []
  const today = new Date().toDateString()

  return {
    myTasks: data.length,
    inProgress: data.filter(t => t.status === 'Open').length,
    completedToday: data.filter(t =>
      t.status === 'Completed' &&
      t.date_of_completion &&
      new Date(t.date_of_completion).toDateString() === today
    ).length,
    overdue: data.filter(t => t.status === 'Overdue').length,
  }
})

// Methods
const getPriorityClass = (priority) => {
  const classes = {
    'Low': 'bg-gray-100 text-gray-800',
    'Medium': 'bg-blue-100 text-blue-800',
    'High': 'bg-orange-100 text-orange-800',
    'Urgent': 'bg-red-100 text-red-800',
  }
  return classes[priority] || classes['Medium']
}

const isOverdue = (dueDate) => {
  if (!dueDate) return false
  return new Date(dueDate) < new Date()
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-NZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const toggleTaskStatus = async (task) => {
  const newStatus = task.status === 'Completed' ? 'Open' : 'Completed'

  try {
    await call('frappe.client.set_value', {
      doctype: 'Project Task',
      name: task.name,
      fieldname: 'status',
      value: newStatus
    })

    tasks.reload()
  } catch (error) {
    console.error('Error toggling task status:', error)
  }
}

const viewRequest = (requestId) => {
  router.push({ name: 'InternalRequestDetail', params: { id: requestId } })
}

const openNewTaskDialog = () => {
  selectedTask.value = null
  showTaskDialog.value = true
}

const openEditTaskDialog = (task) => {
  selectedTask.value = task
  showTaskDialog.value = true
}

const handleTaskSaved = () => {
  tasks.reload()
}
</script>
