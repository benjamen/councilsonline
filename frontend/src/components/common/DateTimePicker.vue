<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-4">
      <!-- Date Picker -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ label || 'Select Date' }}
        </label>
        <input
          :value="dateValue"
          @input="updateDate"
          type="date"
          :min="minDate"
          :required="required"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <!-- Time Picker -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Time
        </label>
        <input
          :value="timeValue"
          @input="updateTime"
          type="time"
          :required="required"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
    </div>

    <!-- Quick Time Presets -->
    <div v-if="showPresets" class="flex flex-wrap gap-2">
      <span class="text-xs text-gray-600 w-full mb-1">Quick select:</span>
      <button
        v-for="preset in timePresets"
        :key="preset.value"
        @click.prevent="setTime(preset.value)"
        type="button"
        class="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
      >
        {{ preset.label }}
      </button>
    </div>

    <!-- Display formatted date/time -->
    <div v-if="dateValue && timeValue" class="text-sm text-gray-600 bg-blue-50 p-2 rounded-lg">
      <div class="flex items-center">
        <svg class="h-4 w-4 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span class="font-medium">{{ formattedDateTime }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: 'Select Date & Time'
  },
  required: {
    type: Boolean,
    default: false
  },
  showPresets: {
    type: Boolean,
    default: true
  },
  minDate: {
    type: String,
    default: () => {
      // Default to tomorrow
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      return tomorrow.toISOString().split('T')[0]
    }
  }
})

const emit = defineEmits(['update:modelValue'])

const timePresets = [
  { label: '9:00 AM', value: '09:00' },
  { label: '10:00 AM', value: '10:00' },
  { label: '11:00 AM', value: '11:00' },
  { label: '1:00 PM', value: '13:00' },
  { label: '2:00 PM', value: '14:00' },
  { label: '3:00 PM', value: '15:00' },
  { label: '4:00 PM', value: '16:00' }
]

// Split the ISO datetime into date and time
const dateValue = ref('')
const timeValue = ref('')

// Initialize from modelValue
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    const dt = new Date(newValue)
    if (!isNaN(dt.getTime())) {
      dateValue.value = dt.toISOString().split('T')[0]
      timeValue.value = dt.toTimeString().slice(0, 5)
    }
  }
}, { immediate: true })

const updateDate = (event) => {
  dateValue.value = event.target.value
  emitDateTime()
}

const updateTime = (event) => {
  timeValue.value = event.target.value
  emitDateTime()
}

const setTime = (time) => {
  timeValue.value = time
  emitDateTime()
}

const emitDateTime = () => {
  if (dateValue.value && timeValue.value) {
    const datetime = `${dateValue.value}T${timeValue.value}:00`
    emit('update:modelValue', datetime)
  }
}

const formattedDateTime = computed(() => {
  if (!dateValue.value || !timeValue.value) return ''

  const dt = new Date(`${dateValue.value}T${timeValue.value}`)
  return dt.toLocaleString('en-NZ', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})
</script>
