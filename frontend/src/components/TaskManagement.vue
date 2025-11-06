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
          <Button @click="showNewTaskDialog = true" variant="solid" theme="green">
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
          <div class="flex items-start justify-between">
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
                    class="text-base font-medium"
                    :class="task.status === 'Completed' ? 'text-gray-400 line-through' : 'text-gray-900'"
                  >
                    {{ task.subject }}
                  </h3>
                  <span
                    v-if="task.priority"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                    :class="getPriorityClass(task.priority)"
                  >
                    {{ task.priority }}
                  </span>
                </div>

                <p class="text-sm text-gray-600 mb-3">{{ task.description }}</p>

                <div class="flex items-center space-x-4 text-sm text-gray-500">
                  <div v-if="task.request" class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {{ task.request_number }}
                  </div>

                  <div v-if="task.expected_time" class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ task.expected_time }} hours
                  </div>

                  <div v-if="task.costing_amount" class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    ${{ task.costing_amount }}
                  </div>

                  <div v-if="task.due_date" class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span :class="isOverdue(task.due_date) ? 'text-red-600 font-medium' : ''">
                      {{ formatDate(task.due_date) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center space-x-2 ml-4">
              <button
                v-if="task.request"
                @click="viewRequest(task.request)"
                class="p-2 text-gray-400 hover:text-blue-600 transition"
                title="View Request"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
              <button
                @click="editTask(task)"
                class="p-2 text-gray-400 hover:text-green-600 transition"
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
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import StatCard from './StatCard.vue'

const router = useRouter()
const showNewTaskDialog = ref(false)

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
    inProgress: data.filter(t => t.status === 'Open' || t.status === 'Working').length,
    completedToday: data.filter(t =>
      t.status === 'Completed' &&
      new Date(t.completed_on).toDateString() === today
    ).length,
    overdue: data.filter(t =>
      t.status !== 'Completed' &&
      t.due_date &&
      new Date(t.due_date) < new Date()
    ).length,
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
  // TODO: Implement task status update
  console.log('Toggle task status:', task.name, newStatus)
  tasks.reload()
}

const viewRequest = (requestId) => {
  router.push({ name: 'InternalRequestDetail', params: { id: requestId } })
}

const editTask = (task) => {
  // TODO: Implement task edit dialog
  console.log('Edit task:', task.name)
}
</script>
