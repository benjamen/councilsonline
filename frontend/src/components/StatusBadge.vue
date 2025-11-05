<template>
  <span :class="badgeClasses" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
    <span :class="dotClasses" class="w-1.5 h-1.5 rounded-full mr-1.5"></span>
    {{ status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const statusConfig = {
  'Draft': {
    badge: 'bg-gray-100 text-gray-800',
    dot: 'bg-gray-400'
  },
  'Submitted': {
    badge: 'bg-blue-100 text-blue-800',
    dot: 'bg-blue-400'
  },
  'Under Review': {
    badge: 'bg-yellow-100 text-yellow-800',
    dot: 'bg-yellow-400'
  },
  'RFI Issued': {
    badge: 'bg-orange-100 text-orange-800',
    dot: 'bg-orange-400'
  },
  'Approved': {
    badge: 'bg-green-100 text-green-800',
    dot: 'bg-green-400'
  },
  'Declined': {
    badge: 'bg-red-100 text-red-800',
    dot: 'bg-red-400'
  },
  'Withdrawn': {
    badge: 'bg-gray-100 text-gray-600',
    dot: 'bg-gray-400'
  },
  'Closed': {
    badge: 'bg-gray-100 text-gray-600',
    dot: 'bg-gray-400'
  }
}

const badgeClasses = computed(() => {
  return statusConfig[props.status]?.badge || 'bg-gray-100 text-gray-800'
})

const dotClasses = computed(() => {
  return statusConfig[props.status]?.dot || 'bg-gray-400'
})
</script>
