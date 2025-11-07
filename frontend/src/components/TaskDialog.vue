<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: isEditMode ? 'Edit Task' : 'Create New Task',
      size: '3xl'
    }"
  >
    <template #body-content>
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Task Title -->
        <div>
          <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
            Title <span class="text-red-500">*</span>
          </label>
          <Input
            id="title"
            v-model="formData.title"
            type="text"
            required
            placeholder="Enter task title"
            class="w-full"
          />
        </div>

        <!-- Description -->
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            id="description"
            v-model="formData.description"
            rows="3"
            placeholder="Describe the task..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Priority and Status Row -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="priority" class="block text-sm font-medium text-gray-700 mb-2">
              Priority <span class="text-red-500">*</span>
            </label>
            <select
              id="priority"
              v-model="formData.priority"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Urgent">Urgent</option>
            </select>
          </div>

          <div>
            <label for="status" class="block text-sm font-medium text-gray-700 mb-2">
              Status <span class="text-red-500">*</span>
            </label>
            <select
              id="status"
              v-model="formData.status"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="Open">Open</option>
              <option value="Working">Working</option>
              <option value="Pending Review">Pending Review</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <!-- Due Date and Assign To Row -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="due_date" class="block text-sm font-medium text-gray-700 mb-2">
              Due Date <span class="text-red-500">*</span>
            </label>
            <Input
              id="due_date"
              v-model="formData.due_date"
              type="date"
              required
              class="w-full"
            />
          </div>

          <div>
            <label for="assign_to" class="block text-sm font-medium text-gray-700 mb-2">
              Assign To <span class="text-red-500">*</span>
            </label>
            <Input
              id="assign_to"
              v-model="formData.assign_to"
              type="text"
              required
              placeholder="User email"
              class="w-full"
            />
          </div>
        </div>

        <!-- Request (optional) -->
        <div>
          <label for="request" class="block text-sm font-medium text-gray-700 mb-2">
            Linked Request (Optional)
          </label>
          <Input
            id="request"
            v-model="formData.request"
            type="text"
            placeholder="Request ID (e.g., RC-2025-001)"
            class="w-full"
          />
        </div>

        <!-- Time Tracking & Costing Section -->
        <div class="border-t border-gray-200 pt-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Time Tracking & Costing</h3>

          <!-- User Role (read-only, fetched from assigned user) -->
          <div class="mb-4">
            <label for="assigned_role" class="block text-sm font-medium text-gray-700 mb-2">
              User Role (Auto-detected)
            </label>
            <div class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-gray-700">
              {{ userRole || 'Role will be detected from assigned user' }}
            </div>
          </div>

          <!-- Hours and Rate -->
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label for="estimated_hours" class="block text-sm font-medium text-gray-700 mb-2">
                Estimated Hours
              </label>
              <Input
                id="estimated_hours"
                v-model.number="formData.estimated_hours"
                type="number"
                step="0.25"
                min="0"
                placeholder="0.00"
                class="w-full"
              />
            </div>

            <div>
              <label for="actual_hours" class="block text-sm font-medium text-gray-700 mb-2">
                Actual Hours
              </label>
              <Input
                id="actual_hours"
                v-model.number="formData.actual_hours"
                type="number"
                step="0.25"
                min="0"
                placeholder="0.00"
                @input="calculateCost"
                class="w-full"
              />
            </div>

            <div>
              <label for="hourly_rate" class="block text-sm font-medium text-gray-700 mb-2">
                Hourly Rate
              </label>
              <div class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-gray-700 font-medium">
                ${{ hourlyRate.toFixed(2) }}
              </div>
            </div>
          </div>

          <!-- Total Cost (calculated) -->
          <div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">Total Cost</span>
              <span class="text-xl font-bold text-blue-900">${{ totalCost.toFixed(2) }}</span>
            </div>
            <p class="text-xs text-gray-600 mt-1">
              Calculated as: {{ formData.actual_hours || 0 }} hours × ${{ hourlyRate.toFixed(2) }}/hr
            </p>
          </div>

          <!-- Activity Type (optional) -->
          <div class="mt-4" v-if="formData.request">
            <label for="activity_type" class="block text-sm font-medium text-gray-700 mb-2">
              Activity Type (Optional)
            </label>
            <Input
              id="activity_type"
              v-model="formData.activity_type"
              type="text"
              placeholder="e.g., Site Inspection"
              class="w-full"
            />
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-red-700">{{ errorMessage }}</p>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <Button
            type="button"
            @click="closeDialog"
            variant="outline"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            :loading="isSubmitting"
            variant="solid"
            theme="green"
          >
            {{ isEditMode ? 'Update Task' : 'Create Task' }}
          </Button>
        </div>
      </form>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Dialog, Input, Button, call } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  task: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'task-saved'])

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEditMode = computed(() => !!props.task)
const isSubmitting = ref(false)
const errorMessage = ref('')

const defaultFormData = () => ({
  title: '',
  description: '',
  priority: 'Medium',
  status: 'Open',
  due_date: '',
  assign_to: '',
  assign_from: '',
  request: '',
  activity_type: '',
  assigned_role: '',
  estimated_hours: null,
  actual_hours: null
})

const formData = ref(defaultFormData())
const userRole = ref('')
const hourlyRate = ref(0)
const totalCost = computed(() => {
  const hours = formData.value.actual_hours || 0
  return hours * hourlyRate.value
})

// Fetch user role and hourly rate when assign_to changes
watch(() => formData.value.assign_to, async (newUser) => {
  if (newUser) {
    try {
      // Get user's primary role
      const userDoc = await call('frappe.client.get', {
        doctype: 'User',
        name: newUser
      })

      if (userDoc && userDoc.roles && userDoc.roles.length > 0) {
        // Get first non-standard role
        const role = userDoc.roles.find(r => !['Guest', 'All'].includes(r.role))
        if (role) {
          userRole.value = role.role
          formData.value.assigned_role = role.role

          // Fetch hourly rate for this role
          const rateData = await call('lodgeick.lodgeick.doctype.role_rate.role_rate.get_hourly_rate', {
            role: role.role
          })

          if (rateData && rateData.hourly_rate) {
            hourlyRate.value = rateData.hourly_rate
          }
        }
      }
    } catch (error) {
      console.error('Error fetching user role and rate:', error)
      userRole.value = ''
      hourlyRate.value = 0
    }
  } else {
    userRole.value = ''
    hourlyRate.value = 0
  }
})

// Calculate cost when actual hours changes
const calculateCost = () => {
  // Cost is automatically calculated via computed property
}

// Watch for task prop changes to populate form
watch(() => props.task, (newTask) => {
  if (newTask) {
    formData.value = {
      title: newTask.title || '',
      description: newTask.description || '',
      priority: newTask.priority || 'Medium',
      status: newTask.status || 'Open',
      due_date: newTask.due_date || '',
      assign_to: newTask.assign_to || '',
      assign_from: newTask.assign_from || '',
      request: newTask.request || '',
      activity_type: newTask.activity_type || '',
      assigned_role: newTask.assigned_role || '',
      estimated_hours: newTask.estimated_hours || null,
      actual_hours: newTask.actual_hours || null
    }

    // Set existing role and rate
    if (newTask.assigned_role) {
      userRole.value = newTask.assigned_role
    }
    if (newTask.hourly_rate) {
      hourlyRate.value = newTask.hourly_rate
    }
  } else {
    formData.value = defaultFormData()
    userRole.value = ''
    hourlyRate.value = 0
  }
}, { immediate: true })

const handleSubmit = async () => {
  errorMessage.value = ''
  isSubmitting.value = true

  try {
    if (isEditMode.value) {
      // Update existing task
      await call('frappe.client.set_value', {
        doctype: 'WB Task',
        name: props.task.name,
        fieldname: formData.value
      })
    } else {
      // Create new task
      const taskData = {
        doctype: 'WB Task',
        ...formData.value,
        assign_from: formData.value.assign_from || 'Administrator'
      }

      await call('frappe.client.insert', {
        doc: taskData
      })
    }

    emit('task-saved')
    closeDialog()
  } catch (error) {
    console.error('Error saving task:', error)
    errorMessage.value = error.message || 'Failed to save task. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

const closeDialog = () => {
  isOpen.value = false
  formData.value = defaultFormData()
  errorMessage.value = ''
}
</script>
